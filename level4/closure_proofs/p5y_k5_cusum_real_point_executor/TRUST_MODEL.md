# Trust model for the first real CUSUM probe (minimal and honest)

**Scope.** This document replaces the r1–r4 attempt to make an on-host verifier authoritative. That attempt failed four
independent reviews because a verifier running inside a repository and on a host that an operator controls cannot
authenticate that operator.

## The five separated stages

| stage | artifact | what is trusted | what it does NOT establish |
|---|---|---|---|
| 1. Scientific preregistration | `p5y_k5_cusum_first_real_probe_protocol/protocol/SCIENCE_PREREGISTRATION_R4.json` (sha256 `9ace6896…`, science content unchanged since `dbbd405a`) | The **public GitHub history** of `p5y-postk1-frontier` as a timestamp: third parties can see the commit existed before any result was published | Git commits are not signed; a writer with push rights could rewrite a branch (a force-push is visible to mirrors and clones but is not cryptographically prevented) |
| 2. Executor qualification | this namespace: frozen executor sources, `EXECUTOR_QUALIFICATION_PROTOCOL.json`, `evidence/qualification/` | The frozen code together with **re-runnable** qualification: anyone can re-run it on manufactured and synthetic inputs and compare hashes; an independent review reads the code | That the host which later runs the executor runs these bytes |
| 3. External authorization | `config/EXTERNAL_AUTHORIZATION_TEMPLATE.json` (INACTIVE) | A **person or session independent of the execution host** who checks stages 1–2 from their own clone of GitHub (not from the host) and countersigns a result-blind authorization naming exact hashes, host, slot and nonce | Nothing cryptographic: the countersignature is a published statement, not a signature verified by the executor |
| 4. Host execution | vultr-02, `CusumPointBackend` behind REAL_INPUT_ARITHMETIC_GUARD | The **host operator** is trusted to run the authorized bytes once, in the authorized slot, and publish every output (including VOID or uninformative ones) | The on-host prelaunch verifier and guard are **consistency and fail-closed mechanisms against accidents**, not trust roots; an operator who controls the host can bypass them |
| 5. Independent result adjudication | a later, separate session | Re-derivation from the sealed record: re-run the frozen consumer, recompute hashes, compare executor sources and runtime facts with the authorization, check the certificate chain; optionally re-run the executor on a second host | That no unpublished run happened before the published one (only process discipline and the ledger speak to this) |

## Explicit assumptions

1. **GitHub history as public timestamp.** GitHub's history of `p5y-postk1-frontier` is the public timestamp. The host
   mirror `/root/work/postk1.git` is not an anchor.
2. **The countersigner is independent.** They do not use the execution host for verification, and they countersign
   only result-blind objects.
3. **The host operator acts in good faith.** They do not run the real backend outside an authorized slot and they
   publish all outputs. This is the principal residual risk, and it is stated, not engineered away.
4. **Arb is correct.** python-flint 0.9.0 (FLINT/Arb) implements outward-rounded ball arithmetic correctly (the same
   assumption as all K1–K4 and R1–R4 certificates).
5. **Reviews are not proofs.** Independent reviews are careful readers of published material. They are not formal
   verification.

## What is NOT claimed

- No cryptographic authorization, signature scheme or tamper-proof execution.
- No claim that a local file on vultr-02, or a commit on a writable branch, is an independent authority.
- No claim that REAL_INPUT_ARITHMETIC_GUARD protects against the host owner. It protects against accidental real
  arithmetic by code paths and operators following the procedure.

## Minimal activation procedure (future; not performed here)

1. A reviewer independent of the host verifies stages 1–2 from GitHub:
   - the science sha256;
   - the executor freeze commit and identity sha256;
   - the qualification result sha256 and gate PASS;
   - the review verdict.
2. The reviewer fills a copy of the template (nonce, slot, countersigner, UTC) and publishes it in a new commit.
3. The host operator sets `config/REAL_INPUT_GUARD.json` to `{"policy": "EXTERNAL_AUTHORIZATION"}` and supplies the
   bundle (the published countersigned object plus a prelaunch report naming its sha256). No source file changes, so
   the executor identity that was reviewed and qualified is the identity that runs; the guard file is deliberately
   outside the executor identity and the pins. `authorization_interface.validate` only checks the bundle for
   consistency with the running executor, the preregistration and the host contract. It authenticates no one.
4. The host operator runs once and publishes the sealed record (or VOID) plus the ledger entries.
5. A separate session adjudicates (stage 5) before any scientific consequence is adopted.
