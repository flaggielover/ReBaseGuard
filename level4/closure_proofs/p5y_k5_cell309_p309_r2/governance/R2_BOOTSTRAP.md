# P309-r2 worker bootstrap (gate step 8, in the owner's order; addendum 2, F8)

**Nothing in this document runs before the owner decisions of step 7.** It also needs:
* **OD-R2-3:** access to the worker through a separate P309 session, never through cell 308's session;
* **OD-R2-4:** the shared-host changes, with the owner's and the cell-308 operator's consent.

Every command below is read-only until step 8c.

NEW Γ309 TARGET EVALUATIONS = 0 throughout.

## 8a. Read-only audit, before any clone, user or install

**The command.** The committed audit is fed to the worker's **system** Python on standard input. Nothing is written on
the worker, and no `.pyc` is created:

```text
python3 - audit --config-json '{"p309_roots": ["<planned P309 root>"], "foreign_roots": ["<cell-308 checkout path>"], "foreign_patterns": ["cell[_-]?308"], "foreign_heavy_patterns": ["<cell-308 heavy-job pattern>"]}' < p309_host.py
```

The keys are those `load_config` accepts: `foreign_patterns` and `foreign_heavy_patterns`. An unknown key, such as
the `cell308_patterns` of this file's first version, is refused (delta review C15). See
`R2_AWS_SESSION_INSTRUCTIONS.md` §1 for `foreign_uids`.

**Getting `p309_host.py` there:**
* it is the blob of `code/p309_host.py` at the reviewed commit;
* it reaches the worker through the P309 session, from GitHub;
* bulk data never passes through the owner's machine.

**What the audit records:**
* identities (hostname, machine-id, instance id) as sha256 only;
* cell-308 processes as counts, pids, uids and command-line sha256 only;
* cell 308's checkout only at its top directory: a `stat` hash, whether it is world-readable, and whether this user
  could read it.

**Output.** The audit's JSON is preserved in FNS2 `evidence/host/AUDIT_<utc>.json`.

## 8b. Verdict and consent

**The verdict.** Apply `R2_HOST_REQUIREMENTS.md` §4 to the audit: HOST_SUITABLE pending bootstrap, HOST_NOT_SUITABLE,
or HOST_SUITABILITY_PENDING.

**What to report to the owner and the cell-308 operator:**
* the CPU, RAM and disk measured;
* the exact list of bootstrap changes needed (below);
* the exclusive windows needed (`R2_HOST_REQUIREMENTS.md` §3).

**STOP** until OD-R2-3 and OD-R2-4 are answered with that list in hand.

## 8c. Bootstrap (only the consented items)

1. **The P309 user,** with no supplementary group that can read cell 308's checkout.
2. **The volume or quota** for the P309 roots (at least 40 GB free).
3. **The clone,** a single-branch clone of the r2 branch with full history (`git clone --single-branch --branch
   claude/p5y-k5-cell309-p309-r2 <repo URL>`). There is no shared object store and no alternates. The credential is
   P309-only and kept out of the repository config.
4. **The interpreter:** a P309-private CPython **3.11.15** under the P309 user's home, built or installed without
   touching the system Python. Record its path and sha256, and glibc's version, for the host configuration.
5. **The launch privilege:** a polkit rule that lets the P309 user start exactly transient system units named
   `p309-r2-*`, with the properties `code/p309_launch.py` sets. Nothing else. The launcher calls `systemd-run`
   directly; a sudo rule is not used by the code.
6. **The durability holds** consented under OD-R2-4: automatic reboot off and upgrades held for the window.
7. **The host configuration file** in the P309 user's home (not in the repository), with:
   * `p309_roots`, `foreign_roots`, `foreign_patterns`, `foreign_heavy_patterns` and `foreign_uids`;
   * the floors, the interpreter and glibc;
   * the launch settings: `unit_user`, `unit_group`, `memory_max`, `oom_score_adjust`, `cpu_weight`, `io_weight`.

After bootstrap, run `isolation` and `preflight` read-only. Both must pass.

## 8d. Worker-tier drill (P14)

**When:** only when the exclusion gate passes, at the start of an agreed window.

**How:** `python3 -B code/p309_launch.py --mode drill --host-config <file>` starts
`code/p309_topology_drill.py --tier worker` in its own unit. It never retries. The unit gets the configuration file's
path as `P309_HOST_CONFIG`, and the launch record binds its sha256.

**What follows:**
* the drill's ledger rows, witnesses and controls are committed in full under `evidence/drill/`;
* if it passes, the pre-freeze follow-up review follows (gate step 9);
* the r2 freeze is made **on the worker** (step 10).
