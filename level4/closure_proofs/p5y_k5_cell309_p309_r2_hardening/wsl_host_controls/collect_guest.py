"""Read-only guest facts for the development proposal. JSON on stdout only."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys


def read(path):
    try: return Path(path).read_text().strip()
    except (OSError,UnicodeError): return None


def hashed(path):
    value=read(path)
    return hashlib.sha256(value.encode()).hexdigest() if value else None


def collect():
    affinity=len(os.sched_getaffinity(0))
    memory={}
    for line in (read('/proc/meminfo') or '').splitlines():
        fields=line.split()
        if fields[0] in ('MemTotal:','MemAvailable:') and fields[-1]=='kB':
            memory[fields[0][:-1]]=int(fields[1])*1024
    quota=None;details=[]
    try:
        relative=next(x.split(':',2)[2] for x in read('/proc/self/cgroup').splitlines() if x.startswith('0::'))
        root=Path('/sys/fs/cgroup').resolve()
        path=(root/relative.lstrip('/')).resolve()
        path.relative_to(root)
        limits=[float(affinity)]
        while True:
            f=path/'cpu.max'
            if f.exists():
                raw=f.read_text().strip();q,period=raw.split()
                if int(period)<=0: raise ValueError('invalid quota period')
                if q!='max':
                    if int(q)<0:raise ValueError('invalid quota')
                    limits.append(int(q)/int(period))
                details.append({'path':str(f),'value':raw})
            if path==root:break
            path=path.parent
        # Empty observations are not evidence that all quotas are unlimited.
        if details:quota=min(limits)
    except (OSError,ValueError,TypeError,StopIteration,AttributeError):
        quota=None
    state=subprocess.run(['systemctl','is-system-running'],capture_output=True,text=True,timeout=10)
    exe=Path(sys.executable).resolve()
    return {'schema':'P309_WSL_CONTROL_FACTS/1','scope':'DEVELOPMENT_ONLY',
        'utc':dt.datetime.now(dt.timezone.utc).isoformat(),'pid1':read('/proc/1/comm'),
        'systemd_state':state.stdout.strip() if state.returncode==0 else None,
        'affinity_cpus':affinity,'effective_cpu_quota':quota,'cgroup_quota_observations':details,
        'available_memory_bytes':memory.get('MemAvailable'),'total_memory_bytes':memory.get('MemTotal'),
        'guest_disk_free_bytes':shutil.disk_usage(Path.home()).free,
        'boot_id_sha256':hashed('/proc/sys/kernel/random/boot_id'),'machine_id_sha256':hashed('/etc/machine-id'),
        'python_version':platform.python_version(),'python_implementation':platform.python_implementation(),
        'private_runtime':str(exe)=='/home/suzhe/p309/runtime/cpython-3.11.15/bin/python3.11',
        'interpreter_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),
        'glibc':os.confstr('CS_GNU_LIBC_VERSION'),
        'limitations':['Current process cgroup only; future launch unit needs separate accounting.']}


if __name__=='__main__': print(json.dumps(collect(),indent=2))
