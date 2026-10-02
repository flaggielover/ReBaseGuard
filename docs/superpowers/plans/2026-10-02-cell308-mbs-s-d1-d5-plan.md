# Cell-308 MB-S D-1–D-5 implementation plan

Base: `4a617793` (`d4734231` plus approved design spec)

1. **D-1 series ledger and watchdog refusal**
   - Inspect the namespace constants and add one fixed campaign-history path that cannot be selected by `--work`.
   - Record `started` before launch, then append `invalid`, `designated`, or interruption status with digest and reasons.
   - Make `designate`, `mbs308_derive`, and official R-rule inputs consult the history; refuse before launch when a prior event series exists and reject designated evidence whose history contains one.
   - Preserve the existing accepted rule text and add regression/mutant coverage for same-work, alternate-work, and interrupted-series cases.

2. **D-2 exact incident exception**
   - Add a configuration entry for the exact committed line-418 digest and zero-exposure predicates.
   - Refactor `ledger_check` to admit only that exact line and keep all other non-pre-grant lines strict.
   - Add controls for exact line, byte mutation, second incident, leak flag, and nonzero evaluation/proxy counts; verify the real research ledger remains unchanged.

3. **D-3 positive R-MEM peaks**
   - Add a named invalid reason and enforce positive integer job, driver, and optional watchdog peaks before aggregation.
   - Remove reliance on the later `min(v) > 0` skip and test zero, negative, bool, missing, and valid values; add corresponding mutants.

4. **D-4 hosting path equality**
   - Carry designated hosting-app paths into the official comparison and require exact equality before `R_RULES_OFFICIAL` derives outputs.
   - Add equal, missing, and mismatched-path cases and mutants.

5. **D-5 resume-decoy propagation**
   - Read the failed decoy record in `mbs308_resume_decoy.py`, propagate the watchdog status, and make aggregate lift the same fail-closed status.
   - Add a watchdog-failure case and mutation that drops the propagation.

6. **Final verification and review**
   - Run affected suites on final bytes, then the full mutant matrix; inspect every result's `error` field and require assertion kills.
   - Run static governance checks against the real committed research ledger and record the builder/reviewer provenance without editing historical evidence.
   - Produce a bounded build report and obtain a fresh non-holder delta review against `18cace37` only.

Safety: no designation, apply, freeze, qualification, authorization, grant, real measurement, or cell309 access.
