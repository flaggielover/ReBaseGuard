#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
CAMPAIGN="$ROOT/level4/closure_proofs/p4_theory_generalization"
PY="$ROOT/level4/.venv/bin/python"

export PYTHONDONTWRITEBYTECODE=1
export PYTEST_ADDOPTS="-p no:cacheprovider"

# The intended verification environment, as documented by the closed Priority-3
# verifier's own environment probes.  Three protected suites are sensitive to
# these two conditions and to nothing else:
#   * `m_gt_1_priority1` hashes a file listing whose sort order is collation
#     dependent, and its recorded hash is the en_US.UTF-8 one;
#   * `sr_derivative` and `m_gt_1_track1b` shell out to `rg` for their
#     seed-confinement assertions.
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
export LC_COLLATE=en_US.UTF-8

if ! command -v rg >/dev/null 2>&1; then
  echo "ERROR: a ripgrep binary named 'rg' must be on PATH." >&2
  echo "Three protected suites shell out to it; without it they fail for" >&2
  echo "environment reasons and the repository gate cannot be evaluated." >&2
  exit 1
fi

echo "== four-route cross-family correspondence campaign (the expensive step) =="
"$PY" "$CAMPAIGN/numerics/run_correspondence.py"

echo "== generalized m-rho stability map, tables and generated report =="
"$PY" "$CAMPAIGN/scripts/build_reports.py"

echo "== figures =="
"$PY" "$CAMPAIGN/scripts/make_figures.py"

echo "== rigorous Arb certification of the three frozen objects =="
"$PY" "$CAMPAIGN/certificates/run_certificate.py"

echo "== Lean spine and axiom audit =="
"$PY" "$CAMPAIGN/run_lean.py"

echo "== repository regression suites, freeze-scoped replays and diagnostics =="
"$PY" "$CAMPAIGN/run_repository_verification.py"

echo "== mechanical Priority-4 closure decision =="
# derived before the final test pass so that the focused suite can assert the
# decision it produced, rather than skipping those checks on a clean run
"$PY" "$CAMPAIGN/derive_closure.py"

echo "== focused Priority-4 tests =="
"$PY" -m pytest "$CAMPAIGN/tests" -q
"$PY" - "$CAMPAIGN/results/closure_decision.json" <<'PYEOF'
import json, sys
d = json.load(open(sys.argv[1]))
# The recorded verdict is PARTIAL.  This reproducer asserts that the campaign
# reproduces its own recorded outcome, including which gates did not pass.  It
# does NOT assert closure, and it fails loudly if a future run silently turns a
# failing gate into a passing one without the report being updated.
assert d["verdict"] == "PARTIAL", d["verdict"]
assert not d["all_required_gates_pass"]
assert set(k for k, v in d["gates"].items() if not v) == {
    "all_theorem_supported_cells_pass",
    "all_outside_assumption_cells_demonstrate_failure",
    "gaussian_consistency_with_closed_core",
    "repository_verification_all_gates_pass",
}, sorted(k for k, v in d["gates"].items() if not v)
assert not any(d["negative_claims_asserted_false"].values())
print("Level-4 Priority 4 -- PARTIAL, as recorded; repository verification: "
      + d["repository_verification_status"])
PYEOF
