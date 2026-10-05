# P309-r2 owner decisions: dependency table and DAG

This is a companion to `OWNER_DECISION_EXECUTION_PACKET.md`. Nothing here is a decision. Validation and review steps
that are **not** owner decisions are shown in square brackets, e.g. `[8a audit]`.

## 1. Ordered dependency table

| order | item | phase | requires first (decisions / steps) | logically impossible before | unlocks |
|---|---|---|---|---|---|
| 1 | OD-R2-0(A) | A | — | — | part of the authority for OD-R2-0(D) |
| 2 | OD-R2-0(B) | A | — | — | part of the authority for OD-R2-0(D) |
| 3 | OD-R2-0(C) | A | — | — | part of the authority for OD-R2-0(D) |
| 4 | OD-R2-1 | A | — | — | the frozen names (needed by the freeze) |
| 5 | OD-R2-1b | A | consistent with OD-R2-1 | — | the frozen bindings |
| 6 | OD-R2-2 | A | consistent with OD-R2-1 | — | the frozen marker / pending names; D5 sites |
| 7 | OD-R2-5 | A | — (option (ii) also needs a message-3 amendment) | — | the run-time policy; the windows (with 8b) |
| 8 | OD-R2-6(ii) | A | — | — | a rule applying before any grant |
| 9 | OD-R2-6(iii) | A | NAME A HOST AT FREEZE needs OD-R2-6(i) first | NAME, before OD-R2-6(i) | the frozen `proposed_execution_host` |
| 10 | OD-R2-3 (audit access) | A | — | — | `[8a audit]` → `[8b verdict]` |
| 11 | SF1 (choice of path) | A | — | — | SF1-A: `[scoped delta + review]`; SF1-B: `[host check]` |
| 12 | OD-R2-H | B | `[formal review 5]` (done: accepted) | — | the owner's fast-forward `101ef2cb` → `a119e978` (C1) |
| 13 | F-DRILL-ORDER | B | OD-R2-H | FD-A before OD-R2-H = H-A (C1 makes the fix inseparable from the candidate) | closure of the defect upon incorporation |
| 14 | `[incorporation: fast-forward]` | — | OD-R2-H = H-A | without H-A | AF-3; SF1-A's delta base; the C3 drill bytes |
| 15 | AF-3 (governance filing in r2) | C | the fast-forward (a separate commit; C1) | before incorporation, when it would break C1 | P-11 |
| 16 | `[8a audit]`, `[8b verdict HOST_SUITABLE]` | — | OD-R2-3 | without OD-R2-3 access | OD-R2-4 (informed); AF-1 / AF-2 (if triggered) |
| 17 | AF-1 (message 3 §6 amendment), only if the checkout is world-readable | C | `[8a audit]` result; the cell-308 operator | before 8a shows it | isolation passes |
| 18 | AF-2 (host portability), only if there is no IMDS | C | host identity / `[8a audit]` | before the host is known | the durability preflight passes |
| 19 | OD-R2-4 (consents M1–M5, limits) | C | `[8a]`, `[8b]`; the cell-308 operator's data and consent (M4) | an informed consent before 8a | `[8c bootstrap]` |
| 20 | SF1 resolution | C | SF1-A: H-A + `[scoped delta review]` + an owner incorporation act; SF1-B: OD-R2-3/4 + `[8c]` | SF1-A before H-A | C2 met |
| 21 | `[8c bootstrap]` | — | OD-R2-4 | without OD-R2-4 | `[8d]` |
| 22 | `[8d worker-tier drill]` (C3) | — | incorporation (H-A); SF1-A incorporated if chosen; OD-R2-3 windows; OD-R2-5; `[8c]`; the cell-308 operator's uids and patterns; whole-host window agreement | before H-A: it refuses at the manifest precondition (F-DRILL-ORDER) | C3 met |
| 23 | `[pre-freeze follow-up review, gate step 9]` | — | `[8d]` PASS | before 8d | P-8 |
| 24 | **OD-R2-0(D)** | D | 1–7, 9, 12–15, 19–23 (P-1 … P-11) | before every prerequisite holds | the freeze and the single official qualification (only) |
| 25 | `[freeze]`, `[official qualification]`, `[qualification review]` | — | OD-R2-0(D) | without (D) | AF-4 (on PASS) or AF-5 (on FAIL) |
| 26 | OD-R2-6(i) | E | a passed qualification and review (recommended) | — (it can be answered earlier, but then it must precede the freeze if named there) | naming the execution host |
| 27 | AF-4 (grant decision) | E | a PASS qualification + `QUALIFICATION_ACCEPTED` review; OD-R2-6(i); OD-R2-6(ii) re-run if required | before a passed, reviewed qualification | the single target execution (the only path to Γ(309)) |
| 28 | AF-5 (r3), only on failure | E | a failed or interrupted r2 qualification (P23) | otherwise | a new campaign |

## 2. DAG

Owner decisions are named; `[ ]` marks a non-decision step.

```
OD-R2-0(A) ─┐
OD-R2-0(B) ─┤
OD-R2-0(C) ─┤
OD-R2-1 ─┬──┤
         ├─ OD-R2-1b ─┤
         └─ OD-R2-2 ──┤
OD-R2-5 ─────────────────────────────────────┐   (+ windows)
OD-R2-6(iii) ────────────────────────────────┤   (NAME → needs OD-R2-6(i) first)
                                             │
[formal review 5: ACCEPTED] ─> OD-R2-H ─(H-A)─> [fast-forward 101ef2cb→a119e978] ─┬─> AF-3 [governance filing]
                                   └─> F-DRILL-ORDER (FD-A)                        ├─> SF1-A [scoped delta → review → owner incorporation]
                                                                                   │
OD-R2-3 ─> [8a audit] ─> [8b verdict] ─┬─> AF-1? ─┐                                │
                                       ├─> AF-2? ─┤                                │
         cell-308 operator data ───────┴─> OD-R2-4 ─> [8c bootstrap] ─(SF1-B check)─┤
                                                                                   ▼
                                     [8d worker-tier drill on the incorporated bytes] (C3)
                                                         │
                                         [pre-freeze follow-up review, step 9]
                                                         │
                     all of the above + OD-R2-0(A–C), OD-R2-1/1b, OD-R2-2, OD-R2-5, OD-R2-6(iii) ──> OD-R2-0(D)
                                                         │
                               [freeze] → [single official qualification] → [qualification review]
                                                         │
                        PASS ──> OD-R2-6(i) + OD-R2-6(ii) [QC10 host re-run] ──> AF-4 grant decision ──> (only then) Γ(309)
                        FAIL ──> AF-5 (r3)
```

## 3. What is logically impossible, and why

- **OD-R2-0(D) before H-A and the incorporation.** Without H-A the r2 bytes are `101ef2cb`, whose worker-tier drill
  refuses at launch (F-DRILL-ORDER). Without a passed drill there is no C3, and no basis for the pre-freeze review.
- **OD-R2-0(D) before SF1 is resolved.** C2 is "before-freeze".
- **OD-R2-0(D) before OD-R2-3/4/5 and the 8a–8d sequence.** Its text binds the freeze to "the qualification host
  approved under OD-R2-3 and OD-R2-4".
- **FD-A without H-A.** C1 admits only the two reviewed commits together. The fix cannot enter r2 alone without a new
  candidate and a new review.
- **SF1-A before H-A.** Its delta is defined on top of the incorporated r2.
- **AF-3 in the same step as the fast-forward.** C1 forbids anything else in the incorporation step.
- **OD-R2-6(iii) = NAME before OD-R2-6(i).** The code names a host only from the owner's OD-R2-6 answer file.
- **AF-4 (grant) before a passed and reviewed qualification.** Message 1 §10, R2_HOST_SESSION §7 and the driver's
  grant check (a PASS at the freeze commit, and `QUALIFICATION_ACCEPTED`).
- **Γ(309) before AF-4.** Only a granted execute arms the marker. No decision in this packet authorizes Γ(309).
