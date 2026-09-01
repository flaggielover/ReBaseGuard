"""G6A: the F3 family must equal the frozen literal declaration.

Membership is derived from the RAW event counts in the frozen P6R arrays and
from the declaration text, never from the generated P6R2 JSON.
"""
import json
from pathlib import Path

import numpy as np
import pytest

from rebaseguard_p6r2 import families as FAM

NS = Path(__file__).resolve().parents[1]
P6R = NS.parent / "p6r_safe_rebaselining_confirmation"
PROTOCOL = P6R / "REPAIRED_PROTOCOL.md"


def _raw_events():
    """Dtail100 exceedance counts per Delta, straight from the frozen arrays."""
    z = np.load(P6R / "results" / "p6r_perrep_eval_P.npz")
    man = json.loads((P6R / "results" / "p6r_confirm_manifest_eval.json").read_text())
    cell = next(c for c in man["cells"] if c["tag"] == "P")
    ctl = f"FIXED_TUNE_rho{cell['rho_tune']:g}"
    out = {}
    for sh in cell["shifts"][1:]:
        dm = np.asarray(z[f"DELAY|SAW_M|{sh}"], float)
        dc = np.asarray(z[f"DELAY|{ctl}|{sh}"], float)
        out[float(sh)] = (int((dm > 100).sum()), int((dc > 100).sum()))
    return out


def test_the_declaration_says_primary_metric_with_dq95_only_as_fallback():
    txt = PROTOCOL.read_text()
    assert "the `Delta`-scope family: the primary metric at `Delta in {0.5, 2}`" \
        in txt.replace("**", "")
    assert "`Dq95` is the declared fallback metric" in txt
    assert FAM.PRIMARY_METRIC == "Dtail100" and FAM.FALLBACK_METRIC == "Dq95"
    assert FAM.TAIL_EVENT_FLOOR == 200 and FAM.F3_DELTAS == (0.5, 2.0)


def test_literal_membership_derived_from_raw_event_counts():
    ev = _raw_events()
    # Delta = 0.5 clears the floor; Delta = 2 does not.  Derived, not asserted.
    assert min(ev[0.5]) >= 200
    assert min(ev[2.0]) < 200
    mem = FAM.f3_membership(ev)
    assert mem[0.5]["included_key"] == "Dtail100@0.5"
    assert mem[0.5]["excluded"] == []
    assert mem[2.0]["included_key"] == "Dq95@2.0"
    assert mem[2.0]["excluded"][0]["key"] == "Dtail100@2.0"
    assert mem[2.0]["excluded"][0]["label"] == "INSUFFICIENT_TAIL_EVENTS"
    assert {m["included_key"] for m in mem.values()} == {"Dtail100@0.5", "Dq95@2.0"}


def test_no_undeclared_fallback_enters_when_the_primary_is_eligible():
    """The exact P6R defect: Dq95@0.5 was included while Dtail100@0.5 was eligible."""
    mem = FAM.f3_membership(_raw_events())
    keys = {m["included_key"] for m in mem.values()}
    assert "Dq95@0.5" not in keys, "undeclared fallback leaked into F3"
    assert len(keys) == len(FAM.F3_DELTAS) == 2, "one test per declared Delta"


@pytest.mark.parametrize("nm,nc,expect", [
    (5000, 5000, "Dtail100"), (199, 5000, "Dq95"), (5000, 199, "Dq95"),
    (200, 200, "Dtail100"), (0, 0, "Dq95")])
def test_membership_rule_is_the_floor_on_BOTH_arms(nm, nc, expect):
    mem = FAM.f3_membership({0.5: (nm, nc), 2.0: (nm, nc)})
    assert mem[0.5]["included_metric"] == expect


def test_bh_over_the_literal_family_uses_only_its_members():
    ev = _raw_events()
    mem = FAM.f3_membership(ev)
    recs = {m["included_key"]: {"status": "OK", "p_value": p, "tail_flag": None}
            for m, p in zip(mem.values(), (0.02, 0.5))}
    fam = FAM.bh_over_defined(recs)
    assert fam["n_tests"] == 2 and set(fam["family"]) == set(recs)
    assert fam["q"] == 0.10
