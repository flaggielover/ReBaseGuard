# Cell-308 successor MB-S r1 architecture: addendum A1 (coordinator; consolidates the review conditions that bind the build)

**What A1 does.** It records, additively, the requirements the independent reviews imposed on the Phase 4–8
architecture (`governance/SUCCESSOR_ARCHITECTURE_308.md`, `8a4a02b4`, unchanged). A1 prevails where they differ. The
builder received these requirements as messages. Their authoritative texts are the cited reviews and errata.

**Timing correction (route re-check R3-N1; governance erratum E1 D2).** The builder was told about GC-6, RC1, RC2,
RC6, GC-8 and GC-10 in one message at about **2026-09-29 18:39Z**, and about DR2 later. Route A1 §3's "at about
20:40Z" is wrong. The builder's ledger lines and BUILD_REPORT record the actual receipt.

## §4 terminal rules, extended (route erratum E1, DR2; route re-check R3-N3)

* **(d) Platform-pin mismatch at resume.** At `execute`, at every `resume`, and in any mode that computes, the full
  RC2 pin (interpreter path and sha256, libpython sha256, `sys.version`, OS build, architecture) is re-verified. A
  mismatch at resume leads to `close-indeterminate` (CONSUMED_UNRECORDED class). There is never a mixed-platform
  resume.
* **(e) The no-update window** runs from the marker to the 7-day resume deadline. Preflight reads the
  automatic-update settings read-only and refuses when automatic installation is enabled. The user disables it; the
  campaign never changes system settings.

## Additions to §1, §2, §5 and §6 (governance S11, S15, S17; route RC1, RC2)

* **RC1 / S11.** These are sha256- and blob-identical to MB r1 at `c46434a3`:
  * the science modules;
  * the pins;
  * THEOREM_MB r1;
  * the rules D1–D10, D12–D14 and §8.

  The driver's science functions are text-identical (an AST source-equality test, which must also cover the
  module-level names those functions use, per route delta N3). The guard differs only in namespace and marker
  constants (a test enforces this).
* **RC2.** Platform pin; the MBR1_REPRO qualification case (exact equality with MB r1's committed r3 non-target
  records, QC02, QC03 and the QC04 pair); no OS or Python update between qualification and execution, and over the
  whole post-marker window.
* **S15 / GC-8.** Preflight and `execute` assert MB r1's recorded state:
  * the marker → `afa93072` is the only ref under its prefix;
  * there is no MB r1 pending ref, emergency file or `evidence/`.

  That marker is a **named** exception to "no prior evaluation". Planted extra and pending MB r1 refs must refuse.
* **S17 / GC-10.** Per-worker memory watchdog, with limits sized at the decoys; memory headroom at preflight;
  host-exclusivity preflight; nothing else runs until the seal.
* **S13 / GC-6.** Caps and limits come from decoy or synthetic evidence only. Whether MB r1's caps are kept or
  re-derived is a user decision under §14 / G2.

## Status

These are requirements. They become facts only at the successor qualification and freeze, which S16 gates. No
target step is authorised. New cell-308 target evaluations: 0.
