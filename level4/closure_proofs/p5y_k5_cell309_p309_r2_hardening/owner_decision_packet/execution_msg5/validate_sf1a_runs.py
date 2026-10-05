"""Independent content validation of the SF1-A regression and light rehearsal (bound to 716946e8's bytes).

usage: validate_sf1a_runs.py <scratch t7 dir> <session repo> <out.json>
"""
import glob
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

t7, repo, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
SF1A = "716946e8d9a6744d0b49de6acc802605b6eb1bf8"
RUN = "level4/closure_proofs/p5y_k5_cell309_p309_r2/code/p309_" + "qualify.py"
runner = subprocess.run(["git", "-C", str(repo), "show", f"{SF1A}:{RUN}"], capture_output=True, check=True).stdout
tree = subprocess.run(["git", "-C", str(repo), "rev-parse", SF1A + "^{tree}"], capture_output=True, text=True,
                      check=True).stdout.strip()
v = json.loads((t7 / "ev" / "REHEARSAL_716946e8_REVALIDATION.json").read_text())
p = json.loads((t7 / "rehearsal_light_sf1a" / "PROVENANCE.json").read_text())
q = (t7 / "rehearsal_light_sf1a" / "attempt" / "QC15.json").read_text()
acks = sorted(set(re.findall(r"(A[0-9]+_[a-z_0-9]+)[^a-zA-Z]{0,12}(true|false)", q)))
g = json.loads((t7 / "ev" / "REG_716946e8.json").read_text())
sc = json.loads(Path(glob.glob(str(t7 / "reg_sf1a" / "evidence" / "fc6" / "STATIC_CONTROLS.json"))[0]).read_text())
gates = {f.stem: json.loads(f.read_text()).get("pass") for f in sorted((t7 / "rehearsal_light_sf1a" / "attempt").glob("QC*.json"))
         if f.stem[2:].replace("_", "").isalnum() and not f.stem.endswith("REHEARSE")}
checks = {
    "rehearsal re-validation PASS, no reasons": v.get("verdict") == "PASS" and not v.get("reasons"),
    "rehearsal bound to 716946e8": p["package"]["commit"] == SF1A,
    "rehearsal tree equals 716946e8's tree": p["package"]["tree"] == tree,
    "rehearsal parent is r2 b66a45f0": p["package"]["parents"] == ["b66a45f097989764176075802c953df4b72c2aef"],
    "all 15 light gates PASS (record content)": len(gates) == 15 and all(gates.values()),
    "QC15 PASS with A1-A10 all true": json.loads(q).get("pass") is True and len(acks) == 10
    and all(x == "true" for _, x in acks),
    "regression: every run rc 0": all(r.get("rc") == 0 for r in g["runs"].values()),
    "regression runner bytes are 716946e8's": g.get("runner_sha256") == hashlib.sha256(runner).hexdigest(),
    "QC11 112/112 flows, 0 failed": g.get("qc11_table", {}).get("flows") == 112 and g["qc11_table"].get("all_pass") is True,
    "scan pins all current": g.get("pins_all_current") is True,
    "static controls 22/22 with T14a PASS": sc["all_pass"] is True and sc["controls"] == 22
    and sc["results"]["T14a_main_preflight_after_the_attempt"]["pass"] is True,
}
res = {"commit": SF1A, "tree": tree, "rehearsal_gates": gates, "qc15_checks": acks,
       "regression_runs": {k: r.get("rc") for k, r in g["runs"].items()}, "checks": checks, "ok": all(checks.values())}
out.write_text(json.dumps(res, indent=1) + "\n")
print(json.dumps(checks, indent=1), "\nok:", res["ok"])
