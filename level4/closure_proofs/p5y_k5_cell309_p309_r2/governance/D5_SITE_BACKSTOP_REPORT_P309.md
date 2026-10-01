# Report to the owner: a strengthened precondition at the two D5 sites (R4F-C1; rev. 2c A31)

**Nature of this document.** This is a report, not a request. It asks for no decision and changes nothing the owner
decided. It is recorded with the D5 record because the independent pre-freeze reviewer R4 required it (condition
R4F-C1, `reviews/REVIEW_PREFREEZE_R4_FOLLOWUP_P309.md`).

## What the owner ratified (unchanged)

`governance/OWNER_D5_RATIFICATION_P309_VERBATIM.md` ratified two things, which remain exactly as ratified:
* the production pending-ref NAME may exist in the frozen package (D5-1);
* the two exactly-once functions `_arm_marker` and `_persist_pending` may exist in the frozen tree (D5-2).

Their AST sha256 values are unchanged:
* `_arm_marker`: `1ee764b7b1cfca7b2fbda9b394e8af235239a2d308905a9f07f521b39b80be0c`;
* `_persist_pending`: `13ee3ec3b7ba4c3ff80103c16671d4697967bfb177f4ae964084c95ab2fbbaaf`.

Execution authority remains withheld, and no production ref exists.

## What R4 found

The scanner and the static checks could be evaded in fifteen ways (R4's M01–M15). More importantly, the check that both
sites run first (`_assert_execute_context`) verified only the process mode and the shape of the context. It did not
check that a grant exists. A caller that bypassed `run_execute` could therefore have reached a site with a
production-shaped context. R4 did not run this; the finding comes from reading the code.

## What changed (before the freeze; the site ASTs untouched)

The site-entry check is now followed by a **runtime backstop**. It lives in the called function, outside the ratified
ASTs, and it acts immediately before each site's ref mutation.

* **Only the two sites pass.** The check identifies its caller by the code objects of the two ratified functions. Any
  other caller is refused (`NOT_A_SITE`).
* **Creating the marker** now also requires, at that moment:
  * `execute` mode;
  * the guard's own pre-marker grant checks to pass: a valid grant at HEAD, bound to the frozen manifest and to this
    guard, on this host and runtime, not expired, with an empty marker namespace;
  * the run nonce of this very process.

  Before the owner's grant exists, these conditions cannot hold, whatever the call path.
* **Creating the pending evidence ref** now also requires, at that moment:
  * the marker to exist;
  * the marker's commit to carry the grant;
  * in `execute` mode, the run nonce of this process.

**Effect on a correct execution: none.** Every one of these conditions already holds when `run_execute` or `run_seal_only`
reaches a site; they were checked earlier on the same path. The backstop can only refuse, and only a call that bypasses
the granted path.

**Direction: fail-closed.** It narrows what the sites can do and widens nothing. The owner's clarification ("frozen,
reviewed, fail-closed CODE CAPABLE of performing those operations after a valid future execution grant may exist")
is met more strictly than before.

## Also changed for R4 (for completeness; details in `governance/P309_REV2C_AMENDMENTS.md`, "Third delta")

* **The scanner allowlists process execution** (schema 4), and the static check T7 was hardened. Each of R4's fifteen
  evasions is now a control that must be rejected.
* **Placeholder test narrowed.** The `authority` field of a grant is refused only if it is the proposal's own
  placeholder text. A grant that quotes the owner's words is no longer refused.
* **Grant validator.** A read-only `validate-grant` step checks a candidate grant before the grant commit.

**The handoff states that a grant commit that `execute` refuses is terminal without a new owner decision.**

## Review

* **R4.** These changes go to R4 for a focused confirmation (R4F-C3): the D5 controls, R4's mutant suite, and one QC11
  run.
* **Delta reviewer.** The rule-level items go to the delta reviewer (conditions C2 and D8): the backstop precondition,
  the authority narrowing, and the required worktree field.

The freeze waits for both verdicts.

## Addendum (R4 follow-up 2; rev. 2c fourth delta, A38 and A40)

* **The backstop is now pinned like the sites.**
  * The AST sha256 values of the three backstop functions and of the mapping of the two sites are pinned in the
    scanner allowance: `_assert_execute_context` `c8a2fb51…`, `_site_backstop` `80d206ad…`, `_require_own_run_nonce`
    `23f3021d…`, and the `_SITE_CODES` statement `696a6102…`.
  * The static check requires equality. Any change is a new delta and is reported here.
  * The code is unchanged since R4 reviewed it.
* **Why the static rules were tightened again.** R4 showed that code the static checks accepted could switch the
  backstop off from inside the same process. The checks are now closed-world allowlists (imports, introspection,
  module stores, environments, git options). Each of R4's 54 mutants is a control that must be rejected.
* **`execute`'s git no longer reads the host's system or global git configuration.**
  * It commits with a fixed identity.
  * Before the marker, it refuses unless the repository's own configuration holds only allowlisted keys and no git hook
    is present.
  * Before this change, a host setting (on the development host, commit signing with an ssh program) would have run a
    program inside the post-marker seal.

  The effect is fail-closed before the marker. After the marker, it removes a host-dependent failure.

Execution authority remains withheld. No production ref exists.

## Addendum 2 (R4 follow-up 3; rev. 2c fifth delta, A43–A45)

* **Unchanged.**
  * The two sites and their owner-ratified AST hashes.
  * The backstop and its A38 pins.
  * R4 found the D5 exception limited to the two ratified sites (`D5_EXCEPTION_LIMITED_TO_RATIFIED_SITES: YES`).
* **Why the freeze was still blocked.** `seal-only`, the recovery step, did not run the host-git check that `execute`
  runs. A repository hook added between `execute` and `seal-only` would have run at `seal-only`'s ref write.
* **Fixed, before the freeze:**
  * `seal-only` now runs that check first;
  * `execute` repeats it just before its first git write after the historical control, and again before the
    post-marker evidence persist. If it refuses there, the evidence goes to the emergency file and `seal-only` seals it
    once the host is clean;
  * the guard's own git calls ignore the host's system and global git configuration.

  Each case is a control.

The effect is fail-closed before the marker. After the marker, the evidence is kept and no git write runs under a hook.
Execution authority remains withheld. No production ref exists.
