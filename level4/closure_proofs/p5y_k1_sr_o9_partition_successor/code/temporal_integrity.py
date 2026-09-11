"""Phase 7 temporal-integrity check, verified against git (not against prose).

usage: temporal_integrity.py ANCHOR_COMMIT STAGE     (STAGE = pre_execution | post_execution)
I1  the anchor commit contains the protocol, generator, table and executable surface, and NO successor certified
    result (no path under evidence/certified/ in `git ls-tree` of the anchor)
I2  every file frozen in config/PROTOCOL_DIGEST.json is byte-identical between the anchor and the working tree
I3  no predecessor namespace changed since 986e617 (committed history and working tree)
I4  the generator, rerun now, reproduces the committed table byte for byte, with the protocol's declared hash
I5  the generator source references no result, verdict or diagnostic (static token scan) and imports only
    json/hashlib/fractions/pathlib/flint and the frozen T1 module
I6  the anchor is an ancestor of HEAD
I7  (post) every certified run manifest records a commit that descends from the anchor, with no dirty paths
I8  the historical cell-313 failure is unchanged history (curvature-successor kill record still m2/m3/m5 > 1)
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parent
W = CP.parents[1]
REL = str(NS.relative_to(W))
PRED = "986e617"


def git(*a):
    return subprocess.run(["git", "-C", str(W), *a], capture_output=True, text=True)


def main():
    anchor, stage = sys.argv[1], sys.argv[2]
    sys.path.insert(0, str(NS / "code"))
    res = {}
    tree = git("ls-tree", "-r", "--name-only", anchor, "--", REL).stdout.split()
    need = [f"{REL}/config/successor_cells.json", f"{REL}/config/PARTITION_PROTOCOL.json", f"{REL}/config/PROTOCOL_DIGEST.json",
            f"{REL}/PROTOCOL.md", f"{REL}/code/partition_generator.py", f"{REL}/code/run_region.sh", f"{REL}/code/succ_t3.py",
            f"{REL}/code/run_stages.py", f"{REL}/code/succ_t4.py", f"{REL}/code/succ_t5.py", f"{REL}/code/temporal_integrity.py"]
    res["I1_anchor_has_protocol_no_results"] = {"PASS": all(p in tree for p in need) and not any("/evidence/certified/" in p for p in tree),
                                                "missing": [p for p in need if p not in tree],
                                                "certified_paths_at_anchor": [p for p in tree if "/evidence/certified/" in p]}
    dig = json.loads((NS / "config/PROTOCOL_DIGEST.json").read_text())
    bad = []
    for rel, h in dig["files"].items():
        blob = subprocess.run(["git", "-C", str(W), "show", f"{anchor}:{REL}/{rel}"], capture_output=True).stdout
        if hashlib.sha256(blob).hexdigest() != h or hashlib.sha256((NS / rel).read_bytes()).hexdigest() != h:
            bad.append(rel)
    res["I2_frozen_files_identical"] = {"PASS": not bad, "changed": bad, "n_files": len(dig["files"])}
    committed = [p for p in git("diff", "--name-only", PRED, "HEAD", "--", "level4/closure_proofs").stdout.split() if not p.startswith(REL)]
    working = [p for p in git("diff", "--name-only", "HEAD", "--", "level4/closure_proofs").stdout.split() if not p.startswith(REL)]
    res["I3_predecessors_unchanged"] = {"PASS": not committed and not working, "committed": committed, "working": working}
    import partition_generator as G
    b = G.canonical(G.generate())
    proto = json.loads((NS / "config/PARTITION_PROTOCOL.json").read_text())
    res["I4_generator_reproduces_table"] = {"PASS": b == (NS / "config/successor_cells.json").read_bytes()
                                            and hashlib.sha256(b).hexdigest() == proto["partition"]["successor_cells_sha256"],
                                            "sha256": hashlib.sha256(b).hexdigest()}
    src = (NS / "code/partition_generator.py").read_text().split('"""', 2)[2]
    toks = re.findall(r"\b(evidence|PASS|FAIL|B_cover|ratio|diag\w*|curvature|kill|t[345]_\w*)\b", src)
    imps = set(re.findall(r"^\s*(?:from|import)\s+([A-Za-z_][\w.]*)", src, re.M))
    res["I5_generator_pre_result_only"] = {"PASS": not toks and imps <= {"hashlib", "json", "fractions", "pathlib", "sr_o9_candidates", "flint"},
                                           "forbidden_tokens": toks, "imports": sorted(imps)}
    res["I6_anchor_ancestor_of_HEAD"] = {"PASS": git("merge-base", "--is-ancestor", anchor, "HEAD").returncode == 0}
    mans = sorted((NS / "evidence/certified").glob("parent_*/RUN_MANIFEST.json")) if (NS / "evidence/certified").exists() else []
    mres = []
    for m in mans:
        d = json.loads(m.read_text())
        ok = git("merge-base", "--is-ancestor", anchor, d["git_commit"]).returncode == 0 and d["dirty_paths"] == 0
        mres.append({"manifest": str(m.relative_to(NS)), "commit": d["git_commit"], "descends_from_anchor_clean": ok})
    res["I7_results_descend_from_anchor"] = {"PASS": all(x["descends_from_anchor_clean"] for x in mres) if stage == "post_execution" else not mres,
                                             "manifests": mres}
    k = json.loads((CP / "p5y_k1_sr_o9_curvature_successor/evidence/kill/t4_c313.json").read_text())
    res["I8_old_313_failure_immutable"] = {"PASS": all(k["B_cover_ratio"][m] > 1 for m in ("2", "3", "5")), "ratios": k["B_cover_ratio"]}
    ok = all(v["PASS"] for v in res.values())
    out = {"schema": "rebaseguard.p5y.k1.sr.partition-successor.temporal-integrity.v1", "anchor": anchor, "stage": stage,
           "head": git("rev-parse", "HEAD").stdout.strip(), "checks": res,
           "verdict": "TEMPORAL_INTEGRITY_PASS" if ok else "PARTITION_SUCCESSOR_TEMPORAL_INTEGRITY_FAIL"}
    (NS / f"evidence/temporal_integrity_{stage}.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(out["verdict"], {k: v["PASS"] for k, v in res.items()})


if __name__ == "__main__":
    main()
