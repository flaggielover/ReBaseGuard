# Codex handoff — Level-4 Priority 4

> **Post-handoff status (independent adjudication, 2026-08-31).**  The audit
> requested by this document has now been completed.  Repository verification
> passes, the skew-normal and P2 discrepancies are reconciled, G3's unproved
> iff wording is narrowed, and the verdict remains `PARTIAL` because three
> literal frozen gates still fail.  See `INDEPENDENT_ADJUDICATION.md` and
> `results/independent_adjudication.json`.  The text below is preserved as the
> original handoff record.

## 0. Do not trust this campaign's verdict

**Do not trust the verdict in `results/closure_decision.json`, and do not
trust this document.**  Everything here was produced by the same agent that
wrote the theorem, wrote the code that tests it, wrote the gates that judge it,
and wrote the report that declares it closed.  That is exactly the arrangement
in which a wrong result survives.

Your job is to decide independently whether the claimed closure is justified.
Re-derive the mathematics, re-run the evidence, read the diff, and reach your
own verdict.  If you reach a different one, yours governs.

At the original handoff nothing had been committed or pushed.  Independent
checkpoint integration is a later action and is reported outside this
historical handoff because a commit cannot contain its own object id.

## 0.1 Current adjudicated status

```text
verdict                          PARTIAL
repository-wide verification     COMPLETED — PASS
committed / pushed               nothing
```

`results/closure_decision.json` is authoritative.  Three literal frozen gates
remain false.  Independent adjudication completed
`run_repository_verification.py`; `results/verification.json` records
`all_gates_pass=true`.  The original interrupted run remains disclosed in
`PROVENANCE.md`, but it is no longer a hole in the current evidence.

## 1. What is claimed

A conditional derivative and local-stability theorem for regular
one-dimensional **location families** under the frozen two-sided CUSUM and the
frozen two-chart Shiryaev-Roberts recursions, for every truncated window length
`m >= 1`:

```text
F'_{rho,m}(0) = rho (1 - Gamma_{D,m,f}),
Gamma_{D,m,f} = E_0[ A_m * sum_{t<=tau} psi(Z_t) ],     psi = -f'/f,
```

with the Gaussian core recovered by the single substitution `psi(z) = z`.
Plus: a neutrality corollary, a sign analysis of the random-denominator
correction, two proved failure modes, and a weakened differentiation
hypothesis.  Full statements in `THEOREM.md`; full proof in `PROOF.md`.

## 2. The six things most likely to be wrong

Attack these first.

0. **The originally inconsistent cell.**  `sr@520.886`, `skewnormal4`,
   `m = 2`: Route A `6.3875 ± 0.0284`, Route B `6.5561 ± 0.0270`, `|z| = 4.29`.
   The whole skew-normal SR column is one-signed at 2.0-2.6% (`|z|` 3.4-4.3),
   while the same family under CUSUM agrees to 0.05-0.53% and every symmetric
   family under SR agrees to 0.03-0.41%.  The campaign's hypothesis is residual
   finite-difference bias that the `h^2` Richardson correction cannot remove
   when the map is not odd.  Independent adjudication tested it at
   `.025/.0125` and `.0125/.00625`, and added a fresh 1.6M-path score replay.
   The smallest-step direct and both score estimates agree.  The original cell
   remains frozen and failed; see `INDEPENDENT_ADJUDICATION.md`.

1. **The prior-art overlap.**  `location_family` and
   `location_family_track3ab` already proved the stopped-score identity for
   `m = 1`.  Read `location_family_track3ab/THEOREM.md` and decide for yourself
   whether Priority 4's extension (truncated window at general `m`, both
   detectors, weaker hypothesis, failure modes, Lean proof of the bridge) is a
   substantive extension or a repackaging.  This is the single most important
   judgement you have to make.
2. **`PROOF.md` Section 1-2, the interchange.**  The whole theorem is one
   dominated-convergence argument.  Check that (A6) as stated really dominates
   the difference quotient uniformly, that (A4) supplies the pointwise limit,
   and that the summation over `{tau = n}` in (1.1)-(1.2) is justified rather
   than assumed.
3. **`PROOF.md` Section 8, L3 and L4.**  These are the only places the
   hypotheses are *discharged* rather than assumed.  L4 in particular has
   several inequalities chained together.  Check `C_d = 4/(d^2 e^2)`, check the
   Cauchy-Schwarz split on `{tau = n}`, and check that the geometric ratio
   really tends to `(1-p)^{1/2}`.
4. **The claim that the correction sign is Gaussian.**  Independent review
   found that the all-path converse was not proved.  G3 now claims Gaussian
   sufficiency plus explicit non-Gaussian failure, not uniqueness.  The
   Laplace witness arithmetic remains valid.
5. **The 1.1% SR gap against Priority 2.**  Priority 4's independent SR
   implementation gives gains about 1.0-1.1% *below* the closed Priority-2
   values, one-signed across all four window lengths, at 2.4-3.0 combined
   standard errors.  Priority 4 used 3.2M paths, Priority 2 used 240k.  The two
   implementations were read line by line and are mathematically identical.
   Independent adjudication reran the frozen P2 implementation on 1.6M fresh
   paths; it agrees with P4 within 1.26-1.49 combined standard errors.  The gap
   is Monte Carlo fluctuation, while the frozen values and literal gate remain
   untouched.

6. **Whether Route A and Route B are really independent.**  They share the
   simulator.  Decide whether Route Q (independent of the simulator) plus the
   Gaussian consistency check against P1/P2's independently implemented values
   is enough mitigation, or whether it is not.

## 3. Files created (all new, all inside one directory)

Everything is under `level4/closure_proofs/p4_theory_generalization/`.
Nothing outside it was created or modified.  Verify with:

```bash
git status --porcelain
git diff HEAD --stat
```

Both should show changes only under that path.

```text
README.md THEOREM.md PROOF.md ASSUMPTION_AUDIT.md EVIDENCE_BOUNDARY.md
LEAN_CORRESPONDENCE.md PROVENANCE.md NOVELTY_AUDIT.md ADVERSARIAL_REVIEW.md
CLOSURE_REPORT.md CODEX_HANDOFF.md P5_HANDOFF.md
NUMERICAL_CORRESPONDENCE.md            (generated)
manifest.json  reproduce.sh
configs/P4_PROTOCOL.json               (frozen, hashed in manifest.json)
certificates/WITNESS.json              (frozen, hashed in manifest.json)
certificates/run_certificate.py  certificates/certificate.json
src/rebaseguard_p4_general/{__init__,families,detectors,simulate,quadrature,
                            estimators}.py
numerics/run_correspondence.py
scripts/{build_reports,make_figures}.py
lean/{GeneralLocationFamilyP4.lean,AxiomAudit.lean}
run_lean.py  run_repository_verification.py  derive_closure.py
tests/{conftest,test_families,test_detectors_and_simulation,
       test_analytic_routes,test_estimators,test_results,test_integrity,
       test_documents}.py
results/  figures/                     (generated)
```

## 4. Exact reproduction

```bash
bash level4/closure_proofs/p4_theory_generalization/reproduce.sh
```

**Environment requirements, and they matter.**  Three protected suites are
sensitive to the host and to nothing else:

* `LANG=LC_ALL=LC_COLLATE=en_US.UTF-8` — `m_gt_1_priority1` hashes a file
  listing whose sort order is collation dependent, and the recorded hash is the
  `en_US.UTF-8` one.  `reproduce.sh` now exports this.
* a **real `rg` binary on PATH** — `sr_derivative` and `m_gt_1_track1b` shell
  out to ripgrep.  On the machine this campaign ran on, ripgrep was only
  reachable as a shell function, so a one-line executable shim
  (`exec -a rg <claude binary> "$@"`) was placed on PATH for the verification
  run.  That shim is genuine ripgrep, not a substitute, but you should use a
  normal `rg` installation and confirm the same three suites pass.
  `reproduce.sh` aborts with an explanation if `rg` is missing.

Individual steps, if you want to run them separately:

```bash
PY=level4/.venv/bin/python
C=level4/closure_proofs/p4_theory_generalization
$PY $C/numerics/run_correspondence.py      # ~2 h, the expensive step
$PY $C/scripts/build_reports.py
$PY $C/scripts/make_figures.py
$PY $C/certificates/run_certificate.py     # seconds
$PY $C/run_lean.py                         # ~20 min (recompiles P1/P2/P3/P4)
$PY $C/run_repository_verification.py      # ~10 min
$PY -m pytest $C/tests -q
$PY $C/derive_closure.py
```

The correspondence campaign is fully deterministic given
`configs/P4_PROTOCOL.json`: every draw comes from a seeded generator, and
`tests/test_detectors_and_simulation.py::test_both_modes_are_reproducible_from_seed_and_batch`
asserts it.  A rerun should reproduce every number bit for bit.

## 5. Independent checks you should perform

**Mathematics.**

1. Re-derive `d/de L_tau(e)|_0 = -sum psi(Z_t)` from scratch under the
   convention `Z_t = eps_t - e`, `f_e(z) = f(z+e)`.  A sign error here would
   flip the whole result, and the convention is inherited from a frozen track
   rather than chosen here.
2. Verify Corollary G2 both ways: that `E_e[A_m] = -e` exactly for
   deterministic `tau` (elementary), and that the score formula returns `1`
   (integration by parts).  If those two disagree, the theorem is wrong.
3. Verify the uniform closed form of `PROOF.md` §9 by direct integration.
4. Check that `PROOF.md` §11's Laplace closed form
   `g_1(e) = -(c+b) tanh(e/b)` is right, including the claim that the infinite
   sum over `n` is carried out exactly by memorylessness.

**Numerics.**

5. Rerun `numerics/run_correspondence.py` and diff
   `results/correspondence.json`.
6. Independently reimplement Route Q for one family and one `m` and check the
   ten-digit agreement.  Route Q is the load-bearing non-Monte-Carlo evidence;
   if it is wrong, everything downstream is suspect.
7. Check the Gaussian consistency table in `NUMERICAL_CORRESPONDENCE.md` §5
   against `m_rho_stability_priority3/results/stability_map.json` yourself.
   This campaign re-implements the frozen detectors from scratch; agreement
   with P1/P2 is the main cross-implementation control.
8. Look for the random-number defect described in `PROVENANCE.md` §2 in any
   *other* seeded code path, and satisfy yourself that
   `test_aligned_streams_do_not_overlap_between_steps` actually guards it.

**Formal and certification.**

9. Recompile the Lean spine and re-run `#print axioms` yourself.  Confirm 19
   declarations, three standard axioms, no `sorry`.
10. Read `hasDerivAt_stoppedMean` and confirm it really proves what
    `LEAN_CORRESPONDENCE.md` claims — in particular that it uses the *Lipschitz*
    Mathlib lemma and not the pointwise-derivative one.
11. Recompute the Arb certificate at a different precision and confirm the
    inequalities still hold.
12. Confirm that `certificates/certificate.json` certifies nothing about any
    frozen CUSUM or SR gain.  If it does, the evidence boundary is wrong.

**Integrity.**

12b. **A near-miss you should verify independently.**  During this session one
    tool call executed a file-patching script from the wrong working directory,
    with `level4/closure_proofs/sr_derivative_priority2` as its cwd, and that
    directory also contains a `derive_closure.py`.  The script rewrote that
    file with byte-identical content (its search patterns did not match), so no
    frozen artifact changed: `git diff HEAD` is clean for all twelve protected
    trees and the file hashes identically to `HEAD`.  This is disclosed because
    an auditor should know a write touched a frozen tree at all.  Verify it:
    `git show HEAD:level4/closure_proofs/sr_derivative_priority2/derive_closure.py | shasum -a 256`
    against `shasum -a 256` of the working copy.

13. `git diff HEAD --stat` must be empty for all twelve trees listed in
    `manifest.json` → `protected_trees_read_only`.
14. Confirm the protocol and witness SHA-256 values in `manifest.json` match
    the files, and that neither file was edited after results were produced
    (check mtimes against `results/`).
15. Read `ASSUMPTION_AUDIT.md` §4.  It records two findings about P1's and
    P2's own hypotheses.  Confirm those findings were **not** applied to the
    frozen artifacts.

## 6. Known limitations you should weigh

* All families run at the *same* frozen threshold, so their in-control ARLs
  differ.  The cross-family gain table is **not** an ARL-matched comparison,
  and no claim is made that one family is more or less stable than another.
  A follow-up campaign with per-family ARL calibration would fix this.
* `t3` and `t1p5` have infinite fourth moments, so their standard errors are
  themselves heavy-tailed; read their `|z|` columns as indicative.
* `t1p5` is at its natural scale, not unit variance (it has none), so its gain
  is not on the same scale as the others.
* Route Q uses a memoryless detector, not the frozen one.  It tests the
  mathematics, not the operating point.
* The protocol was frozen after a pilot, not before.  `PROVENANCE.md` §2
  discloses exactly what the pilot saw and what it changed.
* No novelty verdict.  `NOVELTY_AUDIT.md` returns `NOVELTY-NOT-ADJUDICATED`
  and lists seven prior-art areas a real audit must cover.
* No infinite-horizon interval certification of any frozen CUSUM or SR gain.
  That boundary is unchanged from Priorities 1-3.
* The original repository-wide run was interrupted; independent adjudication
  later completed it successfully.  See §0.1 and `results/verification.json`.
* Nine of the ten non-passing cells are the single infinite-variance family
  `t1p5`, failing a 3% *accuracy* gate with an estimator whose own precision is
  1.5-23%.  They are statistically consistent (`|z|` 0.35-1.49) and Route Q
  covers that family exactly.  Judge for yourself whether the gate or the
  evidence is at fault; the campaign did not rewrite the gate.
* The sixteen Cauchy cells are recorded `COUNTEREXAMPLE-NOT-DEMONSTRATED`.  The
  predicted pathology (`E|A_1| = infinity`, `PROOF.md` §10) is visible in the
  artifacts as non-convergence, but the preregistered gate asks for a sharp
  deterministic disagreement and does not register it.

## 7. If you disagree

The campaign already reports `PARTIAL`.  Do not upgrade it to `CLOSED` on the
strength of this document.  The repository matrix now passes, but the three
frozen numerical gates still do not.

If the Lean audit is not clean on your machine, if a protected tree has moved,
if the skew-normal SR column turns out not to be finite-difference bias, or if
you judge the prior-art overlap against `location_family_track3ab` to be fatal,
the correct verdict is `PARTIAL`, `INCONCLUSIVE` or `FAILED`.  Do not repair
this campaign to make it close, and do not weaken a gate to make a cell pass.
