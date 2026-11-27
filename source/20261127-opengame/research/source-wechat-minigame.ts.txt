/** Local-only WeChat Mini Game publication. No credentials leave this service's responses. */
import { chmod, lstat, mkdir, mkdtemp, readdir, readFile, rename, rm, writeFile } from 'node:fs/promises';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import type { WechatCiJob, WechatCiResult } from './wechat-ci-worker.ts';
import type { Readable } from 'node:stream';
import { randomUUID } from 'node:crypto';
import { homedir, tmpdir } from 'node:os';
import path from 'node:path';
import { GameError, gameProjectsFor } from '../game-projects.ts';

export type ConfirmStep = 'account' | 'testers' | 'category' | 'review' | 'filing' | 'release';
type StepKey = ConfirmStep | 'appid' | 'key' | 'ip' | 'port' | 'preview' | 'upload';
type PublishState = {
  appid?: string;
  confirmed: Partial<Record<ConfirmStep, string>>;
  ipCheck?: { allowed: boolean; ip?: string; checkedAt: string };
  preview?: { createdAt: string };
  upload?: { state: 'done' | 'failed' | 'unknown'; version: string; desc: string; at: string; error?: string };
  uploadedVersion?: string;
  /** WeChat refused the saved key (wrong file, or a key for another AppID). Cleared by a later success; a key saved after it also clears it. */
  keyRejected?: { at: string };
  updatedAt: string;
};
const confirmSteps: ConfirmStep[] = ['account', 'testers', 'category', 'review', 'filing', 'release'];
const stepKeys: StepKey[] = ['account', 'appid', 'key', 'ip', 'port', 'preview', 'upload', 'testers', 'category', 'review', 'filing', 'release'];
const gameBusy = new Set<string>();
/** WeChat's answers when the key does not match the AppID or cannot be read (signature/decoding failures). */
const keyRejection = /signature|private ?key|PEM|decod|asn1|bad key|key.*(invalid|mismatch)|(invalid|mismatch).*key|签名|密钥|私钥/i;
const unknownUpload = /did not answer in time|ETIMEDOUT|ECONNRESET|socket hang up|exited without a result|Invalid WeChat worker result/i;
/**
 * A newly uploaded package is a development version again: the trial-version choice, review and release confirmed
 * for the previous upload no longer apply. Category and filing belong to the Mini Game and stay.
 */
function newVersionUploaded(state: PublishState, version: string) {
  // Any accepted upload is new code (even under the same version number), so these must be confirmed again.
  for (const step of ['testers', 'review', 'release'] as const) delete state.confirmed[step];
  state.uploadedVersion = version;
}

type Ci = {
  Project: new (options: { appid: string; type: 'miniGame'; projectPath: string; privateKeyPath: string; ignores: string[] }) => unknown;
  preview: (options: any) => Promise<unknown>;
  upload: (options: any) => Promise<any>;
};
type Options = {
  keyDirectory?: string;
  loadCi?: () => Promise<Ci>;
  workerPath?: string;
  workerTimeoutMs?: number;
  platform?: NodeJS.Platform;
  env?: NodeJS.ProcessEnv;
};
export class PublishError extends Error {
  status: number;
  code: string;
  constructor(status: number, code: string, message: string) { super(message); this.status = status; this.code = code; }
}
const busy = new Set<string>();
const services = new Map<string, WechatMinigame>();
const validAppid = /^wx[0-9a-f]{16}$/i;
function appId(value: unknown): string {
  if (typeof value !== 'string' || !validAppid.test(value)) throw new PublishError(400, 'INVALID_APPID', 'Invalid WeChat appid');
  return value.toLowerCase();
}
async function info(file: string) {
  try { return await lstat(file); }
  catch (error) { if ((error as NodeJS.ErrnoException).code === 'ENOENT') return null; throw error; }
}
function scrub(message: string, keyPath = '', key = '') {
  let result = message;
  if (key) result = result.split(key).join('[redacted key]');
  if (keyPath) for (const source of [keyPath, path.dirname(keyPath)]) {
    for (const value of [source, source.replaceAll('\\', '/'), source.replaceAll('\\', '\\\\')]) result = result.split(value).join('[redacted key path]');
  }
  // Also remove PEM bodies echoed with escaped newlines, or truncated by the SDK.
  return result.replace(/-----BEGIN[\s\S]*?(?:-----END[^\r\n]*?-----|$)/g, '[redacted key]');
}
function ciMessage(error: unknown, keyPath: string, key: string) {
  const value = error as { message?: unknown; errCode?: unknown; errMsg?: unknown } | null;
  const message = String(value?.message ?? error).replace(/^(?:(?:Error|CodeError):\s*)+/, '');
  const detail = value?.errCode !== undefined || value?.errMsg !== undefined ? `${String(value?.errCode ?? '')}: ${String(value?.errMsg ?? '')}` : '';
  return scrub(detail ? `${message}; ${detail}` : message, keyPath, key);
}

export class WechatMinigame {
  readonly keyDirectory: string;
  private workspace: string;
  private options: Options;
  constructor(workspace: string, options: Options = {}) {
    this.workspace = workspace;
    this.options = options;
    this.keyDirectory = options.keyDirectory ?? path.join(homedir(), '.config', 'opendesign-wechat');
  }
  private keyPath(appid: string) { return path.join(this.keyDirectory, `private.${appid}.key`); }
  private async keyInfo(appid: string) {
    const entry = await info(this.keyPath(appid));
    return entry?.isFile() && !entry.isSymbolicLink() ? entry : null;
  }
  private async publishDirectory(id: string, create = false) {
    const { dir } = await gameProjectsFor(this.workspace).locate(id);
    const directory = path.join(dir, 'publish');
    if (create) await mkdir(directory, { mode: 0o700, recursive: true });
    const entry = await info(directory);
    if (entry && (!entry.isDirectory() || entry.isSymbolicLink())) throw new PublishError(400, 'INVALID_STATE', 'Invalid WeChat publish directory');
    return directory;
  }
  private async publishFile(id: string, name: string, create = false) {
    const file = path.join(await this.publishDirectory(id, create), name);
    const entry = await info(file);
    if (entry && (!entry.isFile() || entry.isSymbolicLink())) throw new PublishError(400, 'INVALID_STATE', 'Invalid WeChat publish file');
    return file;
  }
  private async readState(id: string): Promise<PublishState> {
    const file = await this.publishFile(id, 'wechat.json');
    try { return JSON.parse(await readFile(file, 'utf8')); }
    catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'ENOENT') return { confirmed: {}, updatedAt: new Date().toISOString() };
      throw new PublishError(400, 'INVALID_STATE', 'Cannot read WeChat publish state');
    }
  }
  private async writePublishFile(id: string, name: string, data: string | Buffer) {
    const file = await this.publishFile(id, name, true);
    const temp = path.join(path.dirname(file), `.${randomUUID()}.tmp`);
    try {
      await writeFile(temp, data, { mode: 0o600, flag: 'wx' });
      await rename(temp, file);
    } finally { await rm(temp, { force: true }); }
  }
  private previewUrl(id: string) { return `/motion-api/publish/wechat/preview-image/${encodeURIComponent(id)}`; }
  async status(id: string) {
    const state = await this.readState(id);
    const project = await this.project(id);
    const game = await gameProjectsFor(this.workspace).get(id);
    let smokeTest: unknown;
    try { smokeTest = JSON.parse(await readFile(path.join(project.projectDir, 'port-report.json'), 'utf8')).smokeTest; }
    catch { /* Missing or malformed reports do not establish a verified port. */ }
    const portReady = project.hasGameJs && project.hasGameJson && project.totalBytes <= project.mainPackageLimitBytes && smokeTest === 'passed';
    const keyEntry = state.appid ? await this.keyInfo(state.appid) : undefined;
    const hasKey = Boolean(keyEntry);
    const keyRejected = Boolean(hasKey && state.keyRejected && keyEntry!.mtime.getTime() <= Date.parse(state.keyRejected.at));
    const steps = stepKeys.map(key => {
      let status: 'done' | 'todo' | 'blocked' | 'unknown' = 'todo';
      let at: string | undefined, detail: string | undefined;
      if (key === 'appid' && state.appid || key === 'key' && hasKey || key === 'port' && portReady) status = 'done';
      if (confirmSteps.includes(key as ConfirmStep)) {
        at = state.confirmed[key as ConfirmStep];
        if (at || key === 'account' && state.appid) status = 'done';
      }
      if (key === 'ip' && state.ipCheck) {
        status = state.ipCheck.allowed ? 'done' : 'blocked'; at = state.ipCheck.checkedAt;
        if (!state.ipCheck.allowed) detail = state.ipCheck.ip;
      }
      if (key === 'preview' && state.preview) { status = 'done'; at = state.preview.createdAt; }
      if (key === 'upload' && state.upload) {
        status = state.upload.state === 'failed' ? 'blocked' : state.upload.state; at = state.upload.at;
        if (state.upload.state === 'failed') detail = state.upload.error;
      }
      return { key, status, later: ['category', 'review', 'filing', 'release'].includes(key), ...(at ? { at } : {}), ...(detail ? { detail } : {}) };
    });
    const version = state.uploadedVersion?.split('.');
    const nextVersion = version ? `${version[0]}.${version[1]}.${BigInt(version[2]) + 1n}` : '1.0.0';
    return {
      gameId: id, appid: state.appid ?? null, hasKey, keyRejected,
      project: { exists: project.exists, hasGameJs: project.hasGameJs, hasGameJson: project.hasGameJson,
        totalBytes: project.totalBytes, mainPackageLimitBytes: project.mainPackageLimitBytes, portReady },
      steps, current: steps.find(step => !step.later && step.status !== 'done')?.key ?? steps.find(step => step.later && step.status !== 'done')?.key ?? null,
      ipCheck: state.ipCheck ?? null, preview: state.preview ? { ...state.preview, qrcodeUrl: this.previewUrl(id) } : null,
      upload: state.upload ?? null, uploadedVersion: state.uploadedVersion ?? null, nextVersion,
      game: { title: game.title, description: game.description, controls: game.controls },
    };
  }
  /** Shared MCP and panel operation; only CI internals ever receive credential paths/text. */
  async action(input: any) {
    const actions = ['status', 'set_appid', 'confirm', 'confirm_upload', 'ip_check', 'preview', 'upload'];
    if (!input || typeof input !== 'object' || Array.isArray(input)
      || Object.keys(input).some(key => !['id', 'action', 'appid', 'step', 'version', 'desc', 'confirmMissing', 'present'].includes(key))
      || !actions.includes(input.action)
      || typeof input.id !== 'string' || !/^[a-zA-Z0-9][a-zA-Z0-9_-]{0,100}$/.test(input.id)) {
      throw new PublishError(400, 'INVALID_REQUEST', 'A game id and valid WeChat action are required');
    }
    if (input.appid !== undefined) appId(input.appid);
    if (input.version !== undefined && (typeof input.version !== 'string' || !/^\d+\.\d+\.\d+$/.test(input.version))) throw new PublishError(400, 'INVALID_VERSION', 'Version must have the form 1.0.0');
    if (input.desc !== undefined && (typeof input.desc !== 'string' || input.desc.length > 200)) throw new PublishError(400, 'INVALID_DESC', 'Description must be at most 200 characters');
    if (input.step !== undefined && !confirmSteps.includes(input.step)) throw new PublishError(400, 'INVALID_STEP', 'Invalid confirmation step');
    for (const field of ['present', 'confirmMissing']) if (input[field] !== undefined && typeof input[field] !== 'boolean') throw new PublishError(400, 'INVALID_REQUEST', `${field} must be a boolean`);
    const lock = `${path.resolve(this.workspace)}:${input.id}`;
    if (input.action !== 'status' && gameBusy.has(lock)) throw new PublishError(409, 'BUSY', 'A WeChat operation is already running for this game');
    if (input.action !== 'status') gameBusy.add(lock);
    try {
      if (input.action === 'status') return await this.status(input.id);
      const state = await this.readState(input.id);
      const now = new Date().toISOString();
      let result: Record<string, unknown> | undefined;
      if (input.action === 'set_appid') {
        const appid = appId(input.appid);
        if (appid !== state.appid) {
          state.appid = appid;
          delete state.ipCheck; delete state.preview; delete state.upload; delete state.uploadedVersion; delete state.keyRejected;
          // A different AppID is a different Mini Game: steps confirmed for the old one (testers, review, filing…) do not carry over.
          // The account itself stays confirmed, since the user has one.
          state.confirmed = state.confirmed.account ? { account: state.confirmed.account } : {};
          await rm(await this.publishFile(input.id, 'wechat-preview.png'), { force: true });
        }
      } else if (input.action === 'confirm') {
        if (!confirmSteps.includes(input.step)) throw new PublishError(400, 'INVALID_STEP', 'A confirmation step is required');
        if (['testers', 'review', 'release'].includes(input.step) && state.upload?.state !== 'done') throw new PublishError(409, 'UPLOAD_REQUIRED', 'Confirm a successful upload before this step');
        state.confirmed[input.step as ConfirmStep] = now;
      } else if (input.action === 'confirm_upload') {
        if (typeof input.present !== 'boolean') throw new PublishError(400, 'INVALID_REQUEST', 'present must be a boolean');
        if (state.upload?.state !== 'unknown') throw new PublishError(409, 'UPLOAD_NOT_UNKNOWN', 'There is no uncertain upload to confirm');
        state.upload.state = input.present ? 'done' : 'failed';
        if (input.present) { newVersionUploaded(state, state.upload.version); delete state.upload.error; }
        else state.upload.error = 'Not in Version management';
        result = { outcome: state.upload.state, version: state.upload.version };
      } else {
        if (!state.appid) throw new PublishError(400, 'APPID_REQUIRED', 'Set the game AppID first');
        // A refused key is recorded before the error goes back, so the page can offer to replace the key file.
        const keyRefused = async (error: unknown) => {
          if (error instanceof PublishError && error.code === 'WECHAT_CI_ERROR' && keyRejection.test(error.message)) {
            state.keyRejected = { at: new Date().toISOString() };
            state.updatedAt = state.keyRejected.at;
            await this.writePublishFile(input.id, 'wechat.json', JSON.stringify(state, null, 2) + '\n');
          }
          return error;
        };
        if (input.action === 'ip_check') {
          const checked = await this.ipCheck({ appid: state.appid }).catch(async error => { throw await keyRefused(error); });
          delete state.keyRejected;
          state.ipCheck = { allowed: checked.allowed, ...('ip' in checked ? { ip: checked.ip } : {}), checkedAt: checked.checkedAt };
          result = { allowed: checked.allowed, ...('ip' in checked ? { ip: checked.ip } : {}) };
        } else if (input.action === 'preview') {
          const preview = await this.publish('preview', { appid: state.appid, gameId: input.id }).catch(async error => { throw await keyRefused(error); });
          delete state.keyRejected;
          const data = preview as { qrcode: string; createdAt: string };
          await this.writePublishFile(input.id, 'wechat-preview.png', Buffer.from(data.qrcode.split(',')[1], 'base64'));
          state.preview = { createdAt: data.createdAt };
          result = { createdAt: data.createdAt, qrcodeUrl: this.previewUrl(input.id) };
        } else {
          const version = input.version ?? (await this.status(input.id)).nextVersion;
          if (state.upload?.state === 'unknown' && state.upload.version === version && input.confirmMissing !== true) throw new PublishError(409, 'UPLOAD_UNCONFIRMED', 'Check Version management → Development versions, then confirm_upload before retrying this version');
          const desc = scrub(input.desc ?? 'OpenDesign upload', this.keyPath(state.appid));
          try {
            await this.publish('upload', { appid: state.appid, gameId: input.id, version, desc });
            state.upload = { state: 'done', version, desc, at: new Date().toISOString() };
            delete state.keyRejected;
            newVersionUploaded(state, version);
            result = { outcome: 'done', version };
          } catch (error) {
            if (error instanceof PublishError && error.code === 'BUSY') throw error;
            const message = error instanceof PublishError ? error.message : 'WeChat local operation failed';
            const outcome = unknownUpload.test(message) ? 'unknown' : 'failed';
            if (outcome === 'failed' && keyRejection.test(message)) state.keyRejected = { at: new Date().toISOString() };
            state.upload = { state: outcome, version, desc, at: new Date().toISOString(), error: message };
            result = outcome === 'unknown'
              ? { outcome, version, checkWhere: 'Mini Program console → Management → Version management → Development versions' }
              : { outcome, message };
          }
        }
      }
      state.updatedAt = new Date().toISOString();
      await this.writePublishFile(input.id, 'wechat.json', JSON.stringify(state, null, 2) + '\n');
      return { ...await this.status(input.id), ...(result ? { result } : {}) };
    } catch (error) {
      if (error instanceof PublishError) throw error;
      if (error instanceof GameError) throw new PublishError(error.status, 'PROJECT_MISSING', error.message);
      throw new PublishError(500, 'WECHAT_LOCAL_ERROR', 'WeChat local operation failed');
    } finally { if (input.action !== 'status') gameBusy.delete(lock); }
  }
  private async environment() {
    const platform = this.options.platform ?? process.platform;
    const env = this.options.env ?? process.env;
    const candidates = platform === 'darwin' ? ['/Applications/wechatwebdevtools.app'] : platform === 'win32'
      ? [env['ProgramFiles(x86)'], env.ProgramFiles].filter(Boolean).map(root => path.win32.join(root!, 'Tencent', '微信web开发者工具', 'cli.bat')) : [];
    let found: string | null = null;
    for (const candidate of candidates) if (await info(candidate)) { found = candidate; break; }
    // No public-IP lookup: behind a proxy it reports the proxy's address, not the one WeChat sees. ipCheck asks WeChat itself.
    return { devtools: { installed: found !== null, path: found, platform } };
  }
  private async project(gameId: unknown) {
    if (typeof gameId !== 'string') throw new PublishError(400, 'PROJECT_MISSING', 'A game id is required');
    let dir: string;
    try { ({ dir } = await gameProjectsFor(this.workspace).locate(gameId)); }
    catch { throw new PublishError(400, 'PROJECT_MISSING', 'Game project not found'); }
    const projectDir = path.resolve(dir, 'wechat-minigame');
    const root = await info(projectDir);
    if (root?.isSymbolicLink() || (root && !root.isDirectory())) throw new PublishError(400, 'PROJECT_MISSING', 'Invalid WeChat project directory');
    const files: { path: string; bytes: number }[] = [];
    let totalBytes = 0;
    const walk = async (prefix = '') => {
      for (const entry of await readdir(path.join(projectDir, prefix), { withFileTypes: true })) {
        const relative = prefix ? `${prefix}/${entry.name}` : entry.name;
        // miniprogram-ci also packs dotfiles and follows links, so every entry is checked, hidden or not.
        if (entry.isSymbolicLink()) throw new PublishError(400, 'PROJECT_MISSING', `Symlinks are not allowed in WeChat projects: ${relative}`);
        if (entry.name.startsWith('.') || entry.name === 'node_modules') {
          if (entry.isDirectory()) await walkLinksOnly(relative);
          continue;
        }
        if (entry.isDirectory()) await walk(relative);
        else if (entry.isFile()) {
          const bytes = (await lstat(path.join(projectDir, relative))).size;
          totalBytes += bytes;
          if (files.length < 500) files.push({ path: relative, bytes });
        }
      }
    };
    // Hidden and node_modules folders are not listed, but must not hide a link either.
    const walkLinksOnly = async (prefix: string): Promise<void> => {
      for (const entry of await readdir(path.join(projectDir, prefix), { withFileTypes: true })) {
        const relative = `${prefix}/${entry.name}`;
        if (entry.isSymbolicLink()) throw new PublishError(400, 'PROJECT_MISSING', `Symlinks are not allowed in WeChat projects: ${relative}`);
        if (entry.isDirectory()) await walkLinksOnly(relative);
      }
    };
    if (root) await walk();
    const hasFile = async (name: string) => Boolean((await info(path.join(projectDir, name)))?.isFile());
    return { gameId, projectDir, exists: Boolean(root), files, totalBytes, mainPackageLimitBytes: 4194304,
      hasGameJs: await hasFile('game.js'), hasGameJson: await hasFile('game.json'), hasProjectConfig: await hasFile('project.config.json') };
  }
  private async save(body: any) {
    const appid = appId(body?.appid);
    const key = body?.privateKey;
    if (typeof key !== 'string' || !key.includes('-----BEGIN') || !key.includes('PRIVATE KEY-----')) throw new PublishError(400, 'INVALID_KEY', 'A PEM private key is required');
    if (Buffer.byteLength(JSON.stringify(body)) > 16 * 1024) throw new PublishError(400, 'INVALID_KEY', 'Credentials exceed 16 KB');
    await mkdir(this.keyDirectory, { recursive: true, mode: 0o700 });
    if ((await lstat(this.keyDirectory)).isSymbolicLink()) throw new Error('Invalid credential directory');
    await chmod(this.keyDirectory, 0o700);
    const target = this.keyPath(appid), temp = path.join(this.keyDirectory, `.${randomUUID()}.tmp`);
    try {
      await writeFile(temp, key, { flag: 'wx', mode: 0o600 });
      await chmod(temp, 0o600);
      await rename(temp, target);
      return { appid, hasKey: true, savedAt: (await this.keyInfo(appid))!.mtime.toISOString() };
    } finally { await rm(temp, { force: true }); }
  }
  /** SDK subprocess failures, noisy logs and unhandled rejections cannot reach the daemon. */
  private runWorker(job: WechatCiJob): Promise<unknown> {
    return new Promise((resolve, reject) => {
      const child = spawn(process.execPath, ['--experimental-strip-types',
        this.options.workerPath ?? fileURLToPath(new URL('./wechat-ci-worker.ts', import.meta.url))],
      { stdio: ['pipe', 'pipe', 'pipe', 'pipe'] });
      let stderr = Buffer.alloc(0), protocol = '';
      let result: WechatCiResult | undefined, failure: Error | undefined;
      let settled = false;
      const finish = () => {
        if (settled) return;
        settled = true;
        clearTimeout(timer);
        if (failure) return reject(failure);
        if (!result) return reject(new Error(`WeChat worker exited without a result${stderr.length ? ': ' + stderr.toString('utf8').slice(-1900) : ''}`));
        if (result.ok === false) {
          if (result.errCode === 'WECHAT_CI_MISSING') return reject(new PublishError(500, 'WECHAT_CI_MISSING', 'miniprogram-ci could not be loaded'));
          return reject(new Error(result.message));
        }
        resolve(result.data);
      };
      const timer = setTimeout(() => {
        failure = new Error('WeChat did not answer in time');
        child.kill('SIGKILL');
      }, this.options.workerTimeoutMs ?? 180_000);
      child.on('error', error => { failure = error; finish(); });
      child.on('close', finish);
      // Drain SDK chatter without forwarding potentially sensitive logs or treating them as protocol.
      child.stdout!.on('error', error => { failure = error; child.kill('SIGKILL'); });
      child.stdout!.resume();
      child.stderr!.on('error', error => { failure = error; child.kill('SIGKILL'); });
      child.stderr!.on('data', (chunk: Buffer) => { stderr = Buffer.concat([stderr, chunk]).subarray(-2048); });
      const channel = child.stdio[3] as Readable;
      channel.setEncoding('utf8');
      channel.on('error', error => { failure = error; child.kill('SIGKILL'); });
      channel.on('data', (chunk: string) => {
        if (result || failure) return;
        protocol += chunk;
        const newline = protocol.indexOf('\n');
        if (Buffer.byteLength(protocol) > 64 * 1024) failure = new Error('Invalid WeChat worker result');
        else if (newline >= 0) {
          try {
            const value = JSON.parse(protocol.slice(0, newline));
            if (!value || typeof value.ok !== 'boolean' || (!value.ok && typeof value.message !== 'string')) throw new Error();
            result = value;
          } catch { failure = new Error('Invalid WeChat worker result'); }
        }
        if (result || failure) child.kill('SIGKILL');
      });
      // EPIPE is expected if the child fails before reading the job; close still collects stderr.
      child.stdin!.on('error', () => {});
      child.stdin!.end(JSON.stringify(job));
    });
  }
  private async publish(kind: 'preview' | 'upload', body: any) {
    const appid = appId(body?.appid);
    if (kind === 'upload') {
      if (typeof body?.version !== 'string' || !/^\d+\.\d+\.\d+$/.test(body.version)) throw new PublishError(400, 'INVALID_VERSION', 'Version must have the form 1.0.0');
      if (typeof body?.desc !== 'string' || body.desc.length > 200) throw new PublishError(400, 'INVALID_DESC', 'Description must be at most 200 characters');
    }
    if (busy.has(appid)) throw new PublishError(409, 'BUSY', 'A WeChat preview or upload is already running for this appid');
    busy.add(appid);
    let temp: string | undefined;
    try {
      if (!await this.keyInfo(appid)) throw new PublishError(400, 'KEY_MISSING', 'Save a private key first');
      const projectInfo = await this.project(body?.gameId);
      if (!projectInfo.exists || !projectInfo.hasGameJs || !projectInfo.hasGameJson) throw new PublishError(400, 'PROJECT_MISSING', 'WeChat project requires game.js and game.json');
      const privateKeyPath = this.keyPath(appid);
      const key = await readFile(privateKeyPath, 'utf8');
      try {
        if (kind === 'preview') temp = await mkdtemp(path.join(tmpdir(), 'openmotion-wechat-'));
        const png = temp ? path.join(temp, 'qrcode.png') : undefined;
        let result: any;
        if (this.options.loadCi) {
          let ci: Ci;
          try { ci = await this.options.loadCi(); }
          catch { throw new PublishError(500, 'WECHAT_CI_MISSING', 'miniprogram-ci could not be loaded'); }
          const project = new ci.Project({ appid, type: 'miniGame', projectPath: projectInfo.projectDir, privateKeyPath, ignores: ['node_modules/**/*', 'mock-*.js', 'port-report.json'] });
          const common = { project, setting: { es6: true, minify: true }, robot: 1, onProgressUpdate: () => {} };
          result = kind === 'preview'
            ? await ci.preview({ ...common, desc: 'OpenDesign preview', qrcodeFormat: 'image', qrcodeOutputDest: png })
            : await ci.upload({ ...common, version: body.version, desc: body.desc });
        } else {
          result = await this.runWorker({ kind, appid, projectPath: projectInfo.projectDir, privateKeyPath,
            ...(kind === 'preview' ? { qrcodeOutputDest: png } : { version: body.version, desc: body.desc }) });
        }
        if (kind === 'preview') return { appid, qrcode: `data:image/png;base64,${(await readFile(png!)).toString('base64')}`, createdAt: new Date().toISOString() };
        return { appid, version: body.version, uploadedAt: new Date().toISOString(), ...(result?.subPackageInfo !== undefined ? { subPackageInfo: result.subPackageInfo } : {}) };
      } catch (error) {
        if (error instanceof PublishError && error.code === 'WECHAT_CI_MISSING') throw error;
        throw new PublishError(502, 'WECHAT_CI_ERROR', ciMessage(error, privateKeyPath, key));
      }
    } finally {
      try { if (temp) await rm(temp, { recursive: true, force: true }); }
      finally { busy.delete(appid); }
    }
  }
  /**
   * Asks WeChat which address it sees: previews a two-file throwaway project (nothing is uploaded or
   * versioned). WeChat answers -10008 "invalid ip: X" when X is not on the upload IP allowlist.
   */
  private async ipCheck(body: any) {
    const appid = appId(body?.appid);
    if (busy.has(appid)) throw new PublishError(409, 'BUSY', 'A WeChat preview or upload is already running for this appid');
    busy.add(appid);
    let temp: string | undefined;
    try {
      if (!await this.keyInfo(appid)) throw new PublishError(400, 'KEY_MISSING', 'Save a private key first');
      const privateKeyPath = this.keyPath(appid);
      const key = await readFile(privateKeyPath, 'utf8');
      temp = await mkdtemp(path.join(tmpdir(), 'openmotion-wechat-ip-'));
      const projectPath = path.join(temp, 'project');
      await mkdir(projectPath);
      await writeFile(path.join(projectPath, 'game.js'), '// OpenDesign IP allowlist check\n');
      await writeFile(path.join(projectPath, 'game.json'), JSON.stringify({ deviceOrientation: 'portrait' }));
      const png = path.join(temp, 'qrcode.png');
      try {
        if (this.options.loadCi) {
          const ci = await this.options.loadCi();
          const project = new ci.Project({ appid, type: 'miniGame', projectPath, privateKeyPath, ignores: [] });
          await ci.preview({ project, setting: { es6: true, minify: true }, robot: 2, desc: 'OpenDesign IP check', qrcodeFormat: 'image', qrcodeOutputDest: png, onProgressUpdate: () => {} });
        } else {
          await this.runWorker({ kind: 'preview', appid, projectPath, privateKeyPath, qrcodeOutputDest: png, desc: 'OpenDesign IP check' });
        }
        return { appid, allowed: true, checkedAt: new Date().toISOString() };
      } catch (error) {
        if (error instanceof PublishError && error.code === 'WECHAT_CI_MISSING') throw error;
        const message = ciMessage(error, privateKeyPath, key);
        const ip = /invalid ip:\s*([0-9a-f:.]*[0-9a-f])/i.exec(message)?.[1];
        if (ip) return { appid, allowed: false, ip, checkedAt: new Date().toISOString() };
        throw new PublishError(502, 'WECHAT_CI_ERROR', message);
      }
    } finally {
      try { if (temp) await rm(temp, { recursive: true, force: true }); }
      finally { busy.delete(appid); }
    }
  }
  /** Routing adapter passes its bounded JSON reader; malformed inputs never echo request contents. */
  async handle(method: string, pathname: string, readBody: () => Promise<any> = async () => ({})) {
    try {
      const suffix = pathname.slice('/api/publish/wechat'.length);
      let body: any;
      if (['PUT', 'POST'].includes(method)) {
        try { body = await readBody(); }
        catch { throw new PublishError(400, 'INVALID_REQUEST', 'Expected JSON body of at most 16 KB'); }
      }
      let data: unknown;
      if (method === 'GET' && suffix === '/environment') data = await this.environment();
      else if (method === 'GET' && /^\/state\/[^/]+$/.test(suffix)) data = await this.action({ id: decodeURIComponent(suffix.slice('/state/'.length)), action: 'status' });
      else if (method === 'POST' && /^\/state\/[^/]+\/(appid|confirm)$/.test(suffix)) {
        const [, , id, action] = suffix.split('/');
        data = await this.action({ ...body, id: decodeURIComponent(id), action: action === 'appid' ? 'set_appid' : 'confirm' });
      } else if (method === 'GET' && /^\/preview-image\/[^/]+$/.test(suffix)) {
        const id = decodeURIComponent(suffix.slice('/preview-image/'.length));
        const state = await this.readState(id);
        const file = await this.publishFile(id, 'wechat-preview.png');
        if (!state.preview || !await info(file)) throw new PublishError(404, 'NOT_FOUND', 'WeChat preview image not found');
        return { status: 200, data: await readFile(file), contentType: 'image/png' as const };
      }
      else if (method === 'GET' && /^\/project\/[^/]+$/.test(suffix)) data = await this.project(decodeURIComponent(suffix.slice('/project/'.length)));
      else if (method === 'GET' && suffix === '/credentials') {
        const saved: { appid: string; savedAt: string }[] = [];
        for (const file of await readdir(this.keyDirectory).catch(error => { if (error.code === 'ENOENT') return []; throw error; })) {
          const match = /^private\.(.+)\.key$/.exec(file);
          if (!match || !validAppid.test(match[1])) continue;
          const appid = match[1], entry = await this.keyInfo(appid);
          if (entry) saved.push({ appid, savedAt: entry.mtime.toISOString() });
        }
        data = { saved: saved.sort((a, b) => a.appid.localeCompare(b.appid)) };
      } else if (suffix === '/credentials' && method === 'PUT') data = await this.save(body);
      else if (/^\/credentials\/[^/]+$/.test(suffix) && ['GET', 'DELETE'].includes(method)) {
        const appid = appId(decodeURIComponent(suffix.slice('/credentials/'.length)));
        if (method === 'DELETE') { await rm(this.keyPath(appid), { force: true }); data = { appid, hasKey: false }; }
        else { const entry = await this.keyInfo(appid); data = { appid, hasKey: Boolean(entry), savedAt: entry?.mtime.toISOString() ?? null }; }
      } else if (method === 'POST' && suffix === '/ip-check') data = await this.ipCheck(body);
      else if (method === 'POST' && (suffix === '/preview' || suffix === '/upload')) data = await this.publish(suffix.slice(1) as 'preview' | 'upload', body);
      else throw new PublishError(404, 'NOT_FOUND', 'WeChat publish endpoint not found');
      return { status: 200, data };
    } catch (error) {
      return { status: error instanceof PublishError || error instanceof GameError ? error.status : 500, data: { error: {
        code: error instanceof PublishError ? error.code : error instanceof GameError ? 'PROJECT_MISSING' : 'WECHAT_LOCAL_ERROR',
        message: error instanceof PublishError || error instanceof GameError ? error.message : 'WeChat local operation failed',
      } } };
    }
  }
}
export function wechatMinigameFor(workspace: string) {
  const root = path.resolve(workspace);
  if (!services.has(root)) services.set(root, new WechatMinigame(root));
  return services.get(root)!;
}
