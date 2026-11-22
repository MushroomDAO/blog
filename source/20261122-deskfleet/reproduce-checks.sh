#!/bin/sh
set -eu
deskfleet_tmp=$(mktemp -d)
git clone https://github.com/yet-another-ai/deskfleet.git "$deskfleet_tmp/repo"
git -C "$deskfleet_tmp/repo" checkout 9bd4a762ebb59934117823958577441b6f298c72
cd "$deskfleet_tmp/repo"
node --test apps/daemon/src/peer-admission.test.ts apps/daemon/src/worktree-branch-naming.test.ts apps/daemon/src/linux-desktop-permissions.test.ts
