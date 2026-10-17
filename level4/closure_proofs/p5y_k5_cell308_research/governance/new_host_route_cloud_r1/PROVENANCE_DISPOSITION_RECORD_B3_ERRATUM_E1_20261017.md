# Erratum E1 to the B3 provenance record (Cell-308 Cloud route r1) — YC1 and YC4

**Status: AUTHOR CORRECTION · NOT INDEPENDENTLY CONFIRMED.** This erratum corrects
`PROVENANCE_DISPOSITION_RECORD_B3_20261016.md` (`f8987a93…2046`), which is preserved unchanged. Where they differ, this
erratum governs. Its source is the B3 confirmation (`reviews/external/CONFIRMATION_EXTERNAL_B3_CORRECTIONS.md`,
`6a721ada…253c`), findings YC1 (lines 76–82) and YC4 (lines 104–110). `new_target_evaluations = 0` ·
`cell309_activity = none`.

## E1.1 — The "gate" column (YC4)

The final column of §2–§5 ("gate where remaining evidence arises") is renamed **"intended evidence checkpoint"**.
* A checkpoint is where the record expects applicable evidence to be **checked**. It is **not** proof that the evidence
  exists, will arise there, or can only be produced there.
* A FUT or OPS category, or a checkpoint label, discharges **no** primary-source, corroboration or equivalence gap.

## E1.2 — Missing sources and equivalence evidence, listed on their own (YC4)

These gaps are independent of any host measurement. Each can be closed only by an eligible reviewer reading the
primary source and recording what it says. **None has been closed.** The coordinator side has not consulted any of
them for this purpose.

| row | missing evidence | primary source that would bear on it (not consulted) | does a host reading close it? |
|---|---|---|---|
| T03 | PSI semantics: what `some avg10` measures, and what a displayed `0.00` means. Its relation to macOS memory-pressure level 1 | Linux kernel documentation, `Documentation/accounting/psi.rst`; Apple's documentation of `kern.memorystatus_vm_pressure_level` | **no**: a reading shows a value, not its meaning or equivalence |
| T11 / a23 | CPython's default integer-string digit limit, and the effect of `sys.set_int_max_str_digits(0)` | the Python documentation for `sys.set_int_max_str_digits` and the integer string conversion length limitation | no |
| O01 / O02 | the equivalence of the Linux free-memory and idle-usage quantities to vm_stat and wired memory | `proc(5)` (MemAvailable, Inactive(file)); the cgroup v1 / v2 memory controller documentation; Apple's vm_stat documentation | no |
| O03 | the Linux low-power predicates (`platform_profile`, EPP `power`, `powersave` under each driver) | the kernel ACPI platform-profile documentation; `cpufreq` / `intel_pstate` / `amd-pstate` documentation | no |
| O04 / a17 | the power-supply status vocabulary (`Charging`, `Full`, `Not charging`) | the kernel sysfs ABI documentation for `power_supply` | no |
| O05 / a13 / a14 | the values of the inherited sleep-gap and sample-gap tolerances | the candidate's code at `142d97a9` (not allowlisted to B3) | no |
| O11 / a18 | the complete systemd unit search path list, and the update-vector semantics | `systemd.unit(5)`; the apt and unattended-upgrades documentation; the snapd and cloud-init documentation | no: a host shows its own units, not completeness |
| T06 | thermal-zone and trip-point semantics | the kernel thermal sysfs documentation | no |
| a6–a9 | journal event patterns, persistence and completeness signals | `journalctl(1)`, `journald.conf(5)`; `systemd-sleep(8)`; the kernel PM messages | no |

## E1.3 — §6, "Code-level constants": withdrawn (YC1)

§6's last bullet is **withdrawn**. It deferred the M1-style trace of every code-level constant to the implementation
review (B9-T), and said any untraced code constant blocks B10. It is replaced by the following:

> Every policy number, threshold, limit or rule needs its provenance traced before the owner decision that adopts it.
> Known items are listed, with their status, in `POLICY_PROVENANCE_INVENTORY_YC1_20261017.md`. A policy choice that
> will appear in code does not thereby become a later artifact. B9-T is only an additional conformance check of
> already traced requirements, and clears nothing. A policy choice first introduced after A17 is a later change
> (amendment erratum E2.5).

## E1.4 — Unchanged

Every B3 verdict and qualification recorded in §2–§5 stands. No value or rule is changed.
