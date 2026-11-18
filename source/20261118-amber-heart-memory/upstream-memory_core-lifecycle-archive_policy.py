"""Configurable inactivity windows and a conservative receipt-health gate."""

from dataclasses import dataclass, fields
from datetime import datetime, timedelta, timezone
import math
import os

from .topic_summary_policy import TOPIC_KEYS


@dataclass(frozen=True)
class ArchiveSettings:
    rule_days: int = 365
    reflection_days: int = 180
    knowledge_days: int = 180
    event_days: int = 120
    emotional_days: int = 365
    receipt_window_days: int = 14
    receipt_min_samples: int = 20
    receipt_min_rate: float = 0.8

    def __post_init__(self):
        for field in fields(self):
            value = getattr(self, field.name)
            if field.name != 'receipt_min_rate' and (type(value) is not int or value <= 0):
                raise ValueError('归档天数和最少回执样本数必须是正整数')
        rate = self.receipt_min_rate
        if type(rate) not in (float, int) or not math.isfinite(rate) or not 0 < rate <= 1:
            raise ValueError('归档回执率门槛必须大于 0 且不超过 1')

    @classmethod
    def from_env(cls):
        values = {}
        for field in fields(cls):
            name = 'MEMORY_ARCHIVE_' + field.name.upper()
            if name in os.environ:
                try:
                    values[field.name] = (float if field.name == 'receipt_min_rate' else int)(os.environ[name])
                except ValueError:
                    raise ValueError(name + ' 的数值无效') from None
        return cls(**values)

    def retention_days(self, card):
        days = {
            'tier_0_exempt': None,
            'tier_1_rule': self.rule_days,
            'tier_2_reflection': self.reflection_days,
            'tier_3_semantic': self.knowledge_days,
            'tier_4_episode': self.event_days,
            'tier_5_emotional': self.emotional_days,
        }[card['decay_layer']]
        return max(days, 365) if days is not None and card['is_milestone'] else days

    def due(self, card, now):
        if (card['archive_reason'] is not None or card['item_kind'] != 'atomic'
                or card['parent_reflection_id'] is not None or card['gardener_result'] == 'absorbed'):
            return False
        # Leave these cards available to the gardener until it has made a decision.
        if card.get('primary_topic_key') in TOPIC_KEYS and card['gardener_result'] is None:
            return False
        days = self.retention_days(card)
        if days is None:
            return False
        reference = datetime.fromisoformat(card['last_used_at'] or card['created_at'])
        if card['restored_at']:
            reference = max(reference, datetime.fromisoformat(card['restored_at']))
        return now.astimezone(timezone.utc) - reference.astimezone(timezone.utc) >= timedelta(days=days)


def receipt_health(connection, space, policy, now):
    counts = connection.execute('''SELECT count(*) AS injected_rounds,
        count(*) FILTER (WHERE EXISTS (SELECT 1 FROM memory_core.conversation_requests r
            WHERE r.bot_id=t.bot_id AND r.turn_id=t.id
            AND r.usage_receipt->>'status' IN ('reported','reported_unused','judged','judged_unused'))) AS reported_rounds
        FROM memory_core.conversation_turns t WHERE t.bot_id=%s AND t.history_state='current'
        AND t.generation_state IN ('complete','failed','incomplete') AND t.content_deleted_at IS NULL
        AND t.finished_at::timestamptz >= %s AND t.finished_at::timestamptz <= %s
        AND jsonb_array_length(t.recall_snapshot->'cards')>0''',
        (space, now - timedelta(days=policy.receipt_window_days), now)).fetchone()
    total, reported = counts['injected_rounds'], counts['reported_rounds']
    rate = reported / total if total else None
    reason = ('insufficient_samples' if total < policy.receipt_min_samples
              else 'low_receipt_rate' if rate < policy.receipt_min_rate else 'ready')
    return dict(**counts, rate=rate, reason=reason, paused=reason != 'ready',
        window_days=policy.receipt_window_days, minimum_samples=policy.receipt_min_samples,
        minimum_rate=policy.receipt_min_rate)
