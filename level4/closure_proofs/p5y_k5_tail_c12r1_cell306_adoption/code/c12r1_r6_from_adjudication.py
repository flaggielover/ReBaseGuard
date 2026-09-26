"""C12-R1 -- generate K5 coverage map r6 mechanically from the accepted cell-306 adoption adjudication. Decides nothing.

Frozen with the campaign, before any result exists. The adopted cell set is PARSED OUT OF the adjudication document.
It refuses unless ALL of these hold (N7 hardening included):
  * the working tree is clean, and every input it reads is byte-identical to its committed bytes at HEAD;
  * the sealed result is committed at HEAD, its self-hash verifies, status TARGET_EVALUATED, exactly one target
    evaluation, the control reproduced C2 exactly, and Gamma < 0 under BOTH S_I1 and S_I2 (floor r2 F1'(d));
  * the exactly-once marker exists;
  * review/C12R1_EXECUTION_REVIEW.md line 2 is exactly EXECUTION_ACCEPTED;
  * adjudication/C12R1_ADOPTION_ADJUDICATION.md line 2 is exactly CELL306_ADOPTED and its 'ADOPTED CELL SET' block
    is exactly [306];
  * review/C12R1_ADJUDICATION_REVIEW.md line 2 is exactly ADJUDICATION_ACCEPTED;
  * r5 matches its pinned hash; no r6 exists anywhere; --out is a new file named K5_COVERAGE_MAP_R6*.json that is not r5.
r5 is read and never written. Only the pair (m = 5, cell 306) moves OPEN -> PASS; r6 records its lineage from r5.

    python3.14 -I -S -B c12r1_r6_from_adjudication.py --out .../evidence/coverage/K5_COVERAGE_MAP_R6.json
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
CP = REPO / "level4/closure_proofs"
NS_REL = "level4/closure_proofs/p5y_k5_tail_c12r1_cell306_adoption"
R5_REL = "level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json"
R5_SHA = "e2197051e493df898295a692c580ed676e771f7dfae5a1675d8d8e9b979f684c"
RESULT_REL = NS_REL + "/evidence/execution/C12R1_CELL306_RESULT.json"
EXEC_REVIEW_REL = NS_REL + "/review/C12R1_EXECUTION_REVIEW.md"
ADJ_REL = NS_REL + "/adjudication/C12R1_ADOPTION_ADJUDICATION.md"
ADJ_REVIEW_REL = NS_REL + "/review/C12R1_ADJUDICATION_REVIEW.md"
CONSUMED_REF = "refs/c12r1/cell306-target-consumed"
CELL = 306


def git(*args) -> subprocess.CompletedProcess:
    return subprocess.run(["/usr/bin/git", "-C", str(REPO), *args], capture_output=True, text=True,
                          env={"PATH": "/usr/bin:/bin", "LC_ALL": "C", "GIT_OPTIONAL_LOCKS": "0"})


def refuse(msg: str):
    raise SystemExit(f"REFUSED: {msg}")


def committed(rel: str) -> bytes:
    """The committed bytes at HEAD, which must equal the working-tree bytes (N7)."""
    p = subprocess.run(["/usr/bin/git", "-C", str(REPO), "show", f"HEAD:{rel}"], capture_output=True,
                       env={"PATH": "/usr/bin:/bin", "LC_ALL": "C"})
    if p.returncode:
        refuse(f"{rel} is not committed at HEAD")
    disk = REPO / rel
    if not disk.exists() or disk.read_bytes() != p.stdout:
        refuse(f"{rel}: working-tree bytes differ from the committed bytes")
    return p.stdout


def line2(rel: str, expected: str) -> str:
    text = committed(rel).decode()
    lines = text.splitlines()
    if len(lines) < 2 or lines[1].strip() != expected or sum(ln.strip() == expected for ln in lines) != 1:
        refuse(f"{rel}: line 2 is not exactly {expected}")
    return text


def ranges(xs):
    xs, out = sorted(xs), []
    for x in xs:
        if out and x == out[-1][1] + 1:
            out[-1][1] = x
        else:
            out.append([x, x])
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    out = Path(a.out).resolve()
    if not re.fullmatch(r"K5_COVERAGE_MAP_R6[^/]*\.json", out.name) or out == (REPO / R5_REL).resolve() or out.exists():
        refuse("--out must be a new file named K5_COVERAGE_MAP_R6*.json and never r5")
    if git("status", "--porcelain", "--untracked-files=all").stdout.strip():
        refuse("the working tree is not clean")
    if list(CP.rglob("K5_COVERAGE_MAP_R6*")) or git("log", "--all", "--format=%H", "--", "*K5_COVERAGE_MAP_R6*").stdout.strip():
        refuse("an r6 coverage map already exists")
    r5_raw = committed(R5_REL)
    if hashlib.sha256(r5_raw).hexdigest() != R5_SHA:
        refuse("r5 does not match its pinned hash")
    if not git("rev-parse", "-q", "--verify", CONSUMED_REF).stdout.strip():
        refuse("the exactly-once marker does not exist")
    res_raw = committed(RESULT_REL)
    res = json.loads(res_raw)
    body = {k: v for k, v in res.items() if k != "sha256"}
    if hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest() != res.get("sha256"):
        refuse("the sealed result's self-hash does not verify")
    if res.get("status") != "TARGET_EVALUATED" or res.get("target_evaluations") != 1:
        refuse("the sealed result is not one completed target evaluation")
    if not res["control"]["reproduces_C2_exactly"]:
        refuse("the control did not reproduce C2")
    if not (res["control"]["evaluated"]["pass"] and res["target"]["evaluated"]["pass"]):
        refuse("Gamma < 0 does not hold under both S_I1 and S_I2 (floor r2 F1'(d))")

    line2(EXEC_REVIEW_REL, "EXECUTION_ACCEPTED")
    text = line2(ADJ_REL, "CELL306_ADOPTED")
    blocks = re.findall(r"##\s*ADOPTED CELL SET\s*\n+\s*\[([0-9,\s]*)\]", text)
    if len(blocks) != 1:
        refuse("no unambiguous 'ADOPTED CELL SET' block")
    adopted = sorted(int(x) for x in blocks[0].replace(" ", "").split(",") if x)
    if adopted != [CELL]:
        refuse(f"the adopted set {adopted} is not exactly [306]")
    line2(ADJ_REVIEW_REL, "ADJUDICATION_ACCEPTED")

    sha = lambda rel: hashlib.sha256(committed(rel)).hexdigest()   # noqa: E731
    r5 = json.loads(r5_raw)
    r6 = json.loads(json.dumps(r5))                                         # r5 is read, never written
    r6["schema"] = "rebaseguard.p5y.k5.tail-c12r1.coverage-map.v6"
    r6["attribution_rule"] = (
        "successor of r5. The only change: (m = 5, cell 306) moves OPEN -> PASS, adopted by the accepted C12-R1 "
        "adjudication under K5 tail adoption floor r2 (limb F1': Gamma < 0 under each of two independent "
        "operator-constant implementations' own supplies). Every other entry is r5's, unchanged.")
    r6["inputs"] = {
        "predecessor": "r5", "coverage_map_r5_sha256": R5_SHA,
        "floor_r2_rule_commit": "a15d083b009868e38a5bd5a808f38f19e6ab4b92",
        "floor_r2_review_commit": "3fadb422eaba97123d46e98b9e80277a62a042c8",
        "n9_adjudication_commit": "7d67989d3da6595180ca3c01d34f2bdf4543ae73",
        "n9_adjudication_review_commit": "fb237288a7cf481c14cd2f85c18bb363d2ebe44a",
        "c12r1_result_sha256": sha(RESULT_REL),
        "c12r1_result_commit": git("log", "-1", "--format=%H", "--", RESULT_REL).stdout.strip(),
        "c12r1_execution_review_sha256": sha(EXEC_REVIEW_REL),
        "c12r1_adjudication_sha256": sha(ADJ_REL),
        "c12r1_adjudication_review_sha256": sha(ADJ_REVIEW_REL),
        "adopted_cells_m5": adopted,
    }
    for mm in r6["per_m"].values():
        mm["newly_passing"] = []
        mm["newly_passing_count"] = 0
    m5 = r6["per_m"]["5"]
    by = {c["cell"]: c for c in m5["cells"]}
    if by[CELL]["verdict"] == "PASS":
        refuse("cell 306 is already PASS at m = 5 in r5")
    by[CELL].update({"verdict": "PASS",
                     "route": "theorem TC-T, K5-B direct clause; floor r2 F1' (two-implementation agreement)",
                     "evidence": "C12-R1 sealed cell-306 result (EXECUTION_ACCEPTED; adjudicated CELL306_ADOPTED; "
                                 "ADJUDICATION_ACCEPTED)",
                     "artifact_sha256": sha(RESULT_REL)})
    m5["cells"] = [by[k] for k in sorted(by)]
    open5 = sorted(c["cell"] for c in m5["cells"] if c["verdict"] != "PASS")
    m5["open_ranges"] = ranges(open5)
    m5["open_count"] = len(open5)
    m5["pass_ranges"] = ranges([c["cell"] for c in m5["cells"] if c["verdict"] == "PASS"])
    m5["newly_passing"] = [CELL]
    m5["newly_passing_count"] = 1
    union = sorted({c["cell"] for mm in r6["per_m"].values() for c in mm["cells"] if c["verdict"] != "PASS"})
    r6["union_open_ranges"] = ranges(union)
    r6["union_open_count"] = len(union)
    r6["K5_COVERAGE_COMPLETE"] = not union

    data = json.dumps(r6, sort_keys=True, indent=1) + "\n"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(data)
    print(json.dumps({"adopted_cells_m5": adopted, "m5_open_ranges": m5["open_ranges"],
                      "union_open_ranges": r6["union_open_ranges"], "K5_COVERAGE_COMPLETE": r6["K5_COVERAGE_COMPLETE"],
                      "sha256": hashlib.sha256(data.encode()).hexdigest()}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
