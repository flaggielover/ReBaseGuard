# P9R handoff to Codex — twenty attacks

P9R submits `CLOSED_CANDIDATE`. It does not self-promote. Adjudicate it.

Nothing in this namespace should be taken on trust, including
`TEMPORAL_ANCHOR.md`. Every claim below names the artifact and the command that
settles it.

```text
anchor      c1e8f98bb908aff095814f3c45994ecc0f0846ed   (Checkpoint A, pushed)
completion  see git log --oneline -1                    (Checkpoint B)
P9  = PARTIAL (a3e3cab)   P8 = FAIL (5411e2c)   P8R = CLOSED (dc85167)
```

Recompute every integrity gate with:

```bash
level4/.venv/bin/python level4/closure_proofs/p9r_final_synthesis_repair/scripts/audit_integrity.py --anchor c1e8f98bb908aff095814f3c45994ecc0f0846ed
```

---

## 1. Anchor authenticity

Do not read `TEMPORAL_ANCHOR.md` for this. Run
`git ls-tree -r --name-only c1e8f98 -- level4/closure_proofs/p9r_final_synthesis_repair`.
Assert that the only `results/` entry is `results/integrity/protected_tree_manifest_pre.json`,
that `FROZEN_PROTOCOL.md`, `FROZEN_GATES.md`, `THEORY.md`,
`experiments/ledger_schema.py`, `experiments/claims_source.py` and every
generator are present, and that `c1e8f98` is an ancestor of `HEAD` and was
pushed before any result artifact's recorded `git_commit`. Then diff every path
in `SOURCE_MANIFEST.json` and `PROTOCOL_DIGEST.json` against the anchor blobs.
**Attack:** find any anchored scientific source that changed after the anchor.

## 2. Original P9 immutability

`git log --format=%H -- level4/closure_proofs/p9_final_synthesis` must return
exactly `a3e3cab`. `git rev-parse HEAD:<that path>` must equal
`git rev-parse a3e3cab:<that path>`. **Attack:** find any byte of P9 that moved,
or any P9R document that reads as if `P9 = PARTIAL` had been amended.

## 3. `P9R-T2a` exactness

`THEORY.md` §2. Check each step: the constant kernel at `rho = 0` and its unique
invariant law (`P5-T1`, `P5-T7`); the finite-cycle identity applied to that law
(`P7-A-ID`); integrability from Lemma L2 rather than from an assumption; the
multiplier from `P3-T1`. **Attack:** find an inequality, an operational
conclusion, or a smuggled monotonicity step anywhere inside `T2a`. Also check
that `T2a` really needs no `m`-dependent hypothesis, since it is claimed for all
`m >= 1`.

## 4. `P9R-T2b`'s premise

`ASM-DOM` is `A(e) <= A(0)` a.e. **Attack:** (a) is `ASM-DOM` genuinely weaker
than global monotonicity, as claimed? (b) is the strictness argument really
free — do Lemmas L3 and L4 suffice without any upper bound? (c) is Lemma L4's
`A(e) -> 1` argument correct for **both** detectors, including the SR case?
(d) does anything downstream use the strict deficit without carrying the
hypothesis?

## 5. Hidden exact monotonicity

Rule `V11` forbids monotonicity wording in any `EXACT_THEOREM` statement, and
rule `V2` forbids an exact theorem from carrying an `ASSUMPTION` edge. **Attack:**
grep the whole namespace for monotonicity language and check every occurrence
sits in a `CONDITIONAL_THEOREM`, `EMPIRICAL_ONLY`, `NOT_ESTABLISHED` or
`ASSUMPTION` context. Check `P7-A-ID`'s statement in particular — P9's `P7-A`
row is where the promotion lived.

## 6. SR first-step recurrence

`THEORY.md` §5 and `results/sr_recurrence_check.json`. Re-derive `ell_1` and
`y_1` by hand from `R_0 = 0` and compare with
`src/rebaseguard_p9r/detectors.py::sr_step` and `sr_initial_state`. **Attack:**
show the repaired form is not the frozen `_sr_update` of
`level4/stage_d/src/stopped.py`, or that `tests/test_sr_recurrence.py` merely
re-runs the generator instead of re-deriving the numbers independently.

## 7. Reset recurrence

A cycle reset must restore `y = 0`, so the first post-reset update must be
identical to the first update of cycle one. Check `chain.py`'s reset path uses
`init(...)` and not a stale state, and that the buffer, position and time
counters reset with it. **Attack:** find a per-replicate reset that leaks state
across a cycle boundary.

## 8. Corrected SR reproduction

`REPRODUCTION.md` §3 and §5. Targets must come from P7's `consequences.json` at
run time under P7's own `n_rep`/`n_cycles`/`burn_in`. **Attack:** recompute a
cell with your own implementation; check the combined-SE `z`; check that the
paired defective replay really used the same seed; and check that the
`IMMATERIAL` `S5` verdict is not being used to excuse the defect — `REPRODUCTION.md`
§5 must say the sign is systematic and that the defect is unbounded for
per-path quantities.

## 9. A5/A6 generator completeness

`results/burnin_sensitivity.json` and `results/response_grid.json` must each
name a generator that exists in `SOURCE_MANIFEST.json`, and their
`payload_sha256` must verify. **Attack:** run
`experiments/run_response_grid.py --quick` twice and confirm the payload digest
is stable; find any file under `results/` without a generator; check that the
quadrature error budget's truncation term really follows from Lemma L2 and is
not an estimate dressed as a bound.

## 10. `P3-X1` classification

`CERTIFIED_NUMERICAL`, not `FORMALLY_VERIFIED`. **Attack:** read
`level4/closure_proofs/m_rho_stability_priority3/LEAN_CORRESPONDENCE.md` and
`CLOSURE_REPORT.md` §5 and decide whether `CERTIFIED_NUMERICAL` is the right
class or whether an even weaker one is warranted, given that the witnesses are
exact rational arithmetic and the Arb ball is used only as a consistency
enclosure.

## 11. `P7-A` / `P7-D0` split

Five nodes: `P7-A-ID`, `P7-A-MONO`, `P7-A-OP`, `P7-D0-ID`, `P7-D0-DEF`.
**Attack:** is the exact part of `P7-A` correctly identified — does the
finite-cycle identity really hold without any monotonicity? Is `P7-D0-ID`
genuinely identity-only? Does any downstream node take the empirical or
monotonicity half where it should take the identity half?

## 12. Claim-ledger source traceability

Every row in `experiments/claims_source.py` cites a path and a section.
**Attack:** open the cited section for a sample of rows across every class and
check the statement is actually what the source says. Pay particular attention
to `P1-T1` (downgraded to `CONDITIONAL_THEOREM` on the authority of P1's own
definition audit — is that right, or is it too harsh?) and to `P2-T1` (kept
`EXACT_THEOREM` on the authority of `ASSUMPTION_DISCHARGE.md` — are all eight
obligations really discharged?).

## 13. Dependency-edge semantics

Eleven typed edge types; only `LOGICAL_PREMISE` and `ASSUMPTION` constrain
strength, and `ASSUMPTION` caps at `CONDITIONAL_THEOREM`. **Attack:** is that
cap justified, or does it let a conditional theorem stand on an assumption of
rank 0 without penalty? Is any edge mistyped — a premise recorded as
`EMPIRICAL_SUPPORT` to dodge `V1`, or a scope restriction that is really a
premise? Re-run the collapsed diagnostic and check the 36 violations are the
ones the argument claims.

## 14. `PARTIAL` / `FAIL` premise propagation

Rules `V9a`/`V9b`/`V9c`. **Attack:** find a claim used at a strength its
priority's adjudication does not license; or, conversely, find surviving
evidence P9R wrongly discarded because its priority failed.

## 15. P8 versus P8R

Gate `I12` computes the premise/assumption closure of `P9R-T2a` and `P9R-T2b`
and asserts it contains no P8 or P8R node. **Attack:** recompute that closure;
find any P9R sentence in which `P8R = CLOSED` reads as changing `P8 = FAIL`, or
in which P8R evidence is cited as P8, or in which P8R is read as implying
model-class transfer.

## 16. `D-09` / `D-13` / `D-15`

`DISCREPANCY_REGISTER.md`, frozen at Checkpoint A so the rulings cannot have
been shaped by results. **Attack:** is `DOES_NOT_BLOCK_P9R` right in each case?
In particular, does any P9R claim depend, even indirectly, on `P5-T11`'s plug-in
(`D-13`) or on P3's grid (`D-15`)?

## 17. Formal / certified / empirical firewall

**Attack:** verify the four `FORMALLY_VERIFIED` rows against actual Lean
declarations, axiom audits, and absence of `sorry`; verify `P2-C1`'s interval
against the Arb certificate and its replay; verify that no empirical row is
written in theorem language. Check that P9R claims **no** formal or certified
status for anything it produced itself — it should not, and that is deliberate.

## 18. Novelty

`NOVELTY_STATUS = NOT_ESTABLISHED`. **Attack:** find any sentence anywhere in
the namespace that reads as a novelty claim, or any use of the 2445-work search
as evidence *for* novelty rather than as prior-art evidence.

## 19. Protected tree

`results/integrity/protected_tree_manifest_pre.json` versus
`..._final.json`: 3428 tracked files outside the P9R namespace, zero
differences. **Attack:** recompute independently; check the protected-tree list
covers every namespace it should, including `p9_final_synthesis` and
`p8r_temporal_integrity_repair`; check no root status file was quietly edited.

## 20. Global-closure overclaim

`LEVEL4_GLOBAL_CLOSURE = NO` and
`AUTHORITATIVE_STATUS_RECOMMENDATION = AWAIT_CODEX_ADJUDICATION`. **Attack:**
find any sentence implying that a `CLOSED` P9R would close Level 4, repair P4,
P5 or P8, or resolve the mandatory requirement ledger. It would close the
Priority-9 **repair** lineage and nothing else.

---

## What a fair `FAIL_CANDIDATE` would look like

Per `FROZEN_GATES.md`: temporal integrity failing (`I1`), original P9 mutated
(`I2`), or the recurrence still wrong (`I5`). Per the repair mandate: claim
inflation persisting, or required reproducibility still broken.

## What a fair `PARTIAL_CANDIDATE` would look like

Any other mandatory integrity gate failing, or a repair obligation found
unresolved — for example if `ASM-DOM` turns out to be discharged somewhere in
P1-P7 and P9R missed it (which would make `P9R-T2b` needlessly conditional), or
if a ledger row is found to misstate its source.

## What P9R believes it has earned

Every identified P9 defect repaired; a clean exact/conditional split with the
one open premise named, weakened, and made a graph node; a rebuilt and
independently tested SR recurrence; both orphan artifacts given generators and
a quantified error budget; a source-derived, source-traceable ledger with a
validator that constrains classes rather than grading them; and a valid,
pushed, pre-result temporal anchor. Nothing stronger is claimed.
