"""Route a spoken tool envelope before any text or audio reaches the browser."""

import json
import re

import numpy as np

from sage_demo.protocol import delegate_query


class SpokenQueryRouter:
    """Buffer only a possible tool envelope at the start of a speech turn."""

    def __init__(self, max_characters=6000):
        self.max_characters = max_characters
        self.reset()

    def reset(self):
        self.mode = "prefix"
        self.text = ""
        self.audio = []

    def route(self, result, audio):
        original = result["text"]
        if result.get("speech_interrupted", False):
            self.reset()
        if result["action"] != "speak":
            self.reset()
            return result, audio
        elif self.mode == "speech":
            if result["end_of_turn"]:
                self.reset()
            return result, audio
        else:
            self.text += original
        if audio is not None and audio.size:
            self.audio.append(audio)
        body = self.text.lstrip()
        compact = re.sub(r"\s+", "", body)
        if body.startswith("```"):
            body = body[3:]
            if body.startswith("json"):
                body = body[4:]
            body = body.lstrip()
        header = re.match(r'^\{\s*"query"\s*:', body)
        possible = (
            '{"query":'.startswith(compact)
            or "```json".startswith(compact)
            or "```".startswith(compact)
        )
        if compact.startswith("```json"):
            possible = '{"query":'.startswith(compact[7:])
        elif compact.startswith("```") and not "```json".startswith(compact):
            possible = '{"query":'.startswith(compact[3:])
        if header is not None:
            self.mode = "query"
        if self.mode != "query" and (not possible or result["end_of_turn"]):
            released = dict(result, text=self.text)
            waveform = np.concatenate(self.audio) if self.audio else None
            self.reset()
            self.mode = "prefix" if result["end_of_turn"] else "speech"
            return released, waveform
        state, payload = "buffering", None
        if self.mode == "query":
            try:
                value, end = json.JSONDecoder().raw_decode(body)
            except json.JSONDecodeError:
                value = None
            if value is not None:
                try:
                    query = delegate_query(json.dumps(value, ensure_ascii=False))
                except ValueError:
                    state = "rejected"
                else:
                    state, payload = (
                        "rerouted",
                        json.dumps({"query": query}, ensure_ascii=False),
                    )
            elif result["end_of_turn"] or len(self.text) > self.max_characters:
                state = "rejected"
        elif len(self.text) > self.max_characters:
            state = "rejected"
        routed = dict(
            result,
            action="delegate" if payload is not None else "listen",
            text=payload or "",
            query_routing=dict(
                state=state,
                original_action="speak",
                original_text=original,
                buffered_characters=len(self.text),
            ),
        )
        if state != "buffering":
            routed.update(
                end_of_turn=True, speech_complete=True, native_turn_open=False
            )
            self.reset()
        else:
            routed.update(speech_complete=False)
        return routed, None


def browser_event(event):
    """Keep full envelopes in server traces; expose status and answers to the UI."""
    public = dict(event)
    if event["type"] == "action" and event["action"] == "delegate":
        public["text"] = ""
        public.pop("delegate_decoding", None)
    if "query_routing" in public:
        public["query_routing"] = {
            k: v for k, v in public["query_routing"].items() if k != "original_text"
        }
    if event["type"] in ("delegate_request", "delegate_duplicate"):
        public.pop("query", None)
    elif event["type"] == "delegate_result":
        public.pop("event", None)
        public["payload"] = {k: v for k, v in event["payload"].items() if k != "query"}
    return public
