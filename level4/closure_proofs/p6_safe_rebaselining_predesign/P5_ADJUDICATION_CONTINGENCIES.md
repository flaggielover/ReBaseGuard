# P5 adjudication contingencies

```text
P5 STATUS AT WRITING = CLOSED_CANDIDATE / PENDING_CODEX
```

The purpose of this document is that **P6 does not need to know the verdict to
be designed**. Below, three branches; under each, exactly what changes. The
invariant is stated first, because it is the point.

---

## 0. The branch-invariant core

These survive every branch, because none of them depends on a `PROVISIONAL_P5`
row:

| # | invariant | rests on |
|---|---|---|
| V1 | The primary question (`README.md` §2) | — |
| V2 | The objective hierarchy and the three-layer discipline | `S1`, `S9`, `S18` — all closed |
| V3 | The observability audit in full, including the `-GammaTilde` sensor gain and the increment-observability result | `D1`–`D8`, `L1`, `L2`, `L4` — all closed |
| V4 | Baselines `B0`–`B11` and oracles `Z1`–`Z6` | frozen semantics only |
| V5 | Method families **A, B, C, D, E** | none is derived from a P5 theorem |
| V6 | The evaluation protocol, including the mandatory R1–R4 regimes | `S8`, `S9` — closed |
| V7 | The statistical design and compute plan | — |
| V8 | Every forbidden premise `X1`–`X12` | `S11`, `S18`, `X4`, … — closed or definitional |
| V9 | The novelty-audit plan | — |

**Only these are affected by the verdict:** Family F; theory targets T6-A
through T6-E; whether objectives may be written in stationary form; and whether
P5's provisional numbers may be used for grid selection.

---

## Branch A — P5 CLOSED strongly

*Trigger:* Codex accepts T1, T2, T5, T7 and T11 as exact, and T8–T10 as
conditional theorems on (H1)–(H3) as stated.

| change | detail |
|---|---|
| Stationary objectives become well-posed for **fixed-`rho`** policies | `E_pi[e^2]`, `E_pi[|e|^p]`, `P_pi(|e| > c)` are all finite and unique by `P1` (T7). `OPTIMIZATION_FORMULATIONS.md` may use the stationary version for baselines `B0`–`B4` |
| **Still not** well-posed for state-dependent policies | `H7` is untouched by the verdict. `T6-B` remains mandatory before any adaptive-policy stationary claim. **This is the single most likely place for P6 to over-claim on a good P5 verdict** |
| Family F becomes derivable | the greedy rule `rho_opt = (1/k)/(R^2+S+1/k)` is grounded, and `T6-A`, `T6-C` (one-step half), `T6-D` (routes 1–2) become reachable |
| P7-B/C/D become unconditional in this model | `S16`, `S17` lose their stationary-law hypotheses; useful for diagnostics, not for objectives |
| `R` and `S` tables become citable | Family A's plug-in variance proxy and Family E's likelihood may cite them rather than re-measuring — **but P6 should still re-measure them on its own seed family**, because the P5 tables are grid-interpolated (PCHIP) with an unquantified error budget (`p5/LIMITATIONS.md` §6) |
| P5's `rho*` values become citable as **prior information for grid design only** | `X9` still forbids them as design constants or gate thresholds. Grid design is exactly what `E2` already licenses from the *closed* `S12` |

**What must still be re-verified by P6 even in Branch A:**
`P8` (RMS/ARL co-optimality — P5 asks for this explicitly), `P7` under
`Delta > 0` (P5 worked entirely at `Delta = 0`, `p5/LIMITATIONS.md` §1), and
`P9` beyond `m = 5`.

---

## Branch B — P5 CLOSED but narrowed

*Trigger:* the invariant-law theorem (T7) survives, but the bifurcation/optimum
material is narrowed — e.g. (H2)/(H3) judged insufficiently supported, so
T8–T10 are downgraded; or the `rho*` optimum is judged a grid artefact; or the
T11 residual (`16` chain s.e.) is judged unresolved.

| change | detail |
|---|---|
| Keep everything in Branch A that comes from T1/T2/T5/T7 | the distribution-control programme is intact |
| **Discard every bifurcation-derived design idea** | there were none by construction (`X2`), so nothing is lost. This is the payoff of having refused to build on T9/T10 in the first place |
| Discard `P7`/`P8` as prior information | the `rho` grid then rests on `S12` and `E2`, which are **closed** P7 facts and independently justify resolving `[0.10, 0.35]` |
| Family F survives | it needs T1/T2 only, not the bifurcation analysis |
| `T6-D` route 2 weakens | it wanted a handle on the selection effect that (H2)/(H3) were part of |
| Diagnostics using `Gamma_eff` / `ACF1` are demoted to reporting | they already were (`SAFETY_OBJECTIVES.md` Tier 3) |

**Branch B is the cheapest branch for P6**, and that is by design: the
pre-design deliberately built nothing on T8–T12.

---

## Branch C — P5 PARTIAL (stationary-law theory does not survive)

*Trigger:* T7's two-step Doeblin construction is rejected or materially
narrowed — e.g. the minorisation is found not to be uniform in `e`, or the
`{tau=1}` argument fails for some `m` — so existence/uniqueness of `pi` reverts
to the *evidenced-but-unproved* state P7 recorded (`S19`).

This is the branch the pre-design was written to survive. The changes:

| change | detail |
|---|---|
| **Every objective is rewritten in finite-horizon form** | `(1/J) sum_{j=1}^{J} E[.]` over a preregistered `J`, with the burn-in stated as an empirical choice and never as a mixing guarantee. `SAFETY_OBJECTIVES.md` §3 estimators already have this form — they are per-replicate averages over `J` cycles — so **the change is to the language, not to the code** |
| No stationary-law language anywhere | no `E_pi`, no "invariant law", no "long-run"; the R4 regime is renamed the *late-cycle* regime and is reported with its own convergence diagnostics |
| `T6-B` becomes the campaign's *open problem*, not a target | and P6 says so |
| `T6-A` survives in conditional form | it is a one-step conditional statement; if T1/T2 also fall, it survives as an empirical one-step law estimated by P6 |
| Family F survives as an **empirical** rule | `R^2 + S` is replaced by a P6-measured conditional second moment of `zbar` given the observables. The method is the same; the *novelty claim* weakens from "derived" to "empirically calibrated" (`METHOD_NOVELTY_SEPARATION.md`) |
| Family B's one-step tail proxy is estimated, not derived | more expensive, same design |
| The R3 finite-cycle regime becomes the **primary** evidence | it was already mandatory (`S8`); in Branch C it carries the weight that R4 carried elsewhere |
| Extra compute | roughly `+20%`, for the empirical one-step-law tables and the longer convergence diagnostics |

**What does not change in Branch C:** the primary question, the objectives, the
observability audit, the baselines, the oracles, the evaluation protocol, the
failure register, and the compute plan's shape. That is the test this pre-design
was built to pass.

---

## Branch D — the unplanned case

If Codex returns a verdict that does not fit A/B/C — for instance, if it finds a
defect in the **frozen semantics** rather than in P5's reasoning (an error in
the convention-A implementation, or in the correspondence between the P5 chain
and the P7 chain) — then P6 does **not** proceed on a patch. The frozen core is
shared with P1–P3 and P7, so such a finding invalidates the ledger's §1 and §4,
and the correct response is to halt P6 and re-open the affected campaign.

The entry gate (`FULL_CAMPAIGN_ENTRY_GATE.md` item 3) makes this explicit so
that it cannot be resolved informally.

---

## 5. Execution procedure on the day the verdict arrives

1. Record the verdict verbatim in `results/p5_verdict.json` with the adjudicator
   and date.
2. Rewrite `DEPENDENCY_LEDGER.md` §5: each `PROVISIONAL_P5` row is promoted to
   `AUTHORITATIVE_CLOSED`, restated in its narrowed form, or moved to
   `NOT_ALLOWED_AS_PREMISE`. **Rows are never left at `PROVISIONAL_P5`.**
3. Select the branch and apply its table above.
4. Delete from `P6_METHOD_CANDIDATES.md` and `P6_THEORY_TARGETS.md` anything
   whose stated P5 dependence was rejected. Deletion, not weakening.
5. Re-read this document's §0 and confirm every `V` invariant still holds.
6. Only then execute `FULL_CAMPAIGN_ENTRY_GATE.md`.

Steps 2 and 4 happen **before** any P6 experiment runs, and are committed as a
separate change so the "what we believed when we designed the campaign" state is
recoverable.
