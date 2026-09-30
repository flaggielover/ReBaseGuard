# No unresolved placeholder, mutable scientific decision or post-result choice (owner procedure step 11)

**Mechanical part.** `code/p309_placeholder_check.py` scans every file of the frozen directories and the rev. 2b
package documents. It looks for placeholder markers (TBD, TODO, FIXME, XXX, "to be decided / determined",
"placeholder", "???", "undecided", "open question") and choice phrases ("owner decides / may choose", "may be chosen",
"at the coordinator's discretion", "after seeing / inspecting the result", "depending on the result").
* Every hit must be in the reviewed allowlist, with a reason. The allowlist covers: verbatim owner text; verbatim
  historical briefs; rev. 2b sentences about decisions the owner has since taken; this statement and the checker
  themselves.
* The frozen parameter file must contain no null value outside `post_grant_derivations`.

The checker's result at the freeze is in `evidence/freeze/PLACEHOLDER_CHECK.json` and in QC13.

## 1. What the freeze fixes (nothing here can change after the freeze)

| class | fixed by |
|---|---|
| scope, route, closure criterion (Γ < 0, exact, strict), outcome table, CLOSURE_ONLY | protocol rev. 2b §§1, 4.6, 5; `freeze/P309_FREEZE.json` |
| Stage 1a: cell_blocks rule (the outward 2⁻¹⁰ hull, N_E = 4), ladder {8, 10, 12}, indices 1–4, whole kernel, numerics (THEOREM_SRK §12), per-rung serialization, admission (gate G1–G6, verifier N = 8, max_depth = 24), failure mapping, budget (48 CPU-h start threshold, 12 CPU-h per job, rung-major, ≤ 4 workers) | protocol §2; rev. 2c; the pinned producer (lock 2a03e838) and gate |
| Stage 1b: the RLR307 rules verbatim (C1B_R2 pins; ladder 4/6/8; sub-block width ≤ 1/100; 2⁻²⁰ hulls), fallback to S_I1, budget 21 600 s (start threshold and per-job limit), order | protocol §3; rev. 2c A4–A5; the pinned RLR307 helpers |
| Stage 2: S composition, the pinned consumer, the shim injection, the two-part historical control, the record binding | protocol §4; rev. 2c A11–A13 |
| exactly-once: names, sites, chain, exit codes, recording from memory | package §C; rev. 2c A8, A10 |
| every code and data input | `freeze/P309_FREEZE_MANIFEST.json` (sha256 + git blob); checked at execute, in every worker, and by QC13 |
| the verifier identity (verifier_id) and the guard identity | their sha256 in the manifest |
| the U2 proposition, the independence statement, the disclosed liabilities, the review conditions (verbatim) | `freeze/P309_FREEZE.json` |

## 2. Values the freeze does not fix, and why none of them is a choice

Each has a frozen derivation rule. None is scientific, and none can be selected after any result, because the only
result exists after the marker.

| value | derivation (frozen) | who / when |
|---|---|---|
| `cell_interval` | the CUSUM-filtered entry for the cell in the pinned `cells.json`, as exact rationals | read after the freeze; ledgered (incident review C4). It is structural, not a result |
| `drift_hull_Ew` | `srk_certify.cell_blocks(cell_interval)[0]` | computed from the above. The guard and the verifier each recompute it and refuse if it differs |
| execution host | the host the owner names. The proposed host is this environment (rev. 2c A14) | the owner, in the grant. If it is another host, QC10's host re-run must be repeated there before `execute` |
| `not_after_utc` | the owner's expiry | the owner, in the grant |
| the grant commit, and the marker naming it | created by the owner's grant and by `execute`'s single CAS | after the grant |

## 3. No post-result choice

* **Before the marker:** nothing target-derived exists. The historical control reproduces a committed C2 record by
  equality only, and CONTROL_FAILED stops without consuming the target.
* **After the marker:** the driver has no branch that depends on an operator decision.
  * Stage 1a, 1b and 2 run to completion or to an exception.
  * Fallbacks are mechanical (protocol §2.5, §3).
  * Exceptions give EXECUTION_INDETERMINATE.
  * The result is sealed from memory before anyone inspects it.
  * The adjudication applies the outcome table verbatim.
  * A consumed marker is never rerun.
* **Host dependence when the budget binds** is disclosed (protocol §2.5, §2.8). It is a property of the frozen rule,
  not a choice.
