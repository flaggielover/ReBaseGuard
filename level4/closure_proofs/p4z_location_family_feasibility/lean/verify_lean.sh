#!/bin/sh
# P4Z bounded-survival verification.  Read-only against the prebuilt mathlib in
# the main worktree; touches nothing there.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
PKGS=${P4Z_MATHLIB_PACKAGES:-/Users/suzhe/ReBaseGuard/rebaseguard-lean/.lake/packages}
TOOLCHAIN=${P4Z_LEAN_TOOLCHAIN:-/Users/suzhe/.elan/toolchains/leanprover--lean4---v4.34.0-rc1}
LP=""
for p in "$PKGS"/*/.lake/build/lib/lean; do LP="$LP$p:"; done
export LEAN_PATH="$LP$HERE"
"$TOOLCHAIN/bin/lean" --version
"$TOOLCHAIN/bin/lean" -o "$HERE/BoundedSurvival.olean" "$HERE/BoundedSurvival.lean"
"$TOOLCHAIN/bin/lean" "$HERE/AxiomAudit.lean"
