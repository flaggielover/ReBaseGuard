# Qualification r1 (freeze 5c6667fd): FAIL, and why

**Verdict of the official run.** `QUALIFICATION FAIL: Q1=P Q2=P Q3=P Q4=P Q5=P Q6=P Q7=P Q8=P Q9=P Q10=P Q11=P Q12=F`.

**The cause is a defect in the verifier's gate aggregation, not a failed case.**
* Gate Q12 requires `cases[k]["pass"] is True` for QC10, QC11 and the cap check.
* The QC10 summary (`rlr307_qualify.main`, built from `test_rlr307_flows.run_flows`) carried its result under the key
  `all_ok` (true: 39/39 flows OK, `failed: []`). It had no `pass` key.
* So `P("QC10")` read `None`, and the gate failed closed.
* QC11 passed. The cap check also passed: projected cell-307 Stage-1 wall 8155.6 s, which is ≤ EVAL_CAP/2 = 10800 s and
  ≤ 4 h.

**Every case's own result in this run:**
* QC01: PASS (28/28 exact rung fields, 25/25 ladder fields);
* QC02: PASS (decoy cell 297: 15/15 rungs CERTIFIED; independent checks all equal);
* QC03: PASS (serial rerun bit-identical for d = 4, 6, 8 and for the block record);
* QC04: PASS (15/15 drift points consistent; 4/4 controls flagged; symmetry holds);
* QC05: PASS (2052/2052 exact; 47/47 committed records reproduced; 6/6 historical mutants rejected);
* QC06–QC09 and QC11–QC13, Q8: PASS;
* QC10: all_ok (39/39).

**Repair (freeze r2).**
* `code/rlr307_qualify.py` only: the QC10 summary gets `pass = all_ok`.
* The aggregator now fails loudly, as `cases_missing_pass`, when any case summary lacks a boolean `pass`. This is the
  control for this defect class.
* Unchanged: the driver, the certifier, the guard, Stage 1, the independent reconstruction, the tests, the theorem, the
  cases and every frozen rule.
* No review had happened, so this is a pre-review repair. It is disclosed here and in protocol §0.

**Handling of this run's files.** The outputs are preserved unchanged in this directory. They are evidence of the r1
run, and the r2 run must pass on its own. The r1 decoy records also give a cross-run determinism check against r2.
