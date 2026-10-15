"""Read-only WSL preparation report; never an admission or qualification gate.

python3 -B inspect_wsl.py --workspace <existing Linux path> [--windows-snapshot <json>]
Prints JSON only. No IMDS request, installation, service change or evaluator.
Windows evidence is supplied by collect_windows.ps1 and remains caller-supplied.
"""
import argparse
import datetime
import json
import math
import os
from pathlib import Path
import platform
import shutil
import subprocess

R2 = '501f48cb31fd3f80d5c6dd33f1eef6b8f01b2853'
RAM_FLOOR = 8_000_000_000  # r2's mem_available_gb uses decimal GB
DISK_FLOOR = 40_000_000_000


def read(path):
    try:
        return Path(path).read_text().strip()
    except (OSError, UnicodeError):
        return None


def query(argv):
    try:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=10,
                                stdin=subprocess.DEVNULL)
        return {'rc': result.returncode, 'stdout': result.stdout.strip()}
    except (OSError, subprocess.TimeoutExpired):
        return None


def collect(workspace):
    memory = {}
    for line in (read('/proc/meminfo') or '').splitlines():
        parts = line.split()
        if parts and parts[0] in ('MemTotal:', 'MemAvailable:') and len(parts) == 3 and parts[2] == 'kB':
            memory[parts[0][:-1]] = int(parts[1]) * 1024
    try:
        disk_free = shutil.disk_usage(workspace).free
    except OSError:
        disk_free = None
    try:
        cpus = len(os.sched_getaffinity(0))
    except (OSError, AttributeError):
        cpus = None
    return {'schema': 'P309_WSL_READONLY_FACTS/1',
            'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'system': platform.system(), 'kernel': platform.release(), 'arch': platform.machine(),
            'pid1': read('/proc/1/comm'), 'affinity_cpus': cpus,
            'available_memory_bytes': memory.get('MemAvailable'),
            'total_memory_bytes': memory.get('MemTotal'), 'guest_disk_free_bytes': disk_free,
            'workspace_filesystem': query(['findmnt', '-n', '-o', 'FSTYPE', '--target', workspace]),
            'systemd_state': query(['systemctl', 'is-system-running']),
            'systemd_run_available': bool(shutil.which('systemd-run')),
            'python': {'implementation': platform.python_implementation(), 'version': platform.python_version()},
            'glibc': platform.libc_ver(),
            'ntp': query(['timedatectl', 'show', '-p', 'NTPSynchronized', '--value']),
            'container_detection': query(['systemd-detect-virt', '--container']),
            'cpu_quota': 'NOT_ASSESSED_ACROSS_CGROUP_HIERARCHY',
            'windows_host_process_visibility': 'NOT_AVAILABLE_THROUGH_LINUX_PROC',
            'clock_continuity_across_windows_sleep': 'NOT_VALIDATED'}


def number(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def minimum(*values):
    return min(values) if all(number(v) for v in values) else None


def threshold(value, floor):
    return 'UNKNOWN' if not number(value) else ('PASS' if value >= floor else 'FAIL')


def assess(linux, windows):
    linux_ok = linux.get('schema') == 'P309_WSL_READONLY_FACTS/1'
    windows_ok = windows.get('schema') == 'P309_WINDOWS_READONLY_FACTS/1'
    if not linux_ok:
        linux = {}
    if not windows_ok:
        windows = {}
    # A virtual ext4 filesystem's capacity is not the physical backing drive's capacity.
    backing_known = (windows.get('vhdx_registered_and_present') is True
                     and isinstance(windows.get('backing_drive'), str)
                     and len(windows['backing_drive']) == 2
                     and windows['backing_drive'][0].isalpha() and windows['backing_drive'][1] == ':')
    storage = minimum(linux.get('guest_disk_free_bytes'),
                      windows.get('backing_free_bytes') if backing_known else None)
    memory = minimum(linux.get('available_memory_bytes'), windows.get('available_memory_bytes'))
    python = linux.get('python') if isinstance(linux.get('python'), dict) else {}
    wsl2 = (linux.get('system') == 'Linux' and 'microsoft' in str(linux.get('kernel', '')).lower()
            and type(windows.get('wsl_version')) is int and windows['wsl_version'] == 2)
    checks = {'wsl2_guest_and_registration': 'UNKNOWN' if not linux_ok or not windows_ok else
                  ('PASS' if wsl2 else 'FAIL'),
              'linux_cpu_affinity_at_least_4': threshold(linux.get('affinity_cpus'), 4),
              'available_ram_guest_and_host_at_least_8GB': threshold(memory, RAM_FLOOR),
              'guest_and_backing_storage_at_least_40GB': threshold(storage, DISK_FLOOR),
              'pid1_is_systemd': 'UNKNOWN' if linux.get('pid1') is None else
                  ('PASS' if linux['pid1'] == 'systemd' else 'FAIL'),
              'pinned_python_3_11_15': 'UNKNOWN' if not python else
                  ('PASS' if python.get('implementation') == 'CPython' and python.get('version') == '3.11.15'
                   else 'FAIL')}
    unresolved = ['WSL route amendment and independent review',
                  'AWS IMDS-dependent admission has no accepted WSL replacement',
                  'Windows host workload visibility and compute exclusivity',
                  'Windows sleep, restart, update and WSL shutdown continuity',
                  'Effective cgroup CPU quota and runtime resource accounting',
                  'Private interpreter path, binary hash and glibc binding',
                  'P309 account, isolation, launch privileges and unit controls',
                  'Full current audit, worker-tier drill and pre-freeze review']
    return {'schema': 'P309_WSL_PREPARATION_REPORT/1', 'scope': 'DEVELOPMENT_ONLY', 'r2_reference': R2,
            'input_scope': 'Caller-supplied snapshots; no host identity or freshness attestation',
            'input_schemas_valid': linux_ok and windows_ok,
            'resource_checks': checks, 'effective_available_memory_bytes': memory,
            'effective_free_storage_bytes': storage,
            'warnings': ['Resource values are instantaneous, not reserved capacity.',
                         'Logical CPU visibility does not establish dedicated physical cores.',
                         'The system-drive free-space figure is advisory and must also be monitored.'],
            'unresolved_requirements': unresolved,
            'formal_admission': 'BLOCKED', 'qualification_authorized': False, 'target_execution_authorized': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', required=True)
    parser.add_argument('--windows-snapshot')
    args = parser.parse_args()
    windows = {}
    if args.windows_snapshot:
        with open(args.windows_snapshot, encoding='utf-8-sig') as stream:
            windows = json.load(stream)
        if not isinstance(windows, dict):
            parser.error('Windows snapshot must be an object')
    linux = collect(args.workspace)
    print(json.dumps({'linux': linux, 'windows': windows, 'assessment': assess(linux, windows)}, indent=2))
    # Zero means collection completed. It never means admission passed.


if __name__ == '__main__':
    main()
