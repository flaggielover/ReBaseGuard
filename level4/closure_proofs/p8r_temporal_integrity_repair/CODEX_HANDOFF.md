# P8R handoff to independent adjudication

**Read this as an attack plan, not a summary.** P8R is a repair campaign for a
campaign that failed its integrity spine, so the burden of proof is on the
repair. Claude's verdict in `results/verdict.json` is a **candidate**. It is not
authoritative and must not be promoted to `CLOSED` on this document's say-so.

`AUTHORITATIVE_STATUS_RECOMMENDATION = AWAIT_CODEX_ADJUDICATION`

## 0. What must not change

`P8 = FAIL` is authoritative and is not in question here. P8R cannot change it,
does not ask to, and any reading of this campaign that softens P8's verdict is a
misreading. `level4/closure_proofs/p8_model_class_robustness/` is a historical
protected artifact; if any byte of it differs from the pre-campaign manifest,
that alone is fatal (attack 16).

## 1. Attack the temporal anchor's authenticity

The claim: commit `ee61e240998e468eff66a076226eadc70109f9f5` contains the frozen
protocol, gates, plans, source and tests, and **no production scientific
result**.

Do not take `TEMPORAL_ANCHOR.md` at its word — it is written after the commit it
names, and it is deliberately excluded from `PROTOCOL_DIGEST.json` for that
reason. Check it directly:

```bash
git ls-tree -r --name-only ee61e24 -- level4/closure_proofs/p8r_temporal_integrity_repair/results
git cat-file -p ee61e24 | head
git merge-base --is-ancestor ee61e24 HEAD && echo ancestor
git log --format='%H %cI %s' ee61e24 -1
```

Expect exactly one path under `results/`:
`results/integrity/protected_tree_manifest_pre.json`. Anything else is a
finding. Also confirm the anchor is not a rewritten or amended commit: compare
its hash against `origin/main`'s history, which was pushed before production
began.

## 2. Attack the claim that no result existed before the freeze

Every result artifact records the `git_commit` it was produced at.

```bash
python - <<'EOF'
import json, subprocess, pathlib
R = pathlib.Path("level4/closure_proofs/p8r_temporal_integrity_repair/results")
for p in sorted(R.rglob("*.json")):
    d = json.loads(p.read_text())
    c = d.get("git_commit")
    if not c or c == "UNAVAILABLE": print("NO COMMIT", p); continue
    ok = subprocess.run(["git","merge-base","--is-ancestor","ee61e24",c]).returncode == 0
    print("OK " if ok else "BEFORE-ANCHOR ", c[:12], p.name)
EOF
```

Any artifact whose commit does not descend from the anchor is a finding. Also
check filesystem birth times against the anchor's commit time — they are weaker
evidence than git, but a result older than the anchor would be decisive.

## 3. Attack commit and digest integrity

```bash
cd level4/closure_proofs/p8r_temporal_integrity_repair
python scripts/make_manifests.py --stage final    # recomputes the protected tree
python -c "import json;print(json.load(open('SOURCE_MANIFEST.json'))['aggregate_sha256'])"
git show ee61e24:level4/closure_proofs/p8r_temporal_integrity_repair/SOURCE_MANIFEST.json | shasum -a 256
```

Then recompute every digest yourself rather than trusting `I2`/`I3`: hash each
file in `SOURCE_MANIFEST.json` and `PROTOCOL_DIGEST.json` and compare. A digest
file that agrees with itself proves nothing; a digest file that agrees with the
anchor blob **and** with the working tree is the claim.

Specifically check `src/rebaseguard_p8r/config.py`: it is the single authority
for every budget and every threshold, and `I7` stands or falls on it being
byte-identical to its anchor blob.

## 4. Attack calibration protocol consistency

This is the exact defect that failed P8. P8's protocol prose said 250,000 search
cycles and 2,048,000 verification cycles; its executable used 163,840 and
1,024,000.

* Re-derive the executed budget from `results/cal/<family>.json` **by hand**,
  from the `search_trace` and `verify_*` records, and compare it to
  `config.py`. Do not use `calibrate.executed_budget` — that is the thing under
  test.
* Check that `CALIBRATION_PLAN.md` quotes `config` and does not restate any
  number independently. A second statement of a budget anywhere is the P8 defect
  reappearing.
* Check that the number of S1 and S2 evaluations equals the declared iteration
  counts **exactly**, for every family, with no early stop.

## 5. Attack search/verification leakage

The claim: no calibration search ever read a verification address, and
`CAL_VERIFY_1` was read at most once per family.

* Walk every `search_trace` and `retry_trace` entry and confirm
  `address_class == "cal_search"`.
* Confirm `verify_1.experiment` is `p8r/cal_verify_1/sr_arl0` and
  `verify_2.experiment` is `p8r/cal_verify_2/sr_arl0`, never anything else.
* For any family with `outcome == "ACCEPTED_VERIFY_2"`, confirm that
  `verify_1.threshold` is the **rejected** threshold and differs from the final
  one. If a retried family's `verify_1` record shows the *accepted* threshold,
  the holdout was re-read — that is P8's `A2` all over again.
* Confirm no family has more than two acceptance evaluations, and none has more
  than one retry.
* Try to break the enforcement: call `calibrate._verify` with the search tag and
  confirm it raises, and call `primitives.stopped_address` with a bare or
  P8-style tag and confirm it raises.

## 6. Attack RNG address separation

* Recompute `sha256("p8r/<class>/<name>")[:8]` for every tag in
  `addressing.TAG_INVENTORY` and confirm pairwise distinctness yourself.
* Confirm that the class string is genuinely inside the hashed string — a class
  carried alongside the address rather than inside it would be decorative.
* Draw the same coordinates under `cal_search`, `cal_verify_1` and
  `production` and confirm the values differ.
* Run `scripts/rng_identity.py` and then try to defeat each check: change the
  live set, the execution order, the cache size, the request shape, `rho`, the
  shift, the detector, and confirm the delivered primitive does not move.
* Check that `primitives.chain_field_digest` takes no `rho` and no `shift`
  argument, and that the chain address omits `rho`, shift and drift pattern.

## 7. Attack the possibility of a result-driven amendment

* `git log --follow` every frozen prose file and `config.py`. Anything with more
  than one commit touching it after the anchor is a finding.
* Read `experiments/derive_resolution.py` for threshold literals. It should
  contain none; every number should come from `config`.
* Check that `FROZEN_GATES.md`'s thresholds match `config` numerically **and**
  that they match P8's `G3`, `G4`, `G4-D`, `G4-F`, `G7`, `G8`, `G10` where the
  question is the same one. A quietly loosened threshold on a question P8
  rejected is the single most likely way this campaign could be cheating.
* Check `S17_MAX_OUTLIERS` and `S8_ABS_TOL` in particular: both differ in form
  from P8's nearest gate. `REPAIR_RATIONALE.md` and
  `STATISTICAL_ANALYSIS_PLAN.md` §7 argue why; decide whether you accept the
  argument, and note that both were fixed at the anchor.

## 8. Attack source mutation after the anchor

```bash
git diff ee61e24 HEAD -- level4/closure_proofs/p8r_temporal_integrity_repair/src
git diff ee61e24 HEAD -- level4/closure_proofs/p8r_temporal_integrity_repair/experiments
git diff ee61e24 HEAD -- level4/closure_proofs/p8r_temporal_integrity_repair/tests
```

Expect empty. A test added after results is not automatically illegitimate, but
it is not anchored evidence either, and it changes `SOURCE_MANIFEST`'s
aggregate — so `I3` should have caught it.

## 9. Attack generator completeness

* Walk `results/**` and confirm every artifact has `generator`, `argv`,
  `git_commit`, `environment` and a `payload_sha256` that recomputes.
* Confirm every generator named actually exists and matches
  `audit_integrity.GENERATOR_MAP`.
* Confirm every `argv` corresponds to a command in `COMMAND_MANIFEST.json`.
* Look for the opposite failure: a command in the manifest with no artifact.
* Regenerate at least one cheap cell (`run_regularity.py`, or one
  `run_gamma_matrix.py` cell with `--force` into a scratch copy) and confirm the
  payload digest reproduces bit-for-bit. The addressable field is deterministic,
  so it should.

## 10. Attack the `Gamma` estimator

* Confirm `Gamma_A` is the raw convention-A window against the family score sum,
  and that it — not `Gamma_psipsi` and not `Gamma_naive` — is what every gate
  uses. Stage-D's `Gamma_psi` is a different estimand.
* Check the two exact anchors independently: with a degenerate zero threshold
  `tau = 1` and `Gamma_A = E[eps psi(eps)] = 1`; and the population value of the
  anchor construction is exactly `1 - 1/m`.
* Check the window orientation, the score sign (`psi = -f'/f`, `s = -psi`), the
  random truncated denominator `min(m,tau)`, and the inclusion of the terminal
  observation.
* Re-derive `rho_c = 1/|1 - Gamma_A|` and confirm the reported interval is the
  exact monotone image, not a delta-method approximation.

## 11. Attack the heavy-tail treatment

* `t3` has a divergent third absolute moment for the `Gamma` integrand. Confirm
  it is excluded from `S6`'s count in both directions and still fully reported.
* Confirm `S15` requires three independent intervals and that P8R does **not**
  claim attraction at `t3`/`m=20`. If `S15` came back `SUPPORTED`, scrutinise it
  hard: that would be a stronger claim than P8 was willing to make, on a cell
  outside P3's supported window grid.
* Check whether `S13`'s non-`t3` fraction is genuinely stricter than its
  all-cells fraction, and whether any seed-level overdispersion of the kind P8
  found (nominal SEs apparently underestimated) reappears.

## 12. Attack negative-result preservation

For each of `S7`, `S7D`, `S7F`, `S10`, `S12`, `S15` — the questions P8 resolved
negatively:

* confirm the threshold is numerically identical to P8's;
* confirm the resolution is reported in the wording the rule supports, with no
  softening ("approximately holds", "holds up to scale", "holds for most
  cells");
* if any of them came back `SUPPORTED`, treat that as the highest-priority
  finding in the campaign and re-derive it from the raw batch vectors yourself.

## 13. Attack any detector-transfer overclaim

* Confirm the ratios use the CRN-paired linearised SE and not an independent-SE
  formula. `results/scientific_resolution.json` stores `naive_unpaired_se`
  beside each `se` — check the difference is real and in the direction claimed.
* Confirm that nowhere in the prose is transfer assumed, and that the finding is
  scoped to the tested cells rather than stated as a general detector theorem.
* Note that a measured absence of transfer in these cells is not a proof of
  permanent non-equivalence; check that P8R does not say otherwise.

## 14. Attack any window-law overclaim

* Confirm `m in {10, 20}` never enters `S7`, `S7D` or `S7F`'s evidence.
* Confirm the spread statistic is `max/min - 1` over the eligible cells and that
  the eligible set is the declared one (10 `(D,f)` cells, `t3` excluded).
* Confirm no per-detector or per-family narrowing was used to rescue the law
  after the fact.

## 15. Attack the P3/P7 discrepancy treatment

P8 found its Gaussian SR estimates 0.70–0.80% below P3 while agreeing with P7,
and labelled it `KNOWN_PREEXISTING_DISCREPANCY` without resolving it.

* Check `S16`'s classification against the raw numbers.
* Confirm P8R does not claim to have resolved it, and does not quietly adopt
  either P3's or P7's number as correct.
* If `S16` came back `NEW_DEFECT_CANDIDATE`, that is a campaign-level finding
  and the surrounding results need re-examination.

## 16. Attack the protected tree

```bash
cd level4/closure_proofs/p8r_temporal_integrity_repair
python scripts/make_manifests.py --stage final
python - <<'EOF'
import json
a=json.load(open("results/integrity/protected_tree_manifest_pre.json"))
b=json.load(open("results/integrity/protected_tree_manifest_post.json"))
d={k for k in set(a["files"])|set(b["files"]) if a["files"].get(k)!=b["files"].get(k)}
print(sorted(d))
EOF
```

Expect at most the authorised root status file. Pay particular attention to the
per-tree aggregate for
`level4/closure_proofs/p8_model_class_robustness` — it must be unchanged.

Also verify independently that exactly one commit in the whole history touches
the P8 namespace:

```bash
git log --all --oneline -- level4/closure_proofs/p8_model_class_robustness
```

## 17. Attack novelty inflation

`NOVELTY_STATUS = NOT_ESTABLISHED`, and no independent novelty review was run.
Confirm that:

* nothing in the prose claims novelty, priority or a new algorithm;
* a new negative result is not presented as a contribution;
* a new empirical matrix is not presented as a discovery;
* the absence of a known transfer law is not presented as evidence of one being
  found here.

## 18. What P8R would look like if it were cheating

Worth checking explicitly, because these are the cheap wins a repair campaign
could take:

| cheat | where it would show |
|---|---|
| narrow the question so the failed hypotheses are out of scope | `DEFINITION_AUDIT.md` §3's factor table, against P8's protocol |
| loosen a threshold on a rejected hypothesis | `config.py` against the anchor blob, and against P8's `CLOSURE_GATES.md` |
| shrink a sample size so an interval widens and stops excluding the null | `PRODUCTION_PLAN.md` budgets against P8's §5 |
| declare an inconvenient cell out of scope after seeing it | `git log` on `config.py` and `FROZEN_GATES.md` |
| write the anchor commit after production and backdate it | `git log --format='%H %cI %aI'`, and the artifacts' recorded commits |
| add a "clarifying" test after results that changes a resolution | `git diff ee61e24 HEAD -- tests` |
| call a falsified hypothesis `INCONCLUSIVE` to avoid saying `REJECTED` | each question's frozen rule against its statistic |

## 19. Deliverable

An adjudication that states, independently: whether the anchor is authentic;
whether the calibration was leak-free; whether any threshold moved; whether the
protected tree held; whether each scientific resolution follows from its frozen
rule and the stored numbers; and one of `CLOSED`, `PARTIAL` or `FAIL` for P8R —
with the reasoning, and without deference to the candidate verdict.
