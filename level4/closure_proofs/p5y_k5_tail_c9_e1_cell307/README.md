# C9 — E1 zero-new-real operator certification, CUSUM m=5 cell 307

**Result: `EXECUTION_BLOCKED_ON_RUNTIME_AND_AUTHORIZATION`.** No certification was executed. No scientific address
was evaluated. Guard **DENY** throughout.

Target executions **0**, operator certifications **0**, new-real addresses **0**, AWS contacts **0**,
toolchain provisioned **0**, r6 **not created**.

## What C9 set out to do

C8 selected route **R3 / E1** — a tighter certified operator tuple — with **cell 307 first**. C9 was
chartered to execute exactly that: one cell, one route, one authorized certification.

## What C9 found — corrected after review

The first pass declared two blockers and stopped. A fresh-context review returned **STOP_PREMATURE**
and was right about the important one. Both findings below were independently verified before being
absorbed.

### Blocker 1 — **WITHDRAWN.** The lever was in C9's own inputs, free and unmeasured

C9 defined E1 as "one authorized execution of the **committed** producer", then discovered that a
replay replays. That definition is wrong. C6 defines E1 as *"a BETTER tuple … there is nothing to
replay … a TOOLCHAIN for the WORK … the result does not exist"*, and C8's gate defines R3 as *"a
better certified upper bound"*. Under the real definition the certifier's **search** is the work.
C9's own B0_15 quoted the C6 entry it then contradicted. The dependency scan also read only the
*wrapper's* CLI; `taboo_certify.py` exposes `--alpha`, `--beta`, `--depth`, `--degree` directly.

**The lever.** The wrapper walks the ladder `(6/5, 13/10, 7/5, 3/2, 2, 3)` upward and takes the first
rung that certifies. Cell 307 certified at the **very first** rung, `6/5`, on all ten sub-blocks —
each with a recorded margin of ≈ **0.16 still in hand**. The ladder has no rung below `6/5`, so a
smaller α was never tried. Since the candidate is `w = dyadic(α·g)` and certification is affine in
`w`, a block still certifies whenever `c ≥ 1/(1+margin)`, and `τ` scales with `c`.

| α | c | τ | eff | tightening | closes | adoptable |
|---|---|---|---|---|---|---|
| 1.033688 (floor) | 0.861407 | 4.265736064 | 4.921722733 | **1.137406** | yes | **no** |
| 1.05 | 0.875000 | 4.333049179 | 4.999387287 | **1.119736** | yes | **no** |
| 1.07 | 0.891667 | 4.415583449 | 5.094613711 | **1.098807** | yes | **no** |
| 1.09 | 0.908333 | 4.498117719 | 5.189840136 | 1.078645 | no | no |

Required: closure **1.096007246**, adoption **1.370009058**. Same geometry, same degree, same depth,
essentially the same cost.

> **The α lever closes cell 307 — and cannot make it adoptable.** Even at the window floor the best
> achievable tightening is 1.137406×, far below the 1.370009× the binding C2 adoption floor demands.
> A successful execution would therefore land in class **SCIENTIFICALLY_CLOSED_NOT_ADOPTABLE**.

This is a **counterfactual projection**, not certified: `dyadic` rounding makes the scaling
approximate, `D_lo` is held fixed conservatively, and every sub-block must actually still certify.
Confirming it is exactly the one governed execution C9 was chartered to perform.

### Blocker 2 — stands, for a more precise reason than first given

| | pinned | local |
|---|---|---|
| python | 3.12.3 | 3.14.5, plus 3.11.15 |
| numpy | 2.5.2 | absent |
| python-flint | 0.9.0 | absent |
| FLINT | 3.6.0 | absent |

An isolated venv **was built and tested** on python 3.11.15 (which has pip, venv and a working CA
bundle). It failed: **numpy 2.5.2 requires Python ≥ 3.12**, which is not installed. A different numpy
would break the runtime-identity pin, and the taboo candidate comes from `np.linalg.solve`, so a
different BLAS could change it. Installing Python 3.12 via Homebrew is a *shared system* change, not
the dedicated environment the charter requires, and brew cannot pin FLINT to 3.6.0.

Two first-pass claims here were wrong and are withdrawn: "no network" (the TLS failure belongs to the
3.14 interpreter only) and "deterministic function of the inputs" (numpy linear algebra participates,
which also undercuts the claimed independence of the two blockers).

**And the governance half is dispositive on its own: no C9 host authorization artifact exists.**

### A provenance discrepancy any execution must resolve first

`REGISTRY_C2` records `c2_refined_registry = 4ac24d9e…`; the committed file hashes to `0d1d8021…`.
`taboo_certify` matches. C9's first pass asserted the recorded configuration was "checkable field by
field" and never checked it.

## Verified before the stop

- **Cell 307 reconstructed independently**, importing no C8 module, reproducing C8's thresholds to
  `0.00e+00` and Γ to `6.94e-18`:
  current `eff` **5.597995510441** (binding on `τ/D_lo`), Γ **+0.026354631323**, `M_R2` clip
  **5.335183825**, budget **3.114961361**.
- **Closure 1.0960072461462×** (new `eff` ≤ 5.107626368461) and **adoption 1.3700090576827×**
  (new `eff` ≤ 4.086101094769), carried as *distinct* fields so one can never be substituted for the
  other.
- **E1 is genuinely zero-new-real**, verified at the producer rather than inherited: it declares
  operator-only with no source `S_r`, no candidate object, no K1 record, no value of `R`, and
  `NEW_REAL_ADDRESSES = 0`.
- **Not DATA_BLOCKED**: the certifier needs no K1 records. C6's never-serialized candidate
  polynomials are not required.

## Scope held

Cells **306**, **308** and **309** were never targeted, never evaluated, and no new operator tuple
was computed for any of them. `r5` remains authoritative; **no r6**. C2–C8, r4, r5 and main are
untouched.

## What a successor needs

1. **A governance decision on host provisioning** — still separately governed, as C6 and C8 recorded.
   Python 3.12.x plus FLINT 3.6.0, numpy 2.5.2 and python-flint 0.9.0, in a dedicated environment.
2. **Resolve the producer-hash discrepancy** before claiming to reproduce or improve the registry.
3. **Run the α search**, not a finer partition. The first pass told a successor "more CPU does not
   buy this" and pointed at finer sub-blocks; that advice was wrong and is withdrawn. The cheap lever
   is a lower α rung at the same geometry.
4. **Decide, before spending anything, whether closure without adoption is worth it.** Cell 307 can
   be closed but not adopted by this route. That is a programme judgement, not a campaign's.

## Layout

    code/c9_common.py       process identity by executable, never pgrep -f or ps|grep
    code/c9_chain.py        independent reconstruction of the cell-307 clause
    code/c9_b0_audit.py     22-check predecessor audit, no tautologies
    code/c9_phase1.py       exact reconstruction + cross-check against C8
    code/c9_forensics.py    producer dependency graph and the DATA_BLOCKED test
    code/c9_toolchain.py    runtime qualification and the two blockers
    STOP_RECORD_C9.md       the stop, its authority, and what was not done
