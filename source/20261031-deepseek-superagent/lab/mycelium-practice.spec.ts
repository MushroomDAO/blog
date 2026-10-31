/** Offline integration exercise, not a live agent or deployment script.
 * Uses the upstream MIT Engine/Store/Effects; harness ideas adapted from its tests.
 * Copyright (c) 2026 Mycelium Protocol; see LICENSE and UPSTREAM_LICENSE.
 */
import { afterEach, expect, it } from 'vitest'
import { mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { Engine, runningAssignment, type Candidate, type Outbox, type Policy, type Trigger } from '../src/core/index.ts'
import { Store } from '../src/app/store.ts'
import { Effects } from '../src/app/effects.ts'
import { HealthBoard } from '../src/infra/health.ts'

const cleanups: (() => Promise<void>)[] = []
afterEach(async () => { for (const close of cleanups.splice(0)) await close() })

function laboratory() {
  const directory = mkdtempSync(join(tmpdir(), 'mycelium-superagent-'))
  const dbPath = join(directory, 'state.sqlite')
  const candidates: Candidate[] = []
  // This fake destination ACCEPTS an idempotency key. GitHub comments do not inherit this guarantee.
  const destination = new Map<string, string>()
  let sendAttempts = 0, failAfterAccept = false
  let clock = Date.parse('2026-10-31T00:00:00Z')
  let store: Store, effects: Effects, engine: Engine, outbox: Outbox
  const policy: Policy = {
    version: 'v1', paused: false, evalTimeoutMs: 60_000,
    gate: t => t.human && t.actor.id === 'alice'
      ? { admissible: true, strength: 'explicit', basis: { via: 'listed' } }
      : { admissible: false, reason: 'not allowed to originate work' },
    revalidate: () => true,
    admitsInferred: () => false,
  }
  function open() {
    store = new Store(dbPath)
    effects = new Effects(store, new HealthBoard(), () => clock)
    outbox = {
      send(message) { store.atomic(() => { if (store.receipts.add(message)) effects.enqueue('reply', message.id, {}) }) },
      status: id => store.receipts.get(id)?.status,
      withdraw(id) { store.atomic(() => { if (store.receipts.withdraw(id)) effects.cancel('reply', id) }) },
    }
    engine = new Engine({
      repo: store, policy: () => policy, scope: { scope: () => ({ listened: true, observed: false }) },
      assessor: { request: candidate => { candidates.push(candidate) } }, // deterministic model stand-in
      executor: {
        start(ticket, assignment) { effects.enqueue('launch', assignment.id, { ticketId: ticket.id, assignmentId: assignment.id }) },
        deliver(ticket) { effects.enqueue('delivery', ticket.id, { ticketId: ticket.id }) },
        stop() {}, // no OS process exists in this offline fixture
      },
      outbox, now: () => new Date(clock).toISOString(),
    })
    effects.handle('launch', async p => { engine.assignmentStarted(p.ticketId, p.assignmentId) })
    effects.handle('delivery', async p => {
      const ticket = store.tickets.get(p.ticketId)!
      const assignment = runningAssignment(ticket)
      if (assignment) engine.inputsDelivered(ticket.id, assignment.id, ticket.undelivered)
    })
    effects.handle('reply', async (_payload, id) => {
      const receipt = store.receipts.get(id)!
      if (receipt.status !== 'pending') return
      sendAttempts++
      if (!destination.has(id)) destination.set(id, receipt.text)
      if (failAfterAccept) { failAfterAccept = false; throw new Error('injected failure after destination accepted') }
      store.receipts.settle(receipt, 'sent')
    }, { retry: [1, 100] })
  }
  open()
  const flush = async () => { effects.start(); await effects.idle() }
  const restart = async () => { await effects.drain(); store.close(); open() }
  cleanups.push(async () => { await effects.drain(); store.close(); rmSync(directory, { recursive: true, force: true }) })
  const event = (id: string, actor = 'alice'): Trigger => ({
    id, source: 'chat', threads: [{ source: 'chat', id: 'topic-1' }], actor: { source: 'chat', id: actor },
    human: true, at: new Date(clock).toISOString(), text: 'Reproduce the CI issue; prepare a patch, do not merge.',
    channel: { source: 'chat', thread: 'topic-1', address: { message: id } }, meta: {},
  })
  function accept() {
    engine.receive(event('request-1')); engine.evaluateDue()
    const candidate = candidates.at(-1)!
    const decision = engine.decide('request-1', { evalId: candidate.evalId, kind: 'accept',
      title: 'Reproduce CI issue', scope: 'Prepare a patch; no merge or deployment', reason: 'explicit request', acknowledgement: 'Accepted for offline exercise' })
    return decision.ticketId!
  }
  return {
    get store() { return store }, get engine() { return engine }, get effects() { return effects }, get outbox() { return outbox },
    get sendAttempts() { return sendAttempts }, policy, candidates, destination, event, accept, flush, restart,
    advance(ms: number) { clock += ms }, injectLostAcknowledgement() { failAfterAccept = true },
  }
}

it('replays the same source event after reopening SQLite without creating another record', async () => {
  const h = laboratory()
  expect(h.engine.receive(h.event('same-id'))).toBe('stored')
  await h.restart()
  expect(h.engine.receive(h.event('same-id'))).toBe('duplicate')
  expect(h.store.db.prepare('SELECT COUNT(*) AS n FROM trigger').get()?.n).toBe(1)
})

it('rejects an unauthorized origin before requesting semantic assessment', () => {
  const h = laboratory()
  h.engine.receive(h.event('guest-origin', 'guest')); h.engine.evaluateDue()
  expect(h.candidates).toHaveLength(0)
  expect(h.store.tickets.list()).toHaveLength(0)
})

it('recovers a queued assignment from SQLite without creating a second ticket', async () => {
  const h = laboratory(); const id = h.accept()
  await h.restart(); await h.flush()
  expect(h.store.tickets.list()).toHaveLength(1)
  expect(runningAssignment(h.store.tickets.get(id)!)?.state).toBe('running')
  expect(h.engine.receive(h.event('request-1'))).toBe('duplicate')
})

it('delivers subscribed follow-up as context without a new assessment or wider mandate', async () => {
  const h = laboratory(); const id = h.accept(); await h.flush()
  const before = h.store.tickets.get(id)!.mandate
  // A guest on an already subscribed topic can supply context; that is NOT new authority.
  h.engine.receive(h.event('followup-2', 'guest')); h.engine.evaluateDue(); await h.flush()
  const ticket = h.store.tickets.get(id)!
  expect(h.candidates).toHaveLength(1)
  expect(ticket.mandate).toEqual(before)
  expect(ticket.inputs.some(i => i.kind === 'trigger' && i.triggerId === 'followup-2')).toBe(true)
})

it('distinguishes worker-ready from the owned pull request actually being merged', async () => {
  const h = laboratory(); const id = h.accept(); await h.flush()
  const pr = { source: 'github', id: 'pull-7' }
  h.engine.bindThread(id, pr, true)
  h.engine.report(id, { state: 'ready', summary: 'Patch prepared; awaiting reviewer' })
  expect(h.store.tickets.get(id)!.ended).toBeUndefined()
  h.advance(1000); h.engine.threadClosed(pr, 'merged', '2026-10-31T00:00:01.000Z')
  expect(h.store.tickets.get(id)!.ended?.outcome).toBe('merged')
})

it('rolls back a durable outbox receipt and delivery effect together', async () => {
  const h = laboratory()
  expect(() => h.store.atomic(() => {
    h.outbox.send({ id: 'rolled-back', kind: 'notice', text: 'Never send', channel: { source: 'chat', thread: 'topic-1', address: {} } })
    throw new Error('transaction abort')
  })).toThrow('transaction abort')
  await h.flush()
  expect(h.outbox.status('rolled-back')).toBeUndefined()
  expect(h.destination.size).toBe(0)
})

it('retries an ambiguous delivery using a destination idempotency key, not an exactly-once claim', async () => {
  const h = laboratory(); h.injectLostAcknowledgement()
  h.outbox.send({ id: 'stable-message-key', kind: 'notice', text: 'One logical result', channel: { source: 'chat', thread: 'topic-1', address: {} } })
  await h.flush()
  expect(h.outbox.status('stable-message-key')).toBe('pending')
  expect(h.destination.size).toBe(1)
  await h.restart(); h.advance(2); await h.flush()
  expect(h.sendAttempts).toBe(2)
  expect(h.outbox.status('stable-message-key')).toBe('sent')
  expect(h.destination.size).toBe(1)
})
