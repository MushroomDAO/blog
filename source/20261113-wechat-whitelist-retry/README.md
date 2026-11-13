# WeChat whitelist compensation

The user confirmed that the IP whitelist had been fixed and explicitly authorized one retry of failed drafts. Eight recent failures had no prior creation receipt and no matching server draft; older resolved failures were excluded. The published-list endpoint remained unauthorized (48001), so existing creation receipts were preserved rather than treated as absent.

All eight existing Blog URLs, list membership and five image variants per article were verified. Each missing draft was created once through M2 and read back in full: body text, ordered image identities, title, author, digest, cover ID, original Blog URL and comment settings matched. Original article and asset hashes were unchanged; no Blog build, deploy, rewrite or semantic upsert was required.

See publication-results.json for all verified media IDs. Original failed attempts remain historical evidence. This management request was not turned into an article.
