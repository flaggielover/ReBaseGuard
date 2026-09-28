"""Stream D producer: the ONLY module of this stream that imports the C1b certifier.

It calls the pinned-in-place C1b function ``c1b_certpw.certify_degree(e, d, BW_PW, log, e_r=0)`` at declared
non-target drifts, and stores the certified whole-kernel supersolution

    W = (1 + eta_W) * rec['_c']['W']            (strip-piecewise over t = p + m, strip boundaries BW)

exactly (every coefficient as 'num/den'), together with the producer's A_bar, eta_W and status, in
streams/VERIFY/certs/CERT_e<tag>_d<d>.json, plus a sha256 of the canonical certificate body.

Usage:  python3 -I -B vd_produce.py E_NUM/E_DEN:DEG [E:DEG ...]   (at most 3 worker processes)

Nothing here verifies anything: the verifier (vd_verify.py) never imports this file or any c1b_* module.
Quarantine: guard_drift on every drift before the certifier is imported; import guard installed first.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parents[1]
REPO = NS.parents[2]
OV = NS.parent / "p5y_k5_tail_overnight_research"
C1B_DIR = OV / "streams" / "C_308" / "LR" / "cusum"
CERT_DIR = HERE / "certs"


def _load_quarantine():
    spec = importlib.util.spec_from_file_location("c308_quarantine", NS / "code" / "c308_quarantine.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


Q = _load_quarantine()
Q.install_import_guard()


def fs(x: F) -> str:
    x = F(x)
    return f"{x.numerator}/{x.denominator}"


def tag_of(e: F) -> str:
    return f"{e.numerator}_{e.denominator}"


def canonical_body(cert: dict) -> bytes:
    body = {k: cert[k] for k in ("format", "drift", "BW", "strips", "W_at_atom_producer", "c1b_raw")}
    return json.dumps(body, sort_keys=True, separators=(",", ":")).encode()


def produce(e: F, d: int) -> dict:
    Q.guard_drift(e)
    sys.path.insert(0, str(C1B_DIR))
    import c1b_certpw as CP  # noqa: E402  (the one sanctioned import of the original certifier)
    import c1b_pw as PW  # noqa: E402
    sys.path.pop(0)
    lines: list = []
    t0 = time.process_time()
    rec = CP.certify_degree(F(e), d, PW.BW_PW, log=lambda s: lines.append(str(s)), e_r=F(0))
    cpu = time.process_time() - t0
    out = {"drift": fs(e), "degree": d, "status": rec.get("status"), "producer_cpu_s": round(cpu, 1),
           "producer_log_tail": lines[-6:]}
    if rec.get("status") != "CERTIFIED":
        return out
    etaW = F(rec["eta_W"])
    raw = rec["_c"]["W"]
    strips = []
    for P in raw:
        mons = []
        for (i, j, k), v in sorted(P.items()):
            if k != 0:
                raise ValueError("C1b W polynomial has an e-dependent monomial; point certificates must not")
            c = F(v) * (1 + etaW)
            if c:
                mons.append([i, j, fs(c)])
        strips.append(mons)
    sys.path.insert(0, str(HERE))
    import vd_adapt as AD  # noqa: E402  (layout helper only; imports no certifier and no verifier)
    sys.path.pop(0)
    cert = {
        "c1b_raw": {"layout": "C1b rec['_c']['W'] strips [[i, j, k, c]] (p^i m^j e^k), BW, eta_W",
                    "BW": [fs(F(b)) for b in PW.BW_PW], "W_unscaled": AD.c1b_raw_from_record_polys(raw),
                    "eta_W": fs(etaW)},
        "format": "VD_STRIP_PW/1",
        "semantics": ("W(p,m) = sum c_ij p^i m^j of strip s, s = the right-closed strip [BW[s-1], BW[s]] of t = p+m "
                      "containing t (strip 1 closed at 0); coefficients already scaled by (1 + eta_W)"),
        "drift": fs(e), "BW": [fs(F(b)) for b in PW.BW_PW], "strips": strips,
        "W_at_atom_producer": fs(F(rec["A_bar"])),
        "producer": {"module": "c1b_certpw.certify_degree", "degree": d, "eta_W": fs(etaW),
                     "status": rec["status"], "C_R_producer": fs(F(rec["C_R"])),
                     "residual_enclosure_W": rec["residual_enclosures"]["W"],
                     "supersolution_W": rec["supersolution_W"], "cpu_s": round(cpu, 1)},
    }
    cert["sha256_body"] = hashlib.sha256(canonical_body(cert)).hexdigest()
    path = CERT_DIR / f"CERT_e{tag_of(F(e))}_d{d}.json"
    path.write_text(json.dumps(cert, indent=1, sort_keys=True) + "\n")
    out.update({"file": str(path.relative_to(NS)), "sha256_body": cert["sha256_body"],
                "sha256_file": hashlib.sha256(path.read_bytes()).hexdigest(), "A_bar": fs(F(rec["A_bar"]))})
    return out


def _job(arg):
    e, d = arg
    try:
        return produce(e, d)
    except Exception as exc:  # noqa: BLE001 -- recorded, never silently dropped
        return {"drift": fs(e), "degree": d, "status": "PRODUCER_EXCEPTION", "error": repr(exc)[:300]}


def _sources_sha() -> dict:
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(C1B_DIR.glob("c1b_*.py")) if p.name in
            ("c1b_gauss.py", "c1b_kernel.py", "c1b_float.py", "c1b_pw.py", "c1b_prov.py", "c1b_certpw.py")}


if __name__ == "__main__":
    import multiprocessing as mp
    jobs = []
    for a in sys.argv[1:]:
        es, ds = a.split(":")
        e = F(es)
        Q.guard_drift(e)
        jobs.append((e, int(ds)))
    CERT_DIR.mkdir(parents=True, exist_ok=True)
    Q.log_event("streams/VERIFY/vd_produce.py", "produce C1b whole-kernel supersolution certificates at declared "
                "non-target drifts for independent verification: " + ",".join(sys.argv[1:]),
                klass="NONTARGET_DRIFT_VALIDATION", agent="streamD")
    ctx = mp.get_context("spawn")
    with ctx.Pool(min(3, len(jobs))) as pool:
        res = pool.map(_job, jobs)
    manifest_path = HERE / "certs" / "PRODUCER_MANIFEST.json"
    old = json.loads(manifest_path.read_text()) if manifest_path.exists() else {"runs": []}
    old["runs"].append({"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "args": sys.argv[1:],
                        "c1b_sources_sha256": _sources_sha(), "results": res})
    manifest_path.write_text(json.dumps(old, indent=1, sort_keys=True) + "\n")
    for r in res:
        print(json.dumps({k: v for k, v in r.items() if k != "producer_log_tail"}))
