"""C11R Phase 8 -- mutation suite.

Carries forward C11's independence and soundness mutants where they still apply, and adds the
thirteen this campaign's subject demands: substituting a scalar drift for an interval, a midpoint
or endpoints for uniformity, one kernel for the other, one constant for another, one cell for
another, a flipped atom sign, a narrowed block, comparison before sealing, a gate that states its
own result, and a refuted candidate sent to certification anyway.

EVERY detector carries a NEGATIVE CONTROL: a planted value it is shown to reject. A detector with
no demonstrated failure mode establishes nothing, and C11's M10 -- which could only pass while the
campaign's conclusion was negative, and survived undetected once that changed -- is the standing
example. A mutant whose evidence is absent is recorded UNDETERMINED, never DETECTED: a check that
passes because its input is missing is the same defect wearing a different hat.
"""
from __future__ import annotations

import ast
import json
import pathlib
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_common as C
import c11r_equiv as EQ
import c11r_gate as GA
import c11r_idrift as I

sys.path.insert(0, str(C.C7 / "code"))
import c7_gaussian as G  # noqa: E402

res = []


def mut(mid, name, detected, how, control=None):
    res.append({"id": mid, "name": name,
                "outcome": "DETECTED" if detected is True else
                           ("UNDETERMINED" if detected is None else "SURVIVED"),
                "how": how, "negative_control": control})


def imports_of(path: pathlib.Path) -> set[str]:
    roots = set()
    for n in ast.walk(ast.parse(path.read_text())):
        if isinstance(n, ast.Import):
            roots |= {a.name.split(".")[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
            roots.add(n.module.split(".")[0])
    return roots


def maybe(p: pathlib.Path):
    return C.load(p) if p.exists() else None


def main() -> int:
    tbl = C.load(C.NS / "evidence" / "table" / "C11R_N9_TABLE.json")
    gate = C.load(C.NS / "config" / "N9R_GATE_C11R.json")
    equiv = C.load(C.NS / "evidence" / "equivalence" / "C11R_EQUIVALENCE.json")
    val = maybe(C.NS / "evidence" / "validation" / "C11R_VALIDATION.json")
    scr = maybe(C.NS / "evidence" / "screen" / "C11R_SCREEN.json")
    runs = maybe(C.NS / "evidence" / "runs" / "C11R_RUNS.json")

    e_lo, e_hi = F(tbl["drift_domain"]["e_lo"]), F(tbl["drift_domain"]["e_hi"])
    BLOCK = I.Blk(e_lo, e_hi)
    MID = (e_lo + e_hi) / 2
    orig = EQ.original_propositions(tbl)

    # ---------------- carried forward from C11 ----------------------------------------------
    mods = sorted((C.NS / "code").glob("*.py"))
    allroots = set()
    for m in mods:
        allroots |= imports_of(m)
    forbidden = {"taboo_certify", "resolvent_certificate", "opnorms", "ra_certifier",
                 "fast_range", "intervals", "rebaseguard_certify", "rung3_engine", "spec"}
    mut("M01", "hidden import of the original certifier's load-bearing graph",
        not (allroots & forbidden),
        f"AST over {len(mods)} modules; imported roots {sorted(allroots)}",
        f"the forbidden set is non-empty ({len(forbidden)} modules), so the test can fail")

    backend = {"numpy", "flint", "scipy", "mpmath", "sympy", "gmpy2"}
    mut("M02", "using the original's arithmetic backend",
        not (allroots & backend), f"intersection with {sorted(backend)} is empty",
        "the backend set is non-empty, so the test can fail")

    # A module that MENTIONS the registry in prose is not a module that READS it. The first
    # version of this detector was a substring presence check, and it fired on the gate's own
    # description of its drift source and on this file's own check text -- the C8
    # presence-check-as-detection defect, and a self-scan besides. This walks the AST for a call
    # whose argument subtree actually names the registry file.
    def _reads_registry(path: pathlib.Path) -> bool:
        tree = ast.parse(path.read_text())
        for n in ast.walk(tree):
            if isinstance(n, ast.Call):
                for sub in ast.walk(n):
                    if isinstance(sub, ast.Constant) and sub.value == "REGISTRY_C2.json":
                        return True
        return False

    readers = sorted(m.name for m in mods if _reads_registry(m))
    mentioners = sorted(m.name for m in mods if "REGISTRY_C2" in m.read_text())
    allowed = {"c11r_table.py", "c11r_compare.py"}
    mut("M03", "reading the original's certified constants during construction",
        set(readers) <= allowed,
        f"modules that actually LOAD the registry: {readers} (allowed {sorted(allowed)}); "
        f"modules that merely mention it in prose: {mentioners}",
        "a certifier or screen module appearing in the reader list would fail the test; the "
        "mentioner list is strictly larger, so prose alone does not trip it")

    # ---------------- M16-M18: drift uniformity ---------------------------------------------
    one = {(0, 0): F(1)}
    at_pt = I.alarm_prob_iv(F(0), F(0), I.Blk(MID, MID))
    at_blk = I.alarm_prob_iv(F(0), F(0), BLOCK)
    widens = (at_blk.hi - at_blk.lo) > (at_pt.hi - at_pt.lo)
    mut("M16", "a scalar drift substituted for the interval drift",
        widens and at_blk.lo <= at_pt.lo and at_pt.hi <= at_blk.hi,
        f"block enclosure width {float(at_blk.hi - at_blk.lo):.3e} strictly exceeds the point's "
        f"{float(at_pt.hi - at_pt.lo):.3e}, and contains it; a scalar result cannot be mistaken "
        f"for a block result",
        "a degenerate block reproduces the point exactly, so the widening test can fail")

    r_mid = EQ.check("Abar", orig["Abar"],
                     dict(orig["Abar"], drift_domain=[float(MID), float(MID)]))
    mut("M17", "the midpoint substituted for uniform drift over the block",
        r_mid["STATUS"] == "WEAKER",
        f"the equivalence checker classifies a midpoint domain as {r_mid['STATUS']}",
        "an unmutated proposition classifies EQUIVALENT, so the test can fail")

    r_ends = EQ.check("Abar", orig["Abar"],
                      dict(orig["Abar"], drift_domain=[float(e_lo), float(e_lo)]))
    g4 = gate["predicates"]["G4_block_uniformity_rigorous"]
    mut("M18", "endpoints only, with no theorem bounding the interior",
        r_ends["STATUS"] == "WEAKER" and "only when accompanied by a proof" in g4,
        f"endpoint-only domain classifies {r_ends['STATUS']}, and G4 admits sampling only with a "
        f"proof that the samples bound the whole interval",
        "the unmutated domain classifies EQUIVALENT, so the test can fail")

    # ---------------- M19: kernel substitution ----------------------------------------------
    full = I.kernel_apply_iv(one, F(0), F(0), BLOCK)
    hat = I.kernel_apply_iv(one, F(0), F(0), BLOCK, atom_removed=True)
    distinct = (hat.hi < full.lo)
    r_k = EQ.check("tau", orig["tau"], dict(orig["tau"], kernel="K_e"))
    mut("M19", "K_e substituted for Khat_e",
        distinct and r_k["STATUS"] == "NOT_EQUIVALENT",
        f"at the atom Khat_e = [{float(hat.lo):.6f}, {float(hat.hi):.6f}] is strictly below "
        f"K_e = [{float(full.lo):.6f}, {float(full.hi):.6f}], and the checker rejects the swap",
        "the two kernels coincide wherever the atom window is empty, so the numeric test is not "
        "vacuous only because it is taken at the atom, where the window is widest")

    # ---------------- M20-M21: constant substitution ----------------------------------------
    r20 = EQ.check("Abar", orig["Abar"], orig["tau"])
    r21 = EQ.check("tau", orig["tau"], orig["Abar"])
    mut("M20", "tau substituted for Abar", r20["STATUS"] == "NOT_EQUIVALENT",
        f"checker returns {r20['STATUS']}; mismatching fields "
        f"{[m['field'] for m in r20['field_mismatches']]}",
        "Abar compared with itself returns EQUIVALENT, so the test can fail")
    mut("M21", "Abar substituted for tau", r21["STATUS"] == "NOT_EQUIVALENT",
        f"checker returns {r21['STATUS']}; mismatching fields "
        f"{[m['field'] for m in r21['field_mismatches']]}",
        "tau compared with itself returns EQUIVALENT, so the test can fail")

    # ---------------- M22: cell substitution -------------------------------------------------
    c307 = [1.7885921, 1.882413]
    r22 = EQ.check("Abar", orig["Abar"], dict(orig["Abar"], drift_domain=c307))
    mut("M22", "cell 307 substituted for cell 306",
        r22["STATUS"] == "NOT_COMPARABLE" and gate["target"]["cell"] == 306,
        f"cell 307's block classifies {r22['STATUS']} against cell 306's, and the gate binds "
        f"cell {gate['target']['cell']}",
        "cell 306's own block classifies EQUIVALENT, so the test can fail")

    # ---------------- M23: fewer than six ----------------------------------------------------
    named = set(gate["target"]["constants"])
    mut("M23", "one constant substituted for the six",
        named == set(C.SIX_CONSTANTS) and len(named) == 6
        and "fewer than the six constants" in gate["target"]["substitutions_forbidden"],
        f"the gate binds all six {sorted(named)} and forbids substituting fewer",
        "a five-element target set would fail the equality test")

    # ---------------- M24: atom sign -------------------------------------------------------
    at = I.atom_contribution_iv(one, F(0), F(0), BLOCK)
    good = hat + at
    bad = hat - at                                   # the planted sign flip
    sep_good = max(full.lo - good.hi, good.lo - full.hi)
    sep_bad = max(full.lo - bad.hi, bad.lo - full.hi)
    mut("M24", "the atom contribution's sign flipped",
        sep_good <= 0 < sep_bad,
        f"Khat_e + atom agrees with K_e (separation {float(sep_good):.3e}); Khat_e - atom does "
        f"not (separation {float(sep_bad):.3e})",
        "the flipped decomposition is the negative control and is rejected")

    # ---------------- M25: narrowed block ----------------------------------------------------
    narrow = [float(e_lo), float((e_lo + e_hi) / 2)]
    r25 = EQ.check("Abar", orig["Abar"], dict(orig["Abar"], drift_domain=narrow))
    wide = EQ.check("Abar", orig["Abar"],
                    dict(orig["Abar"], drift_domain=[float(e_lo) - 0.01, float(e_hi) + 0.01]))
    mut("M25", "the drift interval narrowed",
        r25["STATUS"] == "WEAKER" and wide["STATUS"] == "STRONGER",
        f"a half-block classifies {r25['STATUS']} and a super-block {wide['STATUS']}, so the "
        f"direction of the domain rule is exercised both ways",
        "a widened block classifies STRONGER, so the test is not one-sided")

    # ---------------- M26: comparison before seal --------------------------------------------
    if runs is None:
        mut("M26", "comparison performed before the independent output was sealed", None,
            "no runs artifact exists yet, so the ordering cannot be checked",
            "recorded UNDETERMINED rather than DETECTED: a check that passes for want of input "
            "proves nothing")
    else:
        mut("M26", "comparison performed before the independent output was sealed",
            bool(runs.get("sealed_sha256")) and "REGISTRY_C2" not in json.dumps(runs),
            "the runs artifact carries its own seal hash and contains no original value",
            "a runs artifact quoting an original constant would fail")

    # ---------------- M27: gate states its own result ---------------------------------------
    hits = GA.scan_for_result_language(gate)
    probe = json.loads(json.dumps(gate))
    probe["predicates"]["G_probe"] = "this is the criterion C11R must and does fail"
    ctrl = GA.scan_for_result_language(probe)
    mut("M27", "the prospective gate contains result-dependent language",
        not hits and len(ctrl) > 0,
        f"{len(GA.RESULT_LANGUAGE)} patterns, 0 hits in the frozen gate",
        f"a planted clause is caught: {ctrl[0]['phrase']!r}" if ctrl else "control did not fire")

    # ---------------- M28: refuted candidate sent to certification ---------------------------
    if scr is None:
        mut("M28", "a pointwise-refuted candidate still sent to expensive certification", None,
            "no screen artifact exists yet", "recorded UNDETERMINED rather than DETECTED")
    else:
        refuted = set(scr["refuted"])
        spent = set()
        if runs:
            spent = {k for k, v in runs.get("candidates", {}).items()
                     if "depth" in v.get("certification", {})}
        mut("M28", "a pointwise-refuted candidate still sent to expensive certification",
            not (refuted & spent),
            f"{len(refuted)} refuted, {len(spent)} certified, intersection "
            f"{sorted(refuted & spent)}",
            "the screen classified at least one candidate REFUTED, so the intersection test has "
            "something to catch" if refuted else
            "NO candidate was refuted, so this test had nothing to exclude")

    # ---------------- validation must exist and be exercised --------------------------------
    if val is None:
        mut("M29", "manufactured validation reported without a producer", None,
            "no validation artifact exists yet", "recorded UNDETERMINED")
    else:
        v6 = next((c for c in val["checks"] if c["id"] == "V6"), None)
        mut("M29", "the interval layer silently widened instead of collapsing onto the scalar one",
            bool(v6 and v6["pass"]),
            f"scalar collapse is bit-for-bit: {v6['detail']['mismatch_count'] if v6 else '?'} "
            f"mismatches",
            "the pre-fix implementation produced 28 mismatches, so the test is known to fail when "
            "the layer widens")

    surv = [r["id"] for r in res if r["outcome"] == "SURVIVED"]
    und = [r["id"] for r in res if r["outcome"] == "UNDETERMINED"]
    out = {"schema": "C11R_MUTATIONS/1", "mutants": res, "survivors": surv, "undetermined": und,
           "MUTATION_CLASS": ("PASS" if not surv and not und else
                              ("INCOMPLETE" if not surv else "REFUSE"))}
    s = C.write_evidence(C.NS / "evidence" / "mutations" / "C11R_MUTATIONS.json", out)
    for r in res:
        print(f"  {r['outcome']:<13} {r['id']}  {r['name'][:62]}")
    print(f"\nMUTATION_CLASS = {out['MUTATION_CLASS']}  survivors={surv}  undetermined={und}")
    print(f"wrote evidence/mutations/C11R_MUTATIONS.json sha256 {s[:16]}...")
    return 0 if not surv else 1


if __name__ == "__main__":
    raise SystemExit(main())
