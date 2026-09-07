#!/bin/sh
# P4Z verified bundle + patch series + SHA256SUMS + recovery instructions.
set -e
WT=${P4Z_WORKTREE:-/Users/suzhe/ReBaseGuard-p4z}
OUT=${P4Z_BUNDLE_DIR:-/Users/suzhe/rebaseguard-bundles}
BASE=${P4Z_BASE:-p5y-gate1-micropilots}
BR=p4z-location-family-feasibility
mkdir -p "$OUT"
HEAD=$(git -C "$WT" rev-parse HEAD)
git -C "$WT" bundle create "$OUT/$BR.bundle" "$BASE..$BR"
rm -rf "$OUT/$BR-patches"
git -C "$WT" format-patch -o "$OUT/$BR-patches" "$BASE..$BR" >/dev/null
( cd "$OUT" && shasum -a 256 "$BR.bundle" "$BR-patches"/*.patch > "$BR-SHA256SUMS.txt" )
git -C "$WT" bundle verify "$OUT/$BR.bundle" >/dev/null
echo "head    $HEAD"
echo "bundle  $OUT/$BR.bundle"
echo "patches $(ls "$OUT/$BR-patches" | wc -l | tr -d ' ') files"
echo "sums    $OUT/$BR-SHA256SUMS.txt"
