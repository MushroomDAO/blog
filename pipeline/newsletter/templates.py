"""Digest HTML rendering — shared across all content sources."""
import datetime
import html

SITE_URL = "https://blog.mushroom.cv"
MAX_ITEMS = 7

CARD_TPL = """
<tr>
  <td style="padding: 0 0 28px 0;">
    <img src="{banner}" width="100%" alt="" style="display:block;width:100%;max-width:525px;height:auto;border-radius:6px;margin-bottom:12px;" />
    <div style="font-size:18px;font-weight:bold;color:#222;line-height:1.4;margin-bottom:6px;">{title}</div>
    <div style="font-size:14px;color:#555;line-height:1.6;margin-bottom:8px;">{summary}</div>
    <a href="{url}" style="font-size:14px;color:#0055d4;text-decoration:none;font-weight:bold;">阅读全文 →</a>
  </td>
</tr>
"""

# For items with no external link (subscriber-only content) — body_html is
# already-safe HTML, not escaped again.
INLINE_TPL = """
<tr>
  <td style="padding: 0 0 28px 0;">
    <div style="font-size:18px;font-weight:bold;color:#222;line-height:1.4;margin-bottom:6px;">{title}</div>
    <div style="font-size:14px;color:#444;line-height:1.7;">{body_html}</div>
  </td>
</tr>
"""

BASE_TPL = """<!doctype html>
<html>
<body style="margin:0;padding:0;background-color:#F0F1F3;font-family:'Helvetica Neue','Segoe UI',Helvetica,sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#F0F1F3;padding:30px 0;">
    <tr>
      <td align="center">
        <table role="presentation" width="525" cellpadding="0" cellspacing="0" style="background-color:#fff;padding:30px;border-radius:5px;">
          <tr>
            <td style="padding-bottom:20px;">
              <div style="font-size:20px;font-weight:bold;">🍄 Mushroom Research Blog</div>
              <div style="font-size:13px;color:#888;margin-top:4px;">{issue_date} 更新摘要</div>
            </td>
          </tr>
          <tr>
            <td style="padding-bottom:24px;font-size:15px;color:#444;line-height:1.6;">
              这期一共 {count} 条更新，挑重点给你翻一下：
            </td>
          </tr>
          {cards}
          {more_notice}
          <tr>
            <td style="padding-top:20px;border-top:1px solid #eee;font-size:12px;color:#888;text-align:center;">
              🍄 Mushroom Research Blog｜非营利个人科技观察<br/>
              <a href="{{{{ UnsubscribeURL }}}}" style="color:#888;">退订</a>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


def render_card(item, fallback_banner: str) -> str:
    if item.link:
        return CARD_TPL.format(
            banner=html.escape(item.banner_url or fallback_banner, quote=True),
            title=html.escape(item.title),
            summary=html.escape(item.summary),
            url=html.escape(item.link, quote=True),
        )
    return INLINE_TPL.format(title=html.escape(item.title), body_html=item.body_html or "")


def render(items: list, fallback_banner: str) -> str:
    """items: list[DigestItem], already deduped — this only applies the
    per-issue cap, sorts, and renders. Sources are responsible for their
    own dedup against sent_ids.
    """
    items = sorted(items, key=lambda i: i.pub_date, reverse=True)
    shown = items[:MAX_ITEMS]
    rest = len(items) - len(shown)

    cards = "\n".join(render_card(item, fallback_banner) for item in shown)

    more_notice = ""
    if rest > 0:
        # Overflow notice assumes blog is the source most likely to overflow;
        # revisit if a non-blog source regularly produces more than MAX_ITEMS.
        more_notice = (
            f'<tr><td style="padding-bottom:20px;font-size:13px;color:#888;">'
            f'本期还有 {rest} 条，<a href="{SITE_URL}/blog/" style="color:#0055d4;">去博客看全部</a></td></tr>'
        )

    return BASE_TPL.format(
        issue_date=datetime.date.today().isoformat(),
        count=len(items),
        cards=cards,
        more_notice=more_notice,
    )
