"""Shared waiting period for pending cards and future topic-summary review."""

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
import os

from ..storage.clock import business_day_bounds, business_day_label, format_timestamp

# Automatic approval stopped because settings or the day's source changed after
# extraction. Saving the draft in review clears it.
MANUAL_REVIEW = "manual_review_required"


@dataclass(frozen=True)
class ApprovalSettings:
    delay_hours: int = 48

    def __post_init__(self):
        if type(self.delay_hours) is not int or self.delay_hours<=0:
            raise ValueError('自动入库等待小时数必须为正整数')

    @classmethod
    def from_env(cls):
        try:
            return cls(int(os.environ.get('MEMORY_AUTO_APPROVE_AFTER_HOURS','48')))
        except (TypeError,ValueError):
            raise ValueError('MEMORY_AUTO_APPROVE_AFTER_HOURS 必须为正整数') from None

    @property
    def delay_days(self):
        # Counted in business days so a draft made a few minutes after one
        # daily run is not pushed back a whole extra day.
        return max(1, -(-self.delay_hours // 24))

    def ready_before(self, run_label, core):
        """Drafts ready before this instant are due in the run for run_label."""
        start, _ = business_day_bounds(run_label - timedelta(days=self.delay_days - 1), core)
        return start.astimezone(timezone.utc)

    def is_due(self, ready_at, ready_before):
        return datetime.fromisoformat(ready_at).astimezone(timezone.utc) < ready_before

    def scheduled_at(self, ready_at, core, daily):
        label=business_day_label(datetime.fromisoformat(ready_at),core)+timedelta(days=self.delay_days)
        return daily.scheduled_at(label,core)

    def overview(self, connection, space, policy, core, daily, now, *, include_summaries=False, pending_filter=''):
        ready_sql = ("SELECT p.review_ready_at FROM memory_core.pending_memories p WHERE p.bot_id=%s AND p.status='pending'"
                     " AND p.error_code IS DISTINCT FROM %s" + pending_filter)
        values = [space, MANUAL_REVIEW]
        if include_summaries:
            ready_sql += " UNION ALL SELECT review_ready_at FROM memory_core.topic_summary_batches WHERE bot_id=%s AND status='pending'"
            values.append(space)
        row=connection.execute('SELECT min(review_ready_at::timestamptz) AS first_ready,count(*) AS ready FROM ('+ready_sql+') pending',values).fetchone()
        first=row['first_ready']
        scheduled=self.scheduled_at(first.isoformat(),core,daily) if first else None
        task=connection.execute('''SELECT state,last_error_code,business_date FROM memory_core.daily_tasks
            WHERE bot_id=%s AND task_kind='approval' ORDER BY business_date DESC LIMIT 1''',(space,)).fetchone()
        if scheduled and task and task['state'] in ('done','skipped'):
            executed=daily.scheduled_at(date.fromisoformat(task['business_date']),core)
            if scheduled.astimezone(timezone.utc)<=executed.astimezone(timezone.utc):
                scheduled=daily.scheduled_at(date.fromisoformat(task['business_date'])+timedelta(days=1),core)
        manual=connection.execute("SELECT count(*) AS n FROM memory_core.pending_memories WHERE bot_id=%s AND status='pending' AND error_code=%s",
            (space,MANUAL_REVIEW)).fetchone()['n']
        return dict(enabled=policy['auto_approve_enabled'],delay_hours=self.delay_hours,ready_count=row['ready'],manual_count=manual,
            next_run_at=format_timestamp(scheduled,core) if scheduled and policy['auto_approve_enabled'] else None,
            overdue=bool(scheduled and scheduled.astimezone(timezone.utc)<=now.astimezone(timezone.utc)),
            last_error_code=task['last_error_code'] if task and task['state']=='failed' else None)
