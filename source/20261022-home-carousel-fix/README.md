# Homepage carousel ordering fix — 2026-10-22

Maintenance task676b2b45-71fd-4e24-80c0-1c103e618b15. Not a new article or WeChat task.

The live carousel took the first8 posts sorted only by pubDate. Splash1.4 updated the original October5 article on October22, so the article was available at its URL but absent from the carousel. Vitalik was already present in slide6. Date-only publication fields also left same-day ties in collection order.

Fix: homepage carousel independently sorts by the latest of pubDate, updatedDate and optional lastPublishedAt. Stable fallbacks use original publication date and article ID. Existing list ordering stays by original publication date. Carousel date displays activity date. Canonical publish-blog.sh records lastPublishedAt inUTC seconds after validation for actual deploys, keeping original calendar dates intact. This avoids filesystemmtime and hardcodedfeaturedslugs. No-deploy does not stamp.

Regression checks run successfully:

```sh
node --test src/lib/post-activity.test.ts
python3 scripts/test_stamp_blog_publication.py
bash -n scripts/publish-blog.sh
```

Three Node cases cover updated old articles entering latest8, same-day precise publication ordering and stable legacy fallback. Two Python cases cover preserved body/calendar dates, replacement rather than duplicate timestamps, deterministic same-time reruns and invalid frontmatter refusal. Actual Astro build passed.

verify-home.py compares the recorded pre-fix carousel with the built and public post-fix page, asserts exactly8 slides and Splash first, requests the actual first image and checks originalpubDate. Fresh isolated-profile headlessChrome loaded the live page; its first original slide points toSplash and the screenshot was visually reviewed. No user browser profile was used. Homepage and first image returned200.

Public home: https://blog.mushroom.cv/
Current first article: https://blog.mushroom.cv/blog/specialized-inference-engines-rise-hardware-specific-llm-optimization/
Original article date remains2026-10-05; updatedDate remains2026-10-22.

No article body, banner, WeChat receipt or draft was created or replaced for this management request. Existing Splash metadata alone received the publication-order timestamp. No semantic re-embedding was needed: the publisher confirmed2unchanged records. KB maintenance record and ledger exported; source marked processed to prevent an automatic source-scanner article.
