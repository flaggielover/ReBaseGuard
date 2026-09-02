# P8R — Level-4 Priority-8 temporal-integrity repair

**This is a new, independent repair campaign. It is not a rewrite of P8, and it
does not and cannot change P8's verdict.**

> The authoritative status of Priority 8 is and remains **`P8 = FAIL`**, fixed by
> `level4/closure_proofs/p8_model_class_robustness/INDEPENDENT_ADJUDICATION.md`
> at commit `5411e2c7c5ff9af2fb983a5b5a48c1e360bca2e8`. That namespace — its
> protocol, its gates, its results, its adjudication and its `FAIL` verdict — is
> a historical protected artifact. Nothing in P8R modifies a single byte of it,
> and gate `I11` proves that at the end of every run.

## 1. What P8R is for

P8 produced a substantive, independently reproducible body of evidence and then
failed its own integrity spine. Gate `G14` failed for five linked reasons:

1. no pre-result temporal anchor — the entire P8 tree was untracked, so nothing
   in repository history separated "protocol written" from "results obtained";
2. the frozen protocol declared an SR calibration budget (250,000 search cycles,
   2,048,000 verification cycles) that the executable and the artifacts never
   used (163,840 and 1,024,000);
3. amendment `A2` was recorded **after** a verification result was inspected —
   a result-driven protocol change;
4. that amendment then re-verified a retuned threshold at the *same* address the
   first verification had already used, destroying holdout independence;
5. the provenance record hashed neither the protocol, nor the gates, nor the
   source as it stood when each result was produced, so frozen-protocol
   integrity could not be independently established at all.

P8R reruns the same scientific question under a protocol that makes each of
those five failures structurally impossible, and reports whatever survives.

**P8R is not an attempt to turn negative results positive.** The window-
separability law, the sub-gates on detector and family invariance, literal P7
boundary transfer, measured detector transfer and the `t3`/`m=20` attraction
claim were *scientific* findings in P8, not procedural ones. They are re-asked
under the frozen rules and reported honestly. A hypothesis that is false stays
false; §8 of `FROZEN_GATES.md` makes that an admissible, resolved outcome rather
than a campaign failure.

## 2. The scientific question (unchanged from P8)

> Does the recursive re-baselining structure established for the two frozen
> Gaussian specialisations — the stopped-selection gain `Gamma`, the local
> stability boundary `rho_c`, and the operational monitoring degradation —
> survive outside that specialisation, across innovation-distribution families,
> detector families, reuse windows, reuse conventions and drift patterns, and
> which parts fail to transfer?

`DEFINITION_AUDIT.md` establishes that this is the question P7 and the P6
pre-design actually handed over, and that P8R has not quietly narrowed it.

## 3. The repair, in one paragraph

Four disjoint RNG **address classes** — `CAL_SEARCH`, `CAL_VERIFY_1`,
`CAL_VERIFY_2`, `PRODUCTION` — are carried in the address itself, so a
calibration search cannot read a verification address and a calibration cannot
read a production address, by construction rather than by discipline. The SR
calibration is a **fixed-length, non-adaptive** two-stage search followed by a
single held-out acceptance test, with **one** frozen retry ladder declared
before results and no third attempt; a family that fails both holdouts is
recorded as `CALIBRATION_FAILED` and excluded, not retuned. Every budget lives in
exactly one place (`src/rebaseguard_p8r/config.py`), and gate `I13` re-derives
what was executed from the stored trace and compares it. The protocol, the
gates, the plans, the whole executable surface and every test are committed —
with their SHA-256 digests — in a commit that contains **no production result**,
and gates `I1`, `I2`, `I3`, `I6` and `I7` check that against git, not against a
self-report.

## 4. Layout

| path | what it is |
|---|---|
| `REPAIR_RATIONALE.md` | the P8 defect, the repair, and what is deliberately *not* repaired |
| `DEFINITION_AUDIT.md` | that the question is inherited, not invented or narrowed |
| `FROZEN_PROTOCOL.md` | the frozen scientific question, factors, estimands and scope |
| `FROZEN_GATES.md` | integrity gates `I1`–`I13`, resolution questions `S1`–`S17`, the closure rule |
| `CALIBRATION_PLAN.md` | the single authoritative calibration procedure and retry ladder |
| `RNG_ADDRESS_PLAN.md` | the four address classes and their disjointness argument |
| `PRODUCTION_PLAN.md` | every production experiment, budget and command |
| `STATISTICAL_ANALYSIS_PLAN.md` | estimators, pairing, intervals, multiplicity, heavy-tail policy |
| `TEMPORAL_ANCHOR.md` | the anchor commit, digests, environment and the exact commands |
| `COMMAND_MANIFEST.json` | the production commands, verbatim, declared before production |
| `SOURCE_MANIFEST.json` | SHA-256 of every executable file at the anchor |
| `PROTOCOL_DIGEST.json` | SHA-256 of every frozen prose artifact at the anchor |
| `RESULTS.md` | what the rerun found — including what it did not find |
| `LIMITATIONS.md` | what this campaign does not establish |
| `CODEX_HANDOFF.md` | the seventeen attacks an adjudicator should run |
| `src/rebaseguard_p8r/` | the campaign library |
| `experiments/` | production drivers; every result artifact names one |
| `scripts/` | manifests, RNG identity, integrity audit |
| `tests/` | the focused suite, committed at the anchor |
| `results/` | every production artifact, each with a provenance envelope |

## 5. Verdict semantics

P8R emits exactly one of `CLOSED_CANDIDATE`, `PARTIAL_CANDIDATE` or
`FAIL_CANDIDATE`. **A candidate verdict is not authoritative.** It must not be
promoted without independent adjudication; `results/verdict.json` records
`AUTHORITATIVE_STATUS_RECOMMENDATION = AWAIT_CODEX_ADJUDICATION`.

`NOVELTY_STATUS = NOT_ESTABLISHED`. P8R is a repair campaign; no independent
novelty review was run, and a repair does not generate novelty.
