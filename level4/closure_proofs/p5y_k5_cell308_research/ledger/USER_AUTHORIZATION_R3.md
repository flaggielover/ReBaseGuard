# User authorization of freeze r3 and its official run (cell-308 MB r1)

Recorded after the r3 qualification review (`47bb37c7`) noted, as N-b / N6, that the r3 authorization existed only as
a paraphrase in brief 21 and protocol §14. The user's answers are reproduced below word for word. They were given in
chat on 2026-09-29, through structured questions; each question is summarised in italics.

---

**Answer 1.** Given about 05:10Z, after the r2 official qualification FAILED on Q12. *The question: how should the
campaign continue? The options offered were a caps-raising r3, a same-caps r3, or stopping.*

Authorize r3 as an execution-environment / sleep-contamination repair only.

Preserve r2 at d031dad8 as QUALIFICATION_FAILED.

Do NOT raise or recompute the frozen scientific/runtime caps from the sleep-contaminated r2 runtimes, and do not weaken Q12 merely to obtain a pass.

For r3:
- keep the scientific route, theorem, parameters, consumer, target criterion, and exactly-once semantics unchanged;
- preserve the original cap intent;
- add explicit whole-run sleep prevention (e.g. caffeinate);
- require AC power at preflight;
- record sleep/wake and relevant thermal provenance;
- fail closed if suspend/sleep occurs during a load-bearing timing interval or timing provenance is ambiguous;
- add same-decision-path planted controls showing that the timing guard detects contamination while genuine runtime/cap violations remain detectable;
- independently review this r3 repair before relying on it.

Create a new r3 freeze and run a fresh official qualification on an awake machine.

Γ308 must remain 0 through repair, freeze, qualification, and independent qualification review.

Only after r3 qualification PASS and a fresh QUALIFICATION_ACCEPTED review may the existing C4 ruling be incorporated into an explicit grant.

Proceed autonomously with r3 if the committed assessment confirms the r2 failure was purely execution-environment contamination.

---

**Answer 2.** Given about 05:25Z. *The question: the failure is purely environmental but not sleep-only, since there is
also a sleep-free slowdown of about 15 % against r1 in the concurrent window. With the caps unchanged, how should r3
proceed?*

The option chosen: **r3 as specified, cool host (Recommended)**. That option read: exactly the user's r3 spec, with
caps, Q12 and the qualification's concurrency unchanged, run only while the Mac is cool, lid open, on AC and running
no other heavy work.

---

**Answer 3.** Given about 07:02Z, after freeze r3 `c46434a3`. *The question: start the one official r3 qualification
now (about 3.5–5 h; any Q12 FAIL, including one caused by a lid-close sleep or unplugging, stops the campaign under
the pre-declared rules)?*

The option chosen: **Start now (Recommended)**. That option read: "I keep the Mac open, plugged in and free of heavy
work until it finishes".

---

The C4 ruling is recorded separately in `ledger/USER_RULING_C4.md` (`0aeaec23`).
