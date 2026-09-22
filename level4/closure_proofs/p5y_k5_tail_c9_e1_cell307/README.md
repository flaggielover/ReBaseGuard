# C9 — E1 zero-new-real operator certification, CUSUM m=5 cell 307

**Result: `HARD_STOP_BEFORE_AUTHORIZATION`.** No certification was executed. No scientific address
was evaluated. Guard **DENY** throughout.

Target executions **0**, operator certifications **0**, new-real addresses **0**, AWS contacts **0**,
toolchain provisioned **0**, r6 **not created**.

## What C9 set out to do

C8 selected route **R3 / E1** — a tighter certified operator tuple — with **cell 307 first**. C9 was
chartered to execute exactly that: one cell, one route, one authorized certification.

## What C9 found

Two **independent** blockers. The first is scientific and does not depend on any host.

### Blocker 1 — E1 *as committed* cannot close cell 307

Re-running the committed producer on cell 307 reproduces the committed cell-307 block **exactly**.
Every quantity that controls tightness is a hardcoded module constant:

    SUB_BLOCK_MAX_WIDTH = 1/100     DEGREE_TABOO = 20     DEGREE_ARL = 12
    TABOO_ALPHAS = (6/5, 13/10, 7/5, 3/2, 2, 3)
    ARL_ALPHAS   = (5/4, 7/5, 3/2, 2, 3, 5)

The CLI exposes only `--outdir`, `--cells`, `--workers` — none of them scientific. The arithmetic is
exact `Fraction` plus `flint.arb` at fixed precision, and the committed registry records the exact
configuration it was produced under.

> Achieved tightening would be **1.0000×** against a required **1.0960072461462×**.

Obtaining 1.096× requires a **different producer configuration** — finer sub-blocks, higher degree,
or a different alpha ladder. That is a source mutation of a geometry the C2 gate froze as *"the
geometry of the ADOPTED registry r1, rather than a width tuned to the tail"*. It is a new prospective
protocol and a different campaign, not "one authorized execution of the committed E1 producer". The
charter is explicit: *document the blocker, do not improvise around it.*

This is labelled a **structural inference**, not an executed verification — executing it needs the
toolchain that blocker 2 shows is absent.

### Blocker 2 — no qualified runtime, no authorized host

| | pinned in committed evidence | present locally |
|---|---|---|
| python | 3.12.3 | 3.14.5 only |
| numpy | 2.5.2 | absent |
| python-flint | 0.9.0 | absent |
| FLINT | 3.6.0 | absent |

No `python3.12`, no FLINT system libraries, and the local interpreter cannot verify TLS certificates.
**No C9 host authorization artifact exists.** AWS is forbidden by charter. Vultr is not authorized and
the charter forbids assuming authorization from historical use. A Homebrew install is system-wide and
shared, so it is not the *dedicated* certification environment the charter requires, and brew does
not pin FLINT to 3.6.0. The local machine is also macOS/arm64 while the pins point at Linux, and
architecture is part of the runtime identity manifest the charter mandates.

The two blockers are independent: blocker 1 holds with a perfect host; blocker 2 holds even if the
producer could improve.

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

1. A **governance decision on host provisioning** — still a separately governed prerequisite, exactly
   as C6 and C8 recorded.
2. A **new prospective protocol** for a finer operator certification, freezing the changed geometry
   before any result exists.
3. Honest expectations: C2's own refinement (one block → 1/100 sub-blocks) moved `A0` only 4.5–4.9 %
   while making `τ` 1.90–2.24 % **worse**. A further halving is a much smaller step than that one,
   and 8.76 % is required. **More CPU does not buy this.**

## Layout

    code/c9_common.py       process identity by executable, never pgrep -f or ps|grep
    code/c9_chain.py        independent reconstruction of the cell-307 clause
    code/c9_b0_audit.py     22-check predecessor audit, no tautologies
    code/c9_phase1.py       exact reconstruction + cross-check against C8
    code/c9_forensics.py    producer dependency graph and the DATA_BLOCKED test
    code/c9_toolchain.py    runtime qualification and the two blockers
    STOP_RECORD_C9.md       the stop, its authority, and what was not done
