# A0 / C5 — governed execution of the pointwise certifiers inside the band (DESIGN ONLY)

Nothing in this file is implemented. No code path in `streams/A0/` admits a drift in [6/5, 13/5] or its mirror:
every A0 entry point calls `a0_common.declared_drift` (declared validation set + the campaign guard + the overnight
guard), and every pinned certifier calls `ov_quarantine.guard_drift`, which in this stream is bound to a shim that
chains the same two guards. `a0_common` refuses to load if `ov_quarantine` is already bound to anything else.

## 1. Problem

A future formal campaign (its own namespace, frozen, qualified, reviewed, granted, exactly once) must obtain a
pointwise certified upper bound U(b) ≥ Λ(b) at a finite, pre-registered set of drifts b inside the band (by Theorem M,
U(b) at the smaller |e| end of a block is a valid Ā for the whole block). It must do so **without editing any frozen
file**, and the research guards must stay closed.

## 2. Precedent

The cell-307 campaign solved the same problem for C1b: `rlr307_pinned.py` loads the certifier from its pinned bytes
and binds the name `ov_quarantine` to the campaign guard `rlr307_guard.py`. That guard is DECOY by default (band
refused). `arm_target` switches it to TARGET only after verifying, from git, that the exactly-once consumption marker
exists and names the grant commit that is HEAD. It then admits only the armed hull blocks, compared as exact
rationals, and `log_execution` always refuses. The design below reuses that pattern and adds a hash-bound
authorization file.

## 3. Components, all frozen in the formal namespace F before any target computation

1. **`F/code/formal_guard.py`**, bound as `ov_quarantine` for the pinned modules.
   * Default mode DECOY, with the same band rule as `c308_quarantine`.
   * Its source contains one constant, `AUTH_SHA256`, written at freeze time: the sha256 of
     `F/config/AUTHORIZATION.json`.
2. **`F/config/AUTHORIZATION.json`** (content-addressed; its sha256 is in the guard and in the frozen protocol):
   * `drifts`: the exact rationals b_1 … b_k. They are derived by a frozen rule from committed cover geometry only
     (for example, the smaller-|e| end of each pre-registered block, hulled to a dyadic grid if the C1b rung is used).
   * `ladder`: rung set, numerics, per-process CPU cap and the composition rules R1–R6 (`a0_ladder.py` docstring).
   * `pins`: sha256 of every module that will execute:
     * C1b: gauss, kernel, float, pw, prov, certpw;
     * C2b: c7_gaussian, common, exact, float, certify;
     * the A0 core: sub_certify, exact-scale selection, certificate serialisation and verify;
     * `formal_guard`, `formal_driver`.
   * `marker_ref`, `grant_rule` and `multiplicity`: each b is admitted at most once.
3. **`F/code/formal_driver.py`**.
   * It loads every module by verified bytes, as `a0_common._exec_verified` does: the sha256 must equal the pin and
     the git blob at HEAD; there is no filesystem import and no .pyc.
   * It never imports `a0_common`, `a0_run*` or any research wrapper.
   * It calls `formal_guard.arm(path)`, and then, for each authorised b, `formal_guard.admit(b)`, followed by the
     frozen ladder: C2b proposal, exact-scale selection, the pinned `c2b_exact.certify`, the A0 `sub_certify`, and
     optionally the C1b hull rung.
   * Finally it persists every exact certificate (W with its sha256), re-verifies it in the same process with
     `verify_certificate`, and seals the result.

## 4. `arm` and `admit` (the only way a band drift is ever admitted)

`arm(path)` performs these checks, in order. Any failure raises, and the guard stays DECOY.

1. sha256(bytes of `path`) == `AUTH_SHA256`. Editing the authorisation breaks arming. Editing the guard to change the
   constant breaks the guard's own pin in the authorisation and in the protocol.
2. From git (read-only, `--no-replace-objects`, fixed environment, as in `rlr307_pinned._git`):
   * the worktree of F is clean;
   * `marker_ref` exists and names the grant commit;
   * the grant commit is HEAD and contains the frozen protocol, whose recorded hash is `AUTH_SHA256`.
3. Every module named in `pins` that is present in `sys.modules` carries exactly the pinned sha256. Modules that are
   still missing must be loaded later through the driver's verified loader, which re-checks the pins.
4. The armed set is `frozenset(drifts)` and the use counters start at zero.

`admit(b)`:
* b must be an armed element (exact `Fraction` equality) with use counter < multiplicity.
* It sets the *current admitted drift*, increments the counter, and returns a context manager.

`guard_drift(lo, hi)`:
* Outside the band or mirror: allowed, as today; this keeps qualification decoys working.
* Inside the band or mirror: allowed only if lo == hi == the current admitted drift. Every interval meeting the band
  is refused, and so is every other point.
* The certifiers call the guard several times per rung (in `Setup`, `run` and `Ctx`). The counter is therefore
  driver-level, one per b, not per guard call.
* The C1b hull variant admits the exact armed hull [lo, hi] instead, as `rlr307_guard` does.

`log_execution` always refuses. The formal ledger is written by the driver.

## 5. Properties this design must have (qualification checklist)

* **Q1 no bypass in research code.** The research modules keep hard-wired guards. The formal driver replaces the
  binding and does not add a parameter to any research function. Research code has no "authorised" flag.
* **Q2 no code edit between freeze and execution.** Every executable byte is pinned in the authorisation, and the
  authorisation itself is pinned in the guard.
* **Q3 exact rationals end to end.**
  * C2b needs exact e for its Gaussian lattices K ± e.
  * C1b needs dyadic data, hence the frozen hull rule. A non-dyadic b without a hull rule must fail closed, as it does
    today (`a0_c1bh` finding).
* **Q4 fail-closed.**
  * The per-process RLIMIT_CPU is a safety abort. It voids the run and never drops rungs.
  * No certified upper rung means no value.
  * L > U means INCONSISTENT, with no value.
* **Q5 negative controls through the same path.** Qualification must run the driver in DECOY mode on declared
  non-band drifts and show the following:
  1. An unarmed band drift is refused.
  2. An armed drift is refused when the authorisation bytes differ by one byte.
  3. An armed drift is refused when the marker ref is absent, and when it names a commit other than HEAD.
  4. An armed drift is refused a second time (multiplicity).
  5. A non-armed band drift is refused while some other drift is admitted.
  6. A module whose bytes differ from its pin is refused.

  Each of these must be a test that can fail. In particular, the positive case (an armed decoy drift outside the
  band, admitted and certified) must also be shown, or the refusals prove nothing.
* **Q6 re-verification of a sealed target certificate is itself governed.**
  * `verify_certificate` refuses band drifts in research mode, so an independent re-verification of a sealed target
    certificate needs its own authorisation: a separate `verify` marker and the same guard.
  * Alternatively, the driver's in-process re-verification can be sealed with the result and the reviewer
    re-verifies decoys only. This is a governance choice. It must be fixed at freeze.
* **Q7 Theorem-M use is in the consumer, not in the certifier.** The certifier reports U(b) at the admitted point
  only. The block-level use (U(b) as Ā on [b, b′], with b the smaller |e|) is a frozen consumer rule in F. Nothing in
  research computes or states a transferred number.

## 6. What must change in the research code before such a freeze (open item)

`a0_c2b.sub_certify`, the exact-scale selections in `a0_c2bx`, the serialisation helpers and the checks in
`a0_verify` import `a0_common`. That module installs the research shim at import time and refuses a different
`ov_quarantine` binding. A frozen formal driver therefore cannot import them as they are.

Before any freeze, they should be extracted into a side-effect-free `a0_core.py`:
* no module-level guard installation and no drift validation of its own;
* it relies on the pinned `Setup`/`Ctx` guards, which call whatever `ov_quarantine` is bound;
* the research wrappers keep calling `declared_drift` first.

This extraction is a refactor with no change of statement. It must be done, re-validated on the declared drifts
(byte-identical certificates, as in C4) and reviewed before a freeze. It is not done here, so that the evidence of
this study stays bound to the code that produced it.
