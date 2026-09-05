#!/usr/bin/env bash
# Checkout and verify the exact commit. REPO_URL and COMMIT come from the
# environment; nothing secret is written into this script.
set -euo pipefail
: "${REPO_URL:?set REPO_URL}"
: "${COMMIT:?set COMMIT (the frozen pre-production commit)}"
: "${WORKDIR:=$HOME/rebaseguard}"
git clone --no-checkout "$REPO_URL" "$WORKDIR" || true
cd "$WORKDIR"
git fetch --all --tags
git checkout --detach "$COMMIT"
echo "HEAD = $(git rev-parse HEAD)"
test "$(git rev-parse HEAD)" = "$COMMIT" || { echo "COMMIT MISMATCH"; exit 1; }
git status --porcelain | grep . && { echo "WORKTREE DIRTY"; exit 1; } || echo "worktree clean"
