"""Generate K5 coverage map r5 mechanically from the adjudication verdict. Decides nothing.

The adopted cell set is PARSED OUT OF the adjudication document, not supplied on the command line, so this
generator cannot be handed a set the adjudicator did not write. It refuses if the verdict is not an adopting one,
if the ADOPTED CELL SET block is missing or ambiguous, if r4 does not match its pinned hash, if an adopted cell was
not sealed as passing, or if an r5 already exists.

r4 is read and never written. Only the (m = 5, cell) pairs named in the adopted set move OPEN -> CLOSED.

    python3 -B c2_coverage_map_r5.py --out OUT.json
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = Path(__file__).resolve().parents[2]
R4 = CP / "p5y_k5_lower_front_order3/evidence/tc_r1/K5_COVERAGE_MAP_R4.json"
R4_SHA = "a3bddd83234f33983e07b005b4686a5f3971264bb6bdd64d2c639339de210a35"
ADJ = NS / "evidence/adjudication/C2_ADJUDICATION.md"
SEAL = NS / "evidence/seal/C2_SEAL.json"
ADOPTING = {"ADOPTED", "PARTIALLY_ADOPTED"}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def parse_adjudication(text: str):
    v = re.findall(r"\*\*VERDICT:\s*([A-Z_]+)\*\*", text)
    if len(v) != 1:
        raise SystemExit(f"REFUSED: expected exactly one VERDICT line, found {len(v)}")
    m = re.search(r"##\s*ADOPTED CELL SET\s*\n+\s*\[([0-9,\s]*)\]", text)
    if not m:
        raise SystemExit("REFUSED: no unambiguous 'ADOPTED CELL SET' block")
    cells = sorted(int(x) for x in m.group(1).replace(" ", "").split(",") if x)
    return v[0], cells


def ranges(xs):
    xs, out = sorted(xs), []
    for x in xs:
        if out and x == out[-1][1] + 1:
            out[-1][1] = x
        else:
            out.append([x, x])
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    if list(CP.rglob("*COVERAGE_MAP_R5*")):
        raise SystemExit("REFUSED: an r5 coverage map already exists")
    if sha(R4) != R4_SHA:
        raise SystemExit("REFUSED: r4 does not match its pinned hash")

    verdict, adopted = parse_adjudication(ADJ.read_text())
    if verdict not in ADOPTING:
        raise SystemExit(f"REFUSED: verdict {verdict} does not adopt; r4 remains authoritative")
    if not adopted:
        raise SystemExit("REFUSED: adopting verdict with an empty adopted set")

    seal = json.loads(SEAL.read_bytes())
    sealed_pass = {int(k) for k, v in seal["sealed_result"]["per_cell"].items() if v["pass"]}
    not_sealed = [c for c in adopted if c not in sealed_pass]
    if not_sealed:
        raise SystemExit(f"REFUSED: adopted cells not sealed as passing: {not_sealed}")

    r4 = json.loads(R4.read_bytes())
    r5 = json.loads(json.dumps(r4))            # r4 is read, never written
    r5["schema"] = "rebaseguard.p5y.k5.tail-c2.coverage-map.v5"
    r5["attribution_rule"] = (
        "cells passing now but OPEN in r4 are attributed to Campaign C2's deterministic D-stage successor "
        "(theorem TC-T with the pre-registered componentwise-minimum atom-constant supply over Lemma G, the C1 "
        "registry and the C2 refined registry). Only the (m, cell) pairs in the adjudicated adopted set move.")
    r5["inputs"] = {
        "coverage_map_r4_sha256": R4_SHA,
        "c2_freeze_commit": json.loads((NS / "evidence/freeze/C2_FREEZE_RECORD.json").read_bytes())["freeze_commit"],
        "c2_protocol_sha256_bound": json.loads(
            (NS / "evidence/freeze/C2_FREEZE_RECORD.json").read_bytes())["protocol_sha256_bound"],
        "c2_seal_sha256": sha(SEAL),
        "c2_consumption_sha256": sha(NS / "evidence/consumption/C2_CONSUMPTION.json"),
        "c2_adjudication_sha256": sha(ADJ),
        "c2_adjudication_verdict": verdict,
        "adopted_cells": adopted,
    }

    # newly_passing in r5 means "newly passing relative to r4". r4's own values are inherited by the deep copy
    # and would otherwise be read as r5's, so every m is reset and only the adopted pairs are recorded.
    for mm in r5["per_m"].values():
        mm["newly_passing"] = []
        mm["newly_passing_count"] = 0

    m5 = r5["per_m"]["5"]
    by = {c["cell"]: c for c in m5["cells"]}
    moved = []
    for c in adopted:
        if by[c]["verdict"] == "PASS":
            raise SystemExit(f"REFUSED: cell {c} already PASS at m=5 in r4")
        by[c].update({"verdict": "PASS",
                      "route": "theorem TC-T, K5-B direct clause, C2 D-stage deterministic successor",
                      "evidence": "C2 sealed packet (ADJUDICATED, PARTIALLY_ADOPTED)",
                      "artifact_sha256": sha(SEAL)})
        moved.append(c)
    m5["cells"] = [by[k] for k in sorted(by)]
    open5 = sorted(c["cell"] for c in m5["cells"] if c["verdict"] != "PASS")
    m5["open_ranges"] = ranges(open5)
    m5["open_count"] = len(open5)
    m5["pass_ranges"] = ranges([c["cell"] for c in m5["cells"] if c["verdict"] == "PASS"])
    m5["newly_passing"] = moved
    m5["newly_passing_count"] = len(moved)

    union = sorted({c["cell"] for mm in r5["per_m"].values() for c in mm["cells"] if c["verdict"] != "PASS"})
    r5["union_open_ranges"] = ranges(union)
    r5["union_open_count"] = len(union)
    r5["K5_COVERAGE_COMPLETE"] = not union

    data = json.dumps(r5, sort_keys=True, indent=1) + "\n"
    Path(a.out).write_text(data)
    print(json.dumps({"verdict": verdict, "adopted_cells": adopted, "moved_to_PASS_at_m5": moved,
                      "m5_open_ranges": m5["open_ranges"], "union_open_ranges": r5["union_open_ranges"],
                      "K5_COVERAGE_COMPLETE": r5["K5_COVERAGE_COMPLETE"],
                      "sha256": hashlib.sha256(data.encode()).hexdigest()}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
