"""K4R1 tests. SYNTHETIC ONLY: no real source value is read for its value.

The module under test is loaded from $K4R1_CODE_PATH (default: the committed code/k4r1_certificate.py) so the mutation
harness (tests/mutation_harness.py) can run this suite against mutants of the decision path.
"""
import copy
import hashlib
import importlib.util
import json
import os
import random
from fractions import Fraction as F
from pathlib import Path

import pytest

NS = Path(__file__).resolve().parents[1]
CODE = Path(os.environ.get("K4R1_CODE_PATH", NS / "code/k4r1_certificate.py"))
_spec = importlib.util.spec_from_file_location("k4r1_under_test", CODE)
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

E0 = F(5083, 20000000)
X1 = F(5083, 10000000)
A2, A3 = F(10187, 10000000), F(957, 625000)
PID = "3692d0feeaef71365798cd99399fdb6d744573f38d59dba5cfe2e99294f0ae19"


# ------------------------------------------------------------------ odd polynomial truth
class Poly:
    """R(e) = c1 e + c3 e^3 + c5 e^5 (odd, C^inf)."""

    def __init__(self, c1, c3, c5):
        self.c1, self.c3, self.c5 = F(c1), F(c3), F(c5)

    def R(self, e):
        return self.c1 * e + self.c3 * e ** 3 + self.c5 * e ** 5

    def d1(self, e):
        return self.c1 + 3 * self.c3 * e ** 2 + 5 * self.c5 * e ** 4

    def d3(self, e):
        return 6 * self.c3 + 60 * self.c5 * e ** 2

    def d5(self):
        return 120 * self.c5

    def R3_range(self, x):   # R''' monotone in e^2 on [0, x]
        v = (self.d3(F(0)), self.d3(x))
        return min(v), max(v)

    def negative_on(self, a):
        """exact: R(e) < 0 for all e in (0, a]  <=>  q(u) = c1 + c3 u + c5 u^2 < 0 on [0, a^2]"""
        us = [F(0), a * a]
        if self.c5 != 0:
            v = -self.c3 / (2 * self.c5)
            if 0 <= v <= a * a:
                us.append(v)
        return all(self.c1 + self.c3 * u + self.c5 * u * u < 0 for u in us)


def inputs_from(p: Poly, a, slack=F(0), dwidth=F(1, 100)):
    lo3, hi3 = p.R3_range(X1)
    D0 = (p.d1(E0) - dwidth, p.d1(E0) + dwidth / 3)
    return {"D0_hi": D0[1], "L1": lo3 - slack, "U0": p.d3(F(0)) + slack,
            "M3": max(abs(p.d3(F(0))), abs(p.d3(a))) + slack, "M5": abs(p.d5()) + slack}


def certify(p, a, **kw):
    v = inputs_from(p, a, **kw)
    G = K.g_bound(v["D0_hi"], v["L1"], E0)
    T = K.t_bound(v["M3"], v["U0"], v["M5"], a)
    return K.decide(G, T, a)


# ------------------------------------------------------------------ pure certificate
def test_strict_boundary_is_not_pass():
    assert K.decide(F(0), F(0), A3)["PASS"] is False
    a = F(1, 10)
    assert K.decide(F(-1, 600), F(1), a)["PASS"] is False          # B = -1/600 + 1/600 = 0 exactly
    assert K.decide(F(-1, 599), F(1), a)["PASS"] is True


def test_negative_T_cannot_help():
    assert K.decide(F(1, 10), F(-10 ** 9), F(1, 100))["PASS"] is False
    assert K.b_bound(F(-1), F(-5), F(1, 2)) == F(-1)


def test_exact_formulas():
    assert K.g_bound(F(-3), F(7), F(1, 10)) == F(-3) - F(7, 200)
    assert K.g_bound(F(-3), F(-7), F(1, 10)) == F(-3) + F(7, 200)
    assert K.t_bound(F(100), F(1), F(10 ** 6), F(1, 100)) == min(F(100), F(1) + F(1, 20000) * 10 ** 6)
    assert K.t_bound(F(10), F(1), F(10 ** 6), F(1, 100)) == F(10)
    assert K.t_bound(F(10 ** 9), F(1), F(2), F(1, 100)) == F(1) + F(1, 10000)
    assert K.b_bound(F(-2), F(12), F(1, 2)) == F(-2) + F(1, 24) * 12
    with pytest.raises(K.K4R1Refusal):
        K.t_bound(F(-1), F(0), F(1), F(1))
    with pytest.raises(K.K4R1Refusal):
        K.decide(F(-1), F(1), F(0))


def test_floats_refused():
    for bad in (0.5, 1e-3, True):
        with pytest.raises(K.K4R1Refusal):
            K.fr(bad)
    with pytest.raises(K.K4R1Refusal):
        K.interval({"lo": "1", "hi": "0"})


def test_soundness_randomised_odd_polynomials():
    """Whenever the certificate passes, the exact truth R < 0 on (0, a] holds. Both outcomes occur."""
    rng = random.Random(20260927)
    seen = {True: 0, False: 0}
    for _ in range(4000):
        a = rng.choice([A2, A3, F(1, 100), F(1, 3)])
        p = Poly(F(rng.randint(-2000, 400), 100), F(rng.randint(-10 ** 6, 10 ** 6), 10),
                 F(rng.randint(-10 ** 9, 10 ** 9), 1))
        c = certify(p, a, slack=F(rng.randint(0, 50)), dwidth=F(rng.randint(1, 500), 100))
        seen[c["PASS"]] += 1
        if c["PASS"]:
            assert p.negative_on(a), (p.c1, p.c3, p.c5, a)
    assert seen[True] > 200 and seen[False] > 200


def test_certificate_never_passes_a_positive_function():
    rng = random.Random(7)
    for _ in range(2000):
        a = rng.choice([A2, A3, F(1, 5)])
        p = Poly(F(rng.randint(-50, 50), 10), F(rng.randint(-10 ** 5, 10 ** 5)), F(rng.randint(-10 ** 8, 10 ** 8)))
        if not p.negative_on(a):
            assert certify(p, a)["PASS"] is False


def test_transport_term_is_load_bearing():
    """R''' grows away from 0 (large c5): an upper bound using U0 alone would be unsound."""
    a = F(1, 2)
    p = Poly(F(-1, 10), F(0), F(40))          # R(e)/e = -1/10 + 40 e^4 > 0 near e = 1/2
    assert not p.negative_on(a)
    v = inputs_from(p, a)
    v["M3"] = F(10 ** 12)                       # force the transport branch
    G = K.g_bound(v["D0_hi"], v["L1"], E0)
    assert K.decide(G, K.t_bound(v["M3"], v["U0"], v["M5"], a), a)["PASS"] is False
    assert K.decide(G, v["U0"], a)["PASS"] is True   # the unsound shortcut would pass


# ------------------------------------------------------------------ synthetic sources for identity checks
def per_cell(n, right, how):
    cells, left = [], F(0)
    for i in range(n):
        r = right[i]
        cells.append({"index": i, "left": str(left), "right": str(r), "how": how(i), "R_cell_hi": "-1", "Rprime_cell_hi": "-1"})
        left = r
    return cells


def synthetic_report():
    rights = [F(5083, 10000000), A2, A3] + [A3 + F(k, 100) for k in range(1, 201)]
    per = {}
    for d in ("CUSUM", "SR"):
        for m in ("1", "2", "3", "5"):
            nloose = {("CUSUM", "2"): 2, ("CUSUM", "3"): 3, ("CUSUM", "5"): 3}.get((d, m), 0)
            cells = per_cell(len(rights), rights, lambda i, n=nloose: "CERTIFICATE_TOO_LOOSE" if i < n else "DIRECT_R_NEGATIVE")
            per[f"{d}|m={m}"] = {"cells": len(cells), "per_cell": cells, "counterexample_cells": [],
                                 "too_loose_cells": list(range(nloose)),
                                 "outcome": "K4_CERTIFICATE_TOO_LOOSE" if nloose else "K4_CELLWISE_ALL_CERTIFIED"}
    return {"per_Dm": per}


def synthetic_universe():
    return {"detector_scope": ["CUSUM"], "residuals": [
        {"detector": "CUSUM", "m": 2, "cells": [0, 1], "a": str(A2)},
        {"detector": "CUSUM", "m": 3, "cells": [0, 1, 2], "a": str(A3)},
        {"detector": "CUSUM", "m": 5, "cells": [0, 1, 2], "a": str(A3)}]}


def synthetic_sources():
    k1 = {"detector": "CUSUM", "cell_index": 0, "producer_identity_hash": PID, "e0": [str(E0), "0/1"], "rho": [str(E0), "0/1"],
          "m": {m: {"detector": "CUSUM", "D_interval": {"lo": "-5", "hi": "-1"}} for m in ("1", "2", "3", "5")}}
    slot1 = {"scientific": {"binding": {"k1_cell_index": 0, "detector": "CUSUM", "record_sha256": "K1SHA", "left": "0/1",
                                        "right": str(X1)},
                            "context": {"point_e": "0/1", "x1": str(X1)},
                            "per_m": {m: {"L1": "1", "U0": "2"} for m in ("1", "2", "3", "5")}}}
    rows = []
    for i, (lo, hi) in enumerate([(F(0), X1), (X1, A2), (A2, A3), (A3, F(2, 1000))]):
        eta = hi + hi / 10 ** 70
        rows.append({"cell": i, "x_lo": str(lo), "x_hi": str(hi), "hull_norms": {"eta": str(eta)},
                     "M": {n: {m: "10" for m in ("1", "2", "3", "5")} for n in ("2", "3", "4", "5")}})
    text = {"sealed_record_sha256": "S1SHA", "rows": rows}
    return {"historical_report": synthetic_report(), "k1_cell0_record": k1, "slot1_record": slot1, "text_result": text}


PROV = {"identities": {"k1_cusum_producer_identity_hash": PID}, "geometry": {"k1_cell0_e0": str(E0)},
        "sources": {"k1_cell0_record": {"sha256": "K1SHA"}, "slot1_record": {"sha256": "S1SHA"}}}


def test_extract_accepts_consistent_synthetic_sources():
    out = K.extract_inputs(synthetic_sources(), synthetic_universe(), PROV)
    assert sorted(out) == ["2", "3", "5"]
    assert out["2"]["a"] == A2 and out["2"]["hull_cell"] == 1 and out["5"]["hull_cell"] == 2
    assert out["3"]["cells"] == [0, 1, 2]


@pytest.mark.parametrize("mutate", [
    lambda s, u: u["residuals"].pop(),                                                           # m scope shrunk
    lambda s, u: u["residuals"][0]["cells"].append(2),                                           # universe widened
    lambda s, u: u["residuals"][1].__setitem__("a", str(A2)),                                    # wrong a
    lambda s, u: s["historical_report"]["per_Dm"]["CUSUM|m=5"].__setitem__("counterexample_cells", [0]),
    lambda s, u: s["historical_report"]["per_Dm"]["SR|m=1"].__setitem__("too_loose_cells", [7]),  # extra residual elsewhere
    lambda s, u: s["k1_cell0_record"].__setitem__("producer_identity_hash", "0" * 64),
    lambda s, u: s["k1_cell0_record"].__setitem__("cell_index", 1),
    lambda s, u: s["k1_cell0_record"].__setitem__("e0", ["1/1000", "0/1"]),
    lambda s, u: s["slot1_record"]["scientific"]["binding"].__setitem__("record_sha256", "X"),
    lambda s, u: s["slot1_record"]["scientific"]["context"].__setitem__("point_e", "1/100"),
    lambda s, u: s["slot1_record"]["scientific"]["context"].__setitem__("x1", "1/100000000"),
    lambda s, u: s["text_result"].__setitem__("sealed_record_sha256", "X"),
    lambda s, u: s["text_result"]["rows"].pop(2),                                                # no hull for a3
    lambda s, u: s["text_result"]["rows"].append(copy.deepcopy(s["text_result"]["rows"][1])),    # hull not unique
    lambda s, u: s["text_result"]["rows"][1]["hull_norms"].__setitem__("eta", str(A2 - F(1, 10 ** 12))),  # eta below a
    lambda s, u: s["text_result"]["rows"][2]["hull_norms"].__setitem__("eta", str(A3 * 2)),       # eta not a rounding
    lambda s, u: s["slot1_record"]["scientific"]["per_m"]["5"].__setitem__("L1", 0.5),           # float
    lambda s, u: s["text_result"]["rows"][2]["M"]["3"].__setitem__("3", 7.0),                    # float
    lambda s, u: s["k1_cell0_record"]["m"]["2"].__setitem__("detector", "SR"),
])
def test_extract_refusals(mutate):
    s, u = synthetic_sources(), synthetic_universe()
    mutate(s, u)
    with pytest.raises((K.K4R1Refusal, KeyError)):
        K.extract_inputs(s, u, PROV)


def test_non_prefix_residual_refused():
    s, u = synthetic_sources(), synthetic_universe()
    per = s["historical_report"]["per_Dm"]["CUSUM|m=2"]
    per["too_loose_cells"] = [1, 2]
    for c in per["per_cell"]:
        c["how"] = "CERTIFICATE_TOO_LOOSE" if c["index"] in (1, 2) else "DIRECT_R_NEGATIVE"
    u["residuals"][0].update({"cells": [1, 2], "a": str(A3)})
    with pytest.raises(K.K4R1Refusal):
        K.extract_inputs(s, u, PROV)


def test_load_sources_hash_drift(tmp_path):
    (tmp_path / "a.json").write_text('{"x": 1}')
    (tmp_path / "d.md").write_text("doc")
    good = {"sources": {"a": {"kind": "json", "path": "a.json", "sha256": hashlib.sha256(b'{"x": 1}').hexdigest()},
                        "d": {"kind": "document", "path": "d.md", "sha256": hashlib.sha256(b"doc").hexdigest()}}}
    assert K.load_sources(good, tmp_path) == {"a": {"x": 1}}
    bad = copy.deepcopy(good)
    bad["sources"]["d"]["sha256"] = "0" * 64
    with pytest.raises(K.K4R1Refusal):
        K.load_sources(bad, tmp_path)
    bad = copy.deepcopy(good)
    bad["sources"]["a"]["sha256"] = "0" * 64
    with pytest.raises(K.K4R1Refusal):
        K.load_sources(bad, tmp_path)
    bad = copy.deepcopy(good)
    bad["sources"]["a"]["path"] = "missing.json"
    with pytest.raises(K.K4R1Refusal):
        K.load_sources(bad, tmp_path)


# ------------------------------------------------------------------ assembly
def res_map():
    return {"2": ([0, 1], A2), "3": ([0, 1, 2], A3), "5": ([0, 1, 2], A3)}


def certs(ok=("2", "3", "5")):
    return {m: {"PASS": m in ok, "outcome": "K4R1_CERTIFIED" if m in ok else "K4R1_CERTIFICATE_TOO_LOOSE"} for m in ("2", "3", "5")}


def test_assembly_complete():
    asm = K.assemble(synthetic_report(), res_map(), certs())
    assert asm["complete"] is True and len(asm["per_Dm"]) == 8
    assert asm["per_Dm"]["SR|m=1"]["source"] == "INHERITED_HISTORICAL_K4"


def test_assembly_one_certificate_fails():
    asm = K.assemble(synthetic_report(), res_map(), certs(ok=("2", "3")))
    assert asm["complete"] is False and asm["per_Dm"]["CUSUM|m=5"]["status"] == "FAIL"


def test_assembly_gap_and_uncertified_rest():
    rep = synthetic_report()
    rep["per_Dm"]["CUSUM|m=3"]["per_cell"][5]["left"] = "1/2"          # gap in the historical cover
    assert K.assemble(rep, res_map(), certs())["per_Dm"]["CUSUM|m=3"]["status"] == "FAIL"
    rep = synthetic_report()
    rep["per_Dm"]["CUSUM|m=2"]["per_cell"][4]["how"] = "CERTIFICATE_TOO_LOOSE"   # a non-residual cell uncertified
    assert K.assemble(rep, res_map(), certs())["per_Dm"]["CUSUM|m=2"]["status"] == "FAIL"
    rep = synthetic_report()
    rep["per_Dm"]["SR|m=2"]["per_cell"][9]["how"] = "CERTIFICATE_TOO_LOOSE"
    assert K.assemble(rep, res_map(), certs())["per_Dm"]["SR|m=2"]["status"] == "FAIL"
    rep = synthetic_report()
    rep["per_Dm"]["CUSUM|m=5"]["per_cell"] = rep["per_Dm"]["CUSUM|m=5"]["per_cell"][:50]   # cover stops before 2
    assert K.assemble(rep, res_map(), certs())["per_Dm"]["CUSUM|m=5"]["status"] == "FAIL"


def test_assembly_handoff_must_meet_a():
    bad = res_map()
    bad["2"] = ([0, 1], A3)          # K4R1 region end does not meet the first inherited cell
    assert K.assemble(synthetic_report(), bad, certs())["per_Dm"]["CUSUM|m=2"]["status"] == "FAIL"


# ------------------------------------------------------------------ execution gates
def test_execute_locked_without_freeze(tmp_path):
    with pytest.raises(K.K4R1Refusal):
        K.verify_freeze(tmp_path / "FREEZE.json", tmp_path)


def test_freeze_gate(tmp_path):
    code = Path(K.__file__).resolve()
    repo = code.parent                                   # the implementation lies inside this "repository"
    good = {"qualification_verdict": "QUALIFICATION_ACCEPTED",
            "bound_files": {code.name: hashlib.sha256(code.read_bytes()).hexdigest()}}
    p = tmp_path / "FREEZE.json"

    def write(o):
        p.write_text(json.dumps(o))
        (tmp_path / "FREEZE_HASH").write_text(hashlib.sha256(p.read_bytes()).hexdigest())

    write(good)
    assert K.verify_freeze(p, repo)["qualification_verdict"] == "QUALIFICATION_ACCEPTED"   # positive control
    for bad in ({**good, "qualification_verdict": "QUALIFICATION_REJECTED"},
                {**good, "bound_files": {code.name: "0" * 64}},                               # bound-file drift
                {**good, "bound_files": {}}):                                                 # implementation unbound
        write(bad)
        with pytest.raises(K.K4R1Refusal):
            K.verify_freeze(p, repo)
    write(good)
    (tmp_path / "FREEZE_HASH").write_text("0" * 64)                                           # freeze hash mismatch
    with pytest.raises(K.K4R1Refusal):
        K.verify_freeze(p, repo)
    write(good)
    with pytest.raises(K.K4R1Refusal):                                                        # implementation outside repo
        K.verify_freeze(p, tmp_path)


def test_exact_once(tmp_path, monkeypatch):
    out = tmp_path / "RESULT.json"
    out.write_text("{}")
    monkeypatch.setattr(K, "read_config", lambda: ({}, {}))
    monkeypatch.setattr(K, "verify_freeze", lambda *a, **k: {})

    def boom(*a, **k):
        raise AssertionError("sources must not be read when the output already exists")

    monkeypatch.setattr(K, "load_sources", boom)
    with pytest.raises(K.K4R1Refusal):
        K.main(["execute", "--out", str(out)])
