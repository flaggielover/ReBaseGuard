"""R2 reproduction comparison (analysis only, reads JSON): regenerated pinned rungs (NS/validation/C1B_R2_*) versus
the pre-pin rungs (logs/prepin/C1B_*), exact-field by exact-field.  Output NS/validation/C1B_R2_PREPIN_COMPARISON.json.
Reports counts only (identical / tighter / looser); no values (R2.3)."""
from __future__ import annotations

import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parents[3]
sys.path.insert(0, str(NS / "code"))
import ov_quarantine as Q  # noqa: E402

Q.install_import_guard()
UPPER = ("tau", "C_T", "A_bar", "tau_a_up", "S2_up", "TN_up", "D1", "D2", "L1_up", "L2_up")
LOWER = ("tau_a_lo", "D_lo", "Lambda_lo")


def ex(v):
    return F(v["exact"]) if isinstance(v, dict) and "exact" in v else None


def rungs(files):
    out = {}
    for p in files:
        d = json.loads(p.read_text())
        for r in d.get("records", []):
            if r.get("status") == "CERTIFIED":
                out[(d["drift"], d.get("drift_radius", "0/1"), r["degree"])] = (p.name, r)
    return out


def main():
    V = NS / "validation"
    P = HERE / "logs" / "prepin"
    res = {"schema": "C1B_R2_PREPIN_COMPARISON/1", "families": {}}
    for fam, new_glob, old_globs in (("PW", "C1B_R2_PW_*.json", ("C1B_PW9_*.json", "C1B_PW_*.json")),
                                     ("PLAIN", "C1B_R2_PLAIN_*.json", ("C1B_POINT_*.json",))):
        new = rungs(sorted(V.glob(new_glob)))
        old = {}
        for g in old_globs:                                   # PW9 preferred over PW where both exist
            for k, v in rungs(sorted(P.glob(g))).items():
                old.setdefault(k, v)
        rows = []
        for k in sorted(set(new) & set(old)):
            nr, orr = new[k][1], old[k][1]
            cnt = {"identical": 0, "tighter": 0, "looser": 0}
            loose = []
            for f in UPPER + LOWER:
                a, b = ex(orr.get(f)), ex(nr.get(f))
                if a is None or b is None:
                    continue
                if a == b:
                    cnt["identical"] += 1
                elif (b < a) == (f in UPPER):
                    cnt["tighter"] += 1
                else:
                    cnt["looser"] += 1
                    loose.append(f)
            rows.append({"drift": k[0], "radius": k[1], "degree": k[2], **cnt, "looser_fields": loose,
                         "old_file": old[k][0], "new_file": new[k][0]})
        res["families"][fam] = {"compared_rungs": len(rows), "rows": rows,
                                "only_new": [list(k) for k in sorted(set(new) - set(old))],
                                "only_old": [list(k) for k in sorted(set(old) - set(new))]}
        print(fam, len(rows), "rungs;", sum(r["identical"] for r in rows), "identical,",
              sum(r["tighter"] for r in rows), "tighter,", sum(r["looser"] for r in rows), "looser fields")
    import hashlib
    sys.path.insert(0, str(HERE))
    import c1b_prov as PV
    res["provenance"] = PV.provenance({})
    res["provenance"]["own_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    res["provenance"]["own_file"] = Path(__file__).name
    (V / "C1B_R2_PREPIN_COMPARISON.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    Q.log_execution("streams/C_308/LR/cusum/r2_compare_prepin.py", "C1b R2 regeneration vs pre-pin comparison",
                    cells_touched=[], klass="NONTARGET_DRIFT_VALIDATION", notes="reads own JSON only")


if __name__ == "__main__":
    main()
