# Rakazo reuse and failed WeChat draft retry — 2026-11-03

This is a maintenance audit, not a new blog article. Job dab8f8e1-5e63-44fd-8a83-bc53f4c0360e.

Rakazo canonical source: https://github.com/elie222/rakazo and https://rakazo.com/about/ . Existing bilingual Blog reused: https://blog.mushroom.cv/blog/rakazo-persistent-ai-teammate-sandbox-computer-use-teardown/ . Product UI banner manually inspected and matches the project. No article, image, or Blog deployment was recreated. Old star count is historical September30 data, not a current claim.

Existing Rakazo draft receipt was checked against current remote draft list and draft/get. It is absent, get returns40007, published API48001 unavailable. Status recorded, archived credential retained, no new draft created. Other recorded receipts are not failed creations and were not rebuilt.

Workflow DB and job/failure artifacts identify exactly4 completed Blog articles whose WeChat creation failed with40164 and no prior mediaID: Archonos, AI Safety HOT, ESP32/LR2021 ADS-B, Weight-Space Programming/knowledge editing. All4 Blog URLs and5 image URLs each verified200 before one M2 attempt each. No local successful receipt existed and none matched the remote drafts. After token access recovered, all4 attempts succeeded.

Each new mediaID was read with draft/get and compared against the final rendered HTML: complete visible text, image identities and3 image count, title, author, digest, cover material, canonical sourceURL and comments1/0. All passed; HTML byte equality differs because WeChat rewrites markup. No group broadcast was performed.

Original failed workflow jobs now complete with errors cleared and next_retry0 after verification; each job result/progress and per-article failure record updated with the actual current mediaID. Historical failure evidence remains. The DB has0 failed jobs remaining;1 unrelated blocked raw material only says huggingface/paperswithcode and has no identified article/slug, so no draft could be fabricated for it. Its state is preserved.

All5 corresponding KB project memories updated/mined and read back. Publication ledger exported. Rakazo semantic index was checked before mutation and was missing both language records; incremental upsert only fills those two records. Other Blog/index successes were reused.
