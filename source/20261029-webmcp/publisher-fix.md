# Canonical read-more URL at initial draft creation
Earlier Deskflow draft verification reproduced an empty content_source_url while the local index already knew the final slug. The client accepts article.sourceUrl, but pipeline/m2/index.js omitted it. Previously this required a separate draft/update on the same ID.
This change derives the canonical Blog URL once from the existing English article basename, passes sourceUrl into createDraft, and records blogUrl/contentSourceUrl beside the unchanged sourceUrls used for dedup. No retry or draft creation semantics changed. node --check passed; actual first-create remote source URL verification for this article will serve as the behavior check. No second update is planned.

Actual first-create remote verification passed: content_source_url equals the verified canonical Blog URL; complete text, three ordered images, cover and metadata match. No draft/update call was needed.
