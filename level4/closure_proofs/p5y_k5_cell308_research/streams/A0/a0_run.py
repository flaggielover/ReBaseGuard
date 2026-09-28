"""Stream A0 job entry point: one (certifier, declared drift, rung) per process; writes results/ and certs/ files.

  python3 -I -B -S a0_run.py c2b   E N        C2b supersolution (pinned pipeline) + A0 P1 subsolution at mesh N
  python3 -I -B -S a0_run.py c1b   E d        C1b W-only rung (pinned functions), degree d
  python3 -I -B -S a0_run.py c1bx  E d        cross-check: pinned certify_degree vs the W-only rung (exact equality)
  python3 -I -B -S a0_run.py mc    E n seed   NON-CERTIFIED Monte Carlo
  [--out-suffix S]                            (determinism reruns write *_S.json)

Every job validates E as a declared validation drift (a0_common.declared_drift: declared set + both guards) BEFORE
loading any certifier, and writes one ledger line (class NONTARGET_DRIFT_VALIDATION, agent streamC).
"""
from __future__ import annotations

import sys
import time
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # -I drops the script directory from sys.path
import a0_common as A  # noqa: E402


def _suffix(argv):
    if "--out-suffix" in argv:
        i = argv.index("--out-suffix")
        s = argv[i + 1]
        del argv[i:i + 2]
        return "_" + s
    return ""


def main(argv):
    suf = _suffix(argv)
    job, e = argv[1], A.declared_drift(F(argv[2]))
    t0 = time.time()
    if job == "c2b":
        import a0_c2b as C2
        N = int(argv[3])
        sup = C2.c2b_super(e, N)
        out = {"schema": "A0_RESULT/1", "job": "c2b", "drift": A.fs(e), "N": N, "super": sup["record"]}
        if sup["cert"]:
            p = A.CERTS / f"C2B_SUPER_e{A.tag(e)}_N{N}{suf}.json"
            out["super"]["cert_file"] = p.name
            out["super"]["cert_file_sha256"] = A.write_json(p, sup["cert"])
            out["super"]["W_sha256"] = sup["cert"]["W_sha256"]
            sub = C2.c2b_sub(e, N, sup["g_int"], A.load_c2b()["c2b_certify"].Q)
            out["sub"] = sub["record"]
            if sub["cert"]:
                p = A.CERTS / f"C2B_SUB_e{A.tag(e)}_N{N}{suf}.json"
                out["sub"]["cert_file"] = p.name
                out["sub"]["cert_file_sha256"] = A.write_json(p, sub["cert"])
                out["sub"]["W_sha256"] = sub["cert"]["W_sha256"]
        else:
            out["sub"] = {"status": "NOT_RUN (no certified supersolution at this rung: the subsolution lemma needs a "
                                    "bounded E_.[tau]; the proposal is shared)"}
        out["code"] = {"c2b": A.load_c2b()["_sha256"], "a0": A.own_code_sha256()}
        name = f"C2B_e{A.tag(e)}_N{N}{suf}.json"
    elif job == "c1b":
        import a0_c1b as C1
        d = int(argv[3])
        r = C1.c1b_w_rung(e, d)
        out = {"schema": "A0_RESULT/1", "job": "c1b", "drift": A.fs(e), "degree": d, "super": r["record"]}
        if r["cert"]:
            p = A.CERTS / f"C1B_SUPER_e{A.tag(e)}_d{d}{suf}.json"
            out["super"]["cert_file"] = p.name
            out["super"]["cert_file_sha256"] = A.write_json(p, r["cert"])
            out["super"]["W_sha256"] = r["cert"]["W_sha256"]
        out["code"] = {"c1b": A.load_c1b()["_sha256"], "a0": A.own_code_sha256()}
        name = f"C1B_e{A.tag(e)}_d{d}{suf}.json"
    elif job == "c1bx":
        import a0_c1b as C1
        d = int(argv[3])
        full = C1.c1b_full_rung(e, d)
        wonly = C1.c1b_w_rung(e, d)["record"]
        eq = {"A_bar==U": full.get("A_bar") == wonly.get("U"), "Lambda_lo==L": full.get("Lambda_lo") == wonly.get("L"),
              "eta_W": full.get("eta_W") == wonly.get("eta_W")}
        out = {"schema": "A0_RESULT/1", "job": "c1bx", "drift": A.fs(e), "degree": d, "full_pinned": full,
               "w_only": {k: wonly.get(k) for k in ("status", "U", "L", "eta_W", "cpu_seconds")},
               "exact_equality": eq, "PASS": all(eq.values()) and full.get("status") == "CERTIFIED",
               "code": {"c1b": A.load_c1b()["_sha256"], "a0": A.own_code_sha256()}}
        name = f"C1BX_e{A.tag(e)}_d{d}{suf}.json"
    elif job == "mc":
        import a0_mc as MC
        n, seed = int(argv[3]), int(argv[4])
        out = {"schema": "A0_RESULT/1", "job": "mc", **MC.mc_lambda(e, n, seed)}
        name = f"MC_e{A.tag(e)}{suf}.json"
    else:
        raise SystemExit(__doc__)
    out["wall_seconds"] = round(time.time() - t0, 1)
    out["python"] = sys.version.split()[0]
    out["latent_proxy"] = "validation-drift values; stream-internal only (T1/T2)"
    A.write_json(A.RESULTS / name, out)
    A.ledger("a0_run.py", f"stream C pointwise certifier study: job {job} e={A.fs(e)} {' '.join(argv[3:])}",
             notes="declared validation drift (guards passed); no cell id; values stay in streams/A0")
    print("wrote", name, flush=True)


if __name__ == "__main__":
    main(list(sys.argv))
