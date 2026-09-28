# Addendum to the incident audit: the conditions of the independent review (C1–C6)

**Context.** `review/INCIDENT_INDEPENDENCE_REVIEW.md` (committed alone at `c9ff8e3e`) accepted the five conclusions
(INCIDENT_AUDIT_ACCEPTED). Its line-2 verdict holds only with conditions C1–C6, which must be met before the freeze
and carried into the protocol, the grant and the adjudication. This addendum meets them.
* The reviewed audit `audit/INCIDENT_AUDIT_RLR307.md` stays as reviewed.
* Where the addendum corrects or extends the audit, **the addendum prevails.**

## C1: extended incident disclosure

**The audit's inventory was incomplete.** Besides L1–L6 (audit §1) and the non-incident exposures of audit §3, two
qualitative, cell-307-specific exposures of the RLR channel (A1/A2) exist.

* **F1(a): an unledgered, uncommitted B_307 adjacency.**
  * `p5y_k5_tail_overnight_research/streams/B_307/PROGRESS.md`, row 2026-09-27T20:20Z, records an "incident-01
    correction (coordinator, binding)". Stream B_307's pre-commit drafts had placed committed tail-cell shares next to
    route and synthetic factors. The places were:
    * HIGHER_ORDER_AUDIT_307 §2–6;
    * REAL_ORDER3_THEORY §4c;
    * the per-cell (307) section of the route summary.
  * The coordinator's instruction that triggered it is the SendMessage of 2026-09-27T18:50:21Z to the B_307 agent,
    "Remove tail-share x route-factor combination". Its hash is listed below; it is not reproduced here because it
    names shares.
  * The draft content was never committed. The first B_307 commit, `01738aed`, is post-correction. The content is
    therefore **unverifiable**.
  * It predates every real-kernel RLR value (first at `2b118e62`). At most it paired synthetic or fixture factors with
    cell-307 shares.
  * It is recorded now in this campaign's ledger as one DISCLOSURE line. The overnight ledger cannot be edited.
* **F1(b): a co-location still committed at HEAD.**
  * `streams/B_307/HIGHER_ORDER_AUDIT_307.md` §0 quotes cell 307's committed C3/C4 knockout record, its certified A0,
    its per-term radius shares and C2's magnitude elasticities.
  * §2 (HO-5, HO-6) and §3 of the same file state the LR route's asymptotic gap orders, and §5 states fixture rung
    ratios for A1/A2.
  * The same pattern appears in `B_307_ROUTE_SUMMARY.md` (per-cell 307 section) and in the idea note (synthetic LR
    ratios beside "307 blocker is (A1, A2)").
  * Nothing was combined into a number. No LR-stream artifact cites these files, and no RLR parameter depends on them
    (review §2, rows 3–4).

**Corrected counts.** The overnight record has four ledgered qualitative proxy exposures (L1–L4) plus two ledgered rule
breaches (L5, L6). It has, in addition, **one unledgered, uncommitted B_307 adjacency of unverifiable content**
(F1(a)). F1(b) is a committed co-location of the same class as L4. It is listed here, and it is not a separately
ledgered incident.

**Meaning of "independent".** For this campaign, "the RLR design existed independently of target outcome" means
**temporal and parametric independence only**:
* every load-bearing element predates the handover;
* no parameter was selected by a target quantity.

It does **not** mean motivational independence. The route, its channel (A1/A2) and its cell (307) were chosen knowing
committed cell-307 facts: the C3 knockout, the C3/C5 shares and the C8/C9 factors. **Result-chasing risk: MEDIUM.**

## C2: decoy probe

* **Classification.** Every `evidence/explore/TIMING_*.json` output, and the pool dev test
  `evidence/explore/DEVTEST_POOL_297_d4.json`, is in the latent-proxy class. See
  `config/LATENT_PROXY_AMENDMENT_307.json`, which is stricter-only.
* **Ledger.** Each run is ledgered with its output's sha256 at completion.
* **Commit.** The outputs are committed before the freeze.
* **Use.** The protocol (§3.2) uses decoy **runtime, memory and certification status only**. No decoy certified value
  enters any parameter or is placed next to a tail-cell number.
* **Distance rule.**
  * The qualification decoys are:
    * the committed block [1/2, 17/32];
    * cover cell 297 (QC02–QC04).
  * No decoy lies closer to the band than cell 297's hull. Cell 297 itself is the reviewer's reference point.
  * Any further decoy must be declared in the protocol and obey the same bound.

## C3: latent-proxy list

`config/LATENT_PROXY_AMENDMENT_307.json` adds `streams/C_308/LR/cusum/PROGRESS.md` to the latent-proxy class. It also
adds this campaign's decoy and qualification records. The overnight files are not edited.

## C4: the overnight briefs

**They were not in the committed record.** They existed only in:
* the session scratchpad (`SCR/PREAMBLE.md`);
* the session transcript (the agent prompts and coordinator messages).

**Now:**
* `audit/overnight_briefs/BRIEF_HASHES.json` records the sha256 of all of them: the RLR-related ones, the B_307 brief,
  and every coordinator SendMessage of the overnight session.
* For each, it records the count of hits of five tail-number patterns: committed C8/C9 factors, share percentages,
  cell 307's endpoints, "307", and a 3 % scale. The counts are recorded, never the matches.

**Committed verbatim.** Every RLR-related brief has zero hits and is committed in `audit/overnight_briefs/`:
* `SCR_PREAMBLE.md`;
* the C1, C1a and C1b stream briefs;
* the RLR review briefs R1, R2 and R3;
* the coordinator messages to the RLR streams: `send_00`, `send_02`–`06` (rule S8), `send_08`, `send_14`, `send_16`–`19`.

**Hash-only.** Two items carry share patterns and are recorded by hash only, so that no new co-location is created:
* the B_307 brief: 2 share-pattern hits and 6 mentions of 307;
* `send_01`, the F1(a) correction instruction: 4 share-pattern hits.

Items unrelated to RLR (streams A, C2a, D) are also recorded by hash only.

## C5: qualification scope

The qualification reviewer's brief will require a check of the three campaign-added decisions for target dependence:
* the 2^-20 hull;
* the D8 block ladder and its cost rule;
* the exception classification and the caps.

In particular, the reviewer must confirm that no cap or ladder choice cites a decoy certified value or a committed
tail number.

## C6: unchanged mechanics

The protocol keeps:
* one sealed evaluation;
* the Stage-1 stop rule CERTIFICATION_FAILED, with no retry and no other settings;
* no post-result tuning;
* the closure criterion (Γ < 0, strict, exact rationals) frozen before the grant.
