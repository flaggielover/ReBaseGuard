"""Phase I: detect an unsafe host-maintenance configuration BEFORE burning production CPU.

The 2026-09-12T06:01:57Z incident: apt-daily-upgrade.service upgraded systemd, systemd
re-executed, and the resulting service restart cascade tore the transient production unit
twice (06:01:57Z and 06:02:07Z). Root cause was environmental, not scientific.

This module NEVER modifies privileged host policy and never embeds a privilege command of
its own. Mitigation templates carry a {priv} placeholder that is filled from the FROZEN
lifecycle contract's hosts.<ROLE>.launch_prefix, exactly as the live systemd acceptance
does. The operator runs them; this code only reports and fails closed.
"""
from __future__ import annotations

import datetime as _dt
import json
import re
import subprocess
from pathlib import Path

DISRUPTIVE_UNITS = ("apt-daily-upgrade.timer", "apt-daily.timer",
                    "unattended-upgrades.service", "snapd.refresh.timer")

# {priv} is filled from the frozen contract; nothing privileged is hardcoded here.
SUPPRESS_TEMPLATES = [
    "{priv} systemctl mask --now apt-daily-upgrade.timer apt-daily.timer",
    "{priv} systemctl stop unattended-upgrades.service",
]
RESTORE_TEMPLATES = [
    "{priv} systemctl unmask apt-daily-upgrade.timer apt-daily.timer",
    "{priv} systemctl start unattended-upgrades.service",
    "{priv} unattended-upgrade -v",
]
RESTORE_NOTE = ("Masking DEFERS security updates for the authorized production window only. "
                "Restore as soon as the campaign drains; never leave a host unpatched.")


def privilege_prefix(contract_path, role="AWS") -> str:
    c = json.loads(Path(contract_path).read_text())
    return " ".join(c["hosts"][role]["launch_prefix"])


def mitigation(contract_path, role="AWS") -> dict:
    p = privilege_prefix(contract_path, role)
    return {"suppress": [t.format(priv=p) for t in SUPPRESS_TEMPLATES],
            "restore": [t.format(priv=p) for t in RESTORE_TEMPLATES],
            "note": RESTORE_NOTE}


def _run(*a):
    try:
        return subprocess.run(a, capture_output=True, text=True, timeout=30).stdout
    except Exception:
        return ""


def timers() -> list:
    out = []
    for line in _run("systemctl", "list-timers", "--all", "--no-pager", "--no-legend").splitlines():
        for u in DISRUPTIVE_UNITS:
            if u in line:
                m = re.match(r"^(.*?UTC)\s", line.strip())
                out.append({"unit": u, "next_utc": m.group(1) if m else None,
                            "raw": line.strip()[:150]})
    return out


def next_disruption_seconds():
    best, who = None, None
    now = _dt.datetime.now(_dt.timezone.utc)
    for t in timers():
        if not t["next_utc"]:
            continue
        nxt = None
        for fmt in ("%a %Y-%m-%d %H:%M:%S UTC", "%Y-%m-%d %H:%M:%S UTC"):
            try:
                nxt = _dt.datetime.strptime(t["next_utc"].strip(), fmt).replace(tzinfo=_dt.timezone.utc)
                break
            except ValueError:
                pass
        if nxt is None:
            continue
        d = (nxt - now).total_seconds()
        if d >= 0 and (best is None or d < best):
            best, who = d, t["unit"]
    return best, who


def gate(*, window_hours: float, contract_path=None, role="AWS", fail_closed: bool = True) -> dict:
    secs, unit = next_disruption_seconds()
    rep = {"disruptive_timers_active": [t["unit"] for t in timers()],
           "next_disruption_s": secs, "next_disruption_unit": unit,
           "window_hours": window_hours,
           "incident_precedent": "2026-09-12T06:01:57Z apt-daily-upgrade -> systemd re-exec -> unit torn"}
    if secs is None:
        rep["verdict"] = "SAFE_NO_ARMED_DISRUPTIVE_TIMER"
        return rep
    if secs < window_hours * 3600:
        rep["verdict"] = "UNSAFE_MAINTENANCE_INSIDE_WINDOW"
        if contract_path:
            rep["mitigation"] = mitigation(contract_path, role)
        if fail_closed:
            raise RuntimeError(
                f"HOST MAINTENANCE GATE: {unit} fires in {secs/3600:.1f}h, inside the declared "
                f"{window_hours}h window. This is the exact condition that tore run "
                f"20260912T041203Z-962132d3.")
        return rep
    rep["verdict"] = "SAFE_OUTSIDE_WINDOW"
    return rep


if __name__ == "__main__":
    import sys
    w = float(sys.argv[1]) if len(sys.argv) > 1 else 24.0
    print(json.dumps({"timers": timers(), "gate": gate(window_hours=w, fail_closed=False)}, indent=1))
