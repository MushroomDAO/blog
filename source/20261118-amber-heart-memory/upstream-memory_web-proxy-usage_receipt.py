"""Incremental <used> filtering; the downstream and archive share clean text."""

from copy import deepcopy
import json
import re

OPEN = "<used>"
CLOSE = "</used>"
NUMBERS = re.compile(r"\s*(?:[0-9０-９]+\s*(?:[,，]\s*[0-9０-９]+\s*)*)?")
DIGITS = str.maketrans("０１２３４５６７８９", "0123456789")


class UsageFilter:
    def __init__(self):
        self.pending = ""
        self.in_tag = False
        self.tag = ""
        self.overflow = False
        self.whitespace = ""
        self.indices = set()
        self.had_tag = False
        self.none = False
        self.other_report = False

    @property
    def reported(self):
        return sorted(self.indices) if not self.in_tag and not self.pending else []

    @property
    def reported_none(self):
        return self.none and not self.other_report and not self.in_tag and not self.pending

    def _visible(self, value):
        if value.strip():
            self.indices.clear()
            self.had_tag = False
            self.none = False
            self.other_report = False
        combined = self.whitespace + value
        visible = combined.rstrip()
        self.whitespace = combined[len(visible) :]
        return visible

    def feed(self, value):
        self.pending += value
        visible = []
        while self.pending:
            lower = self.pending.lower()
            if self.in_tag:
                end = lower.find(CLOSE)
                if end >= 0:
                    raw = self.tag + self.pending[:end]
                    if not self.overflow and raw.strip() == "无":
                        self.none = True
                    else:
                        # Only an unambiguous terminal report of 'none' may
                        # claim non-use. Valid numbers still take precedence.
                        self.other_report = True
                    if not self.overflow and len(raw) <= 256 and NUMBERS.fullmatch(raw):
                        self.indices.update(
                            int(n)
                            for n in re.findall(r"[0-9]+", raw.translate(DIGITS))
                            if 1 <= int(n) <= 5
                        )
                    self.pending = self.pending[end + len(CLOSE) :]
                    self.in_tag, self.tag, self.overflow = False, "", False
                    self.had_tag = True
                    continue
                keep = next(
                    (
                        i
                        for i in range(min(len(CLOSE) - 1, len(lower)), 0, -1)
                        if CLOSE.startswith(lower[-i:])
                    ),
                    0,
                )
                consumed = self.pending[:-keep] if keep else self.pending
                self.tag += consumed
                if len(self.tag) > 256:
                    self.tag, self.overflow = "", True
                self.pending = self.pending[-keep:] if keep else ""
                break
            start = lower.find(OPEN)
            if start >= 0:
                visible.append(self._visible(self.pending[:start]))
                self.whitespace = ""
                self.pending = self.pending[start + len(OPEN) :]
                self.in_tag, self.had_tag = True, True
                continue
            keep = next(
                (
                    i
                    for i in range(min(len(OPEN) - 1, len(lower)), 0, -1)
                    if OPEN.startswith(lower[-i:])
                ),
                0,
            )
            visible.append(
                self._visible(self.pending[:-keep] if keep else self.pending)
            )
            self.pending = self.pending[-keep:] if keep else ""
            break
        return "".join(visible)

    def finish(self):
        # A partial opening/closing control tag is never exposed or counted.
        tail = (
            self.whitespace
            if not self.had_tag and not self.pending and not self.in_tag
            else ""
        )
        self.whitespace = ""
        return tail


def clean_response(value):
    value = deepcopy(value)
    filter = UsageFilter()
    for choice in value.get("choices", []):
        message = choice.get("message", {})
        if choice.get("index", 0) == 0 and isinstance(message.get("content"), str):
            message["content"] = filter.feed(message["content"]) + filter.finish()
    return value, filter.reported, filter.reported_none


def encode(value):
    return b"data: " + json.dumps(value, ensure_ascii=False).encode() + b"\n\n"


class StreamReceipt:
    def __init__(self):
        self.filter = UsageFilter()
        self.base = None

    def flush(self):
        tail = self.filter.finish()
        if not tail or self.base is None:
            return []
        value = deepcopy(self.base)
        value["choices"] = [
            {"index": 0, "delta": {"content": tail}, "finish_reason": None}
        ]
        value.pop("usage", None)
        return [encode(value)]

    def frames(self, frame, data):
        if data == "done":
            return self.flush() + [frame]
        if not isinstance(data, dict):
            return [frame]
        value = deepcopy(data)
        output = []
        changed = False
        for choice in value.get("choices", []):
            if choice.get("index", 0) != 0:
                continue
            delta = choice.get("delta", {})
            if isinstance(delta.get("content"), str):
                self.base = data
                delta["content"] = self.filter.feed(delta["content"])
                changed = True
            if choice.get("finish_reason"):
                if changed:
                    delta["content"] += self.filter.finish()
                else:
                    output += self.flush()
        return output + [encode(value) if changed else frame]
