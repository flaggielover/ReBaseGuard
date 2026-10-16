"""Fetch a pinned, signed-index build input; extract headers privately, never install.

Run with the pre-verified private CPython 3.11.15 as suzhe, not root. No apt update,
dpkg install, maintainer script, service, endpoint, key, VM or native trial.
"""
import datetime
import hashlib
import io
import json
import os
import pathlib
import re
import subprocess
import sys
import tarfile
import urllib.parse
import urllib.request
from email.utils import parsedate_to_datetime

OLD = pathlib.Path('/mnt/d/ReBaseGuard-309/records/p309-local-control-package-preparation-20261016-01/guest-offline-debs')
OUT = pathlib.Path('/mnt/d/ReBaseGuard-309/records/p309-guest-v9-build-inputs-20261016-01')
BUILD = pathlib.Path('/home/suzhe/p309/builds/guest-v9-build-inputs-20261016-01')
VERSION = '255.4-1ubuntu8.18'
DEB = 'libsystemd-dev_255.4-1ubuntu8.18_amd64.deb'
URL = 'https://security.ubuntu.com/ubuntu/pool/main/s/systemd/' + DEB
PINS = {
    'ubuntu-archive-keyring.gpg': '80a36b0a6de2f69f49d2df75ef473ccde121e9e190b9ea01d20a4f63778d5c31',
    'security.ubuntu.com_ubuntu_dists_noble-security_InRelease': '97d485dd8c7d8d79091073d42b021169c4c6563893f4a680fde10bbc2a6a834a',
    'security.ubuntu.com_ubuntu_dists_noble-security_main_binary-amd64_Packages': 'ba62ef3ceddb89df11c724ba1ec9856091054a78616e3390255b35491bf3c255',
}
sha = lambda b: hashlib.sha256(b).hexdigest()

def fresh_json(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2)
        f.write('\n')

def command(argv, stem):
    p = subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, timeout=30, check=False)
    (OUT / (stem + '.stdout.bin')).write_bytes(p.stdout)
    (OUT / (stem + '.stderr.bin')).write_bytes(p.stderr)
    fresh_json(OUT / (stem + '.command.json'), dict(argv=argv, exit=p.returncode))
    if p.returncode:
        raise RuntimeError(stem + ' failed; preserve output, no package installation fallback')
    return p.stdout

def prepare():
    if os.getuid() != 1000 or sys.version_info[:3] != (3, 11, 15):
        raise RuntimeError('exact private CPython and ordinary build user required')
    if sha(pathlib.Path(sys.executable).read_bytes()) != 'b21d680e5061c20ee39c75f0c6edf8db4220f327de45e52ab2040e15ca0cf194':
        raise RuntimeError('interpreter changed')
    OUT.mkdir(exist_ok=False)
    BUILD.mkdir(exist_ok=False)
    fresh_json(OUT / 'STARTED.json', dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        source_sha256=sha(pathlib.Path(__file__).read_bytes()), url=URL,
        scope='PRIVATE_BUILD_HEADERS_ONLY_NO_PACKAGE_INSTALL', admission='BLOCKED'))
    # Copy already captured signed inputs from verified byte snapshots. Original files are untouched.
    for name, digest in PINS.items():
        data = (OLD / name).read_bytes()
        if sha(data) != digest:
            raise RuntimeError('historical signed input differs: ' + name)
        with (BUILD / name).open('xb') as f:
            f.write(data)
    release_name = 'security.ubuntu.com_ubuntu_dists_noble-security_InRelease'
    verified = BUILD / 'InRelease.verified'
    command(['/usr/bin/gpgv', '--status-fd', '1', '--keyring', str(BUILD/'ubuntu-archive-keyring.gpg'),
             '--output', str(verified), str(BUILD/release_name)], 'verify-release')
    release = verified.read_text(encoding='utf-8')
    until = re.search(r'^Valid-Until: (.+)$', release, re.M)
    date = re.search(r'^Date: (.+)$', release, re.M)
    now = datetime.datetime.now(datetime.timezone.utc)
    if not date or parsedate_to_datetime(date[1]) > now + datetime.timedelta(days=1):
        raise RuntimeError('missing or future Release date')
    if until and parsedate_to_datetime(until[1]) <= now:
        raise RuntimeError('expired Release')
    pins = {}
    section = release.split('\nSHA256:\n', 1)[1]
    for line in section.splitlines():
        if not line.startswith(' '):
            break
        h, n, p = line.split()
        if p in pins:
            raise RuntimeError('duplicate signed index path')
        pins[p] = (h, int(n))
    index_name = 'security.ubuntu.com_ubuntu_dists_noble-security_main_binary-amd64_Packages'
    data = (BUILD/index_name).read_bytes()
    if (sha(data), len(data)) != pins['main/binary-amd64/Packages']:
        raise RuntimeError('Packages not bound to signed Release')
    chosen = []
    for paragraph in data.decode('utf-8').split('\n\n'):
        fields = {}
        for line in paragraph.splitlines():
            if line and not line[0].isspace() and ': ' in line:
                k, v = line.split(': ', 1)
                if k in fields:
                    raise RuntimeError('duplicate package field')
                fields[k] = v
        if fields.get('Package') == 'libsystemd-dev' and fields.get('Version') == VERSION and fields.get('Architecture') == 'amd64':
            chosen.append(fields)
    if len(chosen) != 1:
        raise RuntimeError('exact package not unique')
    pkg = chosen[0]
    if (pkg['Filename'], pkg['Size'], pkg['SHA256'], pkg['Depends']) != (
        'pool/main/s/systemd/' + DEB, '1239004',
        '37f42520029a429bd9931677c965eecab146d5e3bd34e2a54f4e70dffedaeccb',
        'libsystemd0 (= ' + VERSION + ')'):
        raise RuntimeError('exact package metadata differs')
    installed = command(['/usr/bin/dpkg-query', '-W', '-f=${Version}\n', 'libsystemd0:amd64'], 'libsystemd-runtime-version')
    if installed != (VERSION + '\n').encode():
        raise RuntimeError('installed library version differs; no silent replacement')
    class OfficialRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            u = urllib.parse.urlsplit(newurl)
            if u.scheme != 'https' or u.hostname != 'security.ubuntu.com' or u.port not in (None, 443) or u.username or u.password:
                raise RuntimeError('unexpected package redirect')
            return super().redirect_request(req, fp, code, msg, headers, newurl)
    request = urllib.request.Request(URL, headers={'User-Agent': 'P309-private-build-input/1'})
    with urllib.request.build_opener(OfficialRedirect()).open(request, timeout=30) as response:
        content = response.read(int(pkg['Size']) + 1)
    with (OUT/DEB).open('xb') as f:
        f.write(content)
    if len(content) != int(pkg['Size']) or sha(content) != pkg['SHA256']:
        raise RuntimeError('package bytes differ; keep rejected download')
    archive = command(['/usr/bin/dpkg-deb', '--fsys-tarfile', str(OUT/DEB)], 'dpkg-deb-read-only')
    header_dir = BUILD / 'include' / 'systemd'
    header_dir.mkdir(parents=True, exist_ok=False)
    extracted = []
    with tarfile.open(fileobj=io.BytesIO(archive), mode='r:') as tar:
        for member in tar:
            name = member.name.removeprefix('./')
            if re.fullmatch(r'usr/include/systemd/[a-z0-9-]+\.h', name):
                if not member.isfile() or member.size > 1048576:
                    raise RuntimeError('unexpected header type/size')
                b = tar.extractfile(member).read()
                dest = header_dir / pathlib.PurePosixPath(name).name
                with dest.open('xb') as f:
                    f.write(b)
                extracted.append(dict(path=str(dest), bytes=len(b), sha256=sha(b)))
            elif name == 'usr/share/doc/libsystemd-dev/copyright':
                if not member.isfile():
                    raise RuntimeError('unexpected copyright member type')
                with (BUILD/'copyright').open('xb') as f:
                    f.write(tar.extractfile(member).read())
    if not (header_dir/'sd-bus.h').is_file() or not (header_dir/'sd-id128.h').is_file():
        raise RuntimeError('required headers absent')
    library = pathlib.Path('/usr/lib/x86_64-linux-gnu/libsystemd.so.0').resolve(strict=True)
    b = library.read_bytes()
    result = dict(scope='PRIVATE_BUILD_HEADERS_ONLY_NOT_INSTALLED', signed_input_pins=PINS,
        release_date=date[1], valid_until=until[1] if until else None,
        package=pkg, url=URL, download_sha256=sha(content), build_root=str(BUILD),
        headers=extracted, library=dict(path=str(library), bytes=len(b), sha256=sha(b), version=VERSION),
        recommended_build_include=str(BUILD/'include'), recommended_link=str(library),
        maintainer_scripts_run=0, package_installs=0, apt_updates=0, native_trials=0,
        admission='BLOCKED', I1_I7='OPEN')
    fresh_json(OUT/'VERIFIED_BUILD_INPUTS.json', result)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    try:
        prepare()
    except Exception as exc:
        if OUT.is_dir() and not (OUT/'FAILED.json').exists():
            fresh_json(OUT/'FAILED.json', dict(error=repr(exc), admission='BLOCKED',
                cleanup='preserve all new build input files; no install or retry fallback'))
        raise
