"""Stream A0 job entry point, batch 2 (kept separate so that batch-1 provenance of a0_run.py stays exact).

  python3 -I -B -S a0_run2.py c2bx E N [--out-suffix S]    C2b exact-scale rung (a0_c2bx): upper + lower
  python3 -I -B -S a0_run2.py c1bh E d [--out-suffix S]    C1b W-only rung on the dyadic hull (a0_c1bh)
"""
from __future__ import annotations

import sys
import time
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a0_common as A  # noqa: E402

CODE_AT_START = A.own_code_sha256()


def main(argv):
    suf = ""
    if "--out-suffix" in argv:
        i = argv.index("--out-suffix")
        suf = "_" + argv[i + 1]
        del argv[i:i + 2]
    job, e = argv[1], A.declared_drift(F(argv[2]))
    t0 = time.time()
    if job == "c2bx":
        import a0_c2bx as X
        N = int(argv[3])
        r = X.c2bx_rung(e, N)
        out = {"schema": "A0_RESULT/1", "job": "c2bx", "drift": A.fs(e), "N": N, "rung": r["record"]}
        for k, c in r["certs"].items():
            p = A.CERTS / f"C2BX_{k.upper()}_e{A.tag(e)}_N{N}{suf}.json"
            out["rung"][f"cert_file_{k}"] = p.name
            out["rung"][f"cert_file_{k}_sha256"] = A.write_json(p, c)
        out["code"] = {"c2b": A.load_c2b()["_sha256"], "a0_at_process_start": CODE_AT_START}
        name = f"C2BX_e{A.tag(e)}_N{N}{suf}.json"
    elif job == "c1bh":
        import a0_c1bh as H
        d = int(argv[3])
        r = H.c1b_hull_rung(e, d)
        out = {"schema": "A0_RESULT/1", "job": "c1bh", "drift": A.fs(e), "degree": d, "super": r["record"]}
        if r["cert"]:
            p = A.CERTS / f"C1BH_SUPER_e{A.tag(e)}_d{d}{suf}.json"
            out["super"]["cert_file"] = p.name
            out["super"]["cert_file_sha256"] = A.write_json(p, r["cert"])
        out["code"] = {"c1b": A.load_c1b()["_sha256"], "a0_at_process_start": CODE_AT_START}
        name = f"C1BH_e{A.tag(e)}_d{d}{suf}.json"
    else:
        raise SystemExit(__doc__)
    out["wall_seconds"] = round(time.time() - t0, 1)
    out["python"] = sys.version.split()[0]
    out["latent_proxy"] = "validation-drift values; stream-internal only (T1/T2)"
    A.write_json(A.RESULTS / name, out)
    A.ledger("a0_run2.py", f"stream C pointwise certifier study: job {job} e={A.fs(e)} {argv[3]}",
             notes="declared validation drift (guards passed; c1bh: its 2^-20 hull also guarded); no cell id")
    print("wrote", name, flush=True)


if __name__ == "__main__":
    main(list(sys.argv))
