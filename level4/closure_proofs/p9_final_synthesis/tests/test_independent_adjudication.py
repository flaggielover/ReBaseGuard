"""Independent P9 adjudication checks.

These tests record reviewer findings. They do not rewrite candidate gates or
turn the candidate's own expected outputs into scientific validation.
"""
from __future__ import annotations

import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[2]


def load_json(name: str):
    return json.loads((HERE / name).read_text())


def test_authoritative_p7_does_not_prove_global_monotonicity():
    p7 = (REPO / "level4/closure_proofs/p7_statistical_consequences/"
                 "INDEPENDENT_ADJUDICATION.md").read_text()
    assert "Global strict monotonicity of `A` is not proved" in p7


def test_submitted_p9_t2_inflates_that_unproved_premise():
    claims = {c["id"]: c for c in load_json("CLAIM_LEDGER.json")["claims"]}
    assert "non-increasing in |e|" in claims["P7-A"]["statement"]
    assert claims["P9-T2"]["status"] == "EXACT_THEOREM"
    assert "P7-A" in claims["P9-T2"]["parents"]


def test_p9_sr_first_step_is_not_the_frozen_step():
    z = 6.5
    log_threshold = math.log(520.886133602749)
    frozen_log_r = z - 0.5
    p9_log_r = math.log(2.0) + z - 0.5
    assert not (frozen_log_r >= log_threshold)
    assert p9_log_r >= log_threshold
    assert math.isclose(p9_log_r - frozen_log_r, math.log(2.0))


def test_a5_a6_artifacts_have_no_supplied_generator():
    python_source = "\n".join(p.read_text() for p in (HERE / "experiments").glob("*.py"))
    assert (HERE / "results/burnin_sensitivity.json").exists()
    assert (HERE / "results/p9t2_mixture_check.json").exists()
    assert "burnin_sensitivity.json" not in python_source
    assert "p9t2_mixture_check.json" not in python_source


def test_p8_quarantine_is_literal():
    graph = load_json("THEOREM_DEPENDENCY_GRAPH.json")
    p8_ids = {n["id"] for n in graph["nodes"] if n["priority"] == "P8"}
    assert p8_ids
    assert not [e for e in graph["edges"] if e["from"] in p8_ids]


def test_published_edge_count_discrepancy_is_real():
    graph = load_json("THEOREM_DEPENDENCY_GRAPH.json")
    theory = (HERE / "THEORY.md").read_text()
    assert len(graph["edges"]) == 64
    assert "0 cycles over all 66" in theory


def test_independent_verdict_is_partial():
    result = load_json("results/independent_adjudication.json")
    report = (HERE / "INDEPENDENT_ADJUDICATION.md").read_text()
    assert result["final_p9_verdict"] == "PARTIAL"
    assert "FINAL_P9_VERDICT = PARTIAL" in report
