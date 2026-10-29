# mr boxington research

Date2026-10-29. Source https://github.com/jdx/mr-boxington ; docs https://mr-boxington.jdx.dev/ . Main source14ce94d8db352d0f39c5d02786e20ba5a394a680,2026-10-28T14:59:39-05:00. Main mbx crateversion1.28.0; tested release1.28.0 Oct26, source Rust minimum1.91. MIT plus dependency notices. Upstream AGENTS read; no upstream issue/discussion messages or changes made.

## Dedup

Bot query used generic github entity and produced false positives. Fresh exact repoURL+mr-boxington matched only raw bot KB material. No existing article or M2receipt. Remote draft box read successfully8 entries; publishedAPI48001 unavailable, no local old credentials suggest prior publication. New canonical slug justified; rawKB not recreated.

## Release and isolated test

Official Darwinarm64v1.28.0 asset downloaded into /tmp/boxington-bin, archiveSHAac73ba0637a443ba9c43354008f6bcd5d9e8a84b703e46f23202025c1f849472 matches API digest and official SHA256SUMS. This is integrity checking, not independent Sigstore attestation validation. Binary reports1.28.0. No globalmbxinstalled or globalmbxconfig existed. No mbxsetup or settingsset executed. Cache/shims and explicit targets all under fresh /tmp/boxington-smoke/proof-qv8cgmx2. No real user workspace target directories changed.

Self-contained Rust fixture one package with lib+bin, no third-party dependencies, identical copies in different absolute paths. Not actual gitworktrees. Same Cargo.lock, environment/toolchain/profile, isolated store and3 fresh targets. First build0hits/0miss/2unconsulted, savedoutputs. Second copy2hits/0miss, executed binary42. Five bypasses compiler queries/stdin recorded, not failedcratehits. Explainlast says no recorded misses. Change lib to43, build into third fresh target:0hits/1miss/1unconsulted, privateincremental2, executable43. Cache stats and gcdryrun successful; no actualgcdelete. Assertions and command returncodes in smoke-results, source script and raw logs archived.

CARGO_INCREMENTAL=0 was set but mbx learned_incremental stayed default and activated after edit. Record corrected to distinguish Cargo's setting from mbx's private mechanism; no extra rerun necessary, observed outputs retained. This is correctness/reuse smoke test, not speed/physicaldisk/performance/scheduler benchmark. Timings in rawlogs not used to claim speedup. No realcrate dependencies, parallel, CI, remote, Windows, IntelMac or debugger test.

## Boundaries highlighted

Cargo still plans builds; modeled compiler actions restored, others compile. No persistentdaemon, no functionJIT/hotreload/worktree replacement. Fresh target required to distinguish Cargo fresh checks. Shared completeoutputs vs privateincremental and managedtargetscope differ. Explicitcustomtargets not automaticallymanaged. Source/debug paths may retain original checkout. Independentparallelcommands requiretargetseparation despite scheduler. CI Action defaultbranchpushsave, PRrestore with opt-in same-repo exceptions, forksneverwrite; remotebackend rules separate. Defaults and docs not asserted as independently verified production behavior.

## Artwork

Official screenshots mainlyterminaltext; officialtheme-song1920x1080poster inspected, wordmark/postertextdominates and not a useful crop, rejected ashero. Original localFLUXseed8109 cover1200x63091532B,0fail0warn, manuallyinspected plainboxes/trays andcomputer, nopeople/readabletext. Concept photo notproductUI. Three simpleXiaoM bodyfigures generated through publisher-authorizedcodexworker; originals and QA in illustrations.md.
