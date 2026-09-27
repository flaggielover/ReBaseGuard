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
import sys
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


DVAL = {"1": ("-9", "-1/7"), "2": ("-8", "-3/11"), "3": ("-7", "-5/13"), "5": ("-6", "-7/17")}
SLOT = {m: {"L0": F(100 + 10 * k), "U0": F(200 + 10 * k), "M5": F(10 ** 6 * (k + 1))} for k, m in enumerate(("1", "2", "3", "5"))}
TF = X1 * X1 / 2


def slot_per_m():
    out = {}
    for m, v in SLOT.items():
        out[m] = {"L0": str(v["L0"]), "U0": str(v["U0"]), "M5": str(v["M5"]), "transport_factor": str(TF),
                  "L1": str(v["L0"] - TF * v["M5"] - F(1, 1000)), "U1": str(v["U0"] + TF * v["M5"] + F(1, 1000))}
    return out


def mval(n, m, row):
    return F(1000 * int(n) + 7 * int(m) + row, 1)


def synthetic_sources():
    k1 = {"detector": "CUSUM", "cell_index": 0, "producer_identity_hash": PID, "e0": [str(E0), "0/1"], "rho": [str(E0), "0/1"],
          "m": {m: {"detector": "CUSUM", "m": int(m), "cell_index": 0, "e0": [str(E0), "0/1"], "rho": [str(E0), "0/1"],
                    "D_interval": {"lo": DVAL[m][0], "hi": DVAL[m][1]}} for m in ("1", "2", "3", "5")}}
    slot1 = {"scientific": {"binding": {"k1_cell_index": 0, "detector": "CUSUM", "record_sha256": "K1SHA", "left": "0/1",
                                        "right": str(X1)},
                            "context": {"point_e": "0/1", "x1": str(X1)},
                            "per_m": slot_per_m()}}
    rows = []
    for i, (lo, hi) in enumerate([(F(0), X1), (X1, A2), (A2, A3), (A3, F(2, 1000))]):
        eta = hi + hi / 10 ** 70
        rows.append({"cell": i, "x_lo": str(lo), "x_hi": str(hi), "hull_norms": {"eta": str(eta)},
                     "M": {n: {m: str(mval(n, m, i)) for m in ("1", "2", "3", "5")} for n in ("2", "3", "4", "5")}})
    text = {"sealed_record_sha256": "S1SHA", "rows": rows}
    return {"historical_report": synthetic_report(), "k1_cell0_record": k1, "slot1_record": slot1, "text_result": text}


def expected(m, a, row):
    """independent statement of the frozen formulas over the synthetic constants"""
    L1 = SLOT[m]["L0"] - TF * SLOT[m]["M5"] - F(1, 1000)
    G = F(DVAL[m][1]) - L1 * E0 * E0 / 2
    T = min(mval("3", m, row), SLOT[m]["U0"] + a * a / 2 * mval("5", m, row))
    return G, T, G + a * a / 6 * max(T, F(0))


PROV = {"identities": {"k1_cusum_producer_identity_hash": PID}, "geometry": {"k1_cell0_e0": str(E0)},
        "sources": {"k1_cell0_record": {"sha256": "K1SHA"}, "slot1_record": {"sha256": "S1SHA"}}}


def test_extract_accepts_consistent_synthetic_sources():
    out = K.extract_inputs(synthetic_sources(), synthetic_universe(), PROV)
    assert sorted(out) == ["2", "3", "5"]
    assert out["2"]["a"] == A2 and out["2"]["hull_cell"] == 1 and out["5"]["hull_cell"] == 2
    assert out["3"]["cells"] == [0, 1, 2]


def test_extract_values_are_wired_to_the_right_fields():
    out = K.extract_inputs(synthetic_sources(), synthetic_universe(), PROV)
    for m, a, row in (("2", A2, 1), ("3", A3, 2), ("5", A3, 2)):
        v = out[m]
        assert v["_D0_hi"] == F(DVAL[m][1])
        assert v["_L1"] == SLOT[m]["L0"] - TF * SLOT[m]["M5"] - F(1, 1000)
        assert v["_U0"] == SLOT[m]["U0"]
        assert v["_M3"] == mval("3", m, row) and v["_M5"] == mval("5", m, row)
        assert v["e0"] == E0 and v["x1"] == X1 and v["a"] == a


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
    lambda s, u: s["k1_cell0_record"]["m"]["3"].__setitem__("m", 5),                            # entry for the wrong m
    lambda s, u: s["k1_cell0_record"]["m"]["5"].__setitem__("cell_index", 1),
    lambda s, u: s["k1_cell0_record"]["m"]["5"].__setitem__("e0", ["1/1000", "0/1"]),
    lambda s, u: s["slot1_record"]["scientific"]["per_m"]["3"].__setitem__("L1", "1000000"),     # L1 above transport
    lambda s, u: s["slot1_record"]["scientific"]["per_m"]["2"].__setitem__("U1", "0"),           # U1 below transport
    lambda s, u: s["slot1_record"]["scientific"]["per_m"]["5"].__setitem__("transport_factor", "0"),
    lambda s, u: s["slot1_record"]["scientific"]["per_m"]["5"].__setitem__("U0", "-1000000"),    # L0 > U0
])
def test_extract_refusals(mutate):
    s, u = synthetic_sources(), synthetic_universe()
    mutate(s, u)
    with pytest.raises(K.K4R1Refusal):
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
    repo, ns, mod = build_repo(tmp_path)
    fpath = ns / "config/FREEZE.json"
    good = json.loads(fpath.read_text())

    def write(o, hash_ok=True):
        fpath.write_text(json.dumps(o, sort_keys=True))
        (ns / "config/FREEZE_HASH").write_text(_sha(fpath) if hash_ok else "0" * 64)

    write(good)
    assert mod.verify_freeze()["qualification_verdict"] == "QUALIFICATION_ACCEPTED"          # positive control
    code_rel = str(NSREL / "code/k4r1_certificate.py")
    bad_cases = [
        {**good, "qualification_verdict": "QUALIFICATION_REJECTED"},
        {**good, "bound_files": {**good["bound_files"], code_rel: "0" * 64}},                   # bound-file drift
        {**good, "bound_files": {k: v for k, v in good["bound_files"].items() if k != code_rel}},  # code unbound
        {**good, "bound_files": {k: v for k, v in good["bound_files"].items()
                                 if not k.endswith("config/GATE.json")}},                       # gate unbound
        {**good, "qualification_review": None},                                                 # review not named
    ]
    for bad in bad_cases:
        write(bad)
        with pytest.raises(mod.K4R1Refusal):
            mod.verify_freeze()
    write(good, hash_ok=False)                                                                  # freeze hash mismatch
    with pytest.raises(mod.K4R1Refusal):
        mod.verify_freeze()
    write(good)
    with pytest.raises(mod.K4R1Refusal):                                                        # implementation outside repo
        mod.verify_freeze(repo=tmp_path / "elsewhere")
    (fpath).unlink()
    with pytest.raises(mod.K4R1Refusal):                                                        # freeze absent
        mod.verify_freeze()


def test_exact_once(tmp_path, monkeypatch):
    out = tmp_path / "RESULT.json"
    out.write_text("{}")
    monkeypatch.setattr(K, "OUT", out)
    monkeypatch.setattr(K, "read_config", lambda: ({}, {}))
    monkeypatch.setattr(K, "verify_freeze", lambda *a, **k: {})
    monkeypatch.setattr(K, "git_state", lambda *a, **k: {"head": "h", "clean": True, "freeze_committed": True})

    def boom(*a, **k):
        raise AssertionError("sources must not be read when the output already exists")

    monkeypatch.setattr(K, "load_sources", boom)
    with pytest.raises(K.K4R1Refusal):
        K.main(["execute"])


def test_assembly_residual_cell_must_be_the_historical_too_loose_cell():
    rep = synthetic_report()
    rep["per_Dm"]["CUSUM|m=3"]["per_cell"][2]["how"] = "DIRECT_R_NEGATIVE"   # residual claimed where history certified
    assert K.assemble(rep, res_map(), certs())["per_Dm"]["CUSUM|m=3"]["status"] == "FAIL"


# ------------------------------------------------------------------ end-to-end execute in a throwaway git repository
import shutil
import subprocess

NSREL = Path("level4/closure_proofs/p5y_k4r1_nearzero_successor")


def _git(repo, *args):
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *args], check=True,
                   capture_output=True)


def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


MAKE_FREEZE = Path(os.environ.get("K4R1_MAKE_FREEZE_PATH", NS / "code/make_freeze.py"))
REVIEW_DIR = "review/qualification_rT"
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}


def _head(repo):
    return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()


def build_candidate(tmp, *, report=None, sources=None, prov_hook=None):
    repo = tmp / "repo"
    ns = repo / NSREL
    (ns / "code").mkdir(parents=True)
    shutil.copy(CODE, ns / "code/k4r1_certificate.py")
    shutil.copy(MAKE_FREEZE, ns / "code/make_freeze.py")
    for rel in ("tests/test_k4r1.py", "tests/mutation_harness.py", "SPECIFICATION.md", "config/GATE.json", "docs/premise.md"):
        (ns / rel).parent.mkdir(parents=True, exist_ok=True)
        (ns / rel).write_text(f"synthetic {rel}\n")
    src = sources or synthetic_sources()
    if report is not None:
        src["historical_report"] = report
    data = repo / "data"
    data.mkdir()

    def dump(name, obj):
        (data / name).write_text(json.dumps(obj, sort_keys=True))
        return {"kind": "json", "path": f"data/{name}", "sha256": _sha(data / name)}

    prov_sources = {"historical_report": dump("report.json", src["historical_report"]),
                    "k1_cell0_record": dump("k1.json", src["k1_cell0_record"])}
    src["slot1_record"]["scientific"]["binding"]["record_sha256"] = prov_sources["k1_cell0_record"]["sha256"]
    prov_sources["slot1_record"] = dump("slot1.json", src["slot1_record"])
    src["text_result"]["sealed_record_sha256"] = prov_sources["slot1_record"]["sha256"]
    prov_sources["text_result"] = dump("text.json", src["text_result"])
    prov_sources["premise"] = {"kind": "document", "path": str(NSREL / "docs/premise.md"),
                               "sha256": _sha(ns / "docs/premise.md")}
    prov = {"sources": prov_sources, "identities": {"k1_cusum_producer_identity_hash": PID},
            "geometry": {"k1_cell0_e0": str(E0)}}
    if prov_hook:
        prov_hook(prov)
    (ns / "config/PROVENANCE.json").write_text(json.dumps(prov))
    (ns / "config/RESIDUAL_UNIVERSE.json").write_text(json.dumps(synthetic_universe()))
    (repo / ".gitignore").write_text("__pycache__/\n.pytest_cache/\n.DS_Store\n")
    _git(repo, "init", "-q")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "candidate")
    return repo, ns


def run_make_freeze(repo, ns, *, review=None, review_dir=REVIEW_DIR):
    rd = ns / review_dir
    rd.mkdir(parents=True, exist_ok=True)
    (rd / "QUALIFICATION_REVIEW.json").write_text(
        json.dumps(review or {"verdict": "QUALIFICATION_ACCEPTED", "candidate_commit": _head(repo)}))
    (rd / "QUALIFICATION_REVIEW.md").write_text("synthetic review\n")
    return subprocess.run([sys.executable, "-B", str(NSREL / "code/make_freeze.py"), "--review-dir", review_dir],
                          cwd=repo, capture_output=True, text=True, env=ENV)


def load_mod(ns, tag):
    old = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location(f"k4r1_e2e_{tag}", ns / "code/k4r1_certificate.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = old
    return mod


def rewrite_freeze(ns, fn):
    fpath = ns / "config/FREEZE.json"
    fz = json.loads(fpath.read_text())
    fn(fz)
    fpath.write_text(json.dumps(fz, indent=1, sort_keys=True) + "\n")
    (ns / "config/FREEZE_HASH").write_text(_sha(fpath) + "\n")


def build_repo(tmp, *, report=None, sources=None, bind_all=True, commit_freeze=True, freeze=True):
    repo, ns = build_candidate(tmp, report=report, sources=sources)
    if freeze:
        r = run_make_freeze(repo, ns)
        assert r.returncode == 0, r.stderr
        if not bind_all:
            rewrite_freeze(ns, lambda fz: fz["bound_files"].pop(str(NSREL / "tests/mutation_harness.py")))
        if not commit_freeze:
            (repo / ".git/info/exclude").write_text(str(NSREL / "config/FREEZE.json") + "\n")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "freeze")
    return repo, ns, load_mod(ns, abs(hash(str(tmp))))


def run_execute(mod, ns):
    assert not (ns / "evidence/execution_r1").exists()          # a clean checkout has no output directory
    assert mod.main(["ready"]) == 0
    assert mod.main(["execute"]) == 0
    assert mod.OUT == ns / "evidence/execution_r1/K4R1_RESULT.json"
    return json.loads(mod.OUT.read_text())


def test_execute_end_to_end_exact_values(tmp_path):
    repo, ns, mod = build_repo(tmp_path)
    res = run_execute(mod, ns)
    for m, a, row in (("2", A2, 1), ("3", A3, 2), ("5", A3, 2)):
        G, T, B = expected(m, a, row)
        c = res["certificates"][f"CUSUM|m={m}"]
        assert (F(c["G"]), F(c["T"]), F(c["B"]), F(c["a"])) == (G, T, B, a)
        assert c["PASS"] is (B < 0) and c["cells"] == [[0, 1], [0, 1, 2], [0, 1, 2]][["2", "3", "5"].index(m)]
    assert res["K4R1_SUCCESSOR_SCIENCE"] == "PASS" and res["K4R1_COMPLETE_K4_ASSEMBLY"] == "PASS"
    assert res["residual_remaining"] == {} and res["new_real_addresses"] == 0 and res["status"] == "EXECUTED"
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    assert res["executed_at_head"] == head
    assert res["freeze_sha256"] == _sha(ns / "config/FREEZE.json")
    for m, a, row in (("2", A2, 1), ("3", A3, 2), ("5", A3, 2)):
        c = res["certificates"][f"CUSUM|m={m}"]
        assert c["inputs"] == {"D0_hi": DVAL[m][1] if "/" in DVAL[m][1] else str(F(DVAL[m][1])),
                               "L1": str(SLOT[m]["L0"] - TF * SLOT[m]["M5"] - F(1, 1000)), "U0": str(SLOT[m]["U0"]),
                               "M3": str(mval("3", m, row)), "M5": str(mval("5", m, row)), "e0": str(E0), "x1": str(X1)}
        assert c["T_branch"] == "U0+a^2/2*M5"            # synthetic M3 (~3000) exceeds U0 + a^2/2*M5 (~200)
    with pytest.raises(mod.K4R1Refusal):                     # exact once
        mod.main(["execute"])


def test_execute_one_residual_fails(tmp_path):
    s = synthetic_sources()
    s["k1_cell0_record"]["m"]["5"]["D_interval"] = {"lo": "-6", "hi": "-1/1000000000"}   # G ~ 0 -> B > 0
    repo, ns, mod = build_repo(tmp_path, sources=s)
    res = run_execute(mod, ns)
    assert res["certificates"]["CUSUM|m=5"]["PASS"] is False
    assert res["certificates"]["CUSUM|m=2"]["PASS"] is True
    assert res["K4R1_SUCCESSOR_SCIENCE"] == "NOT_CLOSED" and res["K4R1_COMPACT_RESIDUAL_COVERAGE"] == "FAIL"
    assert res["residual_remaining"] == {"CUSUM|m=5": [0, 1, 2]}


def test_execute_all_certified_but_assembly_incomplete(tmp_path):
    rep = synthetic_report()
    rep["per_Dm"]["SR|m=1"]["per_cell"][7]["left"] = "1/2"          # inherited cover broken elsewhere
    repo, ns, mod = build_repo(tmp_path, report=rep)
    res = run_execute(mod, ns)
    assert all(c["PASS"] for c in res["certificates"].values())
    assert res["K4R1_COMPLETE_K4_ASSEMBLY"] == "FAIL" and res["K4R1_SUCCESSOR_SCIENCE"] == "NOT_CLOSED"


def test_execute_refuses_dirty_checkout(tmp_path):
    repo, ns, mod = build_repo(tmp_path)
    (repo / "stray.txt").write_text("x")
    with pytest.raises(mod.K4R1Refusal):
        mod.main(["execute"])
    assert not mod.OUT.exists()


def test_execute_refuses_uncommitted_freeze(tmp_path):
    repo, ns, mod = build_repo(tmp_path, commit_freeze=False)
    with pytest.raises(mod.K4R1Refusal):
        mod.main(["execute"])


def test_execute_refuses_missing_mandatory_binding(tmp_path):
    repo, ns, mod = build_repo(tmp_path, bind_all=False)
    with pytest.raises(mod.K4R1Refusal):
        mod.main(["execute"])


def test_execute_refuses_source_drift_after_freeze(tmp_path):
    repo, ns, mod = build_repo(tmp_path)
    (repo / "data/text.json").write_text("{}")
    _git(repo, "commit", "-q", "-am", "drift")
    with pytest.raises(mod.K4R1Refusal):
        mod.main(["execute"])


def test_execute_T_branch_M3(tmp_path):
    s = synthetic_sources()
    for row in s["text_result"]["rows"]:
        for m in row["M"]["3"]:
            row["M"]["3"][m] = "3"                          # M3 below the transport bound
    repo, ns, mod = build_repo(tmp_path, sources=s)
    res = run_execute(mod, ns)
    for m in ("2", "3", "5"):
        c = res["certificates"][f"CUSUM|m={m}"]
        assert c["T_branch"] == "M3" and F(c["T"]) == 3


def test_literal_command_from_repo_root_and_elsewhere(tmp_path):
    """The gate's literal commands, as subprocesses, with no pre-created output directory."""
    for where in ("root", "elsewhere"):
        repo, ns, mod = build_repo(tmp_path / where)
        script = str(NSREL / "code/k4r1_certificate.py") if where == "root" else str(ns / "code/k4r1_certificate.py")
        cwd = repo if where == "root" else tmp_path
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        r = subprocess.run([sys.executable, "-B", script, "ready"], cwd=cwd, capture_output=True, text=True, env=env)
        assert r.returncode == 0 and '"READY": "PASS"' in r.stdout, r.stderr
        r = subprocess.run([sys.executable, "-B", script, "execute"], cwd=cwd, capture_output=True, text=True, env=env)
        assert r.returncode == 0, r.stderr
        res = json.loads((ns / "evidence/execution_r1/K4R1_RESULT.json").read_text())
        assert res["status"] == "EXECUTED" and res["K4R1_SUCCESSOR_SCIENCE"] == "PASS"
        r = subprocess.run([sys.executable, "-B", script, "execute"], cwd=cwd, capture_output=True, text=True, env=env)
        assert r.returncode == 3 and "EXACT_ONCE" in r.stderr
        r = subprocess.run([sys.executable, "-B", script, "ready"], cwd=cwd, capture_output=True, text=True, env=env)
        assert r.returncode == 3


def test_crash_after_reservation_is_recorded_and_spends_the_execution(tmp_path, monkeypatch):
    repo, ns, mod = build_repo(tmp_path)

    def boom(*a, **k):
        raise RuntimeError("synthetic crash inside the computation")

    monkeypatch.setattr(mod, "assemble", boom)
    with pytest.raises(RuntimeError):
        mod.main(["execute"])
    rec = json.loads(mod.OUT.read_text())
    assert rec["status"] == "EXECUTION_CRASHED" and "synthetic crash" in rec["error"]
    with pytest.raises(mod.K4R1Refusal):
        mod.main(["execute"])


def test_ready_computes_nothing_and_writes_nothing(tmp_path, monkeypatch):
    repo, ns, mod = build_repo(tmp_path)

    def forbidden(*a, **k):
        raise AssertionError("ready must not compute the certificate")

    for name in ("g_bound", "t_bound", "b_bound", "decide", "compute"):
        monkeypatch.setattr(mod, name, forbidden)
    assert mod.main(["ready"]) == 0
    assert not (ns / "evidence/execution_r1").exists()


def test_freeze_bytes_must_equal_head(tmp_path):
    repo, ns, mod = build_repo(tmp_path)
    fpath = ns / "config/FREEZE.json"
    fz = json.loads(fpath.read_text())
    fz["note"] = "edited after commit"
    fpath.write_text(json.dumps(fz, sort_keys=True))
    (ns / "config/FREEZE_HASH").write_text(_sha(fpath))
    _git(repo, "update-index", "--assume-unchanged", str(NSREL / "config/FREEZE.json"), str(NSREL / "config/FREEZE_HASH"))
    assert mod.git_state(repo, fpath)["clean"] is True                      # status hides the edit
    with pytest.raises(mod.K4R1Refusal):
        mod.main(["execute"])
    assert not mod.OUT.exists()


@pytest.mark.parametrize("mutate", [
    lambda s, u, p: s["slot1_record"]["scientific"]["binding"].__setitem__("right", "1/1000"),        # x1 != hull right
    lambda s, u, p: [s["slot1_record"]["scientific"]["binding"].__setitem__("right", "1/100000000"),
                     s["slot1_record"]["scientific"]["context"].__setitem__("x1", "1/100000000")],     # x1 < e0
    lambda s, u, p: p["geometry"].__setitem__("k1_cell0_e0", "1/1000"),                                # frozen e0 differs
    lambda s, u, p: [s["k1_cell0_record"].__setitem__("rho", ["1/1000", "0/1"])] +
    [e.__setitem__("rho", ["1/1000", "0/1"]) for e in s["k1_cell0_record"]["m"].values()],             # e0 != rho
    lambda s, u, p: s["k1_cell0_record"].__setitem__("detector", "SR"),
    lambda s, u, p: s["slot1_record"]["scientific"]["binding"].__setitem__("k1_cell_index", 1),
    lambda s, u, p: s["slot1_record"]["scientific"]["binding"].__setitem__("detector", "SR"),
    lambda s, u, p: s["slot1_record"]["scientific"]["binding"].__setitem__("left", "1/1000000"),     # hull not from 0
    lambda s, u, p: u.__setitem__("detector_scope", ["CUSUM", "SR"]),
    lambda s, u, p: s["slot1_record"]["scientific"]["per_m"]["2"].__setitem__("M5", "-1"),           # negative M5
    lambda s, u, p: s["k1_cell0_record"]["m"]["3"].__setitem__("rho", ["1/1000", "0/1"]),            # entry geometry
])
def test_structural_refusals_r3(mutate):
    s, u, p = synthetic_sources(), synthetic_universe(), copy.deepcopy(PROV)
    mutate(s, u, p)
    with pytest.raises(K.K4R1Refusal):
        K.extract_inputs(s, u, p)


def test_assembly_structural_cases_r3():
    rep = synthetic_report()
    rep["per_Dm"]["SR|m=1"]["per_cell"][0]["left"] = "1/1000000000"          # inherited cover does not start at 0
    assert K.assemble(rep, res_map(), certs())["per_Dm"]["SR|m=1"]["status"] == "FAIL"
    rep = synthetic_report()
    rep["per_Dm"]["CUSUM|m=2"]["counterexample_cells"] = [0]                   # counterexample in history
    assert K.assemble(rep, res_map(), certs())["per_Dm"]["CUSUM|m=2"]["status"] == "FAIL"
    rep = synthetic_report()
    for c in rep["per_Dm"]["CUSUM|m=5"]["per_cell"]:
        c["how"] = "CERTIFICATE_TOO_LOOSE"                                      # nothing inherited after the residual
    allres = res_map()
    allres["5"] = (list(range(len(rep["per_Dm"]["CUSUM|m=5"]["per_cell"]))), F(rep["per_Dm"]["CUSUM|m=5"]["per_cell"][-1]["right"]))
    assert K.assemble(rep, allres, certs())["per_Dm"]["CUSUM|m=5"]["status"] == "FAIL"
    rep = synthetic_report()
    rep["per_Dm"]["SR|m=2"]["outcome"] = "K4_CERTIFICATE_TOO_LOOSE"            # uncertified (D,m) outside the universe
    assert K.assemble(rep, res_map(), certs())["per_Dm"]["SR|m=2"]["status"] == "FAIL"


def test_make_freeze_flow_end_to_end_and_fresh_clone(tmp_path):
    repo, ns, mod = build_repo(tmp_path)
    fz = json.loads((ns / "config/FREEZE.json").read_text())
    tracked = subprocess.run(["git", "-C", str(repo), "ls-files", "--", str(NSREL)], capture_output=True, text=True).stdout.split()
    parent = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD~1"], capture_output=True, text=True).stdout.strip()
    assert fz["target_values_present"] is False and fz["qualified_candidate_commit"] == parent
    assert {k for k in fz["bound_files"] if k.startswith(str(NSREL) + "/")} == set(tracked) - {
        str(NSREL / "config/FREEZE.json"), str(NSREL / "config/FREEZE_HASH")}
    assert "data/text.json" in fz["bound_files"]
    delta = subprocess.run(["git", "-C", str(repo), "diff", "--name-only", fz["qualified_candidate_commit"], "HEAD"],
                           capture_output=True, text=True).stdout.split()
    assert sorted(delta) == fz["allowed_freeze_delta"] and len(delta) == 4
    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", "-q", str(repo), str(clone)], check=True, capture_output=True)
    script = str(NSREL / "code/k4r1_certificate.py")
    r = subprocess.run([sys.executable, "-B", script, "ready"], cwd=clone, capture_output=True, text=True, env=ENV)
    assert r.returncode == 0, r.stderr
    r = subprocess.run([sys.executable, "-B", script, "execute"], cwd=clone, capture_output=True, text=True, env=ENV)
    assert r.returncode == 0, r.stderr
    assert json.loads((clone / NSREL / "evidence/execution_r1/K4R1_RESULT.json").read_text())["K4R1_SUCCESSOR_SCIENCE"] == "PASS"


def _mf_case(tmp, name, prepare, *, review=None, review_dir=REVIEW_DIR, prov_hook=None):
    repo, ns = build_candidate(tmp / name, prov_hook=prov_hook)
    prepare(repo, ns)
    if callable(review):
        review = review(_head(repo))
    r = run_make_freeze(repo, ns, review=review, review_dir=review_dir)
    assert r.returncode != 0, (name, r.stdout)
    assert not (ns / "config/FREEZE.json").exists() and not (ns / "config/FREEZE_HASH").exists()


def test_make_freeze_refusals(tmp_path):
    nop = lambda repo, ns: None
    _mf_case(tmp_path, "rejected", nop, review=lambda head: {"verdict": "QUALIFICATION_REJECTED", "candidate_commit": head})
    _mf_case(tmp_path, "blocked", nop, review=lambda head: {"verdict": "QUALIFICATION_BLOCKED", "candidate_commit": head})
    _mf_case(tmp_path, "wrongcand", nop, review={"verdict": "QUALIFICATION_ACCEPTED", "candidate_commit": "0" * 40})
    _mf_case(tmp_path, "untracked_ns", lambda repo, ns: (ns / "extra.txt").write_text("x"))
    _mf_case(tmp_path, "untracked_out", lambda repo, ns: (repo / "extra.txt").write_text("x"))
    _mf_case(tmp_path, "edited_code", lambda repo, ns: (ns / "code/k4r1_certificate.py").write_text(
        (ns / "code/k4r1_certificate.py").read_text() + "\n# edited after qualification\n"))
    _mf_case(tmp_path, "ignored_ns", lambda repo, ns: (ns / ".DS_Store").write_text("finder"))
    _mf_case(tmp_path, "pycache_ns", lambda repo, ns: [(ns / "code/__pycache__").mkdir(),
                                                        (ns / "code/__pycache__/x.pyc").write_bytes(b"x")])
    _mf_case(tmp_path, "outside_review", nop, review_dir="config/qualification_rT")
    _mf_case(tmp_path, "escape_review", nop, review_dir="review/../../x")

    def tracked_review(repo, ns):
        (ns / REVIEW_DIR).mkdir(parents=True)
        (ns / REVIEW_DIR / "old.md").write_text("old")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "tracked review dir")
    _mf_case(tmp_path, "tracked_review_dir", tracked_review)

    def drift(prov):
        prov["sources"]["text_result"]["sha256"] = "0" * 64
    _mf_case(tmp_path, "source_drift", nop, prov_hook=drift)

    def existing_freeze(repo, ns):
        (ns / "config/FREEZE.json").write_text("{}")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "pre-existing freeze")
    repo, ns = build_candidate(tmp_path / "existing")
    existing_freeze(repo, ns)
    assert run_make_freeze(repo, ns).returncode != 0


def test_post_freeze_change_refused(tmp_path):
    repo, ns, mod = build_repo(tmp_path)
    (ns / "config/GATE.json").write_text("changed after the freeze\n")
    rewrite_freeze(ns, lambda fz: fz["bound_files"].__setitem__(str(NSREL / "config/GATE.json"), _sha(ns / "config/GATE.json")))
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "post-freeze edit")
    with pytest.raises(mod.K4R1Refusal):
        mod.main(["ready"])
    with pytest.raises(mod.K4R1Refusal):
        mod.main(["execute"])
    assert not mod.OUT.exists()


def test_bound_namespace_must_equal_tracked(tmp_path):
    repo, ns, mod = build_repo(tmp_path)
    (ns / ".DS_Store").write_text("finder")                          # ignored, never committed
    rewrite_freeze(ns, lambda fz: fz["bound_files"].__setitem__(str(NSREL / ".DS_Store"), _sha(ns / ".DS_Store")))
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "freeze binds an ignored file")
    with pytest.raises(mod.K4R1Refusal):
        mod.verify_freeze()


def test_missing_bound_file_refused(tmp_path):
    repo, ns, mod = build_repo(tmp_path)
    (repo / "data/text.json").unlink()
    with pytest.raises(mod.K4R1Refusal):
        mod.verify_freeze()


def test_interrupt_after_reservation_recorded(tmp_path, monkeypatch):
    repo, ns, mod = build_repo(tmp_path)

    def interrupt(*a, **k):
        raise KeyboardInterrupt()

    monkeypatch.setattr(mod, "assemble", interrupt)
    with pytest.raises(KeyboardInterrupt):
        mod.main(["execute"])
    rec = json.loads(mod.OUT.read_text())
    assert rec["status"] == "EXECUTION_CRASHED" and rec["executed_at_head"] == _head(repo)
    assert rec["freeze_sha256"] == _sha(ns / "config/FREEZE.json")


def test_negative_majorant_refused_before_reservation():
    for n in ("3", "5"):
        s = synthetic_sources()
        s["text_result"]["rows"][2]["M"][n]["3"] = "-1"
        with pytest.raises(K.K4R1Refusal):
            K.extract_inputs(s, synthetic_universe(), PROV)


def test_tampered_delta_refused(tmp_path):
    """a freeze that widens its own allowed delta to smuggle a post-freeze edit is refused"""
    repo, ns, mod = build_repo(tmp_path)
    gate = str(NSREL / "config/GATE.json")
    (ns / "config/GATE.json").write_text("changed after the freeze\n")

    def widen(fz):
        fz["allowed_freeze_delta"] = sorted(fz["allowed_freeze_delta"] + [gate])
        fz["bound_files"][gate] = _sha(ns / "config/GATE.json")
    rewrite_freeze(ns, widen)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "widened delta")
    with pytest.raises(mod.K4R1Refusal):
        mod.verify_freeze()


def test_freeze_not_descended_from_candidate_refused(tmp_path):
    """same tree as a valid freeze, but an orphan commit: HEAD is not descended from the qualified candidate"""
    repo, ns, mod = build_repo(tmp_path)
    mod.verify_freeze()                                                  # positive control
    orphan = subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", "commit-tree",
                             "HEAD^{tree}", "-m", "orphan"], capture_output=True, text=True, check=True).stdout.strip()
    _git(repo, "reset", "-q", "--hard", orphan)
    with pytest.raises(mod.K4R1Refusal):
        mod.verify_freeze()
