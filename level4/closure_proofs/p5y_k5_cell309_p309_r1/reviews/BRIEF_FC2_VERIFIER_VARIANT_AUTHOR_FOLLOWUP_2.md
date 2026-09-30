# Follow-up brief 2: band-scoped verifier variant (committed before issue)

**Recipient:** the verifier's author.
**Basis:** the independent pre-freeze review R4 (`reviews/REVIEW_PREFREEZE_R4_P309.md`, verdict FREEZE_BLOCKED),
non-blocking notes NB3, NB9 and NB12. None of R4's blocking findings asks for a change to your code:
* B2(a) is fixed on the driver side. The driver will seal a top-level `stage1a.certificates`, as spec §3 says.
* Your review mode stays as it is.

All rules of `reviews/BRIEF_FC2_VERIFIER_VARIANT_AUTHOR.md` and follow-up 1 still apply:
* the firewall;
* never create any ref under `refs/p5y-k5-cell309-p309-r1/`, anywhere;
* REAL-band tests are dry;
* no git writes in this repository;
* ledger every execution through `code/p309_env.py`;
* do not read the producer, the guard or the driver.

The owner's D5 decision (`governance/OWNER_D5_RATIFICATION_P309_VERBATIM.md`) changes nothing for you. Your file must
still contain the production marker NAME only as the one inert constant, under the scanner allowance.

## Changes requested (minimal)

1. **NB3, harness tripwire.** In `verify/run_verify_all_scoped.py`, the prepare-tripwire must classify a certificate with
   the harness's **own** band table (`own_bands`), not with the variant's `cert.bands`. This makes §7(c) independence
   strict. Behaviour on every current input must stay the same. If it does not, stop and report.
2. **NB12, light sandboxes.** `verify/scoped_sandbox.py` still builds `git clone --shared --no-checkout` sandboxes, about
   445 MB each, because this repository is shallow. Switch to the construction allowed by `fc2/FC2_SPEC_R2_ERRATUM_1.md`
   E1-6:
   * `git init`;
   * a read-only `objects/info/alternates` link to this repository's object store;
   * the `shallow` file copied;
   * no remote, never pushed.

   Keep your sandbox's own checks, including the refusal of any production-namespace ref and the teardown. Free disk is
   about 28 GB, and a sandbox must never outlive its test.
3. **NB9, README.** Say plainly that your agent and the coordinator run under the same top-level session
   (`session_01RiV5bfPm5GJ4GcvoBrCC3p`). Independence rests on:
   * subagent separation;
   * your declared list of sources read (no guard, producer or driver code);
   * the independent divergences you found (E1-1 to E1-4).

   Give your own agent identifier if you know it.

Change nothing else. In particular, change no admission rule and no review-mode behaviour.

## Then

* Re-run `tests/test_verify_scoped.py` and I1 (`verify/run_verify_all_scoped.py`) with `--out` under the scratchpad.
  The committed `verify/VERIFY_RESULTS_SCOPED.json` is refreshed only by a full run whose counts are identical to
  before.
* Update `verify/README_VERIFY_SCOPED.md` with the new sha256 values.
* **Report:**
  * the new sha256 of every changed file;
  * a diff summary;
  * the test and I1 results, with counts compared to the previous run;
  * the peak disk use of your sandboxes.
