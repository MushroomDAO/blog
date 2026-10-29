# Minilytics and NSH research publication, 2026-10-29

Job f8cc08f6-98f2-46c4-8793-af700a0eb1db. Two independent topics; incoming bot KBraw is not a publication.

- Source pins: source-pins.json. NSH main and testedrelease deliberately separate.
- Dedup: minilytics-dedup.log and nsh-exact-dedup.log. Broad Native Shell tokensearch falsepositives excluded. Remote9drafts read, publishedAPI48001; no historical mediareceipt orarticle.
- Local verification: local-verification.json plus upstreamsmoke/test sources and logs. No livepayments/analyticsproductiondeployment; NSH nativeAppKitcounter verified, mobile/Webinteraction untested.
- SEO/GEO: seo-geo.json; finalartifacthashes verifyarticles/assetsunchangedthroughbuild.
- Artwork: officialMinilyticsdashboard adopted; generatedNSHcover; eacharticlethreeXiaoMfigures. Generationreports andreproductionscripts preserved, raworiginalsin toolarchive.
- Public URL/list/carousel/assets: verify-public.py writes public-verification.json.
- WeChat fullbodyandmetadata: verify-wechat.cjs with wechat-content-canonical.py. Canonicalreadmoreaccepted; thirdpartyHTMLrewrites do notconstitute a contentchange.
- Reproduce local analytics: npmci/typecheck/test/build in upstreamcheckout, localD1migrate, wranglerdev--local, then BASE=http://127.0.0.1:18787 node scripts/smoke.mjs. Onlysynthetic data.
- Reproduce NSH: officialv0.3.0archive SHA25634fdd2ec43d5e22986723e7633acf9223e365bd5bace1a502b5ae24fb75c266c ; nshinitfixture,build,test--trace,test--targetmacos,check,package--targetweb--out. Sourcefixtureincluded.

Openlicensedupstreamsnapshots retain MIT/Apachelicenses. OpenFreefullpage capture keptprivately in botjob; publicarchive retains factualsource notesinstead. No unrelatedworkspacechanges staged.
