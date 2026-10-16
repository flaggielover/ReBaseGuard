#!/bin/sh
# Ordinary-user build prerequisite facts only. No install, sudo, service or native trial.
set -eu
P309_PRIVATE_PY=/home/suzhe/p309/runtime/cpython-3.11.15/bin/python3.11
P309_EXPECTED_PY=b21d680e5061c20ee39c75f0c6edf8db4220f327de45e52ab2040e15ca0cf194
P309_ACTUAL_PY=$(/usr/bin/sha256sum "$P309_PRIVATE_PY")
P309_ACTUAL_PY=${P309_ACTUAL_PY%% *}
if [ "$P309_ACTUAL_PY" != "$P309_EXPECTED_PY" ]; then
    printf '%s\n' 'PRIVATE_INTERPRETER_BINDING_MISMATCH_NO_SUBSTITUTION' >&2
    exit 71
fi
exec "$P309_PRIVATE_PY" -I -B - <<'PY'
import datetime, hashlib, json, os, pathlib, platform, ssl, subprocess, sys

def run(argv):
    try:
        p = subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=20, check=False)
        return dict(argv=argv, exit=p.returncode,
                    stdout=p.stdout.decode('utf-8', 'backslashreplace'),
                    stderr=p.stderr.decode('utf-8', 'backslashreplace'))
    except (OSError, subprocess.TimeoutExpired) as exc:
        return dict(argv=argv, error=repr(exc))

paths = [sys.executable, '/usr/bin/gcc', '/usr/bin/pkg-config',
         '/usr/include/systemd/sd-bus.h', '/usr/include/openssl/evp.h',
         '/usr/include/openssl/rsa.h']
files = []
for name in paths:
    p = pathlib.Path(name)
    try:
        data = p.read_bytes()
        files.append(dict(path=name, resolved=str(p.resolve()), bytes=len(data),
                          sha256=hashlib.sha256(data).hexdigest()))
    except OSError as exc:
        files.append(dict(path=name, error=repr(exc)))
out = dict(scope='ORDINARY_UBUNTU_READ_ONLY_BUILD_PREREQUISITES',
           utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), uid=os.getuid(),
           private_python=sys.version, interpreter=sys.executable,
           glibc=platform.libc_ver(), openssl=ssl.OPENSSL_VERSION, files=files,
           commands=[run(x) for x in [
               ['/usr/bin/gcc', '--version'],
               ['/usr/bin/pkg-config', '--modversion', 'libsystemd', 'openssl'],
               ['/usr/bin/pkg-config', '--cflags', '--libs', 'libsystemd', 'openssl'],
               ['/usr/bin/dpkg-query', '-W', '-f=${binary:Package}\t${Version}\t${Status}\n',
                'libsystemd-dev', 'libssl-dev', 'libssl3t64', 'systemd']]],
           software_installed=False, services_started=False, native_trial=False,
           tests_repeated=False, I1_I7='OPEN', admission='BLOCKED')
if sys.version_info[:3] != (3, 11, 15) or os.getuid() == 0:
    raise SystemExit('Exact private CPython 3.11.15 and non-root required')
print(json.dumps(out, indent=2))
PY
