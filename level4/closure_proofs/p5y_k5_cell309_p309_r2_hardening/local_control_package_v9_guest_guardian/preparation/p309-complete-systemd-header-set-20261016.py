"""Add the omitted upstream _sd-common.h to the private build header set.
No existing file is replaced; the first preparation and manifest stay historical.
"""
import hashlib, io, json, os, pathlib, re, subprocess, sys, tarfile
ROOT = pathlib.Path('/mnt/d/ReBaseGuard-309/records/p309-guest-v9-build-inputs-20261016-01')
BUILD = pathlib.Path('/home/suzhe/p309/builds/guest-v9-build-inputs-20261016-01')
def sha(b): return hashlib.sha256(b).hexdigest()
if os.getuid() != 1000 or sys.version_info[:3] != (3, 11, 15):
    raise SystemExit('ordinary user and private 3.11.15 required')
if sha(pathlib.Path(sys.executable).read_bytes()) != 'b21d680e5061c20ee39c75f0c6edf8db4220f327de45e52ab2040e15ca0cf194':
    raise SystemExit('interpreter binding mismatch')
deb = ROOT/'libsystemd-dev_255.4-1ubuntu8.18_amd64.deb'
if sha(deb.read_bytes()) != '37f42520029a429bd9931677c965eecab146d5e3bd34e2a54f4e70dffedaeccb':
    raise SystemExit('exact previously signed-index-verified package differs')
p = subprocess.run(['/usr/bin/dpkg-deb','--fsys-tarfile',str(deb)],
                   stdin=subprocess.DEVNULL, capture_output=True, timeout=30, check=False)
if p.returncode:
    raise SystemExit('read-only dpkg-deb failed: '+repr(p.stderr))
rows, added = [], []
with tarfile.open(fileobj=io.BytesIO(p.stdout), mode='r:') as tar:
    for member in tar:
        name = member.name.removeprefix('./')
        if not re.fullmatch(r'usr/include/systemd/[A-Za-z0-9_.-]+\.h',name):
            continue
        if not member.isfile() or member.size > 1048576:
            raise SystemExit('unexpected header type/size')
        data=tar.extractfile(member).read()
        dest=BUILD/'include/systemd'/pathlib.PurePosixPath(name).name
        if dest.exists():
            if not dest.is_file() or dest.is_symlink() or dest.read_bytes()!=data:
                raise SystemExit('existing header differs; no overwrite')
        else:
            with dest.open('xb') as f: f.write(data)
            added.append(dest.name)
        rows.append(dict(member=member.name, file=str(dest), bytes=len(data), sha256=sha(data)))
if len(rows)!=14 or added!=['_sd-common.h']:
    raise SystemExit('unexpected package header set/addition; retain files and refuse')
result=dict(scope='ADDITIVE_COMPLETE_PRIVATE_BUILD_HEADER_SET_NOT_SYSTEM_INSTALL',
            reason='Initial extraction filename filter omitted upstream underscore-prefixed _sd-common.h; original record retained',
            source_sha256=sha(pathlib.Path(__file__).read_bytes()), package_sha256=sha(deb.read_bytes()),
            header_count=len(rows), added=added, headers=rows, installed_packages=0,
            native_trials=0, admission='BLOCKED')
with (ROOT/'COMPLETE_HEADER_SET_ADDITION.json').open('x',encoding='utf-8') as f:
    json.dump(result,f,indent=2); f.write('\n')
print(json.dumps(result,indent=2))
