"""K4R1 freeze builder (git-aware). Writes config/FREEZE.json + config/FREEZE_HASH. Computes no target value.

Run from anywhere (paths resolve from this file), on the qualified candidate commit, after copying EXACTLY the two
files QUALIFICATION_REVIEW.json and QUALIFICATION_REVIEW.md of the accepted review into a NEW namespace directory
review/qualification_rN/:

  python3 -B level4/closure_proofs/p5y_k4r1_nearzero_successor/code/make_freeze.py --review-dir review/qualification_rN

Refuses unless:
  - no freeze exists yet;
  - `git status --porcelain --untracked-files=all --ignored` of the whole checkout shows exactly the two review files
    as untracked, nothing modified/staged/untracked elsewhere, and no ignored entry inside the namespace;
  - the review directory is new (nothing under it is tracked at HEAD);
  - the review JSON verdict is QUALIFICATION_ACCEPTED and its candidate_commit equals HEAD;
  - every PROVENANCE source matches its sha256.
Binds by sha256: every namespace file tracked at HEAD, the two review files, and every PROVENANCE source. Records the
qualified candidate commit and the exact set of paths the freeze commit may add (the review files, FREEZE.json,
FREEZE_HASH); ready/execute verify that set against `git diff --name-only <candidate> HEAD`.
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
REVIEW_FILES = ("QUALIFICATION_REVIEW.json", "QUALIFICATION_REVIEW.md")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def git(*args) -> str:
    r = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"REFUSED: git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--review-dir", required=True, help="namespace-relative new directory, e.g. review/qualification_r4")
    a = ap.parse_args(argv)
    ns_rel = NS.resolve().relative_to(REPO.resolve())
    fz_path, fh_path = NS / "config/FREEZE.json", NS / "config/FREEZE_HASH"
    if fz_path.exists() or fh_path.exists():
        raise SystemExit("REFUSED: a freeze already exists")
    rdir = Path(a.review_dir)
    if rdir.is_absolute() or ".." in rdir.parts or not rdir.parts or rdir.parts[0] != "review":
        raise SystemExit("REFUSED: --review-dir must be a namespace-relative directory under review/")
    review_rel = [str(ns_rel / rdir / f) for f in REVIEW_FILES]
    if git("ls-files", "--", str(ns_rel / rdir)).strip():
        raise SystemExit("REFUSED: the review directory already holds tracked files")
    entries = [line for line in git("status", "--porcelain", "--untracked-files=all", "--ignored").splitlines() if line]
    expected = sorted(f"?? {p}" for p in review_rel)
    ns_prefix = str(ns_rel) + "/"
    other = [e for e in entries if not e.startswith("!! ")]
    ignored_in_ns = [e for e in entries if e.startswith("!! ") and e[3:].startswith(ns_prefix)]
    if sorted(other) != expected or ignored_in_ns:
        raise SystemExit(f"REFUSED: checkout is not the candidate plus exactly the two review files "
                         f"(unexpected: {sorted(set(other) - set(expected))}, missing: {sorted(set(expected) - set(other))}, "
                         f"ignored in namespace: {ignored_in_ns})")
    rv = json.loads((REPO / review_rel[0]).read_text())
    head = git("rev-parse", "HEAD").strip()
    if rv.get("verdict") != "QUALIFICATION_ACCEPTED":
        raise SystemExit(f"REFUSED: review verdict is {rv.get('verdict')!r}")
    if rv.get("candidate_commit") != head:
        raise SystemExit(f"REFUSED: review candidate_commit {rv.get('candidate_commit')!r} != HEAD {head}")
    bound = {p: sha(REPO / p) for p in git("ls-files", "--", str(ns_rel)).splitlines()}
    bound.update({p: sha(REPO / p) for p in review_rel})
    prov = json.loads((NS / "config/PROVENANCE.json").read_text())
    for v in prov["sources"].values():
        h = sha(REPO / v["path"])
        if h != v["sha256"]:
            raise SystemExit(f"REFUSED: source drift {v['path']}")
        bound[v["path"]] = h
    delta = sorted(review_rel + [str(ns_rel / "config/FREEZE.json"), str(ns_rel / "config/FREEZE_HASH")])
    fz = {"schema": "rebaseguard.p5y.k4r1.freeze.v2", "campaign": "P5Y-K4R1",
          "qualified_candidate_commit": head, "qualification_verdict": rv["verdict"],
          "qualification_review": review_rel[0], "review_files": review_rel, "allowed_freeze_delta": delta,
          "frozen_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
          "target_values_present": False, "bound_files": bound}
    fz_path.write_text(json.dumps(fz, indent=1, sort_keys=True) + "\n")
    fh_path.write_text(sha(fz_path) + "\n")
    print(json.dumps({"FREEZE": "WRITTEN", "bound_files": len(bound), "freeze_sha256": sha(fz_path),
                      "commit_exactly": delta}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
