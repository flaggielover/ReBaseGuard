#!/usr/bin/env bash
# Verify the ReBaseGuard Level 4 package.
#
# This runs the Level 4 test suite AND the frozen Level 1-3 suite, because a
# Level 4 change that breaks the frozen closure is a failure regardless of how
# well the new code behaves on its own.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

L4_PY="level4/.venv/bin/python"
L3_PY="rebaseguard-proof/.venv/bin/python"

for interpreter in "$L4_PY" "$L3_PY"; do
  if [ ! -x "$interpreter" ]; then
    echo "missing interpreter: $interpreter" >&2
    echo "see level4/README.md for environment setup" >&2
    exit 1
  fi
done

echo "== frozen Level 1-3 regression suite =="
# The frozen suite resolves its artifact paths relative to the working
# directory, so it must be run from inside rebaseguard-proof.
( cd rebaseguard-proof && ".venv/bin/python" -m pytest -q )

echo
echo "== Level 4 Stage A suite =="
"$L4_PY" -m pytest level4/tests -q

echo
echo "== Level 4 Stage B suite =="
"$L4_PY" -m pytest level4/stage_b/tests -q

echo
echo "== Level 4 Stage C suite =="
"$L4_PY" -m pytest level4/stage_c/tests -q

echo
echo "== Level 4 Stage C.1 suite =="
"$L4_PY" -m pytest level4/stage_c1/tests -q

echo
echo "== Level 4 Stage D suite =="
"$L4_PY" -m pytest level4/stage_d/tests -q

echo
echo "== Level 4 Stage E suite =="
"$L4_PY" -m pytest level4/stage_e/tests -q

echo
echo "== Level 4 Stage F suite =="
"$L4_PY" -m pytest level4/stage_f/tests -q

echo
echo "== Level 4 post-closure re-audit suite =="
"$L4_PY" -m pytest level4/re_audit_post_closure/tests -q

echo
echo "== Level 4 D4 phase-map closure suite =="
"$L4_PY" -m pytest level4/closure_proofs/d4_phase_map/tests -q

echo
echo "== Level 4 novelty-verification closure suite =="
"$L4_PY" -m pytest level4/closure_proofs/novelty_verification/tests -q

echo
echo "== Level 4 external-validation V2 suite =="
"$L4_PY" -m pytest level4/closure_proofs/external_validation_v2/tests -q

echo
echo "== Level 4 external-validation V3 suite =="
"$L4_PY" -m pytest level4/closure_proofs/external_validation_v3/tests -q

echo
echo "== Level 4 final global re-audit suite =="
"$L4_PY" -m pytest level4/final_global_reaudit/tests -q

echo
echo "== Level 4 L4R-06 stability-aware policy suite =="
"$L4_PY" -m pytest level4/closure_proofs/l4r06_policy/tests -q

echo
echo "== Level 4 environment =="
"$L4_PY" - <<'PY'
import sys
sys.path.insert(0, "level4/src")
from rebaseguard_level4 import provenance
state = provenance.git_state()
env = provenance.dependency_versions()
print(f"commit      : {state['commit']}")
print(f"working tree: {'dirty' if state['dirty'] else 'clean'}")
print(f"python      : {env['python_short']}")
print(f"numpy/scipy : {env['numpy']} / {env['scipy']}")
print(f"code digest : {provenance.code_hash()['__combined__'][:16]}...")
PY

echo
echo "== Stage B certificate =="
"$L4_PY" - <<'PYEOF'
import json, pathlib
p = pathlib.Path("level4/stage_b/certificate/period2_certificate.json")
if not p.exists():
    print("  (not built -- run level4/stage_b/reproduce.sh)")
else:
    c = json.loads(p.read_text())
    t = c["theorem"]
    lo, hi = t["root_interval"]
    l2lo, l2hi = t["lambda2"]
    print("  decision   :", c["decision"])
    print("  root I     : [%.6f, %.6f]  (0 excluded: %s)" % (lo, hi, t["zero_excluded"]))
    print("  uniqueness : %s  (min Hprime = %.4f)" % (t["uniqueness_certified"], t["Hprime_min_over_I"]))
    print("  multiplier : [%.6f, %.6f]  (below 1: %s)" % (l2lo, l2hi, t["multiplier_certified"]))
PYEOF

echo
echo "== Stage C decision =="
"$L4_PY" - <<'PYEOF'
import json, pathlib
p = pathlib.Path("level4/stage_c/results/findings.json")
if not p.exists():
    print("  (not built -- run level4/stage_c/reproduce.sh)")
else:
    f = json.loads(p.read_text())
    print("  decision  :", f["decision"])
    failed = f["decision_basis"]["failed"]
    print("  failed    :", ", ".join(failed) if failed else "none")
    d = f["domination"]
    print("  policy rho: %.6f (MSE %.5f)" % (d["rbg_rho"], d["mse_rbg"]))
    print("  oracle rho: %.6g (MSE %.5f)  dominates: %s"
          % (d["oracle_rho"], d["mse_oracle"], d["dominated"]))
PYEOF

echo
echo "== Stage C.1 decision =="
"$L4_PY" - <<'PYEOF'
import json, pathlib
p = pathlib.Path("level4/stage_c1/results/findings_confirmatory.json")
if not p.exists():
    print("  (not built -- run level4/stage_c1/reproduce.sh)")
else:
    f = json.loads(p.read_text())
    print("  decision  :", f["decision"])
    print("  H-C1      : %s at all shifts (epsilon=%.2f)"
          % ("PASS" if f["hc1_all_pass"] else "FAIL", f["epsilon"]))
    for r in f["rows"]:
        print("    Delta=%-5g D=%+.5f  upper95=%+.5f  %s"
              % (r["shift"], r["D"]["point"], r["D"]["ci_high"],
                 "pass" if r["hc1_pass"] else "FAIL"))
    print("  note      : Stage C remains STAGE-C-PARTIAL; C6 stays failed")
PYEOF

echo
echo "== Stage D decision =="
"$L4_PY" - <<'PYEOF'
import json, pathlib
p = pathlib.Path("level4/stage_d/results/stage_d_decision.json")
if not p.exists():
    print("  (not built -- run level4/stage_d/reproduce.sh)")
else:
    d = json.loads(p.read_text())
    print("  decision  :", d["decision"])
    print("  protocol  : %s (%s)"
          % (d["protocol_sha256_actual"][:16] + "...",
             "unchanged" if d["protocol_unchanged"] else "CHANGED"))
    for c in d["criteria"]:
        print("    %-9s %-28s %s" % (c["id"], c["status"], c["value"]))
    print("  note      : D2.3 FAILED and stays failed; the Gamma_m=2 crossing")
    print("              is a local-stability boundary of the deterministic")
    print("              skeleton, NOT an operational transition; t3 AMBIGUOUS")
PYEOF

echo
echo "== Stage D adversarial suite =="
"$L4_PY" - <<'PYEOF'
import json, pathlib
p = pathlib.Path("level4/stage_d/results/adversarial_d.json")
if not p.exists():
    print("  (not built)")
else:
    a = json.loads(p.read_text())
    print("  %d/%d passed" % (a["n_passed"], a["n_checks"]))
    for c in a["checks"]:
        if not c["passed"]:
            print("    FAIL:", c["check"])
PYEOF

echo
echo "== Stage E decision =="
"$L4_PY" - <<'PYEOF'
import json, pathlib
p = pathlib.Path("level4/stage_e/results/stage_e_decision.json")
if not p.exists():
    print("  (not built -- run level4/stage_e/reproduce.sh)")
else:
    d = json.loads(p.read_text())
    print("  decision  :", d["decision"])
    print("  protocol  : %s (%s)" % (d["protocol_sha256_actual"][:16] + "...",
          "unchanged" if d["protocol_unchanged"] else "CHANGED"))
    print("  adversarial: %d/%d" % (d["adversarial"]["passed"], d["adversarial"]["total"]))
    print("  H-E5 support: %d of 3 (2 required); closure unreachable: %s"
          % (d["n_tasks_supporting_H_E5"], d["closure_mathematically_unreachable"]))
    for k, v in d["per_task"].items():
        print("    %-13s %-32s counts=%s" % (k, v["usability"], v["counts_toward_H_E5"]))
    print("  note      : semi-real external validation, NOT deployment; no")
    print("              sample-efficiency claim; E3 is an alert burden")
PYEOF

echo
echo "== Stage F: FINAL LEVEL-4 CLOSURE =="
"$L4_PY" - <<'PYEOF'
import json, pathlib
p = pathlib.Path("level4/stage_f/results/final_decision.json")
if not p.exists():
    print("  (not built -- run level4/stage_f/reproduce.sh)")
else:
    d = json.loads(p.read_text())
    print("  Level 1-3 : CLOSED")
    print("  Level 4   :", d["decision"])
    print("  taxonomy  :", d["taxonomy_source"])
    print("  mandatory : %d pass / %d partial / %d unmet  (of %d)"
          % (d["n_mandatory_passed"], d["n_mandatory_partial_or_negative"],
             d["n_mandatory_unmet"], d["n_mandatory_total"]))
    print("  unmet     :")
    for r in d["mandatory_unmet"]:
        print("    - %-42s %s" % (r["requirement"], r["status"]))
    a = d.get("adversarial_f", {})
    print("  adversarial F: %s/%s" % (a.get("passed"), a.get("total")))
    print("  integrity : %s ; historical artifacts untouched: %s"
          % (d["protocol_integrity"]["status"], d["historical_artifacts_untouched"]))
PYEOF

echo
echo "== Current post-closure Level-4 status =="
"$L4_PY" - <<'PYEOF'
import json, pathlib
p = pathlib.Path("level4/re_audit_post_closure/results/final_decision.json")
if not p.exists():
    print("  (not built -- run level4/re_audit_post_closure/reproduce.sh)")
else:
    d = json.loads(p.read_text())
    print("  historical Stage F:", d["historical_stage_f_status"])
    print("  current Level 4  :", d["current_status"])
    print("  requirements     : %d pass / %d partial / %d fail / %d open"
          % (d["pass_count"], d["partial_count"], d["fail_count"], d["open_count"]))
    print("  mandatory unmet :")
    for row in d["mandatory_unmet"]:
        print("    - %s [%s]" % (row["requirement"], row["blocker_type"]))
PYEOF

echo
echo "LEVEL 4 VERIFICATION OK"
