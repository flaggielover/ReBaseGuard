"""Stdlib-only tests for T-EXT (no python-flint): mutation sites, the independent chain vs the frozen k5b_literal on
randomized synthetic covers (with finite, negative and absent L), channel refusals, and the protocol pins.

    python3 -B tests/test_text_static.py
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
import types
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[3]
sys.path.insert(0, str(NS / "code"))

import text_consume as TC  # noqa: E402
import text_crosscheck as TX  # noqa: E402
import text_mutants as TM  # noqa: E402

KB_PATH = REPO / "level4/closure_proofs/p5y_k5b_independent_countersignature/code/k5b_check.py"
KB_PIN = "ddd54dc469375a2d64352782add8573231be07b94f7246dad83c4e55a2bf35a6"


def load_kb():
    b = KB_PATH.read_bytes()
    assert hashlib.sha256(b).hexdigest() == KB_PIN
    mod = types.ModuleType("k5b_check_test")
    mod.__file__ = str(KB_PATH)
    exec(compile(b, str(KB_PATH), "exec"), mod.__dict__)
    return mod


def test_mutation_sites_unique():
    for fn, lst in (("text_transport.py", TM.TRANSPORT_MUTANTS), ("text_consume.py", TM.CONSUME_MUTANTS)):
        src = (NS / "code" / fn).read_text()
        for name, old, _new in lst:
            assert src.count(old) == 1, (fn, name)
        assert src.count("HERE = Path(__file__).resolve()") == 1


def _convert(c):
    return {"xlo": c["x_lo"], "xhi": c["x_hi"], "rho": c["rho"], "e0": c["e0"], "Rhi": c["R"][1], "Dlo": c["D"][0],
            "Hlo": c["H"][0], "M": c["M"], "L": c["L"]}


def test_chain_equals_k5b_literal():
    KB = load_kb()
    rng = random.Random(20260919)
    n = 0
    for _ in range(300):
        R = KB.random_odd_poly(rng)
        xs = KB.make_cover(rng)
        cells = KB.synthetic_cells(R, xs, rng, widen=rng.choice([0, 1, 3]), l_drop=rng.choice([0.0, 0.3, 0.7]),
                                   l_slack=rng.choice([0, 1, 5]))
        for c in cells:                                  # also exercise large negative finite L
            if c["L"] is not None and rng.random() < 0.2:
                c["L"] = c["L"] - F(rng.randint(1, 10 ** 6))
        want = [r["pass"] for r in KB.k5b_literal(cells)]
        got = TX._chain([_convert(c) for c in cells])
        assert want == got, (want, got)
        n += 1
    assert n == 300


def _synthetic_text(M5=F(10) ** 30):
    rows = []
    for k in range(0, 41):
        x_lo, x_hi = F(k, 100), F(k + 1, 100)
        rows.append({"cell": k, "x_lo": str(x_lo), "x_hi": str(x_hi),
                     "M": {str(n): {m: str(M5) for m in "1235"} for n in (2, 3, 4, 5)}})
    L0 = {m: F(5) for m in "1235"}
    for r in rows[1:]:
        X = F(r["x_hi"])
        B = sum((F(q["M"]["5"]["1"]) * ((X - F(q["x_lo"])) ** 2 - (X - F(q["x_hi"])) ** 2) / 2
                 for q in rows[:r["cell"] + 1]), F(0))
        r["Lambda"] = {m: str(max(L0[m] - B, -M5)) for m in "1235"}
    return {"rows": rows, "channel_cells": list(range(1, 41)), "sealed_record_sha256": TC.SEALED_SHA256,
            "sealed_L1": {"1": "1"}, "L0": {m: "5" for m in "1235"}}


def test_text_objects_refuses():
    good = _synthetic_text()
    lam, m2 = TC.text_objects(good, {"1": "1"})
    assert len(lam["1"]) == 40 and len(m2["5"]) == 41
    bad_lambda = json.loads(json.dumps(good))
    bad_lambda["rows"][7]["Lambda"]["3"] = "0"
    bad_gap = json.loads(json.dumps(good))
    bad_gap["rows"][5]["x_lo"] = "1/3"
    for bad in ({**good, "rows": good["rows"][:-1]}, {**good, "sealed_record_sha256": "0" * 64},
                {**good, "sealed_L1": {"1": "2"}}, {**good, "L0": {m: "6" for m in "1235"}}, bad_lambda, bad_gap,
                {**good, "channel_cells": list(range(1, 40))}):
        try:
            TC.text_objects(bad, {"1": "1"})
        except TC.ConsumeRefusal:
            continue
        raise AssertionError("text_objects accepted a bad TEXT_RESULT")


def test_protocol_pins():
    p = NS / "config/TEXT_PROTOCOL.json"
    if not p.exists():
        return
    proto = json.loads(p.read_text())
    bad = [r for r, h in proto["pins"].items() if hashlib.sha256((REPO / r).read_bytes()).hexdigest() != h]
    assert not bad, bad
    assert proto["hull_cells"] == list(range(1, 41)) and proto["new_real_scientific_addresses"] == 0
    assert proto["status"] == "FROZEN_PRE_RESULT"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
    print("ok", len(tests))
