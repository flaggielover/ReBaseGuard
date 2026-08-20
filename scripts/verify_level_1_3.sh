#!/usr/bin/env bash
#
# verify_level_1_3.sh — unified verification of the ReBaseGuard Level 1–3
# evidence package.
#
# Performs six independent checks:
#   1. Lean toolchain / environment identification
#   2. lake build
#   3. Lean bypass scan (sorry / admit / axiom / unsafe / native_decide)
#   4. Lean axiom audit of the principal theorems (+ #check of the final theorem)
#   5. Arb certificate full-replay audit  (requires the pinned .venv)
#   6. Lightweight numerical sanity checks (pytest + certificate arithmetic)
#
# Exits 0 only if every executed check passes. Any genuine failure exits nonzero.
# Checks that cannot run in this environment are reported as SKIP and, unless
# --allow-skip is given, are treated as failures so that a partial run can never
# masquerade as a full verification.
#
# Non-destructive: the only file the underlying tools rewrite
# (rebaseguard-proof/proofs/audit_report.md) is backed up and restored.
#
# No network access is required or attempted.
#
# Usage:
#   scripts/verify_level_1_3.sh [--quick] [--allow-skip]
#     --quick       skip step 4b (direct source elaboration of the final Lean
#                   module, ~4 min); everything else still runs
#     --allow-skip  treat unavailable-environment SKIPs as non-fatal

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LEAN_DIR="$ROOT/rebaseguard-lean"
PROOF_DIR="$ROOT/rebaseguard-proof"

QUICK=0
ALLOW_SKIP=0
for arg in "$@"; do
  case "$arg" in
    --quick)      QUICK=1 ;;
    --allow-skip) ALLOW_SKIP=1 ;;
    *) echo "unknown argument: $arg" >&2; exit 64 ;;
  esac
done

FAILURES=0
SKIPS=0
WORK="$(mktemp -d)"
cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT

hr()   { printf '%s\n' "------------------------------------------------------------"; }
pass() { printf 'PASS  %s\n' "$*"; }
fail() { printf 'FAIL  %s\n' "$*"; FAILURES=$((FAILURES+1)); }
skip() { printf 'SKIP  %s\n' "$*"; SKIPS=$((SKIPS+1)); }
info() { printf '      %s\n' "$*"; }

printf '============================================================\n'
printf 'ReBaseGuard Level 1-3 verification\n'
printf 'root: %s\n' "$ROOT"
printf 'date: %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
printf '============================================================\n'

# ---------------------------------------------------------------- 1. environment
hr; echo "[1/6] Lean environment"
if ! command -v lake >/dev/null 2>&1; then
  skip "lake not on PATH - Lean checks 1-4 cannot run"
  LEAN_OK=0
else
  LEAN_OK=1
  info "toolchain: $(cat "$LEAN_DIR/lean-toolchain")"
  info "$(lake --version 2>&1 | head -1)"
  MATHLIB_REV="$(python3 - "$LEAN_DIR/lake-manifest.json" <<'PY'
import json,sys
m=json.load(open(sys.argv[1]))
print(next((p.get("rev","?") for p in m["packages"] if p.get("name")=="mathlib"), "?"))
PY
)"
  info "mathlib rev: $MATHLIB_REV"
  pass "Lean environment identified"
fi

# ------------------------------------------------------------------- 2. lake build
hr; echo "[2/6] lake build"
if [ "$LEAN_OK" -eq 1 ]; then
  if (cd "$LEAN_DIR" && lake build) > "$WORK/lake_build.log" 2>&1; then
    pass "lake build exit 0"
    info "$(grep -c '^warning' "$WORK/lake_build.log" || true) warning lines (cosmetic lint; see 08_LIMITATIONS)"
    tail -1 "$WORK/lake_build.log" | sed 's/^/      /'
  else
    fail "lake build exit $? - see $WORK/lake_build.log"
    tail -25 "$WORK/lake_build.log" | sed 's/^/      /'
  fi
else
  skip "lake build (no lake)"
fi

# ------------------------------------------------------------------- 3. bypass scan
hr; echo "[3/6] Lean bypass scan (case-insensitive)"
BYPASS_HITS=0
for pat in sorry admit axiom unsafe native_decide; do
  if hits="$(grep -rniE "$pat" "$LEAN_DIR/RebaseguardLean" "$LEAN_DIR/RebaseguardLean.lean" 2>/dev/null)"; then
    echo "$hits" | sed 's/^/      /'
    BYPASS_HITS=$((BYPASS_HITS+1))
  fi
done
if [ "$BYPASS_HITS" -eq 0 ]; then
  pass "no sorry / admit / axiom / unsafe / native_decide anywhere in the Lean sources"
else
  fail "$BYPASS_HITS bypass pattern(s) matched - inspect the hits above semantically before accepting"
fi

# ------------------------------------------------------- 4. axiom audit + final theorem
hr; echo "[4/6] Lean axiom audit"
if [ "$LEAN_OK" -eq 1 ]; then
  cat > "$WORK/AxCheck.lean" <<'LEANEOF'
import RebaseguardLean
open RebaseguardLean
#check @RebaseguardLean.hasDerivAt_rebaseguard_cusum
#print axioms stoppedIntegrand_hasDerivAt
#print axioms RebaseguardLean.hasDerivAt_integral_stoppedIntegrand_zero
#print axioms RebaseguardLean.hasDerivAt_integral_stoppedIntegrand_zero_of_expMoment
#print axioms RebaseguardLean.isStoppingTime_cusumTau
#print axioms RebaseguardLean.integrable_exp_forcingNat
#print axioms RebaseguardLean.ae_stopped_quantities_eq
#print axioms RebaseguardLean.integrable_exp_abs_walkAt_of_moment_tail
#print axioms RebaseguardLean.exists_pos_integrable_exp_abs_walkAt_rebaseguard
#print axioms RebaseguardLean.hasDerivAt_rebaseguard_cusum
LEANEOF
  if (cd "$LEAN_DIR" && lake env lean "$WORK/AxCheck.lean") > "$WORK/axioms.log" 2>&1; then
    # `#print axioms` wraps long axiom lists over several lines, so the report is
    # parsed after re-joining, never with a line-oriented grep.
    if python3 - "$WORK/axioms.log" <<'PYEOF'
import re, sys
text = open(sys.argv[1]).read()
if 'sorryAx' in text:
    print("sorryAx present in the axiom report"); sys.exit(1)
if re.search(r'^\S*error', text, re.M) or 'error:' in text:
    print("the axiom check reported an error"); sys.exit(1)
flat = " ".join(text.split())
reports = re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", flat)
if len(reports) != 9:
    print(f"expected 9 axiom reports, found {len(reports)}"); sys.exit(1)
baseline = {"propext", "Classical.choice", "Quot.sound"}
bad = [(n, a) for n, a in reports
       if set(x.strip() for x in a.split(",") if x.strip()) - baseline]
if bad:
    for n, a in bad:
        print(f"non-baseline axioms in {n}: [{a}]")
    sys.exit(1)
if not re.search(r'hasDerivAt_rebaseguard_cusum\b.*HasDerivAt', flat):
    print("#check of the final theorem did not elaborate"); sys.exit(1)
print(f"{len(reports)} theorems, all with axioms [propext, Classical.choice, Quot.sound]")
PYEOF
    then
      pass "axiom audit clean; final theorem elaborates"
      sed 's/^/      /' "$WORK/axioms.log" | head -3
    else
      fail "axiom audit failed"
      sed 's/^/      /' "$WORK/axioms.log"
    fi
  else
    fail "lake env lean on the axiom-check file failed"
    tail -20 "$WORK/axioms.log" | sed 's/^/      /'
  fi

  if [ "$QUICK" -eq 0 ]; then
    echo "[4b] direct source elaboration of the final module (slow)"
    if (cd "$LEAN_DIR" && lake env lean RebaseguardLean/ReBaseGuardIdentity.lean) > "$WORK/final.log" 2>&1; then
      if grep -qi 'error' "$WORK/final.log"; then
        fail "ReBaseGuardIdentity.lean elaborated with errors"
        sed 's/^/      /' "$WORK/final.log"
      else
        pass "ReBaseGuardIdentity.lean elaborates from source, exit 0"
      fi
    else
      fail "direct elaboration of ReBaseGuardIdentity.lean exit $?"
      tail -20 "$WORK/final.log" | sed 's/^/      /'
    fi
  else
    info "4b skipped (--quick)"
  fi
else
  skip "axiom audit (no lake)"
fi

# ------------------------------------------------------------ 5. Arb certificate
hr; echo "[5/6] Arb certificate full-replay audit"
VENV_PY="$PROOF_DIR/.venv/bin/python"
if [ ! -x "$VENV_PY" ]; then
  skip "pinned virtualenv not found at $VENV_PY (see closure/07_REPRODUCIBILITY.md to create it)"
elif ! "$VENV_PY" -c 'import flint' >/dev/null 2>&1; then
  skip "python-flint not importable in the pinned virtualenv"
else
  info "python $("$VENV_PY" -c 'import sys;print(sys.version.split()[0])')"
  info "python-flint $("$VENV_PY" -c 'import flint;print(flint.__version__)')"
  REPORT="$PROOF_DIR/proofs/audit_report.md"
  cp "$REPORT" "$WORK/audit_report.md.bak"
  if (cd "$PROOF_DIR" && "$VENV_PY" -m rebaseguard_certify.audit proofs/certificate.json) \
        > "$WORK/arb_audit.log" 2>&1; then
    if grep -q '"status": "PASS"' "$WORK/arb_audit.log" \
       && grep -q '"Gamma_lower_gt_2": true' "$WORK/arb_audit.log" \
       && grep -q '"continuum_residual_replayed": true' "$WORK/arb_audit.log"; then
      pass "certificate full replay: status PASS, Gamma_lower > 2, continuum residual replayed"
      grep -E '"Gamma_(lower|upper)"' "$WORK/arb_audit.log" | cut -c1-96 | sed 's/^/      /'
    else
      fail "auditor exited 0 but the report does not assert a full PASS"
      sed 's/^/      /' "$WORK/arb_audit.log"
    fi
  else
    fail "certificate audit exit $? - see log below"
    tail -20 "$WORK/arb_audit.log" | sed 's/^/      /'
  fi
  # restore the artifact the auditor rewrites, so this script is non-destructive
  if ! cmp -s "$WORK/audit_report.md.bak" "$REPORT"; then
    info "note: auditor rewrote audit_report.md with different content; restoring the original"
    cp "$WORK/audit_report.md.bak" "$REPORT"
  else
    info "regenerated audit_report.md is byte-identical to the stored one"
  fi
fi

# ------------------------------------------------------- 6. numerical sanity checks
hr; echo "[6/6] Numerical sanity checks"
if [ ! -x "$VENV_PY" ]; then
  skip "numerical checks (no virtualenv)"
else
  if (cd "$PROOF_DIR" && "$VENV_PY" -m pytest -q) > "$WORK/pytest.log" 2>&1; then
    pass "regression suite: $(tail -2 "$WORK/pytest.log" | grep -oE '[0-9]+ passed.*' | head -1)"
  else
    fail "regression suite failed"
    tail -20 "$WORK/pytest.log" | sed 's/^/      /'
  fi

  # Certificate arithmetic and Monte Carlo consistency, checked independently of
  # the auditor: the stored interval must be b_hat(0,0) +/- E_b, must exclude 2,
  # and must contain every recorded cross-check value.
  if "$VENV_PY" - "$PROOF_DIR" > "$WORK/sanity.log" 2>&1 <<'PYEOF'
import json, sys
from decimal import Decimal, getcontext
from pathlib import Path
getcontext().prec = 90
root = Path(sys.argv[1])
cert = json.loads((root / "proofs/certificate.json").read_text())
res  = json.loads((root / "proofs/residual.json").read_text())
enc  = json.loads((root / "proofs/enclosure.json").read_text())
diag = json.loads((root / "diagnostics/reference.json").read_text())
bell = json.loads((root / "proofs/bellman_crosscheck.json").read_text())

def ball(s):                       # "[1.234 +/- 5e-6]" or "1.234"
    s = s.strip().lstrip("[").rstrip("]")
    return Decimal(s.split("+/-")[0].strip())

lo, hi = Decimal(cert["Gamma_lower"]), Decimal(cert["Gamma_upper"])
bhat   = ball(res["b_hat_origin"]["ball"])
Eb     = ball(enc["E_b"]["ball"])
errs = []
if not lo > 2:                       errs.append(f"lower endpoint {lo} is not > 2")
if not hi > lo:                      errs.append("interval is not ordered")
# The propagation rounds the radius OUTWARD to a dyadic, so the stored interval
# must CONTAIN b_hat +/- E_b (never equal it), and stay symmetric about b_hat.
if lo > bhat - Eb: errs.append("lower endpoint is inside b_hat - E_b (not outward-rounded)")
if hi < bhat + Eb: errs.append("upper endpoint is inside b_hat + E_b (not outward-rounded)")
if lo + hi != 2 * bhat: errs.append("interval is not symmetric about b_hat(0,0)")
if cert["model"] != {"k": {"numerator":1,"denominator":2},
                     "h": {"numerator":5,"denominator":1}}:
    errs.append("certificate model is not k=1/2, h=5")
if cert["target"] != "E[Z_tau*T_tau]": errs.append("certificate target is not E[Z_tau*T_tau]")
for r in diag["runs"]:
    g = Decimal(repr(r["gamma"]))
    if not (lo < g < hi): errs.append(f"Monte Carlo gamma {g} outside the certified interval")
    d = Decimal(repr(r["mean_z_tau_sq"])) + Decimal(repr(r["cross_term"])) - g
    if abs(d) > Decimal("1e-9"): errs.append(f"decomposition identity off by {d}")
gb = ball(bell["gamma_finite"]["ball"])
if not (lo < gb < hi): errs.append(f"Bellman cross-check {gb} outside the certified interval")

if errs:
    print("SANITY FAILURES:"); [print(" -", e) for e in errs]; sys.exit(1)
print(f"certified interval [{lo}, {hi}]")
print(f"b_hat(0,0) = {bhat}")
print(f"E_b = {Eb}")
print(f"stored radius (hi-lo)/2 = {(hi-lo)/2}  (outward by {(hi-lo)/2 - Eb})")
print(f"margin above 2: {lo - 2}")
print("Monte Carlo, Bellman cross-check and decomposition identity all consistent")
PYEOF
  then
    pass "certificate arithmetic and cross-check consistency"
    sed 's/^/      /' "$WORK/sanity.log"
  else
    fail "certificate/cross-check sanity checks failed"
    sed 's/^/      /' "$WORK/sanity.log"
  fi
fi

# ------------------------------------------------------------------------ verdict
hr
if [ "$SKIPS" -gt 0 ] && [ "$ALLOW_SKIP" -eq 0 ]; then
  printf 'RESULT: INCOMPLETE - %d check(s) skipped, %d failed\n' "$SKIPS" "$FAILURES"
  printf 'A skipped check is not a pass. Re-run with a complete environment,\n'
  printf 'or pass --allow-skip if a partial verification is genuinely intended.\n'
  exit 3
fi
if [ "$FAILURES" -eq 0 ]; then
  printf 'RESULT: ALL CHECKS PASSED (%d skipped, explicitly allowed)\n' "$SKIPS"
  exit 0
fi
printf 'RESULT: %d CHECK(S) FAILED\n' "$FAILURES"
exit 1
