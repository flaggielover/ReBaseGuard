"""Point metadata only. No tests, samples, writes, services or privilege changes."""
import datetime, hashlib, json, os, pathlib, platform, subprocess, sys
def command(argv):
    try:
        p = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=10)
        return dict(argv=argv, exit=p.returncode, stdout=p.stdout, stderr=p.stderr)
    except (OSError, subprocess.TimeoutExpired) as e:
        return dict(argv=argv, status='UNKNOWN', error_type=type(e).__name__)
out = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), scope='READ_ONLY_METADATA',
           interpreter=dict(path=sys.executable, implementation=platform.python_implementation(),
                            version=platform.python_version(), sha256=hashlib.sha256(pathlib.Path(sys.executable).read_bytes()).hexdigest(),
                            glibc=platform.libc_ver()),
           clock=command(['timedatectl','show','-p','NTPSynchronized','-p','NTP','-p','CanNTP','-p','Timezone','-p','LocalRTC']),
           disk=command(['df','-B1','--output=fstype,size,used,avail,target','/home/suzhe/p309']),
           updates=command(['systemctl','show','unattended-upgrades.service','apt-daily.timer','apt-daily-upgrade.timer','-p','Id','-p','ActiveState','-p','UnitFileState']),
           reboot_required=pathlib.Path('/run/reboot-required').exists(),
           network_imds='NOT_PROBED; container rejection already established; not formal 8a audit',
           tests_run=0, host_safety_samples=0)
print(json.dumps(out,indent=2))
