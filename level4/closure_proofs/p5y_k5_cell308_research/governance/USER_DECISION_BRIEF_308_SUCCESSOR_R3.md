# Decision brief r3 — Cell-308 successor MB-S

## Current-state update

This r3 supersedes the status statements in r2 while preserving r1 and r2 as historical decision records. The option text and owner decisions remain those recorded in r2; this document records the accepted implementation state reached afterward.

The bounded D-1–D-5 repair and riders are accepted on successor commit `9e0e98d07b0e702c6d9848abc54e8ba36ee3544a` (`9e0e98d0`). The fresh non-holder delta reviewer `reviewD9` accepted that exact commit after the D-1 history-preflight defect was repaired. The durable history allowlist is exact; all other namespace changes remain blocking. The final target-free checks reported by the builder are static 10/10, cases 29/29, and qualification checks 29/29. The real committed research ledger check passes, including the named line-418 exception and the newly recorded builder/reviewer provenance lines.

The implementation is accepted as a pre-freeze candidate only. No designated measurement, official qualification run, freeze, grant, marker, seal, apply operation, or Cell-308 target evaluation has occurred in this continuation. New MB-S Cell-308 target evaluations remain **0**. Cell 309 remains out of scope. MB r1 remains permanently `CELL308_EXECUTION_INDETERMINATE` and consumed.

The accepted implementation changes are prospective safety and governance mechanics only: persistent series history and watchdog/designation refusal (D-1), the exact line-418 ledger exception (D-2), positive R-MEM peak validation (D-3), exact hosting-app path equality (D-4), and failed-decoy watchdog propagation (D-5), together with the recorded G/O/T riders. No operational constant, carried science function, accepted R-rule, owner record, or scientific membership was changed.

## Decision position

The decisions, alternatives, and withholding options in `USER_DECISION_BRIEF_308_SUCCESSOR_R2.md` remain in force. This update does not recommend a scientific outcome or state that MB-S is worth running. Withholding or deferring remains available on the same terms. Nothing in this brief authorizes a freeze, qualification, grant, or target step.

The successor worktree is clean at `9e0e98d0`, branch `p5y-k5-cell308-mbs-r1`. The qualification framework and its target-free cases are integrated and reviewed; its official qualification mode has not been run. The remaining gates are the fresh MBS-10 neutrality check, the accepted host-readiness gate, designated pre-freeze measurements if and only if that gate passes, the final pre-freeze review, and the separately recorded owner decisions required before freeze/grant. Historical rejected reviews and incidents remain preserved.

## Host boundary

Host readiness must be re-read immediately before any designated measurement. The last recorded host state was not ready: update-policy flags, busy Storage processes, memory pressure, and thermal pressure were outstanding. AC connection or disk space alone is insufficient. This campaign will not change update policy or quit owner applications without explicit authority. If those owner-controlled conditions remain unsatisfied after all safe target-free work, the state is `HOST_PREPARATION_REQUIRED` and the campaign stops before measurement.

## Scientific-neutrality statement (MBS-10 scope)

This brief contains no margin, estimate, likelihood, runtime inference, resource-use inference, or statement about whether MB-S will close Cell 308. Decoy and target-free validation statuses are engineering evidence only and do not imply a scientific result. The only scientific status asserted here is the preserved historical status of MB r1 and the count of new target evaluations, which remains zero.

## Provenance

- Prior decision brief: `USER_DECISION_BRIEF_308_SUCCESSOR_R2.md` (preserved unchanged).
- Rejected implementation review: `18cace37` / `REVIEW_PREMEASUREMENT_IMPLEMENTATION_MBS308.md` (preserved unchanged).
- Accepted implementation: `9e0e98d07b0e702c6d9848abc54e8ba36ee3544a`.
- Fresh delta review: `reviewD9`, ACCEPT.
- Governance ledger: `TARGET_INTEGRITY_LEDGER.jsonl`, append-only; no historical line was edited.
- New MB-S Cell-308 target evaluations: **0**.
