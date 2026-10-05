# OD-R2-4: the host-change decision packet (deliverable 4 of 10)

**Status.** Owner message 5 placed OD-R2-4 at **DEFER**: "Bring OD-R2-4 back to me after the read-only host audit
identifies the exact host changes, if any, that require owner consent. Do not infer consent to host mutation from
OD-R2-3."

**This packet does not answer OD-R2-4.** It is the form in which OD-R2-4 is brought back after 8a. The "current
state" column is filled from the 8a evidence (`HOST_READ_ONLY_AUDIT_8A.md`); here it names the exact audit field to
copy. Items the audit shows to be unnecessary are marked "not needed" with their evidence, and are not asked.

**Who consents.** Each item needs the **owner's** consent. An item marked "host-wide" also needs the **cell-308
operator's** consent (`governance/OWNER_DECISION_PACKET_R2.md`, OD-R2-4's heading: "host changes requiring consent
(the owner's and the cell-308 operator's)"; `governance/R2_DELTA_FOLLOWUP_5_RECORD.md`: OD-R2-4 covers "the cell-308
operator's consent for mutation 4"; message 3 items 3, 6 and 8).

**Who executes.** A host administrator executes, through the P309 host-side session's access path (OD-R2-3). This
Cloud Session never does. Every change is recorded before and after (§4).

## 1. r2's consentable host mutations (M1–M5; `OWNER_DECISION_PACKET_R2.md` OD-R2-4)

### M1: the P309 Unix user

| field | content |
|---|---|
| current state | 8a: no such user (S-17 uid list). The groups that can read the cell-308 checkout: from the operator (Part A), and `foreign_roots.*.meta_sha256` |
| proposed state | a user `<P309_USER>` (proposed name `p309`) with its own primary group `<P309_GROUP>`, a home `<P309_HOME>`, and **no** supplementary group. Not in `sudo`, `adm`, `docker`, `systemd-journal` or any group with access to cell 308's checkout |
| command | `useradd --create-home --user-group --shell /bin/bash <P309_USER>`, then `id <P309_USER>` (it must list only `<P309_GROUP>`) |
| reversibility | full: `userdel --remove <P309_USER>`, after every evidence file is committed and pushed |
| risk | low. A new uid appears in the process table; the cell-308 gate and monitor on cell 308's side, if any, may need to know it |
| why required | `R2_HOST_REQUIREMENTS.md` §5 (separate user); the launcher refuses root as the unit user (A16); `isolation.foreign_roots_unreadable` is judged as this user |
| proceed without it? | **no**. The launcher refuses root, and isolation cannot be shown |

**P309 files inside the home.** Consent to M1 is asked together with these items. They write only inside
`<P309_HOME>` or the M2 volume, and are listed so that nothing is inferred:

| id | item | command (as `<P309_USER>`) | reversible |
|---|---|---|---|
| F-1 | the P309 clone | `git clone --single-branch --branch claude/p5y-k5-cell309-p309-r2 https://github.com/flaggielover/ReBaseGuard.git <CLONE>`, with the credential supplied by a credential helper outside the repository configuration (SI §3: "credential kept outside the repository config"). Then `git -C <CLONE> rev-parse HEAD` = `501f48cb31fd3f80d5c6dd33f1eef6b8f01b2853` | delete the clone |
| F-2 | the P309-only credential's storage | the owner's choice of mechanism, with one constraint from r2's bytes. `isolation.p309_config_has_no_credential` refuses any `credential.*` or `*.extraheader` key, or a URL with user:password, in **every** scope `git config --list --show-scope` shows (system, global and local). So the credential may not be configured in `/etc/gitconfig`, `~/.gitconfig` or `<CLONE>/.git/config`. It is supplied per command (for example `GIT_ASKPASS` pointing to a P309-only helper outside the clone, or `git -c credential.helper=… fetch` for that one command), and only for fetch and push, never while a check or a window runs | delete |
| F-3 | the host configuration file | `<P309_HOME>/p309_host_config.json`, per §2 and SI §3.1 (readable by the P309 user, not world-writable). A copy without the six launch keys sits beside it for `p309_host.py`'s direct subcommands | delete |
| F-4 | the scratch base | `<SCRATCH_BASE>` on the P309 volume. A fresh, empty subdirectory per check and per run (never reused) | delete by literal path after evidence export |
| F-5 | this packet's tools | `<P309_HOME>/p309_packet_tools/`, fetched from the hardening branch at a named commit, sha256-verified, outside the clone | delete |

### M2: the P309 volume or quota

| field | content |
|---|---|
| current state | 8a: `disk_free_gb` for the planned roots; S-01 to S-03 (type, options, inodes) |
| proposed state | every P309 root (`<CLONE>`'s filesystem and `<SCRATCH_BASE>`) with **≥ 40 GB free** (R-DISK-1; 60 GB recommended), owned by `<P309_USER>`. Recommended (HP-only, R-FS-7): a local ext4, xfs or btrfs filesystem without `nobarrier`. Preferably the clone and the scratch base on **one** filesystem, so the drill's `fs_probe` covers the official run's filesystem (R-FS-9) |
| action | **(a)** if the existing filesystem has the space while leaving cell 308 its own: a directory `<P309_VOLDIR>` owned by `<P309_USER>` (`install -d -o <P309_USER> -g <P309_GROUP> -m 0750 <P309_VOLDIR>`). **(b)** otherwise, a new block volume attached by the owner through the cloud provider (not from this Cloud Session): `mkfs.ext4 /dev/<NEWDEV>`; `mkdir /p309vol`; an fstab line `/dev/<NEWDEV> /p309vol ext4 defaults,nofail 0 2`; `mount /p309vol`; `install -d -o <P309_USER> -g <P309_GROUP> -m 0750 /p309vol/scratch` |
| reversibility | (a) remove the directory; (b) unmount, remove the fstab line and detach. Both only after evidence export |
| risk | (a) consumes space cell 308 may need, so agree the space with the operator. (b) a mistyped device can destroy data: the administrator verifies `<NEWDEV>` with `lsblk` first; the fstab line must carry `nofail` so a missing volume cannot block a boot |
| why required | R-DISK-1 (`disk_available` in preflight and gate) |
| proceed without it? | **no**, if 8a shows < 40 GB free on a planned root. "Not needed" only if 8a shows ≥ 40 GB on an acceptable filesystem and the operator agrees to its use |

### M3: the launch privilege (polkit)

| field | content |
|---|---|
| current state | 8a: S-07 (polkit present and its version); S-06 (systemd version). No P309 rule exists |
| proposed state | one rules file, `/etc/polkit-1/rules.d/50-p309-r2.rules`, that lets `<P309_USER>` (and nobody else) manage only transient units named `p309-r2-(drill|qualify|hostrerun)-YYYYMMDDTHHMMSSZ.service`. **Option M3-a** (r2's text, SI §3): verbs `start` and `reset-failed`. **Option M3-b**: also `stop`, so that the P309 session can stop its own unit on a target-integrity incident or on the owner's instruction (HP §11). Without `stop`, such a stop needs the administrator |
| content | see the rule below this table |
| verification | the rule's effect cannot be shown read-only (8a §4). Before relying on it, the administrator confirms read-only that the host's systemd passes the `unit` and `verb` details for `StartTransientUnit` (`pkaction --action-id org.freedesktop.systemd1.manage-units --verbose`; the systemd version from S-06). **If the details are not passed, the rule grants nothing (fail closed), and the item returns to the owner.** It must never be widened to all units. The first real use is the 8d launch; a failed start there is NOT_STARTED, not an attempt |
| reversibility | full: delete the file (polkit reloads its rules) |
| risk | a broader rule than intended would let the P309 user start arbitrary system units. The regular expression and the user test bound it. No sudo rule is used (r2: "the code never uses sudo") |
| why required | R-SD-4: the launcher calls `systemd-run` for a **system** unit with `--uid`/`--gid` |
| proceed without it? | **no**. The unit cannot start |

The proposed rule file, `/etc/polkit-1/rules.d/50-p309-r2.rules`:

```javascript
polkit.addRule(function(action, subject) {
    if (action.id != "org.freedesktop.systemd1.manage-units" || subject.user != "<P309_USER>")
        return polkit.Result.NOT_HANDLED;
    var unit = action.lookup("unit") || "", verb = action.lookup("verb") || "";
    var ok = /^p309-r2-(drill|qualify|hostrerun)-[0-9]{8}T[0-9]{6}Z\.service$/.test(unit);
    if (ok && (verb == "start" || verb == "reset-failed"   /* M3-a */
               /* || verb == "stop"                           M3-b, only if consented */))
        return polkit.Result.YES;
    return polkit.Result.NOT_HANDLED;
});
```

### M4: durability holds per window (host-wide; the cell-308 operator must agree)

| field | content |
|---|---|
| current state | 8a: `auto_update.*` (`apt` keys per file, `automatic_reboot`, `unattended_upgrades_active`, `dnf_automatic_enabled`, `needrestart_mode`, `reboot_required`); S-15, S-16 |
| proposed state, for each agreed window only | `unattended-upgrades.service` inactive; `apt-daily.timer` and `apt-daily-upgrade.timer` stopped; no file under `/etc/apt/apt.conf.d` sets `Unattended-Upgrade::Automatic-Reboot` to `"true"` or `"1"` (the preflight reads **each file**: a later file saying `"false"` does not cure an earlier `"true"`); needrestart mode not `a`; on dnf systems `dnf-automatic.timer` not enabled |
| command (before the window) | `systemctl stop unattended-upgrades.service apt-daily.timer apt-daily-upgrade.timer`. Then edit, in the exact file(s) 8a names, `Unattended-Upgrade::Automatic-Reboot "false";`, and, in `/etc/needrestart/needrestart.conf`, `$nrconf{restart} = 'l';` (list only). Record each file's sha256 before and after |
| command (after the window) | restore each edited file to its recorded bytes; `systemctl start apt-daily.timer apt-daily-upgrade.timer unattended-upgrades.service` |
| reversibility | full, by the after-window commands |
| risk | **host-wide**: security updates are delayed for the window (about 9–12 h). Cell 308 is affected too, which is why the operator must consent |
| why required | R-DUR-1/2 (`no_automatic_reboot`, `upgrades_held`). A reboot or upgrade mid-window ends the attempt (Q-HOST continuity) |
| proceed without it? | **no**. The preflight refuses unless the 8a state already satisfies it |

### M5: the P309-private CPython 3.11.15

| field | content |
|---|---|
| current state | 8a: `tools.python3_11` (whether a system `python3.11` exists; it is never used as the pinned interpreter); S-11; the build dependencies present, observed read-only, e.g. `dpkg -s build-essential libffi-dev zlib1g-dev libbz2-dev liblzma-dev libssl-dev 2>/dev/null \| grep -E '^(Package\|Status)'` |
| proposed state | `<P309_HOME>/opt/python3.11.15/bin/python3.11` (`<INTERP>`): CPython 3.11.15, built by `<P309_USER>` from the python.org source release. Its real path, binary sha256 and the host glibc are recorded for the host configuration (`interpreter`, `glibc`) |
| commands (as `<P309_USER>`) | fetch `Python-3.11.15.tgz` from python.org through the P309 session, and verify it against python.org's published checksum or signature for 3.11.15 (record the sha256); `tar xzf Python-3.11.15.tgz`; `cd Python-3.11.15`; `./configure --prefix=<P309_HOME>/opt/python3.11.15`; `make -j2`; `make install` |
| checks after | `<INTERP> -VV` shows `Python 3.11.15`; `<INTERP> -c 'import platform; print(platform.python_implementation())'` prints `CPython`; `<INTERP> -B -c 'import argparse, ast, copy, datetime, fractions, functools, glob, hashlib, importlib, json, math, multiprocessing, os, pathlib, platform, pwd, random, re, resource, runpy, shutil, signal, socket, stat, subprocess, sys, tempfile, time, types, unittest, urllib.request, uuid'` (the stdlib set r2 imports at `501f48cb`); `sha256sum "$(readlink -f <INTERP>)"`; `getconf GNU_LIBC_VERSION` |
| reversibility | full: delete `<P309_HOME>/opt/python3.11.15` and the build tree |
| risk | the build is CPU work on a shared host. Run it at a time the cell-308 operator agrees (message 3 §3), with `-j2`. If build dependencies are missing, see X-7 |
| why required | R-PY-1–4 (`python_exact`, `interpreter_pinned`, the manifest's runtime binding) |
| proceed without it? | **no** |

## 2. The unit limits and host-configuration values (agreed under OD-R2-4; SI §3.1)

| id | setting | current | proposed | why | proceed without? |
|---|---|---|---|---|---|
| U-1 | `memory_max` | 8a: `mem_total_gb`, `mem_available_gb`; the operator's working-memory figure (8c Part B) | ≤ `mem_total_gb` − the cell-308 working memory − a margin; SI's example `12G` only if that fits. The P309 peak was under 1 GB with 4 jobs, plus the K02 TEST processes (2 × 512 MB) | P20; "must leave cell 308 its working memory" | no (a launch key) |
| U-2 | `oom_score_adjust` | — | `500` (SI's example: P309 is preferred for an OOM kill) | P20 | no (a launch key) |
| U-3 | `cpu_weight` | — | `20` (low; SI) | P20 | no |
| U-4 | `io_weight` | — | `20` (low; SI) | P20 | no |
| U-5 | `unit_user`, `unit_group` | — | `<P309_USER>`, `<P309_GROUP>` | A16 | no |
| U-6 | `load_baseline`, `load_margin` | 8a `cpu.loadavg`; measured with the operator | the measured idle 1-min/5-min load; margin `0.5` (r2's default) | P9; gate `load_at_baseline` | no |
| U-7 | thresholds `heavy_cpu_fraction`, `monitor_heavy_cpu_fraction`, `monitor_aggregate_cpu_fraction`, `monitor_gap_tolerance_s`, `sample_s`, `suspend_tolerance_s`, `ram_floor_gb`, `disk_floor_gb`, `min_cpus`, `python_version` | — | r2's defaults: `0.05`, `0.5`, `1.0`, `45`, `60`, `5`, `8`, `40`, `4`, `3.11.15`. Changing any is a host-configuration change recorded in the launch record (OD-R2-5); this packet proposes none | OD-R2-5 | — |

## 3. Additional host changes that 8a may show to be needed (X-items)

These are not in r2's M1–M5 list. Each is asked only if its 8b row fires. Each is **host-wide** unless stated, so
the cell-308 operator's consent is needed too.

| id | when (8b row) | current state | proposed state | command / action | reversible | risk | why | proceed without? |
|---|---|---|---|---|---|---|---|---|
| X-1 | B-19 pending reboot | `/var/run/reboot-required` present | absent | one reboot at a time the operator agrees, outside any window; then re-run 8a | n/a (the event) | interrupts cell 308 | R-DUR-3 | no |
| X-2 | B-21 NTP | `NTPSynchronized=no` / absent | `yes` | `timedatectl set-ntp true` (systemd-timesyncd), or the host's chrony | yes (`set-ntp false`) | clock step at enable time | R-CLK-1 | no |
| X-3 | B-22/B-23 identity | hostname mismatch / no machine-id | static = running hostname; machine-id present | `hostnamectl set-hostname <current running name>` / `systemd-machine-id-setup` | yes (restore the previous files) | other software keyed on the hostname; never during a window | R-ID-1/2 | no |
| X-4 | B-24 hidepid | `/proc` with `hidepid` | readable as the P309 user | `mount -o remount,hidepid=0 /proc`, and the same in fstab; or `hidepid=…,gid=<a P309 group>` | yes | weakens process privacy host-wide | R-FS-10 | no |
| X-5 | B-25 git | < 2.32 / absent | ≥ 2.32 | the distribution's git package | yes | a package change on the host | R-GIT-1 | no |
| X-6 | B-17a/B-26 | polkit or `systemd-run` absent | present | the distribution packages providing them | yes | a package change | R-SD-2/4 | no |
| X-7 | B-20a | M5's build dependencies absent | present | the distribution packages named in M5's check; or a prebuilt CPython 3.11.15, which r2 does not describe and which would need its own review | yes (remove the packages) | a package change | R-PY-1 (M5) | no (M5 needs it) |
| X-8 | B-27 | a cgroup v2 controller missing | `memory cpu io` available | kernel or boot configuration (a reboot) | yes | a host-wide reboot and configuration change | R-SD-6 | no |
| AF-1 | B-12 | the cell-308 checkout world-readable | the owner's amendment of message 3 §6, with the operator's consent (e.g. restricting the checkout's mode) | return to the owner first (message 5 AF-1). **Nothing of cell 308 is changed by P309** | — | — | R-ISO-4 | no |
| AF-2 | B-10 | no IMDS | a reviewed portability delta of `durability_preflight` | return to the owner (message 5 AF-2); never pre-emptive. It changes r2's bytes, so the drill would no longer be on `501f48cb` | — | re-review and new bytes | R-IMDS-1 | no |

## 4. Applying consented items exactly, and proving it (read-only checks after the change)

For each consented item, the administrator records:
- the UTC;
- the exact command;
- the before and after state, using the read-only command below.

The P309 session then checks the result. The record is `host_evidence/APPLIED_CHANGES_<UTC>.json` in this hardening
namespace.

| item | read-only proof that it was applied exactly |
|---|---|
| M1 | `id -nG <P309_USER>` prints exactly `<P309_GROUP>` (no supplementary group); `getent passwd <P309_USER>` shows `<P309_HOME>` |
| M2 | `findmnt -no SOURCE,FSTYPE,OPTIONS --target <P309_VOLDIR>`; `df -PT <P309_VOLDIR>` (≥ 40 GB); `stat -c '%U:%G %a' <P309_VOLDIR>` |
| M3 | `sha256sum /etc/polkit-1/rules.d/50-p309-r2.rules`, equal to the consented text's sha256; `ls /etc/polkit-1/rules.d` shows no other P309 file |
| M4 | `systemctl is-active unattended-upgrades.service apt-daily.timer apt-daily-upgrade.timer` (all inactive); `grep -rn 'Automatic-Reboot' /etc/apt/apt.conf.d`; `grep -n 'nrconf{restart}' /etc/needrestart/needrestart.conf`; and, after the window, the restore |
| M5 | `<INTERP> -VV`; `sha256sum "$(readlink -f <INTERP>)"`, equal to the host configuration's record; the import check |
| U-1…U-7 | the host configuration file's sha256 equals the consented values' file; A-02d's launch record shows them (`launch_settings`, `host_config`) |
| X-n / AF-n | the 8a field that triggered the row now reads clear (re-run A-01 / A-02) |

**An unconsented change.** Any change not consented, or applied differently, is 8b row B-37: `HOST_REJECTED` until
the owner rules. The P309 session reverts nothing on its own.

## 5. Reply form (for the owner; not filled here)

```text
OD-R2-4 (after 8a <UTC>, audit sha256 <...>):
M1  CONSENT | DECLINE                         (with F-1..F-5)
M2  CONSENT (a) | CONSENT (b) | NOT NEEDED (evidence ...) | DECLINE
M3  CONSENT M3-a | CONSENT M3-b | DECLINE
M4  CONSENT WITH OPERATOR, windows <UTC..UTC> | DECLINE
M5  CONSENT | DECLINE
U-1 memory_max = <value> (operator agrees: yes/no); U-2..U-4 = <values>
X-n <only the rows that fired>: CONSENT | DECLINE
AF-1 / AF-2: <only if triggered; separate owner text>
```

The cell-308 operator's consent for M4, X-1–X-4, X-8 and U-1 is recorded in Part B of the 8c form, with the same
items quoted.
