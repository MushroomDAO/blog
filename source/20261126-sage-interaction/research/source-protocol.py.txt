"""The online backend uses the same tool message envelope as training."""

import json
import os
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]


def configuration(path):
    cfg = json.loads(Path(path).read_text())
    cfg["configuration_path"] = str(Path(path).resolve())
    for key in ("prompt_wav", "backend_prompt"):
        cfg[key] = str(PROJECT / cfg[key])
    if "frontend_prompt_file" in cfg:
        cfg["frontend_prompt_file"] = str(PROJECT / cfg["frontend_prompt_file"])
    return cfg


def backend_headers():
    """Read credentials only in the server process; never put them in config JSON."""
    key = os.environ.get("SAGE_BACKEND_API_KEY", "").strip()
    if not key or any(ord(char) < 33 or ord(char) > 126 for char in key):
        raise ValueError("Set SAGE_BACKEND_API_KEY to a valid API key")
    return {"Authorization": "Bearer " + key}


def delegate_query(text):
    payload = json.loads(text)
    if not isinstance(payload, dict) or set(payload) != {"query"}:
        raise ValueError('Delegate must contain exactly {"query":"..."}')
    else:
        query = payload["query"]
    if not isinstance(query, str) or not query.strip() or len(query) > 6000:
        raise ValueError(
            "Delegate query must be a nonempty string of at most 6000 characters"
        )
    else:
        return query.strip()


def tool_event(task_id, query, content, status="ok", event_name="", event_id=""):
    payload = dict(
        type="delegate_result",
        task_id=task_id,
        status=status,
        query=query,
        content=content,
    )
    if event_name:
        payload["event"] = event_name
    if event_id:
        payload["event_id"] = event_id
    envelope = (
        "<|im_start|>tool\n"
        + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        + "<|im_end|>"
    )
    return payload, envelope


def parse_timer_request(query):
    """Return delay_seconds when the query schedules something for later.

    Deliberately narrow: only explicit relative-delay wording starts a timer,
    so ordinary questions keep the immediate backend path.
    """
    import re

    text = query.strip()
    text = re.sub(r"^\s*TimeSpeak task:\s*", "", text, flags=re.IGNORECASE)
    ones = dict(
        one=1,
        two=2,
        three=3,
        four=4,
        five=5,
        six=6,
        seven=7,
        eight=8,
        nine=9,
        ten=10,
        eleven=11,
        twelve=12,
        fifteen=15,
        twenty=20,
        thirty=30,
        forty=40,
        fifty=50,
        sixty=60,
    )
    text = re.sub(r"\bhalf an? minute\b", "30 seconds", text, flags=re.IGNORECASE)
    text = re.sub(r"\ban? (minute|second)\b", r"1 \1", text, flags=re.IGNORECASE)
    text = re.sub(
        r"\b(" + "|".join(ones) + r")\b",
        lambda m: str(ones[m.group(1).lower()]),
        text,
        flags=re.IGNORECASE,
    )
    patterns = (
        (r"(?:in|after)\s+(\d+(?:\.\d+)?)\s*(?:seconds?|secs?)\b", 1.0),
        (r"(?:in|after)\s+(\d+(?:\.\d+)?)\s*(?:minutes?|mins?)\b", 60.0),
        (r"(\d+(?:\.\d+)?)\s*(?:seconds?|secs?)\s+(?:later|from now)\b", 1.0),
        (r"(\d+(?:\.\d+)?)\s*(?:minutes?|mins?)\s+(?:later|from now)\b", 60.0),
    )
    for pattern, scale in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match is None:
            continue
        delay = float(match.group(1)) * scale
        return delay if 0 < delay <= 86400 else None
    return None


def timer_event(task_id, query, content, event_id):
    """Payload MiniCPM-o waits for before speaking a scheduled reminder."""
    return tool_event(
        task_id, query, content, status="ok", event_name="time_up", event_id=event_id
    )


async def ask_backend(client, cfg, task_id, query):
    """Answer one delegate query, honouring a scheduled-reminder delay.

    A query that requests a later time is served only after that delay, and
    its result is tagged ``event="time_up"`` so the frontend model knows the
    reminder deadline has arrived before it speaks.
    """
    import asyncio
    import time

    timer_delay = None
    if cfg.get("enable_scheduled_reminders", True):
        timer_delay = parse_timer_request(query)
    if timer_delay is not None:
        max_delay = float(cfg.get("max_reminder_seconds", 840))
        if timer_delay > max_delay:
            payload, envelope = tool_event(
                task_id,
                query,
                f"Reminders can be scheduled at most {int(max_delay)} seconds ahead.",
                "error",
            )
            return dict(
                payload=payload,
                event=envelope,
                error="reminder_too_far",
                requested_delay_seconds=timer_delay,
                max_reminder_seconds=max_delay,
                backend_seconds=0.0,
            )
        await asyncio.sleep(timer_delay)
        import re as _re

        reminder = query.strip()
        if not _re.match(r"^\s*TimeSpeak task:", reminder, flags=_re.IGNORECASE):
            reminder = "TimeSpeak task: " + reminder
        payload, envelope = timer_event(task_id, query, reminder, "timer_" + task_id)
        return dict(
            payload=payload,
            event=envelope,
            scheduled=True,
            fixed_content=True,
            reminder_delay_seconds=round(timer_delay, 3),
            reminder_fired_at=round(time.time(), 3),
            backend_seconds=0.0,
        )
    started = time.monotonic()
    limit = cfg["backend_response_max_chars"]
    schema = dict(
        type="object",
        properties=dict(content=dict(type="string", minLength=1, maxLength=limit)),
        required=["content"],
        additionalProperties=False,
    )
    prompt = (
        Path(cfg["backend_prompt"]).read_text().replace("{{MAX_CHARS}}", str(limit))
    )
    request = dict(
        model=cfg["backend_model_name"],
        messages=[
            dict(role="system", content=prompt),
            dict(
                role="user",
                content=json.dumps(
                    dict(type="delegate", task_id=task_id, query=query),
                    ensure_ascii=False,
                ),
            ),
        ],
        max_tokens=cfg["backend_max_tokens"],
        temperature=0.3,
        chat_template_kwargs={
            "thinking": cfg["backend_thinking"],
            "reasoning_effort": cfg["backend_reasoning_effort"],
        },
        response_format=dict(
            type="json_schema",
            json_schema=dict(name="spoken_answer", schema=schema, strict=True),
        ),
    )
    response = await client.post(
        cfg["backend_base_url"].rstrip("/") + "/chat/completions",
        headers=backend_headers(),
        json=request,
    )
    response.raise_for_status()
    result = response.json()
    choice = result["choices"][0]
    message = choice["message"]
    raw = message.get("content")
    if choice.get("finish_reason") == "length":
        raise ValueError(
            f"Backend exhausted its {cfg['backend_max_tokens']}-token budget before completing the answer"
        )
    elif not isinstance(raw, str) or not raw.strip():
        raise ValueError(
            f"Backend returned no final answer (finish_reason={choice.get('finish_reason')})"
        )
    else:
        answer = json.loads(raw)
    if not isinstance(answer, dict) or set(answer) != {"content"}:
        raise ValueError("Backend did not return the spoken answer schema")
    else:
        content = answer["content"]
    if not isinstance(content, str) or not content.strip() or len(content) > limit:
        raise ValueError("Backend answer violates the spoken length budget")
    elif timer_delay is not None:
        payload, event = timer_event(
            task_id, query, content.strip(), "timer_" + task_id
        )
    else:
        payload, event = tool_event(task_id, query, content.strip())
    summary = dict(
        payload=payload,
        event=event,
        requested_model=cfg["backend_model_name"],
        actual_model=result["model"],
        usage=result.get("usage", {}),
        response_format="json_schema",
        content_characters=len(content),
        max_content_characters=limit,
        max_completion_tokens=cfg["backend_max_tokens"],
        finish_reason=choice.get("finish_reason"),
        backend_seconds=round(time.monotonic() - started, 3),
    )
    if timer_delay is not None:
        summary.update(
            scheduled=True,
            reminder_delay_seconds=round(timer_delay, 3),
            reminder_fired_at=round(time.time(), 3),
        )
    else:
        summary["scheduled"] = False
    return summary
