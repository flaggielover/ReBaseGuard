# CLOUD_FEASIBILITY_R2 — erratum E1 (coordinator; review 59 findings F16, F17 and the Q1 basis)

**Why.** The fresh independent review 59 (`reviews/REVIEW_CLOUD_R1_FEASIBILITY_AMENDMENT_DEV.md`, at `b3d8eb5e`)
returned **CLASSIFICATION: HOST_UNSUITABLE_CONFIRMED**, "on a sharper basis than the one given", and listed citation
and evidence errors (F16) and a misreading of the provider page (F17). `CLOUD_FEASIBILITY_R2.md` and
`OFFICIAL_PROVIDER_FACTS_20261014.md` stay byte-unchanged; this erratum prevails where they differ.

`new_target_evaluations = 0` · `cell309_activity = none`.

## 1. The primary basis of U1 (review Q1)

Added, and now the **primary** basis of the classification:

> [ACCEPTED] `registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1_ERRATUM_E1.md`, DR2: "**The no-update rule covers the
> whole post-marker window**, up to the 7-day resume deadline. The host's automatic OS and software updates must be
> disabled for that window. This is an operator action by the user; the campaign never changes system settings."

On the Anthropic-hosted environment the owner has no means to perform that operator action: the image is managed by
the provider, and it changed between the two observed sessions (OS point release 24.04.4 → 24.04.5, kernel build
`-fc-v64` → `-fc-v114`, Python 3.13.14 → 3.13.16, Python 3.10 removed, `libc6` package `2.39-0ubuntu8.7` →
`2.39-0ubuntu8.9`). Inside the guest, provider image updates are UNKNOWN by construction. This is a contradiction with
an accepted requirement, not a missing fact. The documented pause / reclaim behaviour (§2 below) and U3 remain
supporting reasons.

## 2. Pause versus reclaim (F16)

U1 is to be read with this distinction, which the provider page makes (`cloud-environments`, review 59 fetched copy
line 67): after a few minutes without activity the VM **pauses** with its files saved, and "Your next message restores
the same VM"; only a **reclaim** of a paused VM yields a fresh VM. A pause alone keeps the same VM; whether a running
computation survives a pause, and whether the guest clocks show it, is UNKNOWN (D-PAUSE). The owner brief r2 states
the distinction.

## 3. Citation and evidence corrections (F16)

| location | was | now |
|---|---|---|
| §2 E4, §3 U3 (and amendment H7) | "brief R2 §8 item 8" | **brief R2 §7 item 8** ("Failure / recovery consequence (A)", lines 355–357: "A platform change gives close-indeterminate") |
| §2 E2, last sentence | "Every platform-pin-relevant property except architecture and vCPU count differs" | **Overstated.** As recorded, the `glibc` version string is `2.39` on both hosts and `/usr/bin/python3.12` is 3.12.3 on both (with different file digests). The `libc6` **package** differs (r1 `2.39-0ubuntu8.7`, r2 `2.39-0ubuntu8.9`, read on this host with `dpkg-query` and recorded in the supplementary inventory `CLOUD_HOST_INVENTORY_R2B_20261014.json`). The CPU model, kernel build, OS point release, MemTotal, cgroup limit and interpreter set differ. |
| §3 U4 "(both hosts)" | no service manager, no power supply, no thermal zone, no suspend statistics, no journal | holds for both hosts for **systemd not PID 1, power supplies, thermal zones**; the r1 inventory recorded **no** suspend-statistics or journal reading, so those two hold for r2 only. |
| comparison booleans in `CLOUD_HOST_INVENTORY_R2_20261014.json` (`comparison_with_r1_20261004`) | `same: false` rows | the CPU-model, kernel, OS and interpreter rows are **format-confounded** (r1 strings carry suffixes and full `uname` text; r1 listed `/usr/bin/python3`, r2's glob excluded it). The differences are real when read by hand; the normalised comparison is in the supplementary inventory (F19). |

## 4. U2 restated (F17)

U2 is restated as: **no documented basis exists for an 8-hour unattended computation in this environment.** The
sentence "agent commands are limited to ≤ 10 min foreground plus ≤ 30 min background" is withdrawn: the provider page
also says that setting `BASH_DEFAULT_TIMEOUT_MS` above 1 800 000 ms lengthens the background limit (see
`OFFICIAL_PROVIDER_FACTS_20261014_ERRATUM_E1.md`), and the r1 inventory recorded a 2-hour cap in the agent tool's own
definition. Neither figure is a guarantee for a process detached from the agent, and neither reaches EVAL_CAP (8 h).

## 5. Classification after this erratum

Unchanged: **`HOST_UNSUITABLE`** for the official stages on the Anthropic-hosted Cloud session environment —
coordinator determination, **confirmed by review 59**. Every dependent official step stays blocked. The environment
remains usable for target-free development and review.
