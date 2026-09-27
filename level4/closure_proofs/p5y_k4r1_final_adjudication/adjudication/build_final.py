import json, hashlib
rc = json.load(open('RECOMPUTE.json'))
res = json.load(open('clone/level4/closure_proofs/p5y_k4r1_nearzero_successor/evidence/execution_r1/K4R1_RESULT.json'))
recomputed = {}
for k, v in rc['recomputed'].items():
    r = res['certificates'][k]
    recomputed[k] = {
        "a": v["a"], "hull_cell": v["hull_cell"], "eta_outward_of_a": True,
        "inputs": {"D0_hi": v["D0_hi"], "L1": v["L1"], "U0": v["U0"], "M3": v["M3"], "M5": v["M5"],
                   "e0": "5083/20000000", "x1": "5083/10000000"},
        "G": v["G"], "T": v["T"], "B": v["B"], "T_branch": v["T_branch"],
        "G_approx": v["G_approx"], "T_approx": v["T_approx"], "B_approx": v["B_approx"],
        "decision": v["decision"],
        "equal_to_result_file_exact_string": (r["G"] == v["G"] and r["T"] == v["T"] and r["B"] == v["B"]),
    }
checks = {
 "C1_frozen_gate_identity": {"result": "PASS", "evidence": [
   "fresh `git clone --no-local` of the worktree; `git replace -l` empty in the clone and in the real worktree; all object reads with --no-replace-objects",
   "sha256(FREEZE.json) = 874e63e2f7a6b892714a46b5dc167ceea8b41cf8b4bb25bc50c77f875c0cc295 == FREEZE_HASH content",
   "58 bound files: all 58 match their blobs at 8928b8f1 and at b5b4c917; the 56 non-review files match `git show 93d82c87:<path>` exactly; the 2 review files are absent at 93d82c87",
   "bound = 42 namespace files (all namespace files tracked at the freeze commit except FREEZE.json/FREEZE_HASH; none missing, none extra) + the 16 PROVENANCE sources",
   "qualified_candidate_commit = 93d82c87d2f5aa33109f5b37125caf283967b694; qualification_verdict QUALIFICATION_ACCEPTED; review_files = review/qualification_r5/QUALIFICATION_REVIEW.{json,md}",
   "8928b8f1 has exactly one parent 93d82c87; `git diff --no-renames --name-status 93d82c87 8928b8f1` = A FREEZE.json, A FREEZE_HASH, A review/qualification_r5/QUALIFICATION_REVIEW.json, A .../QUALIFICATION_REVIEW.md == allowed_freeze_delta",
   "bound r5 review JSON sha 8e49763026be4aa423f81d8596c5bcc33219314c826e83394bb18c50d4c0552e and MD sha 2166e1f56cc92000370c84fa87d028f660a96550da28f7e7fe9e3c2ff5bb487c equal the stated r5 pair; review JSON verdict QUALIFICATION_ACCEPTED, candidate_commit 93d82c87..., blocking_defects []"]},
 "C2_qualification_ancestry_and_temporal_integrity": {"result": "PASS", "evidence": [
   "linear chain bc4ba08e -> 81f5195a (cand r1) -> ce144fd7 (records r1 REJECTED of 81f5195a) -> 179d5aae (cand r2) -> c5e677a3 (r2 REJECTED of 179d5aae) -> 965f19a6, cb5b6c61 (cand r3) -> 49a48a50 (r3 REJECTED of cb5b6c61) -> 5d33363c (cand r4) -> 0dc949b5 (r4 REJECTED of 5d33363c) -> 93d82c87 (cand r5) -> 8928b8f1 (FREEZE) -> b5b4c917 (result)",
   "each rejection-record commit only adds its review/qualification_rN_REJECTED/ directory; each review names the immediately preceding candidate; no FREEZE.json exists in any commit before 8928b8f1",
   "committer times (UTC): 93d82c87 11:45:07Z; FREEZE frozen_utc 12:17:08Z; freeze commit 12:17:19Z; result runtime.started_utc 12:17:35Z; result commit 12:17:46Z (all 2026-09-27) - monotone and consistent",
   "leak scan: every commit bc4ba08e..8928b8f1 (12 commits incl. bc4ba08e) grepped for the first 30 digits of the numerators of G, T, B for m = 2, 3, 5: zero hits; `git log --all -S` over all 742 reachable commits of all refs: every such string is introduced only by b5b4c917",
   "'K4R1_CERTIFIED' and 'K4R1_SUCCESSOR_SCIENCE: PASS' occur before b5b4c917 only as rule/label text in code/k4r1_certificate.py, config/GATE.json and tests/test_k4r1.py, never in evidence or review files and never as an outcome",
   "no real target string found in any file under /private/tmp/claude-501 outside my own directory (28 reviewer-sandbox K4R1_RESULT.json files are synthetic: none carries the real D0_hi or any real G/T/B)"]},
 "C3_exact_once": {"result": "PASS", "evidence": [
   "exactly one file ever added under evidence/execution_r1 across all refs (b5b4c917, K4R1_RESULT.json); no crash record; no other execution artifact in history",
   "result status EXECUTED; executed_at_head 8928b8f170419e2daf19187085dd502e44a26a6b == freeze commit; freeze_sha256 874e63e2... == sha256(FREEZE.json)",
   "result sha256 cbf1332bdf368ceb747128996d057d7e2acb1017325ec47b67bfba92b15fc7e4, 7228 bytes; its bytes equal json.dumps(parsed, indent=1, sort_keys=True)+newline, i.e. the executor's own serialization (no hand edit)",
   "b5b4c917 adds only that file; real worktree clean (no untracked/ignored entries in the namespace); on disk the only real-valued K4R1_RESULT.json files are the worktree copy and my clone"]},
 "C4_source_provenance": {"result": "PASS", "evidence": [
   "all 16 PROVENANCE sources hash-match on disk, in FREEZE.bound_files, and at 93d82c87; none of them is changed anywhere in bc4ba08e..b5b4c917 (the only changed paths are inside the K4R1 namespace)",
   "K1 cell-0 record 4f8df44c: detector CUSUM, cell_index 0, producer_identity 3692d0fe..., e0 = rho = 5083/20000000; equals COMPOSITE_EXPORT_MANIFEST entry k4_records/aux5_CUSUM_0_256.json and K4_COMPOSITE_ATTESTATION production_provenance.halves.predecessor.pairs[0].record_sha256 (attestation: 326 cells verified, same producer identity)",
   "slot-1 cf90f1ea: last touched 84299314 'published after independent adjudication ... (ADOPTED)'; ADJUDICATION.json adoption_status ADOPTED, label FIRST_CELL_SUPPORTED_ALL_M, per_m exact L0/U0/M5/L1 equal the record",
   "T-EXT TEXT_RESULT cb97cabc sealed 20dc6b98; adjudication a3547b9b ADOPTED 37/37 (failed_checks []), scope 'cells 0-10 pass set'; M_n majorants rest on its tower checks M02/M06/M11 (disclosed in GATE.input_scope_note)",
   "historical K4 report sha 83cabce239630d98a842bd9eec32482c7d0720fc86433ef8ee7c658833aef175 (last touched bc4ba08e)"]},
 "C5_residual_universe": {"result": "PASS", "evidence": [
   "from the historical report: too_loose_cells non-empty only for CUSUM m=2 [0,1], m=3 [0,1,2], m=5 [0,1,2]; each a prefix from cell 0 with left 0; right ends 10187/10000000 and 957/625000; equals RESIDUAL_UNIVERSE.json exactly"]},
 "C6_certificate_decisions": {"result": "PASS", "evidence": [
   "independent_recompute.py (my own, no campaign import) reads the raw JSONs, verifies 88 structural/identity checks, recomputes G, T, B in exact Fractions; all three equal the result file as exact strings, as do inputs, T_branch, hull_cell, cells, PASS and outcome; identical output under Python 3.9.6 and 3.14",
   "structural: slot-1 binding record_sha256 == 4f8df44c, k1_cell_index 0, left 0, right == x1 = 5083/10^7, point_e 0, export_manifest 29ad1f9b, all four addresses bound to the K1 record; e0 = x1/2 <= x1; transport_factor == x1^2/2 exactly and L1 == L0 - tf*M5, U1 == U0 + tf*M5 exactly (stronger than the frozen inequalities); T-EXT sealed_record_sha256 == cf90f1ea, L0 and sealed_L1 equal slot-1, hull-0 M5 reproduces the slot-1 M5 exactly; unique hull row with x_hi == a (cells 1 and 2) and a <= eta <= a*(1+2^-200)",
   "semantics: K1 D_interval is the certified enclosure of R'(e0) (frozen K4 checkpoint target.premises; consistent with historical Rprime_cell_hi = D.hi + rho*M_R2); slot-1 PROTOCOL s2-3: I0 = [L0,U0] contains R'''(0), L1 <= inf R''' on C1 = [0,x1]; TEXT_SPEC Conclusion: M_{n,m}(eta) >= sup_[0,eta] |R^(n)| for n = 2..5",
   "theorem re-derived: P5-T3 oddness gives R(0) = R''(0) = R''''(0) = 0; R''(t) = int_0^t R''' >= t*L1 on [0,e0] so R'(0) = R'(e0) - int_0^e0 R'' <= D0.hi - L1*e0^2/2 = G; |R''''(s)| <= s*M5 on [0,a] gives R''' <= U0 + a^2/2*M5, and R''' <= M3, so R''' <= T on [0,a]; Taylor-Lagrange at 0: R(e) = e*R'(0) + e^3/6*R'''(xi) <= e*(G + a^2/6*max(T,0)) = e*B; B < 0 gives R < 0 on (0,a]. Valid for either sign of L1 and T. L5 used only for C^5 smoothness",
   "robustness: the T term contributes only +4.3e-4 / +9.0e-4 / +7.9e-4; B stays negative even with T replaced by M3 and with the L1 correction dropped; the decision rests on D0.hi < 0 of the K1 CLOSED record",
   "non-load-bearing cross-check: the (unused, not independently reviewed) GammaTilde point certificate 84aaa6a5 encloses R'(0) in [-20.79,-3.7254] (m2), [-19.32,-2.5280] (m3), [-17.44,-0.9375] (m5); consistent with R'(0) <= G"]},
 "C7_endpoint_semantics": {"result": "PASS", "evidence": [
   "obligation on (0,a]; R(0) = 0 exactly by P5-T3 and e = 0 is not in the obligation; certificate gives R(e) <= e*B < 0 for all e in (0,a]",
   "handoff: the first non-residual historical cell starts exactly at a (m2 cell 2 left 10187/10000000; m3/m5 cell 3 left 957/625000) and is DIRECT_R_NEGATIVE, a closed-cell certificate; overlap only at the point a"]},
 "C8_inherited_historical_cells": {"result": "PASS", "evidence": [
   "recomputed from the historical report: all 8 (D,m) have contiguous covers from 0 (CUSUM 310 cells to 2092283/1000000, SR 295 cells to 40372863/20000000), no counterexample cell, every non-residual cell CHAIN_RPRIME_NEGATIVE or DIRECT_R_NEGATIVE with its recorded Rprime_cell_hi or R_cell_hi < 0, chain cells a prefix from 0 (CUSUM m1 189 chain/121 direct; m2 0/308; m3 0/307; m5 0/307; SR m1 198/97; m2 191/104; m3 187/108; m5 183/112)",
   "K4_INDEPENDENT_REVIEW.json (sha 241953c0, bound): K4_ADJUDICATION ACCEPTED, K4_SCIENTIFIC_RESULT NOT_CLOSED, frozen_disposition K4_INCONCLUSIVE_K1_RECORDS, reviewer rerun report_sha256 83cabce2... (byte-identical reproduction)"]},
 "C9_complete_assembly": {"result": "PASS", "evidence": [
   "all 8 (D,m) PASS: 5 inherited CELLWISE_ALL_CERTIFIED, 3 = K4R1 (0,a] + historical [a, end]; each covers (0,2] (last right >= 2); far field e > 2 not asserted, exactly as in the K4 checkpoint target.not_asserted (P5X-T7(1)); no compact gap"]},
 "C10_no_post_result_change": {"result": "PASS", "evidence": [
   "no commit descends from b5b4c917 on any ref (branch p5y-k4r1-nearzero-successor == b5b4c917; not present on GitHub origin per ls-remote)",
   "`git diff --no-renames 93d82c87 b5b4c917` = only additions of FREEZE.json, FREEZE_HASH, the r5 review pair, and the result: GATE, SPECIFICATION, code, tests, PROVENANCE, RESIDUAL_UNIVERSE byte-identical",
   "GATE.obligation_unchanged restates the historical K4 statement verbatim (all D in {CUSUM,SR}, m in {1,2,3,5}, (0,2], strict); strict B < 0, no tolerance; residual universe = all historical TOO_LOOSE cells; result new_real_addresses 0 (inputs are pre-existing adopted records)"]},
}
defects = {
 "BLOCKING": [],
 "NON_BLOCKING": [
  {"id": "F1", "text": "Scope of the T-EXT majorants: the T-EXT adjudication (a3547b9b) adopts the cells 0-10 K5-B pass set, not the M3/M5 hull majorants as standalone objects. K4R1 uses M3(a), M5(a) for hulls 1-2, which lie inside the regime that adjudication's tower checks (M02 tower validity on the hull, M06 M3 floor, M11 load-bearing regime hulls 0..10) examined. Disclosed in GATE.input_scope_note; the majorants also rest on T-EXT premise P1b (R2/R3 producer premises) and on a rule-by-rule reading of the frozen tower rather than an independent reimplementation. Not a defect of K4R1 but an inherited dependency that should be stated with any closure claim."},
  {"id": "F2", "text": "Qualification review r5 note N31 is itself wrong: PROVENANCE.identities.k1_successor_final_adjudication_commit is 7d5cf02b7f4b29439c59d803fe90ce62bc0841da in every candidate and at HEAD; that commit exists (branch p5y-k1-successor-final-assembly). The field is informational and unread by code."},
  {"id": "F3", "text": "Designer and r1 qualification reviewer had partial prior exposure (historical D0.hi, order of magnitude of slot-1 L1; r1 reviewer saw exact slot-1 rationals through a faulty redaction filter). Disclosed in FEASIBILITY.md. The gate has no tunable parameter and B is decisively negative regardless, so no bias is possible."},
  {"id": "F4", "text": "The K1 cell-0 record carries production_run=false / result_bearing=false; per the accepted K4 independent review these are documented certifier-constant flags, and the record is bound by the composite export manifest and attestation. No action."},
  {"id": "F5", "text": "The caller's summary gives the execution time as 12:17:34Z; the result records started_utc 12:17:35Z. Immaterial."},
  {"id": "F6", "text": "Independence limit: this adjudicator is the same model family as the designer, executor and qualification reviewers (separate context). I did not rerun the 102-mutant harness (the r5 reviewer reports 102/102); I did rerun the 92 synthetic tests (92 passed, Python 3.9.6). I did not inspect remote hosts (AWS/Vultr) for other execution artifacts; the gate requires no host and the local evidence shows a single execution."}
 ]
}
out = {
 "schema": "final-adjudicator.p5y.k4r1.final-adjudication.v1",
 "campaign": "P5Y-K4R1 - Near-Zero Successor Certificate",
 "verdict": "ACCEPTED",
 "adjudicated_result_commit": "b5b4c91764a44f3b7438bcc571c1360cbbc1379d",
 "freeze_commit": "8928b8f170419e2daf19187085dd502e44a26a6b",
 "qualified_candidate_commit": "93d82c87d2f5aa33109f5b37125caf283967b694",
 "result_file_sha256": "cbf1332bdf368ceb747128996d057d7e2acb1017325ec47b67bfba92b15fc7e4",
 "freeze_sha256": "874e63e2f7a6b892714a46b5dc167ceea8b41cf8b4bb25bc50c77f875c0cc295",
 "adjudication_date_utc": "2026-09-27",
 "checks": checks,
 "recomputed_certificates": recomputed,
 "independent_recompute": {"script": "independent_recompute.py", "output": "RECOMPUTE.json", "n_checks": rc["n_checks"], "failed": rc["failed"]},
 "K4R1_SUCCESSOR_SCIENCE": rc["K4R1_SUCCESSOR_SCIENCE"],
 "K4R1_COMPACT_RESIDUAL_COVERAGE": "PASS",
 "K4R1_COMPLETE_K4_ASSEMBLY": "PASS",
 "consequence": "Per GATE.adoption_rule, K4R1_SUCCESSOR_SCIENCE = PASS plus this ACCEPTED fresh-context final adjudication supports K4_SCIENTIFIC_LINE = CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN. The historical K4 verdict NOT_CLOSED (K4_INCONCLUSIVE_K1_RECORDS, bc4ba08e) is preserved unchanged. H2 for e > 2 is not asserted.",
 "defects": defects,
 "disclosures": [
  "all commands against the real worktree /Users/suzhe/ReBaseGuard-k4r1 were read-only: git rev-parse HEAD; git status --short; git replace -l; git log --oneline -15; git worktree list; git status --porcelain --ignored -- <namespace>; git rev-parse p5y-k4r1-nearzero-successor; git ls-remote --heads origin p5y-k4r1-nearzero-successor (network read of GitHub); git clone --no-local (source of my clone)",
  "a filesystem `find` for K4R1_RESULT.json under /Users/suzhe (excluding Library) and /private/tmp/claude-501, and grep of /private/tmp/claude-501 for target strings (read-only)",
  "in my own clone only: checkout of b5b4c917 (detached), git show/diff/log/grep/cat-file with --no-replace-objects, `python3 -I -B .../k4r1_certificate.py preflight` (PREFLIGHT PASS, values_computed false, head null), and `/usr/bin/python3 -B -m pytest -p no:cacheprovider tests/test_k4r1.py` (92 passed; synthetic sources in tmp repos)",
  "never run: `k4r1_certificate.py ready` or `execute` (anywhere), `make_freeze.py`, or the mutation harness",
  "no file in /Users/suzhe/ReBaseGuard or the k4r1 worktree was edited, staged or committed"
 ]
}
s = json.dumps(out, indent=1, sort_keys=False, ensure_ascii=True) + "\n"
s.encode('ascii')
open('FINAL_ADJUDICATION.json', 'w').write(s)
print('ok')
