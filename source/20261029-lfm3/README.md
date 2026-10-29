# Liquid AI LFM3 research publication

Job2ff78751-8427-4745-9d7e-3c20c5d9d8f0,2026-10-29.

- model-pins.json / model-facts.json: nineHFcards, sevenprimarycheckpoints and twoofficialtextformats, independentrevisionpins. Fullcards and8.7MBlaunchpage keptprivately under /tmp/lfm3-research, publicarchive recordsownfactualnotes instead.
- LFM-Open-License-v1.0.txt: actual modellicense, commercialrevenuethresholdnotApache/MIT. Modelconfigs retainthatlicense.
- local-verification.json: officialllama.cppb11960AppleSiliconarchive+officialQ4_K_M LFSdigestsverified. Tempserver127.0.0.1:18788,context4096,parallel1,no existingtoolreplaced.
- smoke.py / smoke-results.json: threehandpickedshortsyntheticprompts; initial2matches,thirdJSONemptyafter96generatedtokens. No accuracy/performancebenchmark.
- diagnose-budget.py / budget-followup.json: onlybudgetchangedto512,125generatedtokens,correctvisibleJSON. Initialfailureretained; reasoningfieldredactedtocharacterlength/hash/summaryfrompublicartifact. Modeltextonly; noaudio/vision/d1/fullcontext/peakmemorytests.
- No weightsorbinaries mirroredinGit. To reproduce, download pinnedGGUFandb11960binary namedinverificationJSON,matchdigests,startllama-server with model/context4096/parallel1/ngl99/jinja,runbothscripts. Stopserverafterwards.
- Scriptsverify-public.py andverify-wechat.cjs checkactualproductionartifacts/fullvisiblebody and imageidentities.
- seo-geo.json: bilingualmetadata,BLUF,FAQ,primaryreferences,relatedearliergenerationlink andscopechecks.
- Banner: officialLiquidAIwordmarkcandidateinspected/rejected,darktextdominates. OriginalFLUXseed8111edge-devicephoto1200x63091273B,0fail0warn,manualaccepted. DoesnotdepictarealLFM3producttest.
