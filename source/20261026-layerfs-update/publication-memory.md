---
name: LayerFS recursive agent filesystem
description: Existing LayerFS article updated October26 with worktree comparison and v1.1 breaking changes; WeChat recorded/current status unverified.
type: project
---

# LayerFS

Source: https://github.com/Ephemeral-AI-Lab/layerfs ; release https://github.com/Ephemeral-AI-Lab/layerfs/releases/tag/v1.1.0 ; Git worktree documentation https://git-scm.com/docs/git-worktree . Original raw material already in KB, original publication2026-10-22. Reuse slug layerfs-v1-recursive-agent-filesystem and original source identity; no new topic route.

Article: https://blog.mushroom.cv/blog/layerfs-v1-recursive-agent-filesystem/ . Updated2026-10-26, deploy2e59de6f, HTTP200 plus all5imagevariants200, list25, carousel1. Original verified FLUX cover and3XiaoMfigures reused; bilingual worktreecomparison and1.1 update inserted, original1.0 code/bench review retained explicitly historical. Semantic2vectorsupserted, stale2deleted; livequerymatched updated Chinese title score0.65743905.

Git worktree shares repository objects, not an independent complete Git-history clone; separate working-tree/dependency/cache costs differ. LayerFS MIT Rust/FUSE/SQLite; shared committed history plus independent writable Workspaces. Explicit commits required by v1.0 SDK; Harness may wrap automatic checkpoints. Store onlyDisposable, no crash/powerloss durability; append-only history does not imply permanent reliable backup, no process snapshots or external side-effect rollback. Official1.0 single-sample e5c7aaae05 fsbench1.71x and157snapshots100.1MB versus1994.6MB19.9x; not universal or our reproduction. Originalreview notesfioseqwrite0.31x and POSIX707differentialassertions includingcascades.

v1.1.0 released2026-10-24, tag9f97a7ec95 (mainatcheckad78914e36b258b360daf13aec164b5655814689). Breaking API split @layerfs/agent/backend/runtime, LayerFS.open/init factories, explicitSandboxbeforemount andlayerfsCLI. macOS worker inLinuxcontainer; WindowsWSL2; not nativeAPFS/NTFS FUSE. Sourceonly; matchingcomponentsrequired; no newperformanceclaim. Release records disclose Linux host/FUSE/realStoreJS tests notrun; authorMac/Windowsverificationnotours. No localFUSE/Docker/runtime/performance/recovery test claimed.

WeChat originalcreation2026-10-22 credential prCUE631thH1cmNLi42prNAqjTxBxCcQryG-mPZMUBMyNxcC2_cvrYR4rLbiScXi retained unchanged. Current2026-10-26 draft/get40007; remote5draftsnone matching; freepublish/batchget48001unauthorized. recorded/currentstatusunverified; mediaIdempty,archivedMediaIdold. No duplicate draft/add.
