# P9 novelty audit — project level

```text
P9_SYNTHESIS_NOVELTY      = NOT_ESTABLISHED
NEW_SEARCH_RUN_BY_P9      = NONE
POSITION                  = inherited from the repository's own campaigns, conservatively
```

**P9 ran no new literature search.** Two reasons. First, the repository already
contains a far more thorough search than P9 could add to. Second, prompt §20
forbids inferring novelty from the absence of an exact phrase — and a synthesis
priority re-running a thin search would do exactly that. P9's contribution here
is to **separate the novelty questions and refuse to let closure imply any of
them**, not to advance a novelty claim.

## 1. What the repository already established

`level4/closure_proofs/novelty_verification/FINAL_REPORT.md`:

```text
NOVELTY-VERIFICATION-CLOSED
N2 — PARTIAL-OVERLAP-FOUND-CLAIMS-NARROWED
```

* Indexes: Crossref, OpenAlex completed; Google Scholar and Semantic Scholar
  recorded `ACCESS-UNAVAILABLE`.
* **2445** unique works inspected after deduplication; **33** classified.
* **DIRECT: 0.** **HIGH-PARTIAL: 9** (W01, W03, W05, W06, W08, W10, W14, W25,
  W33). Two snowball rounds added no new DIRECT or HIGH-PARTIAL.
* Strong partial overlap in exactly the close classes prompt §20 names:
  self-starting/adaptive CUSUM, adaptive SR, post-CUSUM estimation bias,
  nonanticipating unknown-parameter detection, multi-cyclic detection,
  forgetting/reset systems, adaptive drift windows.
* **Claims were narrowed**: adaptive reference updating, post-alarm estimation,
  repeated detection, reset maps and adaptive reference windows "may not be
  described as if introduced by ReBaseGuard".

`p6_safe_rebaselining/NOVELTY_AUDIT.md` is more negative still, and P9 endorses
its framing:

```text
ALGORITHMIC_NOVELTY  = OVERLAPPING (the weight-adaptation SHAPE has close prior art)
THEORETICAL_NOVELTY  = PLAUSIBLE, NOT ESTABLISHED
```

P6 states outright that the closest prior art is adaptive EWMA (Capizzi &
Masarotto, *Technometrics* 45(3), 2003), and that a reader who stops at "SAW
makes the reuse weight a decreasing function of `|zbar|`" is entitled to call it
a renamed AEWMA. That audit was executed **before** confirmation numbers were
read. P9 does not soften it.

The independent adjudication then set `NOVELTY_STATUS = NOT_ESTABLISHED` for P6,
and P4 and P5 both carry `NOVELTY-NOT-ADJUDICATED`.

## 2. The four questions, kept separate

Prompt §16's distinction, applied across the project:

| question | position | basis |
|---|---|---|
| **scientific validity** | supported within frozen scope for P1/P2/P3/P7; `PARTIAL` for P4/P5/P6 | adjudication records |
| **operational effectiveness** | measured and replicated **in a synthetic frozen model**; regime-scoped semi-real evidence; no production validation | `P6-EMP`, `P7-E1` |
| **algorithmic novelty** | **`NOT_ESTABLISHED`** — and P6's own audit reports it as `OVERLAPPING` | `P6-NOV` |
| **theoretical novelty** | **`NOT_ESTABLISHED`** — "plausible" is not established | `P6-NOV`, `P4-NOV`, `P5-NOV` |

**A closure verdict speaks only to the first two.** P6's closure, if it ever
comes, is not a novelty claim — and P6 is `PARTIAL` in any case (`D-10`).

## 3. Novelty of the P9 synthesis itself

| component | position |
|---|---|
| the claim ledger | **not novel** — a project-management artifact |
| `P9-T1` (no-inflation bound) | **not novel** as mathematics (a minimum over a DAG). The `verifies`/`premise` distinction is a defensible modelling choice; provenance-and-evidence-graph work is an established field (argumentation frameworks, provenance calculi, proof-carrying claims) and P9 ran **no** search against it. `NOT_ESTABLISHED`. |
| `P9-T2` (separation) | **not novel** in mechanism. That an *estimated* reference degrades a chart calibrated for a known one is the core observation of the entire self-starting / unknown-parameter control-chart literature — one of the HIGH-PARTIAL families already identified. P9's contribution is to make it **exact for this frozen model** and to draw the specific corollary that no `rho` threshold can be an operational safety boundary. Whether *that corollary* is new is **`NOT_ESTABLISHED`**; no search was run. |
| `P9-N1` (oscillatory transient) | **not novel** — slow oscillatory approach to stationarity is unremarkable for such a chain. Reported as a measurement and a convention warning, not a discovery. |

## 4. What must not be said

* Not "ReBaseGuard introduces recursive re-baselining." Partial overlap is
  documented across nine HIGH-PARTIAL works.
* Not "the safe re-baselining policy is novel." `OVERLAPPING`.
* Not "P9 proves a new theorem about monitoring." `P9-T2` reorganises exact
  claims that already existed; it introduces no new premise, by design.
* Not "no prior work covers this." Two major indexes were `ACCESS-UNAVAILABLE`
  in the original search, and P9 added nothing.

## 5. The honest floor

What the repository can defend is **integration**: the specific combination of
the stopping-selected post-alarm cross-cycle reference-reuse mechanism with the
frozen model's certified derivative core, its stationary theory, and its
operational evaluation. The original campaign called this the "honest floor" and
recorded that its strongest neighbours (W08 on paper, W25 in practice) do not
cover the complete mechanism together with `C3`–`C9`.

P9 adopts that floor unchanged and adds nothing to it.
