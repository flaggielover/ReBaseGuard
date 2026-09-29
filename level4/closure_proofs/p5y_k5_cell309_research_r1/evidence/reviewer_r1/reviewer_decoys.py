"""Reviewer decoys RD-1 / RD-2 (declared in reviews/REVIEW_SRK_R1.md before running). Synthetic h=3, k=1/2,
E=[1/4, 9/32], index 1, degree 8. Outputs to the scratchpad only; exec-ledger redirected to the scratchpad."""
import json, sys, time
from fractions import Fraction as F
from pathlib import Path
NS = Path("/home/user/ReBaseGuard/level4/closure_proofs/p5y_k5_cell309_research_r1")
SCR = Path(__file__).resolve().parent
sys.path.insert(0, str(NS / "code"))
import q309_guard as Q
Q.EXEC_LEDGER = SCR / "reviewer_exec_ledger.jsonl"
Q.EXPOSURE_LEDGER = SCR / "reviewer_exposure_ledger.jsonl"
sys.path.insert(0, str(NS / "impl")); sys.path.insert(0, str(NS / "verify"))
import srk_certify as S, srk_kernel as KX
import srk_verify_indep as V
g = KX.Geom(3, F(1, 2)); elo, ehi = F(1, 4), F(9, 32); d = 8; i = 1
logs = []
def blk_of(Wr, Vr):
    return {"geometry": {"h": S.fstr(g.h), "k": S.fstr(g.k)}, "block": [S.fstr(elo), S.fstr(ehi)],
            "rungs": [{"degree": d, "W": Wr, "V": {i: Vr}}]}
def verdict(raw, fk):
    r = V.verify_cert(raw, fk, N=8, max_depth=24, procs=1)
    return {k: r.get(k) for k in ("verdict", "reason", "false", "describe")}
which = sys.argv[1]
t0 = time.time()
if which == "RD1":
    Wr = S.certify_W(g, elo, ehi, d, logs.append, True)
    Vr = S.certify_weight(g, i, elo, ehi, d, Wr, logs.append, mutant="shrink_window")
    cert = S.certificate_json(blk_of(Wr, Vr), i)
    (SCR / "RD1_cert.json").write_text(json.dumps(cert))
    out = {"RD1_shrink_window_as_whole": verdict(cert, None)}
else:
    Wr = S.certify_W(g, elo, ehi, d, logs.append, False)
    Vr = S.certify_weight(g, i, elo, ehi, d, Wr, logs.append)
    cert = S.certificate_json(blk_of(Wr, Vr), i)
    (SCR / "RD2_cert.json").write_text(json.dumps(cert))
    out = {"RD2_kernel_key_in_body": "kernel" in cert,
           "RD2_taboo_cert_as_whole": verdict(cert, None),
           "RD2_taboo_cert_with_file_kernel_taboo": verdict(cert, "taboo")}
out["seconds"] = round(time.time() - t0, 1)
out["statuses"] = [l.split(":")[0] + ":" + l.split(":")[1][:12] for l in logs]
print(json.dumps(out, indent=1, default=str))
