# 07 — Reproducibility

A technically competent external reader should be able to reproduce the whole
Level 1–3 evidence base from a clean checkout using only this document.

**Reference machine** (everything below was measured on it):
macOS 26.5.2, arm64, Apple A18 Pro.

---

## A. Lean — the machine-checked analytic chain

### A.1 Prerequisites

* `elan` (the Lean toolchain manager) — <https://github.com/leanprover/elan>.
  `elan` reads `rebaseguard-lean/lean-toolchain` and installs the right compiler
  automatically; no manual version selection is needed.
* ~10 GB free disk for the Mathlib build cache.
* Network access **once**, for `lake exe cache get`. Everything afterwards is offline.

### A.2 Exact toolchain of record

| Component | Pinned value |
|---|---|
| Lean | `leanprover/lean4:v4.34.0-rc1` (`rebaseguard-lean/lean-toolchain`) |
| Lake | `5.0.0-src+3447a66` |
| Mathlib | `v4.34.0-rc1`, rev `de5ce8a9a66a4aa68a9bdbb35b63a06d34d9ca11` |
| batteries | `01bc479e7432594821ba3fb0ca465211941de86d` |
| aesop | `c1c4362a130f12e632d252180a6c2a31d8fd4726` |
| Qq | `3b55e9d00c6b0018e5d984eb011b6f93c09bd163` |
| proofwidgets | `99e8adeea3c3cd86b6b79ba01a1383bf2d31d055` |
| importGraph | `978b7ec9fbbf9a535114f1de8fe5b3778b358870` |
| plausible | `38e9c3ce15cbb63c92e90bb9a92e4eb82131f669` |
| LeanSearchClient | `2bc7cf064315b26bc38dac2e9612fb581be9b75f` |
| Cli | `af8bc067a4cc6c6df472a68909a3f40b1c76c43e` |

All revisions are fixed in `rebaseguard-lean/lake-manifest.json`; do not run
`lake update`, which would move them.

### A.3 Commands

```bash
cd /Users/suzhe/ReBaseGuard/rebaseguard-lean

# one-time: fetch the prebuilt Mathlib oleans (this is the only network step)
lake exe cache get

# full build of the ReBaseGuard chain
lake build
```

**Expected:** exit code `0`, final line `Build completed successfully (8717 jobs).`
Cosmetic deprecation/style warnings are expected and are listed in
`08_LIMITATIONS_AND_BOUNDARIES.md` §2.7.

Cold build from a fetched Mathlib cache: a few minutes. Warm rebuild: seconds
(jobs are replayed from `.lake/build`).

### A.4 Direct module compilation

`lake build` replays cached artifacts. To force genuine re-elaboration from
source, invoke the compiler directly:

```bash
cd /Users/suzhe/ReBaseGuard/rebaseguard-lean
for m in Basic StoppedLikelihood IntegralBridge Domination CUSUMBridge \
         StoppedQuantities StoppedWalkMoment SmallMoment ReBaseGuardIdentity; do
  echo "== $m"
  lake env lean "RebaseguardLean/$m.lean"; echo "exit=$?"
done
lake env lean RebaseguardLean.lean; echo "exit=$?"
```

**Expected:** every `exit=0`. Each module takes roughly 3.5–5 minutes wall time,
dominated by loading the Mathlib `.olean` files (the process is I/O-bound, ~10%
CPU); budget ~40 minutes for the full sweep. Measured times are recorded in
`03_LEAN_VERIFICATION.md`.

### A.5 Bypass scan

```bash
cd /Users/suzhe/ReBaseGuard/rebaseguard-lean
for pat in sorry admit axiom unsafe native_decide; do
  echo "--- $pat"
  grep -rniE "$pat" RebaseguardLean/ RebaseguardLean.lean || echo "  (none)"
done
```

**Expected:** `(none)` for all five patterns. Matches must be inspected
semantically, not treated as automatic failures — but in this project there are
none at all, including inside comments and docstrings.

### A.6 Axiom audit

```bash
cd /Users/suzhe/ReBaseGuard/rebaseguard-lean
cat > /tmp/AxCheck.lean <<'EOF'
import RebaseguardLean
open RebaseguardLean
#check @RebaseguardLean.hasDerivAt_rebaseguard_cusum
#print axioms stoppedIntegrand_hasDerivAt
#print axioms RebaseguardLean.hasDerivAt_integral_stoppedIntegrand_zero
#print axioms RebaseguardLean.hasDerivAt_integral_stoppedIntegrand_zero_of_expMoment
#print axioms RebaseguardLean.isStoppingTime_cusumTau
#print axioms RebaseguardLean.integrable_exp_forcingNat
#print axioms RebaseguardLean.ae_stopped_quantities_eq
#print axioms RebaseguardLean.integrable_exp_abs_walkAt_of_moment_tail
#print axioms RebaseguardLean.exists_pos_integrable_exp_abs_walkAt_rebaseguard
#print axioms RebaseguardLean.hasDerivAt_rebaseguard_cusum
EOF
lake env lean /tmp/AxCheck.lean
```

**Expected:** nine lines of the form

```text
'<name>' depends on axioms: [propext, Classical.choice, Quot.sound]
```

and no occurrence of `sorryAx`. Anything else is a hard failure.

---

## B. Arb — the rigorous numerical certificate

### B.1 Environment

| Component | Pinned value |
|---|---|
| CPython | `3.14.5` (`requires-python = "==3.14.*"`) |
| python-flint | `0.9.0` |
| FLINT / Arb | `3.6.0` |
| NumPy | `2.5.2` (candidate + diagnostics only) |
| SciPy | `1.18.0` (candidate + diagnostics only) |
| pytest | `9.1.1` |
| Working precision | 256 bits (residual, propagation); 192 bits (stored contraction) |

Full pin list: `rebaseguard-proof/requirements.lock` (11 lines, fully pinned
including transitive `iniconfig`, `packaging`, `pluggy`, `Pygments`, `pip`,
`setuptools`).

### B.2 Creating the environment

```bash
cd /Users/suzhe/ReBaseGuard/rebaseguard-proof
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip install --no-build-isolation --no-deps -e .
```

(The second `pip install` is the only network step; the editable install of the
local package uses `--no-deps` so the lock file remains authoritative.)

Verify:

```bash
.venv/bin/python -c "import sys, flint; print(sys.version.split()[0], flint.__version__)"
# expected: 3.14.5 0.9.0
```

### B.3 The certificate command

Replay the existing certificate (does **not** re-run the candidate solver):

```bash
cd /Users/suzhe/ReBaseGuard/rebaseguard-proof
.venv/bin/python -m rebaseguard_certify.audit proofs/certificate.json
#   or:  make audit
```

Regenerate everything from the candidate solve onwards, then audit:

```bash
make proof
```

> **Note:** `make audit` and `make proof` **rewrite** `proofs/audit_report.md`.
> In a clean reproduction the rewrite is byte-identical.

### B.4 Expected certified interval

```text
Gamma_lower = 3.9243482005828971281857775466050952672958374023437500000000000000000000000000000
Gamma_upper = 27.849382127546703280529527546605095267295837402343750000000000000000000000000000
Gamma_lower_gt_2 = true
status = PASS
mode = full replay
continuum_residual_replayed = true
```

Exit code `0`. On any failure the auditor prints `AUDIT FAIL: <reason>` and
exits `2`; `Gamma lower endpoint is not greater than two` is one of the guarded
conditions.

### B.5 Runtime and memory

| Task | Documented budget | Measured (reference machine) |
|---|---|---|
| `make test` | ~4 s | 3.87 s |
| `make audit` (full replay) | 100–420 s | **129 s** (this session); 187.91 s cold / 104.39 s warm on record |
| `make proof` + audit | 240–600 s | not re-run this session |
| Peak RSS | budget 268 435 456 B | 56 573 952 B on record |
| Artifact size | — | ~56 KiB |

### B.6 Output location

`rebaseguard-proof/proofs/` (certificate, audit report, residual, contraction,
enclosure, candidates, Bellman cross-check) and
`rebaseguard-proof/results/reproducibility.json` (environment, timings, hashes).

---

## C. Numerical validation

### C.1 Environment

Same virtualenv as §B.

### C.2 Commands, seeds and expected outputs

```bash
cd /Users/suzhe/ReBaseGuard/rebaseguard-proof

# 1. regression suite
.venv/bin/pytest -q
#    expected: "90 passed" (44 core + 20 phase4b + 26 phase4c), exit 0, ~4 s

# 2. Monte Carlo reference diagnostic  (seeds 1729 and 20260818, n = 200 000 each)
.venv/bin/python scripts/run_diagnostics.py
#    rewrites diagnostics/reference.json; ~5 s
```

Expected Monte Carlo values (deterministic given the seeds):

| Quantity | seed 1729 | seed 20260818 |
|---|---|---|
| `gamma` | `15.961901323226364` | `15.900990186311688` |
| `mean_z_tau_sq` | `4.051321303599967` | `4.050728751813283` |
| `cross_term` | `11.910580019626394` | `11.850261434498407` |
| `mean_tau` | `465.60712` | `462.539075` |
| `mean_t_tau_sq` | `463.8578273336159` | `463.2465185555655` |
| `up_fraction` | `0.498475` | `0.501055` |

> **Known drift.** The current `diagnostics.py` emits five extra summary fields
> (`arl`, `down_fraction`, `gamma_se`, `alarm_symmetry_gap`, `wald_second_gap`)
> that the stored `reference.json` predates. All *stored* fields reproduce
> bit-for-bit; the file will nonetheless differ by those additions. Use
> `git checkout -- diagnostics/reference.json` (or restore from a copy) if you
> want to leave the historical artifact untouched.

---

## D. Unified verification

```bash
/Users/suzhe/ReBaseGuard/scripts/verify_level_1_3.sh            # full (~7 min)
/Users/suzhe/ReBaseGuard/scripts/verify_level_1_3.sh --quick    # skips the 4-min direct elaboration
```

### What it checks

1. Lean toolchain identification (Lean/Lake versions, Mathlib rev).
2. `lake build` — fails on nonzero exit.
3. Bypass scan for `sorry`/`admit`/`axiom`/`unsafe`/`native_decide` — any hit is
   reported in full and fails the run.
4. Axiom audit of the nine principal theorems plus `#check` of the final
   theorem — fails on `sorryAx`, on any non-baseline axiom set, or if fewer than
   nine reports appear. (`4b`, skipped by `--quick`, additionally re-elaborates
   `ReBaseGuardIdentity.lean` from source.)
5. Arb certificate **full replay** — requires `status: PASS`,
   `Gamma_lower_gt_2: true` *and* `continuum_residual_replayed: true`, so a
   `--quick` audit could not be mistaken for a full one.
6. Numerical sanity — the regression suite, plus an **independent**
   recomputation (in `Decimal`, not via the auditor) that the stored interval
   equals `b̂(0,0) ± E_b`, excludes 2, carries the right model constants and
   target string, and contains both Monte Carlo estimates and the Bellman
   cross-check; it also re-checks the decomposition identity
   `Γ = E[Z_τ²] + E[Z_τT_{τ−1}]`.

### Design guarantees

* **Fails loudly.** Every failure prints the underlying log tail.
* **Nonzero exit on genuine failure** (`1`), on incomplete environment (`3`), on
  bad arguments (`64`).
* **No fake PASS.** A check that cannot run prints `SKIP` and, by default, makes
  the whole run exit `3` with `RESULT: INCOMPLETE`. `--allow-skip` is required to
  accept a partial verification, and even then the skip count is printed.
* **Non-destructive.** The one file the tools rewrite (`proofs/audit_report.md`)
  is backed up before and restored after; the script reports whether the
  regenerated file was byte-identical. Temporary files go to a `mktemp -d`
  directory removed on exit.
* **No network.** Nothing in the script fetches anything. (The one-time
  `lake exe cache get` of §A.3 is a prerequisite, not part of the script.)

### Execution record

See `03_LEAN_VERIFICATION.md` §7 and `LEVEL_1_3_CLOSURE_REPORT.md` §9 for the
actual exit code obtained in this session.
