"""T1 frozen-reference reproduction for F_0 under the AUTHORIZED runtime contract.

Task1R (2026-09-04) recorded construction diagnostics on the pre-resize host; the
frozen aux4 evidence (blas_kernel_sensitivity.json) shows OpenBLAS kernel choice
alone moves 62/240 dyadic candidates, including F:0:0. The governing identity for
the genuine F_0 candidate under the authorized runtime contract d49f0437... is the
byte-exact scientific hash committed by the cap-authorized scaling study, which
contracted `task1_f0.build_candidate`'s F_0 over the 44 frozen (patch, panel, shift)
contexts. This module recomputes that hash with the T1 candidate, using the
committed packet.py VERBATIM (only its hard-coded ROOT is repointed to this
worktree) and the committed worker.py hashing procedure.
"""
from __future__ import annotations

import hashlib
import json
import types
from pathlib import Path

import sr_o9_candidates as T

CAP_EVIDENCE = T.CP / "p5y_k1_sr_cap_authorized_successor/evidence"
_ROOT_LINE = 'ROOT = Path("/home/ubuntu/work/ReBaseGuard")'


def load_cap_packet():
    src = (CAP_EVIDENCE / "packet.py").read_text()
    if src.count(_ROOT_LINE) != 1:
        raise T.ConstructionFailure("committed packet.py ROOT line not found exactly once")
    mod = types.ModuleType("cap_packet_replica")
    mod.__file__ = str(CAP_EVIDENCE / "packet.py")
    exec(compile(src.replace(_ROOT_LINE, f"ROOT = Path({str(T.ROOT)!r})"),
                 mod.__file__, "exec"), mod.__dict__)
    return mod, hashlib.sha256(src.encode()).hexdigest()


def exact(x):
    """Verbatim worker.py: exact dyadic (mantissa, exponent) of midpoint and radius."""
    return (x.mid().man_exp(), x.rad().man_exp())


def packet_scientific_hash(P, cand) -> str:
    """Verbatim worker.py hash: first packet, first contract of every context."""
    ctxs = P.build_contexts()
    AVs = [P.absvecs_of(c['sh']) for c in ctxs]
    h = hashlib.sha256()
    for ci, c in enumerate(ctxs):
        Rb = P.build_Rbig(c['pd'])
        coef, ex, ez = P.contract_O9(c['pd'], cand, Rb, AVs[ci])
        h.update(repr((c['patch'], c['panel'], c['shift'])).encode())
        for r_ in coef:
            for v_ in r_:
                h.update(repr(exact(v_)).encode())
        h.update(repr(exact(ex)).encode())
        h.update(repr(exact(ez)).encode())
    return h.hexdigest()


def recorded_hashes() -> dict:
    out = {}
    for f in sorted((CAP_EVIDENCE / "scaling_runs").glob("*.json")):
        d = json.loads(f.read_text())
        out.setdefault(d["cand"], set()).update(d["scientific_hashes"])
    return {k: sorted(v) for k, v in out.items()}


def reproduce() -> dict:
    rec = recorded_hashes()
    if len(rec.get("real", [])) != 1 or len(rec.get("dense", [])) != 1:
        raise T.ConstructionFailure(f"committed scaling runs are not self-consistent: {rec}")
    mine, _diag, _cond = T.reference_F0()
    with T.scientific_precision():
        P, packet_sha = load_cap_packet()
        cand = T.to_arb_matrix(mine)
        h_real = packet_scientific_hash(P, cand)
        h_dense = packet_scientific_hash(P, P.dense_random_candidate(1))
    return {"packet_py_sha256": packet_sha,
            "recorded_real": rec["real"][0], "recorded_dense": rec["dense"][0],
            "t1_F0_packet_hash": h_real, "dense_control_packet_hash": h_dense,
            "dense_control_replica_faithful": h_dense == rec["dense"][0],
            "t1_F0_matches_authorized_runtime_identity": h_real == rec["real"][0]}


if __name__ == "__main__":
    print(json.dumps(reproduce(), indent=1))
