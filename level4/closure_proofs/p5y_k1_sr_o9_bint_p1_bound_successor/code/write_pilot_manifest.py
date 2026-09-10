"""Collect the 4-case kill test and the 36-case bounded pilot into config/BINT_P1_PILOT_MANIFEST.json."""
import glob
import hashlib
import json
from fractions import Fraction as Fr
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parent
NEST = {"eq": Fr(9, 500), "trunc": Fr(3, 500), "tail": Fr(3, 500), "end": Fr(1, 250), "int": Fr(1, 500), "round": Fr(1, 500)}
diag = {(x["cell"], tuple(x["patch"])): x for x in json.loads(
    (CP / "p5y_k1_sr_o9_bint_representation_successor/evidence/bint_audit.json").read_text())["alternative_diagnostic_NOT_ADOPTED"]}


def row(f):
    p = Path(f)
    r = json.loads(p.read_text())
    c = r["comparison_b48973d6"]
    C = Fr(r["scientific"]["C_upper"])
    case = r["scientific"]["case"]
    k = (case["cell"], tuple(case["patch"]))
    old = c["channels_old"]
    worst_old = {ch: max(o[ch] for o in old.values()) / float(NEST[ch] / C) for ch in NEST}
    worst_new = {ch: max(v["channels_float"][ch] for v in r["per_node"].values()) / float(NEST[ch] / C) for ch in NEST}
    out = {"case": case, "file": str(p.relative_to(NS)), "file_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
           "scientific_hash": r["scientific_hash"], **r["summary"],
           "invariants_vs_b48973d6": {x: c[x] for x in c if x.endswith("_equal")},
           "predecessor_file_sha256": c["predecessor_file_sha256"], "predecessor_failing": c["failing_old"],
           "worst_over_allowance_old": worst_old, "worst_over_allowance_new": worst_new,
           "lagrange_factor_stats": r["lagrange_factor_stats"],
           "certify_cpu_s": r["timing"]["certify_cpu_s"], "peak_rss_kib": r["peak_rss_kib"]}
    if k in diag:
        d = diag[k]["p1_bound_ball"]
        out["fa92afb_diagnostic"] = {"worst_int_over_allowance": d["worst_int_over_allowance"], "nodes_hash": d["hash"],
                                     "nodes_hash_equal": r["diag_comparable_nodes_hash"] == d["hash"]}
    return out


kill = [row(f) for f in sorted(glob.glob(str(NS / "evidence/kill/*.json")))]
pilot = [row(f) for f in sorted(glob.glob(str(NS / "evidence/pilot36/*.json")))]
cnt = lambda rows, k: sum(1 for x in rows if x[k])   # noqa: E731
man = {"schema": "rebaseguard.p5y.k1.sr.o9.bint_p1_pilot.v1",
       "authorization": "P1_DERIVATIVE_BOUND_REUSE_FOR_SOFTPLUS_LAGRANGE_FACTOR",
       "authorization_file_sha256": hashlib.sha256((NS / "config/P1_BOUND_REUSE_AUTHORIZATION.json").read_bytes()).hexdigest(),
       "code_sha256": {f: hashlib.sha256((NS / f).read_bytes()).hexdigest() for f in ("code/sr_o9_bint_p1.py",)},
       "kill_test": kill, "bounded_pilot": pilot,
       "counts": {"kill_all_pass": cnt(kill, "all_local_gates_PASS"), "kill_n": len(kill),
                  "pilot_n": len(pilot), "pilot_B_int_PASS": cnt(pilot, "B_int_PASS"),
                  "pilot_endpoint_PASS": cnt(pilot, "endpoint_PASS"), "pilot_all_local_gates_PASS": cnt(pilot, "all_local_gates_PASS"),
                  "pilot_predecessor_all_pass": sum(1 for x in pilot if not x["predecessor_failing"]),
                  "pilot_invariant_violations": sum(1 for x in pilot if not all(x["invariants_vs_b48973d6"].values())),
                  "lagrange_calls": sum(x["lagrange_factor_stats"]["calls"] for x in pilot),
                  "lagrange_calls_old_ball_contains_new": sum(x["lagrange_factor_stats"]["old_ball_contains_new"] for x in pilot)},
       "resources": {"pilot_cpu_s_sum": sum(x["certify_cpu_s"] for x in pilot), "pilot_cpu_s_max": max(x["certify_cpu_s"] for x in pilot),
                     "peak_rss_kib_max": max(x["peak_rss_kib"] for x in kill + pilot)},
       "T2_CLOSED": False}
p = NS / "config/BINT_P1_PILOT_MANIFEST.json"
p.write_text(json.dumps(man, indent=1, sort_keys=True) + "\n")
print(json.dumps({"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), **man["counts"], **man["resources"]}, indent=1))
