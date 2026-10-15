"""Offline development diagnostics. No execution or admission API exists here."""
import argparse
import datetime as dt
import json
import math
import re
import time

SCHEMA = 'P309_WINDOWS_CONTROL_SAMPLE/1'
THRESHOLDS = dict(min_cpus=4, ram_floor_gb=8, disk_floor_gb=40, sample_s=60.0,
                  heavy_cpu_fraction=0.05, monitor_heavy_cpu_fraction=0.5,
                  monitor_aggregate_cpu_fraction=1.0, suspend_tolerance_s=5.0,
                  monitor_gap_tolerance_s=45.0)
AWS_REPLACEMENTS = {
    'cloud_metadata_available': 'PENDING: authenticated host/boot/guest bridge',
    'not_spot': 'PENDING: local custody and interruption-risk evidence',
    'not_burstable': 'PENDING: effective quota and dedicated host capacity',
    'no_scheduled_maintenance': 'PENDING: update/task/window evidence and monitoring',
    'not_in_container': 'PENDING: explicit independently reviewed WSL exception',
}


def number(v):
    try:
        return type(v) in (int, float) and math.isfinite(v) and v >= 0
    except OverflowError:
        return False


def digest(v):
    return isinstance(v, str) and re.fullmatch('[a-f0-9]{64}', v) is not None


def stamp(v):
    try:
        parsed = dt.datetime.fromisoformat(v.replace('Z', '+00:00'))
        return parsed.timestamp() if parsed.tzinfo else None
    except (ValueError, TypeError, AttributeError, OverflowError):
        return None


def clock_valid(c):
    return (isinstance(c, dict) and all(number(c.get(k)) for k in ('wall_s', 'uptime_s', 'active_s'))
            and c['active_s'] <= c['uptime_s']
            and all(digest(c.get(k)) for k in ('host_id_sha256', 'boot_id_sha256')))


def continuity(a, b, max_gap=None):
    if not clock_valid(a) or not clock_valid(b):
        return False
    wall = b['wall_s'] - a['wall_s']
    elapsed = b['uptime_s'] - a['uptime_s']
    active = b['active_s'] - a['active_s']
    return (all(a[k] == b[k] for k in ('host_id_sha256', 'boot_id_sha256'))
            and wall >= 0 and elapsed > 0 and active >= 0
            and abs(wall - elapsed) <= THRESHOLDS['suspend_tolerance_s']
            and -0.05 <= elapsed - active <= THRESHOLDS['suspend_tolerance_s']
            and (max_gap is None or elapsed <= max_gap))


def assess(host, guest, previous=None, now=None, phase='start', baseline=None):
    """All inputs are untrusted observations, never signed/accepted claims."""
    checks = {}
    host = host if isinstance(host, dict) else {}
    guest = guest if isinstance(guest, dict) else {}
    previous = previous if isinstance(previous, dict) else {}
    baseline = baseline if isinstance(baseline, dict) else {}
    now = time.time() if now is None else now
    checks['schemas'] = host.get('schema') == SCHEMA and guest.get('schema') == 'P309_WSL_CONTROL_FACTS/1'
    checks['phase'] = phase in ('start', 'monitor')
    age_limit = THRESHOLDS['sample_s'] + THRESHOLDS['monitor_gap_tolerance_s']
    start, end = host.get('start'), host.get('end')
    checks['sample_continuity'] = continuity(start, end, age_limit if phase == 'monitor' else None)
    elapsed = end['uptime_s'] - start['uptime_s'] if checks['sample_continuity'] else None
    checks['full_sample_duration'] = number(elapsed) and elapsed >= THRESHOLDS['sample_s']
    # Proposal: evidence age bounded by existing sample + gap allowance (105 s).
    guest_time = stamp(guest.get('utc'))
    checks['freshness'] = (number(now) and clock_valid(end) and number(guest_time)
                           and 0 <= now - end['wall_s'] <= age_limit
                           and 0 <= now - guest_time <= age_limit)
    obs = host.get('process_observation')
    obs = obs if isinstance(obs, dict) else {}
    period = obs.get('cpu_elapsed_lower_bound_s')
    checks['full_sample_duration'] = (checks['full_sample_duration'] and number(period)
        and THRESHOLDS['sample_s'] <= period <= elapsed)
    rows = obs.get('rows')
    rows_ok = isinstance(rows, list) and bool(rows)
    identities = set()
    pids = set()
    if rows_ok:
        for row in rows:
            if (not isinstance(row, dict) or type(row.get('pid')) is not int or row['pid'] <= 0
                    or not digest(row.get('creation_sha256')) or not number(row.get('cpu_fraction'))):
                rows_ok = False
                break
            key = (row['pid'], row['creation_sha256'])
            if key in identities or row['pid'] in pids:
                rows_ok = False
            identities.add(key)
            pids.add(row['pid'])
    checks['process_rows_valid'] = rows_ok
    checks['visibility_complete'] = (obs.get('coverage') == 'ATTESTED_COMPLETE'
        and obs.get('protected_process_coverage') is True
        and obs.get('process_lifetime_events_complete') is True
        and type(obs.get('unreadable_count')) is int and obs['unreadable_count'] == 0
        and type(obs.get('disappeared_count')) is int and obs['disappeared_count'] == 0
        and type(obs.get('observed_count')) is int and isinstance(rows, list)
        and obs['observed_count'] == len(rows))
    limit = THRESHOLDS['heavy_cpu_fraction' if phase == 'start' else 'monitor_heavy_cpu_fraction']
    checks['individual_cpu_quiet'] = rows_ok and all(r['cpu_fraction'] <= limit for r in rows)
    checks['aggregate_cpu_quiet'] = rows_ok and (phase == 'start' or
        sum(r['cpu_fraction'] for r in rows) <= THRESHOLDS['monitor_aggregate_cpu_fraction'])
    policy = host.get('policy')
    policy = policy if isinstance(policy, dict) else {}
    checks['no_pending_reboot'] = policy.get('pending_reboot') is False
    checks['power_policy_observed'] = policy.get('power_query_ok') is True and all(
        type(policy.get(k)) is int and policy[k] == 0
        for k in ('sleep_ac_s', 'sleep_dc_s', 'hibernate_ac_s', 'hibernate_dc_s'))
    checks['update_and_task_coverage'] = (policy.get('update_policy_known') is True
        and policy.get('scheduled_tasks_query_ok') is True
        and policy.get('maintenance_window_approved') is True)
    checks['event_coverage'] = (policy.get('event_query_ok') is True
        and policy.get('event_window_covers_sample') is True
        and policy.get('events_since_start') == []
        and policy.get('event_log_cleared') is False)
    win = host.get('resources')
    win = win if isinstance(win, dict) else {}
    checks['ram_floor'] = all(number(v) and v >= 8_000_000_000 for v in (
        win.get('available_memory_bytes'), guest.get('available_memory_bytes')))
    checks['disk_floor'] = all(number(v) and v >= 40_000_000_000 for v in (
        win.get('backing_free_bytes'), guest.get('guest_disk_free_bytes')))
    checks['cpu_floor'] = all(number(v) and v >= 4 for v in (
        guest.get('affinity_cpus'), guest.get('effective_cpu_quota')))
    checks['systemd'] = guest.get('pid1') == 'systemd' and guest.get('systemd_state') == 'running'
    checks['private_runtime'] = (guest.get('python_version') == '3.11.15'
        and guest.get('python_implementation') == 'CPython'
        and guest.get('private_runtime') is True and digest(guest.get('interpreter_sha256'))
        and isinstance(guest.get('glibc'), str) and guest['glibc'].startswith('glibc '))
    checks['guest_identity_valid'] = all(digest(guest.get(k)) for k in ('boot_id_sha256', 'machine_id_sha256'))
    checks['policy_identity_valid'] = digest(policy.get('policy_sha256'))
    if phase == 'monitor':
        before_host = previous.get('host') if isinstance(previous.get('host'), dict) else {}
        before_guest = previous.get('guest') if isinstance(previous.get('guest'), dict) else {}
        checks['prior_checkpoint_continuity'] = continuity(before_host.get('end'), start, age_limit)
        checks['same_guest_runtime'] = all(guest.get(k) is not None and guest.get(k) == before_guest.get(k)
            for k in ('boot_id_sha256', 'machine_id_sha256', 'interpreter_sha256', 'glibc'))
        checks['unchanged_policy'] = (isinstance(before_host.get('policy'), dict)
            and digest(policy.get('policy_sha256'))
            and policy.get('policy_sha256') == before_host['policy'].get('policy_sha256'))
        base_host = baseline.get('host') if isinstance(baseline.get('host'), dict) else {}
        base_guest = baseline.get('guest') if isinstance(baseline.get('guest'), dict) else {}
        # Compare to immutable run baseline too: repeated sub-tolerance sleeps must accumulate.
        checks['baseline_continuity'] = continuity(base_host.get('start'), end)
        checks['baseline_guest_runtime'] = all(guest.get(k) is not None and guest.get(k) == base_guest.get(k)
            for k in ('boot_id_sha256', 'machine_id_sha256', 'interpreter_sha256', 'glibc'))
        checks['baseline_policy'] = (isinstance(base_host.get('policy'), dict)
            and digest(policy.get('policy_sha256'))
            and policy.get('policy_sha256') == base_host['policy'].get('policy_sha256'))
    return {'schema': 'P309_WSL_HOST_CONTROL_PROPOSAL/1', 'scope': 'DEVELOPMENT_ONLY',
            'phase': phase, 'checks': checks, 'candidate_observations_pass': all(checks.values()),
            'failed_or_unknown': [k for k, v in checks.items() if not v],
            'thresholds': dict(THRESHOLDS), 'proposed_aws_replacements': dict(AWS_REPLACEMENTS),
            'route_accepted': False, 'formal_admission': 'BLOCKED',
            'qualification_authorized': False, 'target_execution_authorized': False,
            'limitations': ['Inputs are caller-supplied, not authenticated or anti-replay protected.',
                           'Existing Linux load, isolation, NTP, unit and exactly-once gates still apply.',
                           'No accepted WSL route, long-window proof, or enforcement is provided.']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--host', required=True)
    p.add_argument('--guest', required=True)
    p.add_argument('--previous')
    p.add_argument('--baseline')
    p.add_argument('--phase', choices=('start', 'monitor'), default='start')
    args = p.parse_args()
    def load(path):
        with open(path, encoding='utf-8-sig') as f:
            return json.load(f)
    print(json.dumps(assess(load(args.host), load(args.guest),
                           load(args.previous) if args.previous else None, phase=args.phase,
                           baseline=load(args.baseline) if args.baseline else None), indent=2))


if __name__ == '__main__':
    main()
