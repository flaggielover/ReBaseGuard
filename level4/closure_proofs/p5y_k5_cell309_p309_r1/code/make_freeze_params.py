"""Build freeze/P309_FREEZE.json: the frozen parameters of P309 package 1 (package rev. 2b section A, as amended by
rev. 2c), with every governing document pinned by git blob, and the review conditions and the U2 proposition carried
verbatim.  Deterministic (no timestamps): the same tree gives the same bytes.

  python3 code/make_freeze_params.py [--check]

Post-grant derivations (not choices; each has a frozen rule): the cell interval (from the pinned cells.json), Ew (the
outward 2^-10 hull of the cell), the execution-host binding (the host the owner names; QC10 re-run there if it is not
the proposed host) and the grant's expiry.  They are named in `post_grant_derivations` and are the only values not
fixed by this file.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

FNS = Path(__file__).resolve().parents[1]
REPO = FNS.parents[2]
sys.path.insert(0, str(FNS / "code"))
import p309_guard as G  # noqa: E402

NS = "level4/closure_proofs/p5y_k5_cell309_p309_r1/"
RNS = "level4/closure_proofs/p5y_k5_cell309_research_r1/"
OUT = FNS / "freeze" / "P309_FREEZE.json"
DOCS = {
    "protocol_rev2b": RNS + "protocol_prep/P309_PROTOCOL.md",
    "formal_package_rev2b": RNS + "protocol_prep/P309_FORMAL_PACKAGE.md",
    "review_briefs_rev2b": RNS + "protocol_prep/P309_REVIEW_BRIEFS.md",
    "owner_decisions_package_rev2b": RNS + "protocol_prep/P309_OWNER_DECISIONS.md",
    "theorem_srk": RNS + "theory/THEOREM_SRK.md",
    "srk_cert_spec": RNS + "impl/SRK_CERT_SPEC.md",
    "route_selection_rule": RNS + "registry/ROUTE_SELECTION_RULE.md",
    "amendments_rev2c": NS + "governance/P309_REV2C_AMENDMENTS.md",
    "fc2_spec_r2": NS + "fc2/FC2_SPEC_R2.md",
    "fc2_spec_r2_erratum_1": NS + "fc2/FC2_SPEC_R2_ERRATUM_1.md",
    "u2_corrected_proposition_r2": NS + "governance/U2_CORRECTED_PROPOSITION_R2.md",
    "owner_decisions_verbatim": NS + "governance/OWNER_DECISIONS_P309_VERBATIM.md",
    "owner_rulings_2_verbatim": NS + "governance/OWNER_RULINGS_2_P309_VERBATIM.md",
    "owner_d5_ratification_verbatim": NS + "governance/OWNER_D5_RATIFICATION_P309_VERBATIM.md",
    "d5_ratification_request": NS + "governance/D5_OWNER_RATIFICATION_REQUEST_P309.md",
    "formal_quarantine": NS + "config/FORMAL_QUARANTINE_P309.json",
    "scanner_allowance": NS + "config/SCANNER_ALLOWANCE_P309.json",
    "errata_formal": NS + "governance/ERRATA_FORMAL_P309.md",
    "briefs_recovered": NS + "governance/briefs_recovered/README.md",
    "incident_p309f_01": NS + "governance/INCIDENT_P309F_01_FC2_REV1_INSTRUCTION.md",
    "no_placeholder_statement": NS + "governance/NO_PLACEHOLDER_STATEMENT_P309.md",
}
# the disclosed liabilities (carried verbatim into the proposed grant); delta review D3 adds its section 5 items
DISCLOSED_LIABILITIES = [
    "overnight incidents 01-03 (2026-09-27 UTC) and residues", "309R1-01 (qualitative mental proxy: TPT at 309)",
    "309R1-02 (mental in-band estimate; SRK)", "309R1-03 (refused in-band probe; NONE)",
    "309R1-04 (premature drafting; LOW)", "ERRATA E-3", "ERRATA E-17(a)", "ERRATA E-18 and the manifest-generator runs",
    "the ledgered necessary reads (research and formal exposure ledgers)",
    "SRK motivation provenance MEDIUM-HIGH (upper end); RLR MEDIUM (knockout known)",
    "rule choices with direction: exceptions -> INDETERMINATE (against closure); budget exhaustion -> fallback and "
    "6 -> 48 CPU-h (toward closure); Stage-1b fallback to S_I1 (toward closure)",
    "briefs not committed before issue (C5; recovered verbatim, content not timing)",
    "zero computed target-equivalent proxies; one qualitative mental proxy exposure (309R1-01) and one mental in-band "
    "estimate (309R1-02) (formal errata FE-4)",
    "the formal errata FE-1..FE-8", "host dependence of the Stage-1a outcome when the budget binds",
    "rev. 2c closure-relevant changes with direction (delta review section 5): A4 toward closure (restores "
    "executability); E1-1 toward closure (prevents a silent SRK loss); A6 toward a conclusive outcome (no wall cap; wall "
    "time unbounded); A5 a new parameter, efficacy-relevant, ambiguous direction, the maximal per-job limit 21 600 s "
    "(corrected per D2); A14 host speed is efficacy-relevant",
    "the reader-A brief (2026-09-29 12:59:21Z, before 309R1-01 and THEOREM_SRK) solicited the terms identified "
    "(qualitatively) as dominant for 309 by committed records: the 309-specific qualitative dominance behind SRK was "  # q309: literal-ok (disclosure text)
    "solicited (delta review section 4)",
    "incident P309F-01: the FC2(b) rev-1 brief (2026-09-30 01:49:53Z) instructed an in-band synthetic test band and the "
    "REAL names in a sandbox; never executed; withdrawn by FC2_SPEC_R2 and owner rulings 2; liability NONE",
    "the verifier author's rev-1 read-only inspections, ledgered only retrospectively (ZTL lines 7-8; FE-6)",
    "FE-8: before the freeze, a QC11 development run found that Stage 1b could not load the pinned certifier in execute "
    "(it would have made every execution INDETERMINATE); repaired by an isolated load (toward a conclusive outcome; no "
    "rule, parameter or binding changed)",
    "delta result-chasing component LOW-MEDIUM; the route's overall rating unchanged: MEDIUM-HIGH, upper end",
    "the independent pre-freeze review R4 was FREEZE_BLOCKED (B1-B8: the cell taken from the grant; post-seal checks "
    "that would fail a correct run; post-marker-only grant checks; SIGKILL as fallback; an impossible grant window; "
    "unsealed verdict reasons; QC blind spots; retry-until-pass); resolved before the freeze by rev. 2c A20-A30 and "
    "re-reviewed (R4 follow-up); FE-9 (cells.json endpoint form)",
    "owner D5: the two production mutation sites (_arm_marker, _persist_pending) and the pending-ref NAME were "
    "ratified to EXIST in the frozen tree (not to be used before the grant); scanner schema 3 rejects every other "
    "ref-moving path; independently verified",
    "second-delta rule choices with direction (delta-2 review E9(a)): A20 against an invalid closure; A21 toward a "
    "conclusive outcome, 14-day minimum horizon, residual mid-run expiry for runs longer than the horizon; A22 "
    "against closure in a failure case (including E2: a SIGXCPU below the CPU limit is a job exception); A25 toward a "
    "conclusive outcome; A26 and A28 against closure in a failure case; A27 no retry (a failed or interrupted single "
    "attempt ends the campaign); A23 and A24 neutral",
    "FE-9's pre-freeze in-memory parse of the target cell interval (and of cells 305-309), no value displayed: a "
    "departure from C4's letter (delta-2 E3)",
    "QC11 I03 read the cell-307 campaign's decoy record (cover cell 297) in development runs, outside the enumerated "
    "reads and unledgered at the time; removed (manufactured Stage-1b records) and ledgered retrospectively (E4)",
    "the Stage-1b decoy outputs (QC09, cover cells 297 and 316) are latent-proxy class: labelled, never displayed in "
    "summaries or handoffs, never juxtaposed with any tail-cell quantity; the two decoys bracket the band (297 below, "
    "316 above, by the cover's ordering; both guard-checked outside the band), which the research SRK decoy rule "
    "avoided (delta-2 E5; A15/D6 unchanged)",
    "second delta result-chasing component LOW (delta-2 review)",
]
REVIEWS = {
    "incident_independence": (NS + "reviews/REVIEW_INCIDENT_INDEPENDENCE_P309.md", "## 10. Conditions"),
    "u2_check": (NS + "reviews/REVIEW_U2_CHECK_P309.md", "## 8. Conditions"),
    "delta_incident_independence": (NS + "reviews/REVIEW_DELTA_INCIDENT_P309.md", "## 7. Conditions"),
    "prefreeze_r4": (NS + "reviews/REVIEW_PREFREEZE_R4_P309.md", "## 7. Conditions"),
    "prefreeze_r4_followup": (NS + "reviews/REVIEW_PREFREEZE_R4_FOLLOWUP_P309.md", "## Conditions"),
    "delta2_incident_independence": (NS + "reviews/REVIEW_DELTA2_INCIDENT_P309.md", "## Conditions"),
}


def git(*a) -> str:
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True, check=True).stdout.strip()


def blob(rel: str) -> str:
    raw = (REPO / rel).read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest()


def section(text: str, heading: str | None) -> str | None:
    if heading is None:
        return None
    i = text.find(heading)
    if i < 0:
        return None
    rest = text[i:]
    j = rest.find("\n---", len(heading))
    return rest[: j if j > 0 else len(rest)].strip() + "\n"


def build() -> dict:
    docs = {k: {"path": v, "git_blob": blob(v)} for k, v in DOCS.items()}
    reviews = {}
    for k, (rel, head) in REVIEWS.items():
        p = REPO / rel
        if not p.exists():
            raise SystemExit(f"review missing at the freeze: {rel}")
        t = p.read_text()
        lines = t.splitlines()
        reviews[k] = {"path": rel, "git_blob": blob(rel), "verdict_lines_verbatim": lines[1:3],
                      "conditions_verbatim": section(t, head)}
    u2 = (REPO / DOCS["u2_corrected_proposition_r2"]).read_text()
    quote = "\n".join(l[2:] if l.startswith("> ") else l[1:] for l in u2.splitlines() if l.startswith(">"))
    driver = (FNS / "code" / "p309_driver.py").read_bytes()
    allowance = json.loads((FNS / "config" / "SCANNER_ALLOWANCE_P309.json").read_text())
    return {
        "schema": "P309_FREEZE/1",
        "campaign": "p5y_k5_cell309_p309_r1",
        "cell": 309,  # q309: literal-ok (the frozen target cell of the closure-only campaign)
        "detector": "CUSUM", "m": 5,
        "route": "P309 package 1: frozen K5-B direct clause; S = (A0_I1, min(A1_I1, A1_RLR), min(A2_I1, A2_RLR)); the "
                 "TC-T order-0 channel replaced by the SRK B3/B4 min construction (THEOREM_SRK section 3)",
        "scope": "CLOSURE_ONLY (U3); never adoption, never a floor change, never r6, never a K5/P5Y status change",
        "closure_criterion": "Gamma < 0, exact and strict; Gamma = 0 or an incomplete evaluation is not a pass",
        "documents": docs,
        "reviews": reviews,
        "stage1a": {"blocks": "srk_certify.cell_blocks(C): outward 2^-10 dyadic hull Ew of C, N_E = 4 equal check "
                              "sub-blocks; weight block = Ew", "ladder": [8, 10, 12], "indices": [1, 2, 3, 4],
                    "kernel": "whole (SRK-T OUT, rule S C5)",
                    "numerics": "THEOREM_SRK section 12 (A4) verbatim, as pinned in the producer at lock 2a03e838",
                    "serialization": "per rung: one job per (sub-block, rung) calls run_block with ladder=(d,), then "
                                     "certificate_json per index; never best-rung-only",
                    "admission": "srk_gate.gate (G1-G6) with in-process verdicts of the band-scoped verifier "
                                 "(verify/srk_verify_indep_scoped.py) at N = 8, max_depth = 24; verdict_source = its "
                                 "sha256",
                    "failure_mapping": "protocol 2.5: a producer status other than CERTIFIED, a verdict other than "
                                       "ACCEPT, or jobs not started / terminated by the budget mechanics -> fallback "
                                       "(Gamma-bar_i = None, TC-T term), no retry; any exception (producer, guard "
                                       "refusal, verifier, gate, driver) after the marker -> EXECUTION_INDETERMINATE",
                    "budget": {"start_threshold_cpu_s": 48 * 3600, "per_job_limit_cpu_s": 12 * 3600, "workers_max": 4,
                               "order": "rung-major: b1..b4 at d = 8, then 10, then 12",
                               "accounting": "user + system CPU of each job process, verification included",
                               "stopping": "only by not starting jobs and by discarding a terminated job; never raises",
                               "total_cpu_bound": "< threshold + 4 x (per-job limit + 5 s hard margin) (rev. 2c A6 as "
                                                  "corrected, D2; R4 3.2)",
                               "termination_mapping": "only SIGXCPU, or SIGKILL with CPU >= the per-job limit, is a "
                                                      "budget termination (fallback); any other abnormal end is "
                                                      "JOB_EXCEPTION -> EXECUTION_INDETERMINATE (rev. 2c A22)",
                               "wall_clock": "unbounded; no post-marker wall-clock cap (rev. 2c A6)"},
                    "genuine_only": "no mutant battery, no shifted or widened probe on in-band certificates"},
        "stage1b": {"rules": "RLR307 Stage-1 rules verbatim (rlr307_stage1 / rlr307_independent / rlr307_pinned at "
                             "their pinned bytes; C1B_R2 certifier pins)", "ladder": [4, 6, 8],
                    "partition": "rlr307_stage1.blocks_for (sub-block width <= 1/100; outward 2^-20 hulls)",
                    "fallback": "CERTIFICATION_FAILED -> A1_RLR, A2_RLR := None -> S = S_I1 (protocol 3; owner G3)",
                    "budget": {"start_threshold_cpu_s": 21600, "per_job_limit_cpu_s": 21600, "workers_max": 4,
                               "order": "degree descending, then block (the RLR307 order)",
                               "per_job_limit_classification": "rev. 2c A5 as corrected (D2): a new parameter, "
                                                               "efficacy-relevant, ambiguous direction; the maximal limit",
                               "total_cpu_bound": "< 21 600 + 4 x (21 600 + 5) s (rev. 2c A6 as corrected, D2; R4 3.2)",
                               "termination_mapping": "as Stage 1a (rev. 2c A22)",
                               "wall_clock": "unbounded; no post-marker wall-clock cap (rev. 2c A6)"},
                    "exceptions": "an exception or an independent-reconstruction mismatch -> EXECUTION_INDETERMINATE",
                    "guard": "code/p309_guard.producer_adapter injected as ov_quarantine (rev. 2c A4)"},
        "stage2": {"supply": "S = (A0_I1, min(A1_I1, A1_RLR), min(A2_I1, A2_RLR)); S_I1 from the frozen combine",
                   "enclosure": "pinned tct_rule.tail_enclosure + crosscheck, then srk_adapter.srk_enclosure with the "
                                "exact reproduction gate and binding to cell, geometry (5, 1/2), whole kernel and "
                                "verifier_id",
                   "clause": "the pinned c2_d5_forecast.direct called unchanged through the shim (rev. 2c A11)",
                   "historical_control": "post-grant, pre-marker; both parts of rev. 2c A12 must reproduce C2's "
                                         "committed record for the cell byte-identically; CONTROL_FAILED -> not "
                                         "consumed, STOP",
                   "record_binding": "rev. 2c A13 (the 307 pattern)"},
        "outcome_table": "protocol rev. 2b section 5 verbatim: CELL309_CLOSED_UNDER_P309 (scientific closure only) iff "  # q309: literal-ok (label)
                         "TARGET_EVALUATED, checks passed and Gamma < 0 exact; NOT_CLOSED iff Gamma >= 0; "
                         "EXECUTION_INDETERMINATE for any post-marker failure or a disagreeing post-seal "
                         "re-verification / control digest; CONTROL_FAILED -> no conclusion, not consumed",
        "exactly_once": {"marker": G.PRODUCTION_MARKER, "pending_ref": G.PENDING_REF,
                         "emergency_file": "<gitdir>/p309-emergency-result.json",
                         "result_path": NS + "evidence/execution/P309_RESULT.json",
                         "sites": allowance["exactly_once_sites"],
                         "exit_codes": {"0": "sealed", "2": "refused pre-marker", "3": "CONTROL_FAILED (not consumed)",
                                        "4": "UNSEALED", "5": "sealed failure status", "6": "CONSUMED_UNRECORDED",
                                        "7": "sealed, not materialized"},
                         "chain": "freeze F <- freeze record FR <- qualification Q <- review Rv <- [window commits] "
                                  "<- grant G; checkpoint-record commits anywhere (rev. 2c A8, A23, A24)",
                         "run_nonce": "<gitdir>/p309-run-nonce.json, O_EXCL, created just before the marker, binds "
                                      "target-mode jobs to the live execute process (A28)",
                         "seal_only_gate": "the pending ref is created by seal-only only for emergency evidence bound to "
                                           "a marker that names a commit carrying the grant (owner D5; A29)"},
        "grant_rules": {"cell_source": "execute derives the cell interval from the pinned cells.json (canonical sum "
                                       "form); the grant's cell_interval and drift_hull_Ew must equal it (A20)",
                        "min_horizon_s_at_arming": 14 * 86400,
                        "premarker_admission": "the guard's checks 2-6, 8, 9 and 7 without the marker, plus exact "
                                               "strings, pinned ids, host, worktree, runtime, issued_utc not in the "
                                               "future, non-placeholder authority, committer identity (A21)",
                        "window_paths": ["ledger/ZERO_TARGET_LEDGER.jsonl", "ledger/EXPOSURE_LEDGER.jsonl",
                                         "ledger/CHECKPOINT_PUSHES.jsonl", "handoff/", "qualification/host_rerun/"],
                        "freeze_record": NS + "ledger/FREEZE_RECORD.json",
                        "nothing_between_grant_and_execute": True},
        "qualification_rule": "one complete run (qualification/attempt_1, O_EXCL); no retry, no resumption (A27); "
                              "gates Q01-Q17, Q-U2, Q-D5",
        "driver": {"path": NS + "code/p309_driver.py", "sha256": hashlib.sha256(driver).hexdigest()},
        "u2": {"incident_review_finding": "U2_FINDING: NOT_TRIGGERED_WORDING_DISCREPANCY",
               "u2_check_verdict": "U2_CP_ESTABLISHED",
               "corrected_proposition_rev2_verbatim": quote,
               "classification": "a governance reading adopted by the owner's ruling; not a mechanical result",
               "withdrawn_wording": "P309 uses no P3-derived quantity (withdrawn as false)"},
        "independence_statement": "temporal and parametric independence only (incident review C1); route choice and "
                                  "motivation are NOT independent (MEDIUM-HIGH, upper end)",
        "disclosed_liabilities": DISCLOSED_LIABILITIES,
        "efficacy": "UNKNOWN BY DESIGN; no decoy output is used to predict Gamma309 or SRK's efficacy at 309",
        "proposed_execution_host": {"description": "this isolated cloud environment (rev. 2c A14)",
                                    "host_id_sha256": G.host_id()},
        "post_grant_derivations": {
            "cell_interval": "derived by execute itself from the pinned cells.json (the canonical sum form), after "
                             "check_grant; the grant's value must equal it (rev. 2c A20); the proposal tool reads it "
                             "after the qualification review, ledgered (C4). Disclosed departure: FE-9's pre-freeze "
                             "in-memory equality check parsed it, no value displayed (delta-2 E3)",
            "drift_hull_Ew": "srk_certify.cell_blocks(cell_interval)[0]: the outward 2^-10 dyadic hull",
            "execution_host": "the host the owner names in the grant; if it is not the proposed host, QC10's host "
                              "re-run is repeated there before execute",
            "not_after_utc": "the grant's expiry, set by the owner: at least 14 days after execute starts (rev. 2c "
                             "A21, checked before the marker); a run longer than the horizon turns the per-call expiry "
                             "check into EXECUTION_INDETERMINATE or a silent SRK loss (delta-2 E7)"},
    }


if __name__ == "__main__":
    m = build()
    data = json.dumps(m, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    if "--check" in sys.argv:
        same = OUT.exists() and OUT.read_text() == data
        print("FREEZE PARAMS", "IDENTICAL" if same else "DIFFER")
        sys.exit(0 if same else 1)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(data)
    print(f"-> {OUT.relative_to(REPO)} ({len(data)} bytes)")
