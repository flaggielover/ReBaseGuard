"""C11R Phase 1 -- the exact N9 statement table, reconstructed mechanically.

Authoritative for the whole campaign. No implementation starts until every field is resolved; any
unresolved field is a HARD STOP. Every value is read from committed sources: the original certifier
`taboo_certify.py`, REGISTRY_C2, and the C2 adjudication that words N9.

REVISION 2 (erratum E8): the table is SPLIT. Revision 1 wrote the six original magnitudes beside
the semantics, and c11r_screen.py -- a module that influenced candidate selection -- read them from
here and printed them. Now:
  * evidence/table/C11R_N9_STATEMENTS.json carries SEMANTICS ONLY and contains no magnitude;
  * evidence/quarantine/C11R_ORIGINAL_MAGNITUDES.json carries the six values, and exactly two
    modules may load it: this one, which extracts them, and the post-seal comparator.
This module reads the registry, so it is one of the two magnitude-aware modules, but it prints no
magnitude and writes none into the statement table. c11r_firewall.py proves the separation by AST.

The single most important thing this table records is that the six constants are NOT six instances
of one statement. They come from THREE different producers proving THREE different propositions,
and two of them are CONDITIONAL on the other two.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_common as C
import c11r_schema as S

CELL = C.TARGET_CELL
unresolved: list[str] = []


def need(field: str, value, why: str = ""):
    if value in (None, "", [], {}):
        unresolved.append(f"{field}: {why or 'unresolved'}")
    return value


LEAK_METHOD = ("each original magnitude as its exact rational string, and as a decimal ROUNDED and "
               "TRUNCATED to 4, 5, 6, 7 and 8 places; each pattern is left-bounded so that it cannot "
               "match inside a longer number (12.3456 does not match 2.3456)")


def leak_patterns(magnitudes: dict) -> dict:
    """constant -> compiled patterns for its value. Built only inside this sanctioned module."""
    import re
    from decimal import Decimal, ROUND_DOWN, ROUND_HALF_EVEN
    pats = {}
    for k, mv in magnitudes.items():
        exact = F(mv["value"])
        forms = {mv["value"]}
        d = Decimal(exact.numerator) / Decimal(exact.denominator)
        for n in range(4, 9):
            q = Decimal(1).scaleb(-n)
            forms.add(str(d.quantize(q, rounding=ROUND_HALF_EVEN)))
            forms.add(str(d.quantize(q, rounding=ROUND_DOWN)))
        pats[k] = [re.compile(r"(?<![0-9])" + re.escape(f)) for f in sorted(forms)]
    return pats


def scan_text(text: str, pats: dict) -> dict:
    """constant -> number of matches. Returns counts only; never the matched text."""
    out = {}
    for k, ps in pats.items():
        n = sum(len(p.findall(text)) for p in ps)
        if n:
            out[k] = n
    return out


def leak_check() -> int:
    """Scan every allowlisted pre-result artifact and every campaign module for original values.

    Run by c11r_regen.py after the mutation suite. The magnitudes are loaded HERE, in the
    sanctioned extractor, and never leave it: the artifact records only per-file match counts.
    The historical review files are not scanned -- they are immutable evidence known to quote
    rounded originals -- and the firewall forbids any production module from reading them.
    """
    q = C.load(C.NS / C.QUARANTINE_REL)
    pats = leak_patterns(q["magnitudes"])
    files = []
    for rel in C.PRE_RESULT_ARTIFACTS:
        if rel in ("evidence/leakcheck/C11R_LEAKCHECK.json", "evidence/status/C11R_STATUS.json"):
            continue
        path = C.NS / rel
        if path.exists():
            files.append(path)
    closure = {}
    for m in sorted(C.HERE.glob("c11r_*.py")):
        closure.update(C.code_closure(m))
    files += [C.REPO / rel for rel in sorted(closure)]
    rows, total = [], 0
    for path in files:
        text = path.read_text()
        hits = scan_text(text, pats)
        n = sum(hits.values())
        total += n
        rows.append({"file": str(path.relative_to(C.REPO)), "sha256": C.sha256_file(path),
                     "matches": n, "constants_matched": sorted(hits)})
    # the declared external input every pre-comparison module may read (the r5 coverage map)
    for ext in C.DECLARED_EXTERNAL_INPUTS:
        hits = scan_text(C.git("show", f"HEAD:{ext}"), pats)
        n = sum(hits.values())
        total += n
        rows.append({"file": ext, "git_object": C.git("rev-parse", f"HEAD:{ext}"),
                     "matches": n, "constants_matched": sorted(hits)})
    # DISCLOSURE, not part of the class: this campaign's own commit messages. They are history
    # (never rewritten) and no production module reads them; any match is reported, not hidden.
    msgs = C.git("log", "--format=%H%n%B%n----", f"{C.C11_HEAD}..HEAD")
    msg_hits = scan_text(msgs, pats)
    out = {"schema": "C11R_LEAKCHECK/1",
           "method": LEAK_METHOD,
           "scope": ("every allowlisted pre-result artifact produced before this step, and every "
                     "module in the campaign's code closure"),
           "not_scanned": ["the historical review files (immutable, known to quote rounded "
                           "originals; no production module may read them)",
                           "the quarantine itself", "this artifact and the status report"],
           "files": rows, "files_scanned": len(rows), "total_matches": total,
           "disclosure_commit_messages_since_C11": {
               "commits": len([x for x in C.git("rev-list", f"{C.C11_HEAD}..HEAD").splitlines()
                               if x]),
               "matches": sum(msg_hits.values()), "constants_matched": sorted(msg_hits),
               "counts_toward_class": False},
           "LEAK_CLASS": "PASS" if total == 0 else "REFUSE"}
    sh = C.write_evidence(C.NS / "evidence" / "leakcheck" / "C11R_LEAKCHECK.json", out,
                          producer=__file__)
    bad = [r for r in rows if r["matches"]]
    for r in bad:
        print(f"  LEAK  {r['file']}  constants {r['constants_matched']}  ({r['matches']} matches)")
    print(f"leak check: {len(rows)} files, {total} matches -> LEAK_CLASS = {out['LEAK_CLASS']}")
    print(f"disclosure: commit messages since C11 carry {sum(msg_hits.values())} matches "
          f"{sorted(msg_hits)}")
    print(f"wrote evidence/leakcheck/C11R_LEAKCHECK.json sha256 {sh[:16]}...")
    return 0 if total == 0 else 1


def main() -> int:
    src = (C.REPO / C.ORIGINAL_CERTIFIER).read_text()
    reg = C.load(C.C2 / "evidence" / "registry_c2" / "REGISTRY_C2.json")
    blk = {b["cell"]: b for b in reg["blocks"]}[CELL]
    rows = blk["sub_rows"]

    # ---- the drift domain, resolved from the registry, NOT from prose ----------------------
    e_lo, e_hi = F(blk["e_lo"]), F(blk["e_hi"])
    e0, rho = F(blk["e0"]), F(blk["rho"])
    sub = [(F(r["e_lo"]), F(r["e_hi"])) for r in rows]
    contiguous = all(sub[i][1] == sub[i + 1][0] for i in range(len(sub) - 1))
    covers = sub[0][0] == e_lo and sub[-1][1] == e_hi
    centred = (e0 - rho == e_lo) and (e0 + rho == e_hi)

    drift = {
        "cell": CELL,
        "e_lo": str(e_lo), "e_hi": str(e_hi),
        "e_lo_float": float(e_lo), "e_hi_float": float(e_hi),
        "width": float(e_hi - e_lo),
        "e0": str(e0), "rho": str(rho),
        "midpoint_form_matches_block": centred,
        "sub_blocks": len(sub),
        "sub_block_max_width": reg["sub_block_max_width"],
        "sub_blocks_contiguous": contiguous,
        "sub_blocks_cover_exactly": covers,
        "sub_block_bounds": [[str(a), str(b)] for a, b in sub],
        "CAMPAIGN_INSTRUCTION_DISCREPANCY": {
            "instruction_quoted": "[1.7885921, 1.882413]",
            "that_interval_is": "cell 307's block, not cell 306's",
            "cell_306_actual": [float(e_lo), float(e_hi)],
            "why_confusable": ("the blocks are adjacent -- cell 307's e_lo equals cell 306's e_hi "
                              "exactly (17885921/10000000), so the quoted pair is 306's upper "
                              "endpoint followed by 307's upper endpoint"),
            "resolution": ("the campaign states the target is cell 306 repeatedly and forbids "
                           "substituting 307, so the governing interval is cell 306's own block "
                           "read from REGISTRY_C2. The quoted numbers are treated as a carry-over "
                           "from the C11 report, which discussed 307."),
            "resolved_without_stop": True},
    }
    need("drift.contiguous", contiguous or None, "sub-blocks do not tile the cell block")
    need("drift.covers", covers or None, "sub-blocks do not cover the cell block exactly")

    # ---- the three propositions, quoted from the original certifier ------------------------
    def grab(pat):
        m = re.search(pat, src, re.S)
        return re.sub(r"\s+", " ", m.group(1)).strip() if m else None

    stmt_taboo = need("statement.taboo", grab(
        r'"for every e in \[e_lo, e_hi\]: w >= 1 \+ Khat_e w on X, hence (.*?)"\)\}'),
        "Lemma T statement string not found")
    stmt_full = need("statement.full", grab(
        r'"(for every e in \[e_lo, e_hi\]: w >= 1 \+ K_e w on X.*?)"\s*if full'),
        "full-kernel statement string not found")
    stmt_cell = need("statement.cell", grab(
        r'"statement": "(for every e in \[e0 - rho, e0 \+ rho\].*?)"\}'),
        "cell statement string not found")

    # ---- the atom split, recovered from the code rather than assumed -----------------------
    atom_skip = grab(r"(if beta < alpha and a >= beta - 1e-15 and b <= alpha \+ 1e-15:)")
    atom = {
        "atom_state": "a = (p, m) = (0, 0)",
        "evidence_in_code": "dv = {k: bi_eval(P[k], arb(0), arb(0)) ...}  -- evaluated at (0, 0)",
        "atom_z_window": "[beta, alpha] = [m - K, K - p]",
        "window_nonempty_iff": "m - K < K - p, i.e. p + m < 2K = 1",
        "meaning": ("the z-window on which BOTH arms clamp to zero, so the chain lands exactly on "
                    "the atom; Khat_e is K_e with that piece removed"),
        "removal_in_code": need("atom.removal", atom_skip, "atom-skip branch not located"),
        "decomposition_to_recover": "K_e = Khat_e + (atom contribution); sign and normalisation "
                                    "MUST be recovered by test, not assumed",
    }

    # ---- the six constants ------------------------------------------------------------------
    U, L = "UPPER_BOUND", "LOWER_BOUND"
    common_block = {"drift_domain": f"[{e_lo}, {e_hi}] block-uniform",
                    "drift_domain_float": [float(e_lo), float(e_hi)]}

    consts = {
        "C_T": {
            "producer": "taboo_certify.certify_block", "mode": "full=False", "kernel": "Khat_e",
            "proposition": "w >= 1 + Khat_e w on X, uniformly on the e-block",
            "quantity": "C_T = sup over the reachable set R of w",
            "bounds": "the induced sup-norm of the taboo resolvent: ||Ghat_e|| <= C_T",
            "state_convention": "supremum over R, not a point value",
            "norm": "sup-norm on the reachable set R",
            "direction": U, "alpha": rows[0]["taboo_alpha"],
            "artifacts": sorted({r["taboo_artifact_sha256"] for r in rows}),
            "aggregation": "max over the 9 sub-blocks",
            "value": blk["C_T"], "value_float": float(F(blk["C_T"])),
            "depends_on": []},
        "tau": {
            "producer": "taboo_certify.certify_block", "mode": "full=False", "kernel": "Khat_e",
            "proposition": "w >= 1 + Khat_e w on X, uniformly on the e-block",
            "quantity": "tau = w(a), the same supersolution evaluated at the atom",
            "bounds": "(Ghat_e 1)(a) <= tau",
            "state_convention": "point value at the atom a = (0, 0)",
            "norm": "point evaluation",
            "direction": U, "alpha": rows[0]["taboo_alpha"],
            "artifacts": sorted({r["taboo_artifact_sha256"] for r in rows}),
            "aggregation": "max over the 9 sub-blocks",
            "value": blk["tau"], "value_float": float(F(blk["tau"])),
            "depends_on": []},
        "Abar": {
            "producer": "taboo_certify.certify_block", "mode": "full=True", "kernel": "K_e",
            "proposition": "w >= 1 + K_e w on X, uniformly on the e-block",
            "quantity": "Abar = w(a)",
            "bounds": "E_a[tau] <= Abar -- the ARL at the atom",
            "state_convention": "point value at the atom a = (0, 0)",
            "norm": "point evaluation",
            "direction": U, "alpha": blk["arl"]["arl_alpha"],
            "artifacts": [blk["arl"]["arl_artifact_sha256"]],
            "aggregation": "single cell-level artifact (not sub-blocked)",
            "value": blk["Abar"], "value_float": float(F(blk["Abar"])),
            "depends_on": [],
            "THIS_IS_WHAT_C11_PROVED": True},
        "D_lo": {
            "producer": "taboo_certify.certify_cell", "mode": "n/a", "kernel": "Khat_e",
            "proposition": "d = Ghat h_1 ; D_e = d(a) = P_a(tau < T_a)",
            "quantity": "D_lo, a LOWER bound on D_e",
            "bounds": "D_e >= D_lo for every e in the block",
            "state_convention": "point value at the atom a = (0, 0)",
            "norm": "point evaluation",
            "direction": L, "alpha": None,
            "artifacts": sorted({r["denominator_artifact_sha256"] for r in rows}),
            "aggregation": "min over the 9 sub-blocks",
            "value": blk["D_lo"], "value_float": float(F(blk["D_lo"])),
            "depends_on": ["C_T", "tau"]},
        "D1": {
            "producer": "taboo_certify.certify_cell", "mode": "n/a", "kernel": "Khat_e",
            "proposition": "d' = Ghat (Khat' d + h_1') ; derivative with respect to the DRIFT e",
            "quantity": "D1, an UPPER bound on |D_e'|",
            "bounds": "|D_e'| <= D1 for every e in the block",
            "state_convention": "point value at the atom a = (0, 0)",
            "norm": "absolute value, point evaluation",
            "direction": U, "alpha": None,
            "artifacts": sorted({r["denominator_artifact_sha256"] for r in rows}),
            "aggregation": "max over the 9 sub-blocks",
            "value": blk["D1"], "value_float": float(F(blk["D1"])),
            "depends_on": ["C_T", "tau"]},
        "D2": {
            "producer": "taboo_certify.certify_cell", "mode": "n/a", "kernel": "Khat_e",
            "proposition": "d'' = Ghat (Khat'' d + 2 Khat' d' + h_1'') ; second drift derivative",
            "quantity": "D2, an UPPER bound on |D_e''|",
            "bounds": "|D_e''| <= D2 for every e in the block",
            "state_convention": "point value at the atom a = (0, 0)",
            "norm": "absolute value, point evaluation",
            "direction": U, "alpha": None,
            "artifacts": sorted({r["denominator_artifact_sha256"] for r in rows}),
            "aggregation": "max over the 9 sub-blocks",
            "value": blk["D2"], "value_float": float(F(blk["D2"])),
            "depends_on": ["C_T", "tau"]},
    }
    magnitudes = {}
    for k, v in consts.items():
        v.update(common_block)
        magnitudes[k] = {"value": v.pop("value"), "value_float": v.pop("value_float")}
        need(f"{k}.value", magnitudes[k]["value"])
        need(f"{k}.artifacts", v["artifacts"])
        need(f"{k}.direction", v["direction"])
        if v["direction"] != S.DIRECTION[k] or v["kernel"] != S.KERNEL[k]:
            unresolved.append(f"{k}: table semantics disagree with c11r_schema")

    # ---- the ORIGINAL's six statement records, in the shared schema --------------------------
    orig_file_sha = C.sha256_file(C.REPO / C.ORIGINAL_CERTIFIER)
    original_statements = {}
    for k in S.SIX_CONSTANTS:
        v = consts[k]
        cell_route = v["producer"].endswith("certify_cell")
        if k == "Abar":
            agg = {"method": "single_certificate_whole_block", "sub_blocks": 1,
                   "artifacts": v["artifacts"]}
        else:
            agg = {"method": ("min_over_sub_blocks" if v["direction"] == "LOWER_BOUND"
                              else "max_over_sub_blocks"),
                   "sub_blocks": len(rows), "artifacts": v["artifacts"]}
        original_statements[k] = S.statement(
            k, drift_domain=(str(e_lo), str(e_hi)), aggregation=agg,
            dependencies=S.ROUTE_REQUIRED_DEPENDENCIES[
                "original_certify_cell" if cell_route else "original_certify_block"],
            producer={"module": v["producer"], "file": C.ORIGINAL_CERTIFIER,
                      "file_sha256": orig_file_sha,
                      "route": "original_certify_cell" if cell_route
                               else "original_certify_block",
                      "mode": v["mode"]})
        if cell_route:
            original_statements[k]["dependency_granularity"] = (
                "PER SUB-BLOCK: each of the 9 certify_cell artifacts was run with its OWN "
                "sub-block's C_T and tau (verified 9/9 by content hash in the pre-freeze review, "
                "item 2). A block-uniform C_T/tau pair is also sound, since the propagation is "
                "increasing in both.")

    # the aggregation rule must be verified, not asserted
    agg_ok = {}
    for k, fn in (("C_T", max), ("tau", max), ("D1", max), ("D2", max), ("D_lo", min)):
        agg_ok[k] = F(blk[k]) == fn(F(r[k]) for r in rows)
    need("aggregation", all(agg_ok.values()) or None, f"aggregation mismatch: {agg_ok}")

    # ---- comparison semantics, frozen here BEFORE any independent value exists --------------
    comparison = {
        "factor": 2,
        "UPPER_BOUND": {
            "STRONGER": "independent <= original",
            "AGREES": "original < independent <= 2 * original",
            "INSUFFICIENT": "independent > 2 * original"},
        "LOWER_BOUND": {
            "STRONGER": "independent >= original",
            "AGREES": "original / 2 <= independent < original",
            "INSUFFICIENT": "independent < original / 2"},
        "why_the_asymmetry_matters": (
            "D_lo is the only LOWER bound of the six. For an upper bound a smaller independent "
            "value is stronger; for a lower bound a larger one is. Applying the upper-bound rule "
            "to D_lo would invert the verdict, so the direction field is load-bearing and is "
            "frozen here, before any independent value exists."),
        "statement_precedence": (
            "SAME STATEMENT BEFORE SAME NUMBER. A numerically agreeing value certified over a "
            "narrower drift domain, at a scalar drift, on the wrong kernel, or at the wrong state "
            "does NOT count as agreement at any factor."),
    }

    dependency_finding = {
        "finding": ("the six constants are not six instances of one statement. D_lo, D1 and D2 are "
                    "CONDITIONAL on C_T and tau -- the cell certificate's own statement says so "
                    "verbatim: 'given ||Ghat_e|| <= C_T and (Ghat_e 1)(a) <= tau on the same set'."),
        "consequence_for_independence": (
            "an independent certifier cannot produce D_lo, D1 or D2 by feeding in the ORIGINAL's "
            "C_T and tau -- that would consume the original's outputs and violate the independence "
            "N9 exists to establish. It must first certify its own C_T and tau via Khat_e, then "
            "propagate with those."),
        "ordering_forced": ["Khat_e supersolution -> C_T, tau",
                            "K_e supersolution -> Abar",
                            "independent C_T, tau -> D_lo, D1, D2"],
        "additional_machinery_D_requires": [
            "drift derivatives of the kernel, Khat' and Khat'' (Hermite-weighted densities)",
            "closed forms of h_1, h_1' and h_1''",
            "operator norm bounds kernel_norm(0..3)",
            "a residual-to-error propagation theorem (the lambda/prop machinery)",
            "sup_source_derivative bounds"],
    }

    out = {"schema": "C11R_N9_STATEMENTS/1",
           "supersedes": "C11R_N9_TABLE/1 (38f59993), which mixed magnitudes with semantics",
           "authoritative_for": "the whole C11R campaign",
           "CONTAINS_NO_ORIGINAL_MAGNITUDE": True,
           "N9_wording": {
               "source": "p5y_k5_tail_c2_closure/evidence/adjudication/C2_ADJUDICATION.md:501",
               "text": ("a second, independently written certifier reproducing the six operator "
                        "constants for cell 306 (closing N9)"),
               "scope_note": ("the disposition file OPEN_NOTES_DISPOSITION_C2.md frames the trust "
                              "surface as the SUPERSOLUTIONS, which produce only C_T, tau and "
                              "Abar; D_lo, D1 and D2 come from certify_cell. The adjudicator's "
                              "'six' governs closure, so the six-constant requirement is WIDER "
                              "than the surface the disposition file names (pre-freeze review, "
                              "item 1)."),
               "target_cell": CELL, "constant_count": 6},
           "original_certifier": {"path": C.ORIGINAL_CERTIFIER, "sha256": orig_file_sha,
                                  "registry_recorded_sha256": reg["code_sha256"]["taboo_certify"]},
           "drift_domain": drift,
           "state_set": S.STATE_SET_R,
           "atom_convention": atom,
           "propositions": {"taboo_full_false": stmt_taboo, "full_true": stmt_full,
                            "cell": stmt_cell},
           "constants": consts,
           "original_statements": original_statements,
           "aggregation_verified": agg_ok,
           "comparison_semantics_frozen_before_results": comparison,
           "DEPENDENCY_FINDING": dependency_finding,
           "unresolved_fields": unresolved,
           "TABLE_CLASS": "RESOLVED" if not unresolved else "HARD_STOP"}
    # The quarantine is written FIRST, so that the statement table can record its content-free id.
    # Later modules verify the quarantine by that id (git hash-object) without reading it.
    quarantine = {"schema": "C11R_ORIGINAL_MAGNITUDES/1",
                  "QUARANTINE": ("the six original magnitudes for cell 306. Loadable ONLY by "
                                 "c11r_table.py (which extracts them) and c11r_compare.py (after "
                                 "the independent outputs are sealed). c11r_firewall.py enforces "
                                 "this by AST."),
                  "cell": CELL, "magnitudes": magnitudes,
                  "source": "p5y_k5_tail_c2_closure/evidence/registry_c2/REGISTRY_C2.json"}
    q = C.write_evidence(C.NS / C.QUARANTINE_REL, quarantine, producer=__file__)
    out["quarantine"] = {"path": C.QUARANTINE_REL,
                         "content_free_id": C.content_free_id(C.NS / C.QUARANTINE_REL),
                         "note": ("verify with c11r_common.content_free_id; never read it")}

    # VALUE-BASED LEAK CHECK of the statement table, here because this module already holds the
    # magnitudes legitimately. `--leak-check` runs the same scan over EVERY allowlisted artifact
    # and every campaign module at the end of the regeneration.
    hits = scan_text(json.dumps(out, sort_keys=True), leak_patterns(magnitudes))
    if hits:
        raise SystemExit(f"REFUSE: original magnitudes would leak into the statement table: "
                         f"{sorted(hits)}")
    out["leak_check"] = {"method": LEAK_METHOD, "magnitudes_found": 0}
    s = C.write_evidence(C.NS / "evidence" / "table" / "C11R_N9_STATEMENTS.json", out,
                         producer=__file__)

    print(f"drift domain (cell {CELL}) = [{e_lo}, {e_hi}]  width {e_hi - e_lo}, "
          f"{len(sub)} sub-blocks, contiguous={contiguous}")
    print(f"  NOTE: the campaign quoted [1.7885921, 1.882413] -- that is CELL 307's block.\n")
    print(f"{'constant':6s} {'producer':16s} {'mode':11s} {'kernel':8s} {'dir':12s} depends_on")
    for k in S.SIX_CONSTANTS:
        v = consts[k]
        print(f"{k:6s} {v['producer'].split('.')[-1]:16s} {v['mode']:11s} {v['kernel']:8s} "
              f"{v['direction']:12s} {original_statements[k]['dependencies']}")
    print("  (magnitudes are NOT printed; they are written only to the quarantine artifact)")
    print(f"\nTABLE_CLASS = {out['TABLE_CLASS']}   unresolved = {unresolved}")
    print(f"wrote evidence/table/C11R_N9_STATEMENTS.json sha256 {s[:16]}...")
    print(f"wrote evidence/quarantine/C11R_ORIGINAL_MAGNITUDES.json sha256 {q[:16]}...")
    return 0 if not unresolved else 1


if __name__ == "__main__":
    raise SystemExit(leak_check() if "--leak-check" in sys.argv[1:] else main())
