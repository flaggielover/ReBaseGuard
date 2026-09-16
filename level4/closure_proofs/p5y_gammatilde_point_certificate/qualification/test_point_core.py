"""Q1 fail-closed unit qualification of the point evaluator's pure logic (stdlib only, no kernel arithmetic).

    python3 -B qualification/test_point_core.py
"""
import copy
import json
import sys
import tempfile
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "code"))

import point_core as PC  # noqa: E402

PROTOCOL = PC.load_protocol()
CELL0 = next(c for c in json.loads((PC.ROOT / PC.CP / "p5y_k1_cover_ledger_successor/config/cells.json").read_text())
             if c["detector"] == "CUSUM" and c["index"] == 0)


def raises(fn, exc=PC.ProtocolViolation):
    try:
        fn()
    except exc:
        return True
    return False


# ---------------------------------------------------------------- manufactured exact derivatives
def manufactured(a: F, r: F):
    """R(e) = a e + b e^3 (odd, R'(0) = a exactly); an enclosure of R'(0) of radius r."""
    return a - r, a + r


def test_negative_derivative_certifies():
    lo, hi = manufactured(F(-9), F(8))
    g = PC.gamma_from_rprime(lo, hi)
    assert g["status"] == PC.CERTIFIED and F(g["GAMMATILDE_INTERVAL"][0]) == 2 and F(g["MARGIN_ABOVE_1"]) == 1


def test_positive_derivative_refutes():
    assert PC.adjudicate(*manufactured(F(3), F(1))) == PC.REFUTED


def test_zero_derivative_never_certifies():
    assert PC.adjudicate(0, 0) == PC.REFUTED                      # degenerate [0,0]: GammaTilde = 1, not > 1
    assert PC.adjudicate(*manufactured(F(0), F(1, 10))) == PC.INCONCLUSIVE
    assert PC.adjudicate(F(-1), F(0)) == PC.INCONCLUSIVE          # touches 0 from below
    assert PC.adjudicate(F(0), F(1)) == PC.REFUTED                # touches 0 from above


def test_near_zero_derivative():
    tiny = F(1, 2 ** 300)
    assert PC.adjudicate(-2 * tiny, -tiny) == PC.CERTIFIED
    assert PC.adjudicate(-tiny, tiny) == PC.INCONCLUSIVE
    assert PC.adjudicate(tiny, 2 * tiny) == PC.REFUTED


def test_malformed_interval():
    assert raises(lambda: PC.adjudicate(1, -1))


# ---------------------------------------------------------------- identity, m, manifest, pins
def test_wrong_m_refused():
    assert PC.require_m_values(PROTOCOL, [5, 3, 2, 1]) == (1, 2, 3, 5)
    for bad in ([3, 5], [1, 2, 3, 4, 5], [1, 2, 3, 6], [2, 3, 5]):
        assert raises(lambda bad=bad: PC.require_m_values(PROTOCOL, bad))


def test_identity_and_wrong_manifest():
    good = dict(PROTOCOL["producer_identity"])
    assert PC.identity_problems(PROTOCOL, good) == []
    wrong = dict(good, producer_manifest_hash="72c75c2244f553d6fd08a6b1e0369eaaf01b2c3cda77a9e5a54943b6805b21cb")
    assert PC.identity_problems(PROTOCOL, wrong)
    for bad in ({}, dict(good, producer_identity_hash="3692d0fe"), dict(good, runtime_contract_hash=None)):
        assert PC.identity_problems(PROTOCOL, bad)


def test_protocol_and_wrapper_tamper():
    assert PC.wrapper_pin_problems(PROTOCOL) == [] and PC.source_pin_problems(PROTOCOL) == []
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "P.json"
        h = Path(d) / "H"
        p.write_bytes(PC.PROTOCOL.read_bytes() + b" ")
        h.write_text(PC.PROTOCOL_HASH.read_text())
        assert raises(lambda: PC.load_protocol(p, h))
    tampered = copy.deepcopy(PROTOCOL)
    first = sorted(tampered["wrapper_files"])[0]
    tampered["wrapper_files"][first] = "0" * 64
    assert PC.wrapper_pin_problems(tampered)
    tampered = copy.deepcopy(PROTOCOL)
    first = sorted(tampered["source_hashes"])[0]
    tampered["source_hashes"][first] = "0" * 64
    assert PC.source_pin_problems(tampered)


# ---------------------------------------------------------------- geometry
def test_point_cell():
    cell = PC.point_cell(CELL0, F(0))
    assert cell["e0"] == cell["left"] == cell["right"] == ["0/1", "0/1"] and cell["rho"] == ["0/1", "0/1"]
    assert cell["C_upper"] == CELL0["C_upper"]
    e0 = F(CELL0["e0"][0])
    assert PC.point_cell(CELL0, e0)["e0"] == CELL0["e0"]
    assert raises(lambda: PC.point_cell(CELL0, F(-1, 10 ** 9)))
    assert raises(lambda: PC.point_cell(CELL0, 2 * e0 + F(1, 10 ** 12)))
    assert raises(lambda: PC.point_cell(dict(CELL0, index=1), F(0)))
    assert raises(lambda: PC.point_cell(dict(CELL0, C_evaluation=["1/2", "0/1"]), F(0)))


# ---------------------------------------------------------------- precision ladder
def test_precision_ladder():
    L = PROTOCOL["precision_ladder"]["bits"]
    I, C, R = PC.INCONCLUSIVE, PC.CERTIFIED, PC.REFUTED
    assert PC.next_rung(PROTOCOL, []) == L[0]
    assert PC.next_rung(PROTOCOL, [{"bits": L[0], "status": {"3": C, "5": C}}]) is None
    assert PC.next_rung(PROTOCOL, [{"bits": L[0], "status": {"3": C, "5": R}}]) is None
    assert PC.next_rung(PROTOCOL, [{"bits": L[0], "status": {"3": C, "5": I}}]) == L[1]
    done = [{"bits": b, "status": {"3": C, "5": I}} for b in L]
    assert PC.next_rung(PROTOCOL, done) is None
    assert PC.final_statuses(PROTOCOL, done) == {"3": C, "5": I}
    assert raises(lambda: PC.next_rung(PROTOCOL, [{"bits": L[1], "status": {"3": I, "5": I}}]))
    assert raises(lambda: PC.final_statuses(PROTOCOL, [{"bits": L[0], "status": {"3": C, "5": I}},
                                                       {"bits": L[1], "status": {"3": R, "5": C}}]))


# ---------------------------------------------------------------- controls
def _rung(d2, d1, r0=("-1/100", "1/100")):
    m = {str(k): {"R_interval": {"lo": r0[0], "hi": r0[1]}, "D_interval": {"lo": "-12", "hi": "-2"}}
         for k in (1, 2, 3, 5)}
    m["2"]["D_interval"] = {"lo": d2[0], "hi": d2[1]}
    m["1"]["D_interval"] = {"lo": d1[0], "hi": d1[1]}
    return {"m": m}


def test_controls():
    assert PC.control_problems(PROTOCOL, _rung(("-20", "-3"), ("-19", "-10"))) == []
    assert PC.control_problems(PROTOCOL, _rung(("-20", "-3"), ("-19", "-10"), r0=("1/100", "2/100")))
    assert PC.control_problems(PROTOCOL, _rung(("50", "60"), ("-19", "-10")))       # m=2 disjoint from reuse cert
    assert PC.control_problems(PROTOCOL, _rung(("-20", "-3"), ("-100", "-90")))     # m=1 disjoint from CORE-C1


def test_premise():
    C, I, R = PC.CERTIFIED, PC.INCONCLUSIVE, PC.REFUTED
    assert PC.premise({"3": C, "5": C}) == "SATISFIED"
    assert PC.premise({"3": C, "5": I}) == "OPEN"
    assert PC.premise({"3": R, "5": C}) == "REFUTED"


if __name__ == "__main__":
    n = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            n += 1
    print(f"ok {n}")
