# Full result-free rehearsal: one command, restart-safe, never qualification

**Tool:** `code/r2h_rehearse.py`, plus the shared `code/r2h_replica.py` and the independent `code/r2h_validator.py`
(this namespace, branch `claude/p309-r2-hardening-20261005`).

A rehearsal runs the package's **own** gate functions on a **synthetic, non-target freeze**. It is never
qualification evidence, it never invokes a target evaluator, and it never calls the runner's `main()`, the launcher or
Q-HOST.

## The command

```bash
# on the durable host, as the P309 user, into a NEW root on the P309 volume
python3 code/r2h_rehearse.py run \
    --source <path or https URL of the repository> \
    --commit <exact package commit>          # e.g. the hardening branch head, or r2 101ef2cb
    --root   <new directory>                 # created exclusively; must not exist
    --gates  all                             # 'light' = all but the decoy batteries QC06, QC08-QC10 (development)
    --workers 4 \
    --require-durable-host                   # refuse unless the host meets the durable-host rules

python3 code/r2h_rehearse.py status --root <same directory>     # read-only classification, at any time
```

Exit status: 0 only when the independent validator says **PASS**. `status` is read-only and safe during a run.

## What it does, in order (each step refuses on failure; nothing is retried, resumed or repaired)

| step | action | requirement it meets |
|---|---|---|
| 1 | `os.mkdir(root)` exclusively, then fsync its parent. An existing root is refused with an explicit message | restart-safety: an interrupted rehearsal can never be continued or turned into a success |
| 2 | Host and runtime facts are recorded: CPUs, available RAM, free disk, **filesystem type**, interpreter path and sha256, glibc, kernel, boot id, machine id and hostname as sha256, PID 1, container flags, uptime. `--require-durable-host` refuses below 4 CPUs, 8 GB RAM or 40 GB disk; without CPython 3.11.15; off {ext4, xfs, btrfs, zfs, ext3}; without systemd PID 1; or inside a container | host / runtime prerequisites |
| 3 | `git clone --no-local --no-checkout` of `--source`; fetch `--commit` if needed; **remove the remote** (nothing can be pushed from the clone); check out the exact commit; verify the clean tree and no protected ref; record commit, tree and parents, and whether the commit descends from r2 `101ef2cb` | fresh clone; exact refs and ancestry; clean state |
| 4 | Synthetic freeze: the package's **unmodified** `make_freeze_params.py`, then `make_freeze_manifest.py`, then `p309_placeholder_check.py` (the order of a real freeze: the manifest pins the parameter file); commit F′, a record-only child FR′, one checkpoint-style commit; witness: exactly one record commit at HEAD, its parent is F′, none in F′'s history, FR′ touches only the record | synthetic / non-target freeze setup (this order fixes F-DRILL-ORDER for the rehearsal) |
| 5 | `PROVENANCE.json` (durable) and a `RUN_START` row in `GATE_LEDGER.jsonl` (O_APPEND + fsync) | provenance, order |
| 6 | Import the package's `p309_qualify` **from the fresh clone** and wrap its `run()` with a self-guard that refuses the driver's `execute` / `seal-only` / `validate-grant` modes and the launcher or runner `main`. Then write the RUN START line in the clone's ledger (QC13 reads it), build the mirror, and run every requested gate through `items_table()` / `run_item()` (the runner's own lambdas and record writes) into `root/attempt` | every permitted gate; never a target evaluator |
| 7 | After each gate: a `GATE_RECORDED` row binding the record's sha256, pass flag and wall time (durable append) | gate content, hashes, order, timing |
| 8 | After the last gate: no protected ref and no grant or result file in the clone; a durable `REHEARSAL_SUMMARY.json` binding every record and the provenance; a `SUMMARY_RECORDED` row | completion marker |
| 9 | `r2h_validator.py rehearsal root` writes `root/VALIDATION.json`; the verdict is the rehearsal's result | independent validation of the finished evidence |

## Why a restart cannot turn an interrupted run into a success

- The root is created exclusively, so a second `run` into it is refused (shown below).
- A validator `PASS` requires all of: a `PROVENANCE.json` bound by the first ledger row; **exactly one** `RUN_START`;
  every requested gate's record present, parsing, naming itself and carrying the synthetic freeze; exactly one
  ledger row per record with the matching sha256 (rows only after records); no temporary file; a summary binding
  every record and the provenance; and the summary row last.
- An interruption at any step leaves at least one of those false. The result is `INTERRUPTED` (or `CORRUPT` if
  something was altered), never `PASS`.
- `status` also reports a reboot: the boot id differs from the provenance's.
- Copying records from another rehearsal fails the provenance binding and the per-row hashes. Appending rows fails
  "exactly one RUN_START" and the per-gate exactly-once check.

## What was demonstrated here (development only, this cloud container)

These runs are labelled DEVELOPMENT_ONLY, because message 4 item 13 excludes the cloud session as a durable host.

| run | result |
|---|---|
| kill test: a light rehearsal SIGKILLed after QC05 (runner and its gate child) | `status` gives **INTERRUPTED** ("no summary (10 record(s) missing)"); a second `run` into the same root gives `REHEARSAL REFUSED: … exists -- a rehearsal is never restarted or resumed` (rc 2); `status` afterwards: still INTERRUPTED |
| light rehearsal of the hardened package `3c191ac2` (all gates but QC06, QC08–QC10) | the validator reports **FAIL (COMPLETE_FAIL: QC15)**. Every protocol check passed: one RUN_START, every record bound by its ledger row, the summary last, no temporary file, no protected ref and no grant or result file in the clone. QC01–QC05, QC07, QC11–QC14, QC16, QC17, QC_U2 and QC_D5 (2 921 s) passed. QC15 fails on A7 only: the hardening branch carries `.claude/**` and the hardening namespace outside r2's namespace (a packaging artefact; R18). Host checks: DEVELOPMENT_ONLY. `evidence/rehearsal/light_3c191ac2/` |
| what this shows | the tool runs end to end, validates by content, and reports a gate failure as FAIL, not PASS. The full `--gates all --require-durable-host` run belongs on the durable host, on the package actually adopted (single file onto r2, T14a comment restored) |

## On the durable host

1. Run `--gates all --require-durable-host` once on the package that will be frozen. It must report **PASS**. This is
   a full ~6–9 h run, needs the §5 window of the host packet, and is itself subject to the exclusion gate's rules if
   the host is shared.
2. Then run the package's own worker-tier drill through the launcher (Q-HOST and the systemd unit, which this tool
   does not exercise). This requires F-DRILL-ORDER fixed in `p309_topology_drill.py`.
3. Only then, with the owner's OD-R2-0 (D), the freeze and the single official attempt
   (`DURABLE_HOST_EXECUTION_PACKET.md` §8).
