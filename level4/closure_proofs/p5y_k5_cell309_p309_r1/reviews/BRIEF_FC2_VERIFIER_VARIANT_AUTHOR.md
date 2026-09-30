# Brief: the band-scoped verifier variant (FC2(b)), for the independent verifier's author

This brief is committed before it is issued (incident review condition C5). The recipient is the author of the
independent verifier `RNS/verify/srk_verify_indep.py` (sha a32d5d39…), in a session separate from the producer side.

## Authorization

The owner's rulings 2 (`governance/OWNER_RULINGS_2_P309_VERBATIM.md`, "OWNER RULING — GRANT ADMISSION CODE"):
> The independent verifier/admission author IS authorized to implement the grant-scoped admission mechanism needed
> by FC2. This authorization is permission to WRITE AND TEST THE MECHANISM ONLY. It is NOT permission to issue a grant
> or lift the real quarantine.

If the tooling still refuses a write, **stop and report**. Do not look for another way to get the write done.

## Task

Implement, exactly per `fc2/FC2_SPEC_R2.md` (§§1–4, 6, 8, 9):
* `verify/srk_verify_indep_scoped.py`: a copy of your verifier, changed only as the spec requires (compiled band
  tables, contexts, `admission_decision`, the `verify_cert` hook, review mode, fail-closed behaviour).
* `verify/run_verify_all_scoped.py`: harness v2 against the variant, with its own compiled band table for probe
  construction (§4). It writes `verify/VERIFY_RESULTS_SCOPED.json`.
* `tests/test_verify_scoped.py`: the 21 self-tests ported, plus N1–N13, P1, P2 and D1 of spec §8. Each test builds
  and tears down its own sandbox (§6).
* `verify/README_VERIFY_SCOPED.md`: the variant's sha256, the harness sha256, a results summary, and the §9
  independence statement (your session identifier, the sources you read, and a statement that no producer or guard
  code was consulted).

Then run, in this order:
1. The self-tests and the N/P/D tests.
2. I1: the harness on every certificate in `RNS/evidence/srk_decoys/` and `RNS/evidence/srk_decoys_cell/`, genuine
   plus the v2 batteries.
   * Outside every band, the result must be identical in verdict and reason to the committed
     `RNS/verify/VERIFY_RESULTS.json`.
   * The h3 decoy-cell files meet the TEST band. Without a test context they must be REFUSE. With the P1 sandbox test
     context they must match the committed results (genuine), and the batteries must match the expectation rule you
     derive from §3 (admission first, then the original expectation). **Write that rule down before you run it.**

## Firewall and rules

* **Read:**
  * the spec;
  * protocol rev. 2b §§6–7;
  * your own verifier, harness and tests;
  * `FORMAL_QUARANTINE_P309.json`;
  * the band clauses of `TARGET_QUARANTINE_309.json`;
  * the owner rulings;
  * `code/p309_env.py`;
  * the decoy evidence files (inputs).
* **Do not read:**
  * any producer code (`RNS/impl/srk_*.py`, except the certificate JSON files as data);
  * `code/p309_guard.py` or its tests;
  * any number of cells 305–309.
* **Never:**
  * create the production marker name, or any ref under `refs/p5y-k5-cell309-p309-r1/`, anywhere, sandboxes
    included;
  * write the production grant path anywhere;
  * evaluate a REAL-band certificate: REAL-band tests are dry, using `admission_decision` or a refusal before
    evaluation;
  * write to git in this repository (sandboxes are separate clones under
    `/tmp/claude-0/-home-user-ReBaseGuard/ea54e9f6-e828-5447-be15-220ef2c329fd/scratchpad/fc2_sandbox_verifier/`,
    with origin removed and never pushed);
  * modify anything in RNS.
* **Ledger every execution** through `code/p309_env.py` (`import p309_env as E; E.log(...)`). That includes
  inspections and scans, with class SYNTHETIC or NONTARGET_DECOY or GOVERNANCE, and the drifts evaluated (TEST band
  and decoy drifts only).
* **Resources:** up to 3 worker processes.

## Report

Report:
* the variant sha256 and the harness sha256;
* the diff summary against the original verifier;
* each test's result;
* the I1 summary, with every difference explained against the spec;
* every spec ambiguity you found, and how you resolved it;
* the §9 statement.
