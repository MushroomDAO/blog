# Relax primary-source and local verification

PinnedGit436868926ffae73495a4b1eab8382024368d6663. RootLICENSEMIT,runnerMIT OR Apache2,NOTICE acknowledges ported rustc/std and other licenses. Read pinnedREADME,KNOWN_GAPS,Cargo manifests and compiler/src/jit.rs check_first_events/note_first_borrowck. README differs stale search snippet: defaultbackgroundborrowchecking and current21workloadtable. Never claim timing/semantic equivalence of allcheckers.

Own offlinecargo metadata:35localpackages,no externalregistry. cargo/rustc1.98.1 bootstrap with2jobs onAppleM4 succeeded. Build uses existingmachineMBXwrapper shown inlog (not envRUSTC_WRAPPER),no comparativetimingclaim. Offline temporaryfixture: validcheckexit0,2JITtestspass,borrowconflictrejected,hotpatchfunction1to2 while counter2→7(firstnewvalue)→31 with monotoniccounter/processnormalexit. No fullsuite,MakepadUI,game,devhub,throughputcomparison or arbitrarylayoutmigration.

Officialgame11s/1.15s are not reproduced. Official21workloadtime ratios vsstockx641.12/arm1.24;vsnative1.22/1.25,not throughputspeedups. Stock/nativeCPUbaseline matters. Separate30kernelmicrobenchprovisional duewarmcachetierupbug;21tablemarkedunaffected. Zeroexternalregistrydependencies is notzero internalcrates/nosysteminterfaces. Native integrations liveinMakepadrepo.
