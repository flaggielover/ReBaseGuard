# Claim-language policy — evidence class to permitted wording

This **extends** the existing project firewall
(`level4/final_global_reaudit/CLAIM_FIREWALL.md`,
`docs/research_synthesis/CLAIM_CATALOG.md`); it does not fork it. Where the two
overlap the existing artifacts remain authoritative. P9 adds only the mapping
from the ledger's status vocabulary to permitted verbs, and the audit in §3.

Intended governance scope: `README`, paper/preprint, presentation, thesis, and
future campaign prompts.

---

## 1. The mapping

| status | permitted | forbidden |
|---|---|---|
| `EXACT_THEOREM` | "proves", "establishes", "it follows that" — **with the convention named** | dropping the convention ("proves that reuse is unstable" with no model named) |
| `FORMALLY_VERIFIED` | "machine-checked", "kernel-checked", naming **exactly** what was checked | "verified" applied to the surrounding science; implying the formal layer discharges the human obligations |
| `CONDITIONAL_THEOREM` | "under assumptions (A1)–(A7), proves"; "conditional on a stationary law" | "proves" bare; stating a converse that was narrowed |
| `CERTIFIED_NUMERICAL` | "certifies within [a,b]", "rigorously encloses" | "computes", "shows the value is" (drops the enclosure); implying the certificate proves the surrounding theorem |
| `EMPIRICAL_REPRODUCED` | "observed and independently reproduced in the tested regimes" | "always", "in general", any universal quantifier |
| `EMPIRICAL_ONLY` | "measured, on the stated finite grid, not independently reproduced" | "reproduced"; "robust"; extrapolation off the grid |
| `PARTIAL_PRIORITY_RESULT` | "the priority is PARTIAL; the following survived" | citing the priority as if closed |
| `NEGATIVE_RESULT` | "rejects the preregistered hypothesis under the tested conditions" | silence; "inconclusive"; using the failure as evidence for a weaker positive claim |
| `NOT_ESTABLISHED` | "not established"; may be named as an open item | any presentation as fact, including by implicature |
| `REJECTED_CLAIM` | "was asserted and rejected on adjudication" | restatement in softened form |
| `PROVISIONAL_P8_PENDING_CODEX` | "a Claude-side candidate result, not adjudicated" | use as a premise anywhere |

## 2. Four standing rules

**R1 — name the model.** Every headline sentence names the detector, `m`, the
convention, and Gaussian-vs-not. "The phenomenon is unstable" is never
permitted; "for the frozen two-sided Gaussian CUSUM with `m=1`, `rho=1`,
`k=1/2`, `h=5`, zero is locally repelling for the deterministic conditional-mean
map" is.

**R2 — never let a formal layer upgrade the science.** `THEORY.md` §1.4. Lean
does not certify a numerical interval; Arb does not prove differentiation under
the expectation. Say which layer did what.

**R3 — negative results appear in the same register as positive ones.**
`P4-F1/F2/F3`, `P5-F1`, `P7-R1`, `P7-R2` and `PROJ-L4R11` are results, not
caveats to be relegated to a final paragraph.

**R4 — separate the four novelty questions.** Scientific validity, operational
effectiveness, algorithmic novelty, theoretical novelty. A closure verdict
speaks only to the first two (`P6-NOV`, `P4-NOV`, `P5-NOV` are all
`NOT_ESTABLISHED`).

## 3. Audit of existing wording

P9 scanned `README.md` and `docs/research_synthesis/` for violations.

**The existing layer is well disciplined.** `CLAIM_CATALOG.md` carries an
explicit *"must not claim"* column; `LIMITATIONS_AND_OPEN_ITEMS.md` and
`RESULT_DEPENDENCY_GRAPH.md` name the forbidden over-readings
("universal safety or optimality", "distribution-free validity", "universal
absence of operational effects"). P6's pre-design goes further, registering
`rho_c` reintroduced as a fake safety rule as failure mode `F15` and excluding
it as `X1`. P9 found **no** instance of `rho < rho_c` presented as a safety rule
anywhere in the repository.

Findings:

| # | location | finding | class | P9 action |
|---|---|---|---|---|
| W-01 | `README.md:34` (at anchor) | "P6 has a pre-design directory only; its full campaign has not started" — false at `HEAD` | **omission / staleness**, not inflation | recorded (`D-08`); **not edited** — outside P9 scope. **Since fixed by the owner.** |
| W-02 | `README.md` Level-4 status table (at anchor) | no `P6` row, no `P8` row | omission | recorded (`D-08`); not edited. **Since fixed**: the table now carries `P6 = CLOSED` and `P8 = FAIL`. |
| W-03 | `README.md:51` | "an independent outward-rounded Arb certificate **proves** `Gamma_CUSUM > 2`" | **compliant** — an outward-rounded enclosure is a rigorous proof of a strict inequality, and the sentence explicitly adds "Together—not Lean or Arb alone" | none |
| W-04 | `README.md:158` | "P5 now proves those properties for the same frozen Gaussian constant-policy convention-A chain" | **compliant** — `P5-T7` is `EXACT_THEOREM` and the convention is named in the same clause | none |
| W-05 | `docs/research_synthesis/DEFINITIONS_AND_NOTATION.md:38` | "It **always** reuses exactly `m` observations and divides by `m`" | **compliant** — this is convention B's *definition*, not an empirical universal | none |

**No claim-class inflation was found in the published synthesis layer.** The
one real defect is staleness (`W-01`, `W-02`), which understates the campaign
rather than overstating it. P9 does not edit frozen historical artifacts to
harmonise prose; the correction is owed to whoever owns the publication layer
and is listed in `LIMITATIONS.md`.

## 4. Sentences P9 itself is forbidden to write

Recorded so the adversarial review can check P9 against its own policy:

* "P9 closes Level 4." — `U4`; P9 declares no status but its own.
* "P6 is closed." — `D-10`; repository says `PARTIAL`.
* "The phenomenon is robust across model classes." — P8 is `FAIL`; detector
  transfer is measured **absent** and the window law is **rejected**.
* "P8 partially closed." — the authoritative verdict is `FAIL`, and P9 must not
  describe P8 as a successful preregistered closure campaign.
* "`rho_c` is meaningless." — `P3-T1` is exact; `P9-T2` bounds its *use*, not its truth.
* "All cross-priority discrepancies are resolved." — three are `OPEN`.
* "The synthesis is novel." — `NOVELTY_AUDIT.md` returns `NOT_ESTABLISHED`.
