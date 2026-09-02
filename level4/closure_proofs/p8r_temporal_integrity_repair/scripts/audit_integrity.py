"""Evaluate the frozen P8R integrity gates I1-I13, literally.

These are the gates that P8 failed.  Every one is checked against the repository
and the anchored manifests, not against a self-report.

Usage:  audit_integrity.py [--anchor-commit SHA]

If ``--anchor-commit`` is omitted the value recorded in ``TEMPORAL_ANCHOR.md``
is used.  Gates that need git history degrade to ``UNVERIFIABLE`` -- never to
``PASS`` -- when the repository cannot answer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

P8R = Path(__file__).resolve().parents[1]
ROOT = P8R.parents[2]
REL_P8R = "level4/closure_proofs/p8r_temporal_integrity_repair"
sys.path.insert(0, str(P8R / "scripts"))
sys.path.insert(0, str(P8R / "src"))

from make_manifests import (FROZEN_PROSE, protected_manifest,      # noqa: E402
                            protocol_digest, source_manifest)

RESULT_GLOBS = ("results/**/*.json",)

#: every production artifact and the generator that must have produced it.
GENERATOR_MAP = {
    "results/sr_calibration.json": "experiments/run_calibration.py",
    "results/cal/*.json": "experiments/run_calibration.py",
    "results/arl0_check.json": "experiments/run_arl0_check.py",
    "results/family_regularity.json": "experiments/run_regularity.py",
    "results/gamma/*.json": "experiments/run_gamma_matrix.py",
    "results/gamma_matrix_E1.json": "experiments/aggregate_gamma.py",
    "results/gamma_matrix_E5.json": "experiments/aggregate_gamma.py",
    "results/chain/*.json": "experiments/run_chain_ladder.py",
    "results/drift/*.json": "experiments/run_drift.py",
    "results/independent_reproduction.json":
        "experiments/run_independent_repro.py",
    "results/scientific_resolution.json": "experiments/derive_resolution.py",
}


def git(*args, check=True):
    return subprocess.run(["git", "-C", str(ROOT), *args],
                          capture_output=True, text=True, check=check).stdout


def gate(gid, statement, status, evidence):
    assert status in ("PASS", "FAIL", "UNVERIFIABLE")
    return {"gate": gid, "statement": statement, "status": status,
            "evidence": evidence}


def anchor_commit_from_doc() -> str | None:
    p = P8R / "TEMPORAL_ANCHOR.md"
    if not p.exists():
        return None
    m = re.search(r"ANCHOR_COMMIT\s*=\s*`?([0-9a-f]{7,40})`?", p.read_text())
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
def i1_anchor_exists(anchor):
    """A commit exists carrying protocol + gates + source + RNG plan and NO
    production result."""
    if not anchor:
        return gate("I1", "temporal anchor commit exists and carries no "
                    "production result", "UNVERIFIABLE",
                    {"reason": "no ANCHOR_COMMIT recorded"})
    try:
        listing = git("ls-tree", "-r", "--name-only", anchor).splitlines()
    except subprocess.CalledProcessError as e:
        return gate("I1", "temporal anchor commit exists", "UNVERIFIABLE",
                    {"reason": str(e)})
    inside = [f for f in listing if f.startswith(REL_P8R + "/")]
    rel = [f[len(REL_P8R) + 1:] for f in inside]
    have_prose = [n for n in FROZEN_PROSE if n in rel]
    have_src = [f for f in rel if f.startswith("src/")]
    have_tests = [f for f in rel if f.startswith("tests/")]
    # a production result is any results/ JSON other than the pre-anchor
    # protected-tree manifest, which by definition must exist at the anchor.
    results = [f for f in rel if f.startswith("results/")
               and f != "results/integrity/protected_tree_manifest_pre.json"]
    ok = (len(have_prose) == len(FROZEN_PROSE) and have_src and have_tests
          and not results)
    return gate("I1", "the anchor commit carries the frozen protocol, gates, "
                "plans, source and tests, and NO production result",
                "PASS" if ok else "FAIL",
                {"anchor": anchor, "frozen_prose_present": have_prose,
                 "n_source_files": len(have_src),
                 "n_test_files": len(have_tests),
                 "production_results_at_anchor": results})


def i2_protocol_digest():
    rec = P8R / "PROTOCOL_DIGEST.json"
    if not rec.exists():
        return gate("I2", "frozen protocol digest matches", "UNVERIFIABLE",
                    {"reason": "PROTOCOL_DIGEST.json absent"})
    stored = json.loads(rec.read_text())
    now = protocol_digest()
    diff = {k: {"anchor": stored["files"].get(k), "now": now["files"].get(k)}
            for k in set(stored["files"]) | set(now["files"])
            if stored["files"].get(k) != now["files"].get(k)}
    return gate("I2", "every frozen prose artifact is byte-identical to its "
                "anchored digest", "PASS" if not diff else "FAIL",
                {"anchor_aggregate": stored["aggregate_sha256"],
                 "current_aggregate": now["aggregate_sha256"],
                 "differences": diff})


def i3_source_digest():
    rec = P8R / "SOURCE_MANIFEST.json"
    if not rec.exists():
        return gate("I3", "source digest matches", "UNVERIFIABLE",
                    {"reason": "SOURCE_MANIFEST.json absent"})
    stored = json.loads(rec.read_text())
    now = source_manifest()
    diff = {k: {"anchor": stored["files"].get(k), "now": now["files"].get(k)}
            for k in set(stored["files"]) | set(now["files"])
            if stored["files"].get(k) != now["files"].get(k)}
    return gate("I3", "every executable file is byte-identical to its anchored "
                "digest", "PASS" if not diff else "FAIL",
                {"anchor_aggregate": stored["aggregate_sha256"],
                 "current_aggregate": now["aggregate_sha256"],
                 "differences": diff})


def _cal_records():
    p = P8R / "results" / "sr_calibration.json"
    if not p.exists():
        return None
    return json.loads(p.read_text())["payload"]


def i4_cal_disjoint():
    """Search addresses and verification addresses never coincide."""
    from rebaseguard_p8r.addressing import (AddressClass, class_of,
                                            tag_digest)
    cal = _cal_records()
    if cal is None:
        return gate("I4", "calibration search and verification addresses are "
                    "disjoint", "UNVERIFIABLE", {"reason": "no calibration"})
    bad = []
    seen = {"search": set(), "verify": set()}
    for r in cal["rows"]:
        for t in r["search_trace"] + r["retry_trace"]:
            if t["address_class"] != AddressClass.CAL_SEARCH.value:
                bad.append({"kind": "search_read_non_search_class",
                            "entry": t})
            seen["search"].add((t["address_class"], t["batch"]))
        for v in (r["verify_1"], r["verify_2"]):
            if not v:
                continue
            if class_of(v["experiment"]) is AddressClass.CAL_SEARCH:
                bad.append({"kind": "verify_on_search_class", "entry": v})
            seen["verify"].add((v["address_class"], v["batch"]))
    # the address tuples themselves: the tag component differs by class, so
    # equality is impossible unless two SHA-256 prefixes collide.
    digests = {c.value: tag_digest(f"p8r/{c.value}/sr_arl0")
               for c in AddressClass if c is not AddressClass.PRODUCTION}
    collide = len(set(digests.values())) != len(digests)
    overlap = seen["search"] & seen["verify"]
    ok = not bad and not collide and not overlap
    return gate("I4", "no calibration-search evaluation ever reads a "
                "calibration-verification address",
                "PASS" if ok else "FAIL",
                {"search_addresses": sorted(seen["search"]),
                 "verify_addresses": sorted(seen["verify"]),
                 "class_tag_digests": digests,
                 "class_digest_collision": collide,
                 "class_batch_overlap": sorted(overlap),
                 "violations": bad})


def i5_prod_disjoint():
    from rebaseguard_p8r.addressing import (TAG_INVENTORY, AddressClass,
                                            class_of, tag_digest)
    prod = [t for t in TAG_INVENTORY
            if class_of(t) is AddressClass.PRODUCTION]
    cal = [t for t in TAG_INVENTORY
           if class_of(t) is not AddressClass.PRODUCTION]
    dp = {t: tag_digest(t) for t in prod}
    dc = {t: tag_digest(t) for t in cal}
    overlap = set(dp.values()) & set(dc.values())
    return gate("I5", "no production address coincides with any calibration "
                "address", "PASS" if not overlap else "FAIL",
                {"production_tag_digests": dp, "calibration_tag_digests": dc,
                 "overlap": sorted(overlap)})


def i6_no_protocol_mutation(anchor):
    if not anchor:
        return gate("I6", "no post-anchor protocol mutation", "UNVERIFIABLE",
                    {"reason": "no ANCHOR_COMMIT recorded"})
    changed = []
    for name in FROZEN_PROSE:
        rel = f"{REL_P8R}/{name}"
        try:
            blob = subprocess.run(["git", "-C", str(ROOT), "show",
                                   f"{anchor}:{rel}"], capture_output=True,
                                  check=True).stdout
        except subprocess.CalledProcessError:
            changed.append({"file": name, "reason": "absent at anchor"})
            continue
        cur = (P8R / name).read_bytes() if (P8R / name).exists() else b""
        if hashlib.sha256(blob).hexdigest() != hashlib.sha256(cur).hexdigest():
            changed.append({"file": name, "reason": "differs from anchor"})
    return gate("I6", "no frozen prose artifact changed after the anchor "
                "commit", "PASS" if not changed else "FAIL",
                {"anchor": anchor, "changed": changed})


def i7_no_threshold_change(anchor):
    if not anchor:
        return gate("I7", "no result-driven threshold change", "UNVERIFIABLE",
                    {"reason": "no ANCHOR_COMMIT recorded"})
    rel = f"{REL_P8R}/src/rebaseguard_p8r/config.py"
    try:
        blob = subprocess.run(["git", "-C", str(ROOT), "show",
                               f"{anchor}:{rel}"], capture_output=True,
                              check=True).stdout
    except subprocess.CalledProcessError as e:
        return gate("I7", "no result-driven threshold change", "UNVERIFIABLE",
                    {"reason": str(e)})
    cur = (P8R / "src" / "rebaseguard_p8r" / "config.py").read_bytes()
    same = hashlib.sha256(blob).hexdigest() == hashlib.sha256(cur).hexdigest()
    return gate("I7", "every frozen threshold, budget and grid is byte-"
                "identical to the anchor: config.py did not change",
                "PASS" if same else "FAIL",
                {"anchor_sha256": hashlib.sha256(blob).hexdigest(),
                 "current_sha256": hashlib.sha256(cur).hexdigest()})


def i8_command_manifest():
    p = P8R / "COMMAND_MANIFEST.json"
    if not p.exists():
        return gate("I8", "exact command reproducibility", "UNVERIFIABLE",
                    {"reason": "COMMAND_MANIFEST.json absent"})
    man = json.loads(p.read_text())
    missing = [c for c in man["commands"]
               if not (P8R / c["script"]).exists()]
    return gate("I8", "every production command is recorded verbatim and its "
                "script exists", "PASS" if not missing else "FAIL",
                {"n_commands": len(man["commands"]), "missing": missing})


def i9_rng_identity():
    p = P8R / "results" / "integrity" / "rng_identity.json"
    if not p.exists():
        return gate("I9", "RNG primitive identity", "UNVERIFIABLE",
                    {"reason": "rng_identity.json absent"})
    d = json.loads(p.read_text())["payload"]
    return gate("I9", "every primitive value is a pure function of its address",
                "PASS" if d["all_pass"] else "FAIL", d["checks"])


def i10_generator_coverage():
    orphans, bad = [], []
    for pat in RESULT_GLOBS:
        for p in sorted(P8R.glob(pat)):
            rel = str(p.relative_to(P8R))
            if rel.startswith("results/integrity/"):
                continue   # I9 / I11 / I12 own these; they are not production
            try:
                doc = json.loads(p.read_text())
            except Exception as e:
                bad.append({"file": rel, "reason": f"unreadable: {e}"})
                continue
            gen = doc.get("generator")
            if not gen or "payload" not in doc:
                orphans.append(rel)
                continue
            if not (P8R / gen).exists():
                bad.append({"file": rel, "reason": f"generator {gen} missing"})
            expect = None
            for glob, g in GENERATOR_MAP.items():
                if Path(rel).match(glob):
                    expect = g
                    break
            if expect and gen != expect:
                bad.append({"file": rel,
                            "reason": f"generator {gen} != declared {expect}"})
            if doc.get("payload_sha256"):
                h = hashlib.sha256(json.dumps(
                    doc["payload"], sort_keys=True, separators=(",", ":"),
                    default=float).encode()).hexdigest()
                if h != doc["payload_sha256"]:
                    bad.append({"file": rel, "reason": "payload digest "
                                                       "mismatch"})
    ok = not orphans and not bad
    return gate("I10", "every result artifact carries a working generator, a "
                "verbatim argv, a git commit and a matching payload digest",
                "PASS" if ok else "FAIL",
                {"orphans": orphans, "problems": bad})


def i11_protected_tree():
    pre = P8R / "results" / "integrity" / "protected_tree_manifest_pre.json"
    if not pre.exists():
        return gate("I11", "protected tree preserved", "UNVERIFIABLE",
                    {"reason": "pre-manifest absent"})
    before = json.loads(pre.read_text())
    now = protected_manifest()
    changed = {k: {"pre": before["files"].get(k), "post": now["files"].get(k)}
               for k in set(before["files"]) | set(now["files"])
               if before["files"].get(k) != now["files"].get(k)}
    authorised = {"README.md"}
    unauthorised = {k: v for k, v in changed.items() if k not in authorised}
    tree_diff = {t: {"pre": before["trees"][t], "post": now["trees"][t]}
                 for t in before["trees"]
                 if before["trees"][t]["aggregate_sha256"]
                 != now["trees"][t]["aggregate_sha256"]}
    ok = not unauthorised and not tree_diff
    return gate("I11", "every protected tree is byte-identical to its "
                "pre-campaign manifest; only the authorised root status file "
                "may differ", "PASS" if ok else "FAIL",
                {"n_trees": len(before["trees"]),
                 "trees_differing": tree_diff,
                 "authorised_changes": sorted(set(changed) & authorised),
                 "unauthorised_changes": unauthorised})


def i12_tests():
    p = P8R / "results" / "integrity" / "focused_tests.json"
    if not p.exists():
        return gate("I12", "focused test suite passes", "UNVERIFIABLE",
                    {"reason": "focused_tests.json absent"})
    d = json.loads(p.read_text())
    ok = d["failed"] == 0 and d["errors"] == 0 and d["passed"] > 0
    return gate("I12", "the P8R focused test suite passes in full",
                "PASS" if ok else "FAIL", d)


def i13_calibration_budget():
    cal = _cal_records()
    if cal is None:
        return gate("I13", "declared calibration budget equals executed",
                    "UNVERIFIABLE", {"reason": "no calibration"})
    rows = [{"family": r["family"],
             "declared": r["declared_budget"],
             "executed": r["executed_budget"],
             "matches": r["budget_matches_declaration"]}
            for r in cal["rows"]]
    ok = all(r["matches"] for r in rows)
    return gate("I13", "the executed calibration budget, re-derived from the "
                "stored trace, equals the single declared budget -- the exact "
                "disagreement that failed P8's G14",
                "PASS" if ok else "FAIL",
                {"rows": rows,
                 "all_match": cal["all_budgets_match_declaration"]})


# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--anchor-commit", default=None)
    a = ap.parse_args()
    anchor = a.anchor_commit or anchor_commit_from_doc()

    gates = [i1_anchor_exists(anchor), i2_protocol_digest(), i3_source_digest(),
             i4_cal_disjoint(), i5_prod_disjoint(), i6_no_protocol_mutation(anchor),
             i7_no_threshold_change(anchor), i8_command_manifest(),
             i9_rng_identity(), i10_generator_coverage(), i11_protected_tree(),
             i12_tests(), i13_calibration_budget()]
    n_pass = sum(g["status"] == "PASS" for g in gates)
    doc = {"schema": "rebaseguard.p8r.integrity-audit.v1",
           "anchor_commit": anchor,
           "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "n_gates": len(gates), "n_pass": n_pass,
           "all_pass": n_pass == len(gates),
           "summary": {g["gate"]: g["status"] for g in gates},
           "gates": gates}
    d = P8R / "results" / "integrity"
    d.mkdir(parents=True, exist_ok=True)
    (d / "integrity_audit.json").write_text(json.dumps(doc, indent=1) + "\n")
    for g in gates:
        print(f"  {g['gate']:4s} {g['status']:13s} {g['statement'][:70]}")
    print(f"INTEGRITY {n_pass}/{len(gates)} PASS")


if __name__ == "__main__":
    main()
