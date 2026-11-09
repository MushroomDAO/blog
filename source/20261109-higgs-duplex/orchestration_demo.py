"""Local orchestration example, not a model or Boson API implementation.

Run: python3 orchestration_demo.py
No networking, microphone, model weights, avatar rendering, or API credentials.
In-memory call IDs are not durable exactly-once execution or authorization.
"""
import asyncio
from collections import deque
import unittest


class Coordinator:
    def __init__(self):
        self.generation = 0
        self.playback = deque(maxlen=4)
        self.jobs = {}

    def audio(self, generation, chunk):
        if generation != self.generation:
            return False
        self.playback.append(chunk)
        return True

    def interrupt(self):
        self.generation += 1
        self.playback.clear()
        return self.generation

    def start_job(self, call_id, operation):
        if call_id not in self.jobs:
            self.jobs[call_id] = asyncio.create_task(operation())
        return self.jobs[call_id]

    async def cancel_job(self, call_id):
        task = self.jobs[call_id]
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)


class OrchestrationChecks(unittest.IsolatedAsyncioTestCase):
    async def test_pending_tool_does_not_block_new_audio_events(self):
        c = Coordinator()
        started, release = asyncio.Event(), asyncio.Event()
        async def lookup():
            started.set()
            await release.wait()
            return {"answer": 42}
        task = c.start_job("lookup", lookup)
        await started.wait()
        self.assertFalse(task.done())
        self.assertTrue(c.audio(0, b"speech"))
        self.assertEqual(list(c.playback), [b"speech"])
        release.set()
        self.assertEqual(await task, {"answer": 42})

    async def test_barge_in_flushes_playback_and_rejects_old_generation(self):
        c = Coordinator()
        c.audio(0, b"queued old speech")
        new = c.interrupt()
        self.assertEqual(list(c.playback), [])
        self.assertFalse(c.audio(0, b"late old packet"))
        self.assertTrue(c.audio(new, b"current speech"))
        self.assertEqual(list(c.playback), [b"current speech"])

    async def test_barge_in_keeps_background_job_and_does_not_auto_speak_it(self):
        c = Coordinator()
        release = asyncio.Event()
        async def lookup():
            await release.wait()
            return "saved result"
        task = c.start_job("lookup", lookup)
        c.interrupt()
        self.assertFalse(task.cancelled())
        release.set()
        self.assertEqual(await task, "saved result")
        self.assertEqual(list(c.playback), [])

    async def test_repeated_call_id_reuses_one_job_in_this_process(self):
        c = Coordinator()
        calls = []
        async def side_effect():
            calls.append("executed")
            return "done"
        a = c.start_job("same-call", side_effect)
        b = c.start_job("same-call", side_effect)
        self.assertIs(a, b)
        self.assertEqual(await a, "done")
        self.assertEqual(calls, ["executed"])

    async def test_explicit_job_cancellation_is_separate_from_speech(self):
        c = Coordinator()
        started = asyncio.Event()
        async def lookup():
            started.set()
            await asyncio.Event().wait()
        task = c.start_job("lookup", lookup)
        await started.wait()
        await c.cancel_job("lookup")
        self.assertTrue(task.cancelled())


if __name__ == "__main__":
    unittest.main(verbosity=2)
