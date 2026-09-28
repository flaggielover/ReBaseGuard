"""Stream A0 task C2/C4: the DETERMINISTIC pointwise ladder (research declaration; see A0_CERTIFIER_STUDY.md s2).

  python3 -I -B -S a0_ladder.py run E SUFFIX       run every declared rung at declared drift E in THIS process,
                                                    persist every certificate, compose, write
                                                    results/LADDER_e<E>_<SUFFIX>.json and certs/*_<SUFFIX>.json
  python3 -I -B -S a0_ladder.py compare E S1 S2    C4: byte-identity of the exact outputs of two runs

Rules (declared; every choice is justified in the study from validation-drift evidence only):
  R1 rung set      fixed, no early stopping: C2b P1 meshes LADDER_C2B_N with exact-scale selection (a0_c2bx: upper
                   certified by the pinned c2b_exact.certify, lower by a0_c2b.sub_certify) and C1b W-only degrees
                   LADDER_C1B_D (pinned functions; pointwise at a dyadic drift, on the 2^-20 dyadic hull otherwise).
  R2 operation     all loops are bounded by declared counts (C2b Jacobi maxit 20000 / tol 1e-13, BUMP_MAX 64,
     bounds       A0 sub decrements <= 64, C1b enclosure extra_levels 4); there is no wall-clock or CPU-time rule.
  R3 composition   U = min over CERTIFIED upper rungs, L = max over CERTIFIED lower rungs (each rung is a proof).
  R4 consistency   L <= U (exact) is REQUIRED: two independent implementations must bracket the same number.
                   L > U  =>  status INCONSISTENT, no value (a soundness alarm, not a tightness event).
  R5 fail-closed   no certified upper rung => status NOT_CERTIFIED, no U; no certified lower rung => no L.
  R6 CPU cap       a per-process RLIMIT_CPU (declared, sum of the per-rung caps) is a SAFETY ABORT: if it fires the
                   process dies and NO ladder file is written (the run is void; it never falls back to fewer rungs,
                   so the reported value never depends on machine speed).
"""
from __future__ import annotations

import json
import resource
import sys
import time
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a0_common as A  # noqa: E402

LADDER_C2B_N = (20, 40, 80)          # C2b P1, exact-scale selection (a0_c2bx): upper = pinned certify, lower = A0 sub
LADDER_C1B_D = (8, 10, 12)           # C1b PW W-only (pinned functions): pointwise at dyadic e, 2^-20 hull otherwise
# (the C4 determinism runs LADDER_e{3,7_2}_det{A,B} were made with LADDER_C1B_D = (10, 12) and caps {10: 1800,
#  12: 3600}, sha256 of this file then recorded in their 'code.a0'; d = 8 determinism: results/C4_FILEPAIRS_C1B_d8.json)
RUNG_CPU_CAP = {"C2B": {20: 300, 40: 900, 80: 3600}, "C1B": {8: 900, 10: 1800, 12: 3600}}
CODE_AT_START = A.own_code_sha256()
EXACT_KEYS = ("U", "L", "status", "U_rungs", "L_rungs", "consistent")


def run(e, suffix: str) -> dict:
    import a0_c1b as C1
    import a0_c1bh as H
    import a0_c2bx as X
    e = A.declared_drift(F(e))
    cap = sum(RUNG_CPU_CAP["C2B"][n] for n in LADDER_C2B_N) + sum(RUNG_CPU_CAP["C1B"][d] for d in LADDER_C1B_D)
    soft, hard = resource.getrlimit(resource.RLIMIT_CPU)
    eff = cap if hard == resource.RLIM_INFINITY else min(cap, hard)      # never raise an outer (queue) hard cap
    resource.setrlimit(resource.RLIMIT_CPU, (eff, hard if hard != resource.RLIM_INFINITY else eff + 30))
    t0 = time.process_time()
    rungs, certs = [], {}
    for N in LADDER_C2B_N:
        x = X.c2bx_rung(e, N)
        rec = x["record"]
        rungs.append({"certifier": "C2B_P1_EXACT_SCALE", "rung": f"N={N}", "U": rec.get("U"), "L": rec.get("L"),
                      "status_U": rec["status_U"], "status_L": rec["status_L"], "cpu": rec["cpu_seconds"]["total"]})
        for k, c in x["certs"].items():
            certs[f"C2BX_{k.upper()}_e{A.tag(e)}_N{N}_{suffix}.json"] = c
    dyadic = (e.denominator & (e.denominator - 1)) == 0
    for d in LADDER_C1B_D:
        w = C1.c1b_w_rung(e, d) if dyadic else H.c1b_hull_rung(e, d)
        rec = w["record"]
        rungs.append({"certifier": "C1B_PW" if dyadic else "C1B_PW_HULL", "rung": f"d={d}", "U": rec.get("U"),
                      "L": rec.get("L"), "status_U": rec["status"], "status_L": rec["status"],
                      "cpu": rec.get("cpu_seconds")})
        if w["cert"]:
            certs[f"{'C1B' if dyadic else 'C1BH'}_SUPER_e{A.tag(e)}_d{d}_{suffix}.json"] = w["cert"]
    out = compose(rungs)
    out.update({"schema": "A0_LADDER/1", "drift": A.fs(e), "suffix": suffix, "rungs": rungs,
                "declared": {"C2B_N": LADDER_C2B_N, "C1B_d": LADDER_C1B_D, "rung_cpu_cap": RUNG_CPU_CAP,
                             "process_cpu_cap": cap, "effective_cpu_cap": eff, "c1b_mode": "pointwise" if dyadic else "dyadic 2^-20 hull"},
                "cpu_seconds_total": round(time.process_time() - t0, 1),
                "code": {"c2b": A.load_c2b()["_sha256"], "c1b": A.load_c1b()["_sha256"], "a0": CODE_AT_START},
                "latent_proxy": "validation-drift values; stream-internal only (T1/T2)"})
    out["cert_files"] = {n: A.write_json(A.CERTS / n, c) for n, c in sorted(certs.items())}
    out["exact_projection_sha256"] = A.sha256_bytes(A.canon({k: out.get(k) for k in EXACT_KEYS}))
    A.write_json(A.RESULTS / f"LADDER_e{A.tag(e)}_{suffix}.json", out)
    A.ledger("a0_ladder.py", f"stream C ladder run e={A.fs(e)} suffix={suffix}",
             notes="declared validation drift; determinism study (C4)")
    return out


def compose(rungs: list) -> dict:
    Us = [(F(r["U"]), r["rung"], r["certifier"]) for r in rungs if r.get("status_U") == "CERTIFIED" and r.get("U")]
    Ls = [(F(r["L"]), r["rung"], r["certifier"]) for r in rungs if r.get("status_L") == "CERTIFIED" and r.get("L")]
    if not Us:
        return {"status": "NOT_CERTIFIED", "U": None, "L": None, "U_rungs": [], "L_rungs": [], "consistent": None}
    u = min(x[0] for x in Us)
    lo = max(x[0] for x in Ls) if Ls else None
    consistent = (lo is None) or (lo <= u)
    return {"status": "CERTIFIED" if consistent else "INCONSISTENT", "U": A.fs(u) if consistent else None,
            "L": (A.fs(lo) if lo is not None else None) if consistent else None,
            "U_rungs": [f"{c}:{r}" for (v, r, c) in Us if v == u], "L_rungs": [f"{c}:{r}" for (v, r, c) in Ls if v == lo],
            "consistent": consistent}


def compare(e, s1: str, s2: str) -> dict:
    e = A.declared_drift(F(e))
    a = json.loads((A.RESULTS / f"LADDER_e{A.tag(e)}_{s1}.json").read_text())
    b = json.loads((A.RESULTS / f"LADDER_e{A.tag(e)}_{s2}.json").read_text())
    files = []
    for n1 in sorted(a["cert_files"]):
        n2 = n1[: -len(f"_{s1}.json")] + f"_{s2}.json"
        b1, b2 = (A.CERTS / n1).read_bytes(), (A.CERTS / n2).read_bytes() if (A.CERTS / n2).exists() else b""
        files.append({"a": n1, "b": n2, "byte_identical": b1 == b2, "sha256": A.sha256_bytes(b1)})
    exact_a = {k: a.get(k) for k in EXACT_KEYS}
    exact_b = {k: b.get(k) for k in EXACT_KEYS}
    rung_exact = lambda L: [{k: r.get(k) for k in ("certifier", "rung", "U", "L", "status_U", "status_L")} for r in L]  # noqa: E731
    out = {"schema": "A0_C4_DETERMINISM/1", "drift": A.fs(e), "runs": [s1, s2],
           "cert_files": files, "all_cert_files_byte_identical": bool(files) and all(f["byte_identical"] for f in files)
           and set(a["cert_files"]) == {n[: -len(f"_{s2}.json")] + f"_{s1}.json" for n in b["cert_files"]},
           "exact_projection_identical": exact_a == exact_b and a["exact_projection_sha256"] == b["exact_projection_sha256"],
           "rung_exact_fields_identical": rung_exact(a["rungs"]) == rung_exact(b["rungs"]),
           "cpu_seconds": [a["cpu_seconds_total"], b["cpu_seconds_total"]]}
    out["PASS"] = out["all_cert_files_byte_identical"] and out["exact_projection_identical"] and out["rung_exact_fields_identical"]
    A.write_json(A.RESULTS / f"C4_DETERMINISM_e{A.tag(e)}.json", out)
    return out


if __name__ == "__main__":
    if sys.argv[1] == "run":
        r = run(sys.argv[2], sys.argv[3])
        print(r["status"], r["exact_projection_sha256"], flush=True)
    elif sys.argv[1] == "compare":
        r = compare(sys.argv[2], sys.argv[3], sys.argv[4])
        print("PASS" if r["PASS"] else "FAIL", flush=True)
