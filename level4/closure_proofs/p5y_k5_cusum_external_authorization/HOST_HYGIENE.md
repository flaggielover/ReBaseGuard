# Host hygiene on rebaseguard-vultr-02 before the authorization packet (2026-09-18)

Non-scientific cleanup, requested by the owner, so that leftover debris cannot confuse a later preflight or
adjudication. Nothing listed here is evidence for any protocol. None of the following was touched: a K1 export,
qualification evidence, a frozen checkout, a scientific artifact, the real namespace `/root/work/k5-first-real-probe`
(absent), or AWS.

| time (UTC) | change |
|---|---|
| 14:18:32 | Stopped the stale diagnostic shell loop, pid 182342, with SIGTERM. It was `bash -c` from r3 infrastructure development in `/root/work/k5r-wt` and had run about 50 h. Its `pgrep -f '[r]esolvent_certificate'` waiter matched its own command line, so it never exited. It had launched nothing since it started, and no python child existed. |
| 14:18:30–14:18:58 | Archived and then removed three 2026-09-17 executor mutation-check scratch directories: `/tmp/exec-mc-hi0_0poj`, `/tmp/exec-mc-kyu6g4m4` and `/tmp/exec-mc-rw50vtd4` (87 files). |

**Why the three directories were removed.** Each held `rf/t14_*/o/VOID_RECORD_SEALED.json` from a tripwire test, with:
- failure "TRIPWIRE_REACHED: real backend entered";
- `computed_before_failure = {}`;
- executor binding `UNBOUND_QUALIFICATION`.

So none contained any scientific number. No committed evidence referenced them.

**Where they are kept.**
- Archive: `/var/tmp/hygiene-20260918-extauth/exec-mc-tripwire-debris.tgz`, sha256
  `7dae3bd08dcc7840cb9dbf2dcb03c7937a51890b6ba1a8cf620c9e2e15e1cc4e`.
- Per-file sha256: `ORIGINAL_FILES_SHA256.txt` in the same directory.

The other `/tmp/exec-mc-*` and `/tmp/exec-cramer-*` scratch directories were left in place; they contain no file
with a sealed-record name.

**Not changed:**
- The unattended-upgrade timers stay active. The next `apt-daily-upgrade` run is 2026-09-19 06:04 UTC, so the final
  preflight must re-check P07.
- The repository mirror `/root/work/postk1.git` is not changed by this record. Its handling is reported in the
  packet's RESULT.
