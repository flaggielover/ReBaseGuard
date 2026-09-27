"""K4R1 freeze builder. Writes config/FREEZE.json + config/FREEZE_HASH. Computes no target value.

Refuses unless: FREEZE.json does not exist yet; the named qualification review lies inside the namespace and its JSON
`verdict` is exactly QUALIFICATION_ACCEPTED; and its `candidate_commit` equals the current HEAD (the freeze binds
exactly the candidate that was qualified, plus the review itself). Binds by sha256 every file under the namespace
(except FREEZE.json / FREEZE_HASH, execution outputs and caches) and every PROVENANCE source.

  python3 -B level4/closure_proofs/p5y_k4r1_nearzero_successor/code/make_freeze.py \
      --review level4/closure_proofs/p5y_k4r1_nearzero_successor/review/qualification_r3/QUALIFICATION_REVIEW.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[2]
EXCLUDE_PARTS = {"__pycache__", ".pytest_cache", "execution_r1"}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", required=True, help="repo-relative path of the accepted qualification review JSON")
    a = ap.parse_args(argv)
    fz_path, fh_path = NS / "config/FREEZE.json", NS / "config/FREEZE_HASH"
    if fz_path.exists() or fh_path.exists():
        raise SystemExit("REFUSED: a freeze already exists")
    review = (REPO / a.review).resolve()
    try:
        review.relative_to(NS.resolve())
    except ValueError:
        raise SystemExit("REFUSED: the qualification review must lie inside the namespace") from None
    rv = json.loads(review.read_text())
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    if rv.get("verdict") != "QUALIFICATION_ACCEPTED":
        raise SystemExit(f"REFUSED: review verdict is {rv.get('verdict')!r}")
    if rv.get("candidate_commit") != head:
        raise SystemExit(f"REFUSED: review candidate_commit {rv.get('candidate_commit')!r} != HEAD {head}")
    bound = {}
    for p in sorted(NS.rglob("*")):
        if p.is_file() and not (EXCLUDE_PARTS & set(p.relative_to(NS).parts)) and p not in (fz_path, fh_path):
            bound[str(p.relative_to(REPO))] = sha(p)
    prov = json.loads((NS / "config/PROVENANCE.json").read_text())
    for v in prov["sources"].values():
        bound[v["path"]] = sha(REPO / v["path"])
        if bound[v["path"]] != v["sha256"]:
            raise SystemExit(f"REFUSED: source drift {v['path']}")
    fz = {"schema": "rebaseguard.p5y.k4r1.freeze.v1", "campaign": "P5Y-K4R1",
          "qualified_candidate_commit": head, "qualification_verdict": rv["verdict"],
          "qualification_review": str(review.relative_to(REPO)), "frozen_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
          "target_values_present": False, "bound_files": bound}
    fz_path.write_text(json.dumps(fz, indent=1, sort_keys=True) + "\n")
    fh_path.write_text(sha(fz_path) + "\n")
    print(json.dumps({"FREEZE": "WRITTEN", "bound_files": len(bound), "freeze_sha256": sha(fz_path)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
