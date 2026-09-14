# Host containment plan: automatic package drift on rebaseguard-vultr-02

**Status: PROPOSED, NOT APPLIED.** No package, hold, timer, service or apt configuration was changed. Applying this plan needs explicit operator approval. It must be applied before the new-glibc requalification and kept until the successor campaign reaches COMPLETE or is drained.

## 1. What upgraded glibc (read-only findings, 2026-09-14)

| Item | Observed |
|---|---|
| Trigger | `apt-daily-upgrade.timer` (`OnCalendar=*-*-* 6:00`, `RandomizedDelaySec=60m`, `Persistent=true`) fired at 06:10:40Z |
| Job | `apt-daily-upgrade.service` ran `unattended-upgrade`, which installed 51 packages between 06:10:49Z and 06:11:35Z |
| Policy | `/etc/apt/apt.conf.d/20auto-upgrades`: `APT::Periodic::Update-Package-Lists "1"`, `APT::Periodic::Unattended-Upgrade "1"` |
| Origins | `Unattended-Upgrade::Origins-Pattern`: Debian trixie, Debian-Security trixie, trixie-security |
| glibc | `libc6` / `libc-bin` went from `2.41-12+deb13u3` to `2.41-12+deb13u4` at 06:10:59; `libc.so.6` ctime 06:10:59.784621549Z |
| Lists-only timer | `apt-daily.timer` (`OnCalendar=*-*-* 6,18:00`, `RandomizedDelaySec=12h`) refreshes lists and does not install |
| `unattended-upgrades.service` | enabled and active. It is the shutdown helper; no install-on-shutdown key is set, so it installs nothing |
| Holds | none (`apt-mark showhold` is empty) |
| needrestart | not installed |
| Next scheduled install | `apt-daily-upgrade.timer` at 2026-09-15 06:27:29Z |

Runtime-relevant system packages at this freeze are `libc6`/`libc-bin 2.41-12+deb13u4`, `libgcc-s1 14.2.0-19`, `libstdc++6 14.2.0-19`, `zlib1g 1:1.3.dfsg+really1.3.1-1+b1` and `libcrypt1 1:4.4.38-1`. The kernel is `6.12.107+deb13-amd64` (`linux-image-amd64 6.12.107-1`). Exact hashes are in `config/REQUALIFICATION_PROTOCOL.json`.

## 2. Proposed containment (minimal, reversible)

**Step 0: record the pre-state.** Write `evidence/containment/PRE_STATE.json` containing:
- `systemctl is-enabled` and `is-active` for `apt-daily.timer`, `apt-daily-upgrade.timer`, `apt-daily.service`, `apt-daily-upgrade.service`, `unattended-upgrades.service`;
- sha256 of `/etc/apt/apt.conf.d/20auto-upgrades` and `/etc/apt/apt.conf.d/50unattended-upgrades`;
- the `apt-mark showhold` output (empty);
- the `dpkg-query` versions of the packages in §1.

**Step 1: stop the scheduled install and list refresh.**

```text
systemctl disable --now apt-daily-upgrade.timer apt-daily.timer
systemctl mask apt-daily-upgrade.service apt-daily.service
```

Masking the services also stops a `Persistent=true` catch-up run and any other unit from starting them.

**Step 2: disable periodic unattended upgrades as a new drop-in file.** No Debian-shipped file is edited.

```text
/etc/apt/apt.conf.d/99-rebaseguard-cusum-freeze:
APT::Periodic::Update-Package-Lists "0";
APT::Periodic::Unattended-Upgrade "0";
```

**Step 3: hold the runtime-bound packages** as a second, independent barrier.

```text
apt-mark hold libc6 libc-bin libgcc-s1 libstdc++6 zlib1g libcrypt1 linux-image-amd64 linux-image-6.12.107+deb13-amd64
```

**Step 4: verify, then record `evidence/containment/POST_STATE.json`.**
- Both timers are `disabled`/`inactive`, and both services are `masked`.
- `apt-config dump` shows both periodic keys at `"0"`.
- `apt-mark showhold` lists exactly the 8 packages.
- Every bound library hash still equals `config/REQUALIFICATION_PROTOCOL.json`.

`unattended-upgrades.service` is left unchanged. It installs nothing without an install-on-shutdown key, and steps 2–3 cover it anyway.

## 3. Restore procedure

Run it after the successor campaign is COMPLETE, or after a governed drain with no open attempts.

1. Check that no supervisor, keeper or worker is running and that no successor admission can happen.
2. `rm /etc/apt/apt.conf.d/99-rebaseguard-cusum-freeze`
3. `apt-mark unhold libc6 libc-bin libgcc-s1 libstdc++6 zlib1g libcrypt1 linux-image-amd64 linux-image-6.12.107+deb13-amd64`
4. `systemctl unmask apt-daily-upgrade.service apt-daily.service`
5. `systemctl enable --now apt-daily.timer apt-daily-upgrade.timer`
6. Check that unit states, apt config hashes and the (empty) hold list equal `PRE_STATE.json`.
7. Run one supervised `unattended-upgrade -v` in a maintenance window and record its package changes.

Any later campaign on this host must rebind the host facts.

## 4. Risks and disclosures

- **Security updates are deferred** for the containment window (projected at ~30–45 h of compute plus review time). The deferral must be explicitly accepted by the operator.
- **Provider maintenance is not covered.** Vultr host maintenance, a restart (new boot id) or a kernel change is outside this plan. The successor host guard fails closed on any bound-fact change.
- **Not an authorization.** This plan does not authorize requalification, carry-over or production.
