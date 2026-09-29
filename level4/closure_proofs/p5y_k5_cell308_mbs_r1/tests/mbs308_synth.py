"""MB-S r1 tests: the SYNTHETIC evaluator (a stub Stage-1 job function over fake job keys, and a stub Stage 2).

No certifier, no drift, no cell: the job records are deterministic functions of the job key (sha256-derived exact
fractions, a tuple and an int-keyed dict so the lossless checkpoint encoding is exercised). They run through MB r1's
UNCHANGED stage1() (pool, VER follow-ups, the admission rule S1M.pointwise and the aggregation) with only
S1M.rlr_block replaced by a stub, then a stub Stage 2 (a digest). Test controls via the environment (workers inherit
it): MBS308_TEST_JOBLOG (one line per completed job execution), MBS308_TEST_WORKER_DIE (a job key whose worker dies
once), MBS308_TEST_JOB_SLEEP, MBS308_TEST_ALLOC_MB (memory the job holds, for the watchdog test).
"""
from __future__ import annotations

import hashlib
import os
import time
import types
from fractions import Fraction as F

N_BLOCKS = 3
LADDER = {"RLR": (4, 6), "C2B": (20,), "C1B": (4, 8)}          # C1B d4 <= 6 -> one VER follow-up per block


def _frac(tag: str, lo: int, hi: int) -> F:
    h = int(hashlib.sha256(tag.encode()).hexdigest()[:12], 16)
    return F(lo) + F(h % 10 ** 6, 10 ** 6) * (hi - lo)


def synth_init(*_args) -> None:
    """Replaces _worker_init in the workers (no pinned science is loaded; nothing is armed)."""


def synth_job(kind: str, block: dict, rung: int, payload=None) -> dict:
    key = f"{kind}.{block['index']}.{rung}"
    die = os.environ.get("MBS308_TEST_WORKER_DIE")
    flag = os.environ.get("MBS308_TEST_DIEFLAG")
    if die == key and flag and not os.path.exists(flag):
        open(flag, "w").close()
        os._exit(99)
    mb = int(os.environ.get("MBS308_TEST_ALLOC_MB") or 0)
    hold = bytearray(mb * 1024 * 1024) if mb else None
    if hold is not None:
        for i in range(0, len(hold), 4096):
            hold[i] = 1
    sl = float(os.environ.get("MBS308_TEST_JOB_SLEEP") or 0)
    if sl:
        time.sleep(sl)
    base = {"kind": kind, "block": block["index"], "rung": rung}
    if kind == "RLR":
        out = {**base, "status": "CERTIFIED",
               "record": {"status": "CERTIFIED", "x": _frac(key, 1, 2), "pair": (rung, block["index"]),
                          "by_degree": {rung: _frac(key + "d", 0, 1)}}}
    elif kind == "C1B":
        out = {**base, "status": "CERTIFIED", "record": {"status": "CERTIFIED", "L": str(_frac(key + "L", 1, 2)),
                                                          "U": str(_frac(key + "U", 3, 4))},
               "cert": {"drift": "1/2", "W": [str(_frac(key + "w", 0, 1))], "tuple": (1, 2)}}
    elif kind == "C2B":
        out = {**base, "status_U": "CERTIFIED", "status_L": "CERTIFIED",
               "record": {"U": str(_frac(key + "U", 3, 4)), "L": str(_frac(key + "L", 1, 2))},
               "verification": {"verdict": "VERIFIED", "accepted": True}}
    elif kind == "VER":
        out = {**base, "verification": {"verdict": "VERIFIED", "accepted": True, "payload_sha256":
                                        hashlib.sha256(repr(payload).encode()).hexdigest()}}
    else:
        raise ValueError(kind)
    log = os.environ.get("MBS308_TEST_JOBLOG")
    if log:
        fd = os.open(log, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        try:
            os.write(fd, (key + "\n").encode())
        finally:
            os.close(fd)
    del hold
    return out


def synth_rlr_block(S1, IND7, cp, rl, kappa):
    cert = [r["record"] for r in rl if r.get("status") == "CERTIFIED"]
    if not cert:
        return None
    return {"status": "CERTIFIED", "n": len(cert), "x_min": min(F(r["x"]) for r in cert)}


def install(D, spec: dict) -> dict:
    """Patch the loaded sandbox driver: stubs for the consumer / science / controls / prepare, the synthetic job path,
    the launcher and host gates (their own tests cover them), and return {"evaluator", "prepare"}."""
    real_S1M = D.S1M
    fake = types.SimpleNamespace(**{k: getattr(real_S1M, k) for k in dir(real_S1M) if not k.startswith("__")})
    fake.rlr_block = synth_rlr_block
    D.S1M = fake
    D._worker_job = synth_job
    D._worker_init = synth_init
    D.load_consumer = lambda: {"stub": True}
    D.load_science = lambda allow_uncommitted=False, with_decoy_gen=False: {"stub": True}
    ctl_pass = spec.get("control_pass", True)
    D.control = lambda con, sci, k: {"pass": ctl_pass, "C_A": {"stub": True}, "C_B": {"stub": True},
                                     "_ca": {"_A": {"A0": F(1), "A1": F(1), "A2": F(1)}}, "_bundle": None}
    if not spec.get("real_launch_check"):
        D.check_launched = lambda: {"pass": True, "stub": "launchd integration is test_mbs308_launch"}
    D.host_preflight = lambda launched: {"pass": True, "stub": "gates are unit-tested"}
    if spec.get("mem_cap_mb"):
        D.MEM_CAP_BYTES = int(spec["mem_cap_mb"]) * 1024 * 1024
        D.MEM_POLL_S = 0.3
    if spec.get("eval_cap_s"):
        D.EVAL_CAP_S = float(spec["eval_cap_s"])

    def prepare(con, ctl, own_sha, grant, sci):
        pairs = [(D.fs(a), D.fs(b)) for a, b in sorted(D.GUARD.target_admitted_set())]
        return {"blocks": [], "pairs": pairs, "grant_commit": grant["grant_commit"], "own_sha": own_sha,
                "kappa_check": {"stub": True}}

    def evaluator(con, prep):
        blocks = [{"index": i, "tile": (F(i, 7), F(i + 1, 7)), "hull": (F(i, 7), F(i + 1, 7)), "b": F(i, 7)}
                  for i in range(N_BLOCKS)]
        sci = {"S1": None, "IND7": None, "cp": None, "indep": None, "kappa": (F(1), F(1))}
        st1 = D.stage1("target", blocks, prep["grant_commit"], prep["own_sha"], sci, LADDER, prep["pairs"], workers=2)
        pub = D.jsonable(D.public_stage1(st1))
        dig = hashlib.sha256(repr(pub).encode()).hexdigest()
        return {"cell": 308, "stage1": pub, "stage2": {"synthetic_digest": dig},
                "decision": {"mechanical_outcome": "STUB_DECOY"}}
    return {"evaluator": evaluator, "prepare": prepare}
