set -euo pipefail
export LC_ALL=C
record=/mnt/d/ReBaseGuard-309/records/p309-local-control-package-preparation-20261016-01
base=/home/suzhe/p309/builds/guest-runtime-stage-20261016
source=/mnt/d/ReBaseGuard-309/records/p309-runtime-hostdev-20261015-183413/Python-3.11.15.tar.xz
prefix=/opt/rebaseguard-p309/cpython-3.11.15
test "$(id -u)" = 1000
test "$(findmnt -no FSTYPE --target /home/suzhe/p309)" = ext4
test ! -e "$base"
printf '%s  %s\n' 272179ddd9a2e41a0fc8e42e33dfbdca0b3711aa5abf372d3f2d51543d09b625 "$source" | sha256sum -c -
mkdir "$base"
mkdir "$base/stage"
sha256sum /usr/bin/python3.12 > "$base/system-python-before.sha256"
dpkg-query -W -f='${Package}\t${Version}\t${Architecture}\n' > "$base/build-host-packages.tsv"
gcc --version > "$base/compiler.txt"
ldd --version > "$base/glibc.txt"
cp "$source" "$base/Python-3.11.15.tar.xz"
tar -xf "$base/Python-3.11.15.tar.xz" -C "$base"
cd "$base/Python-3.11.15"
printf '%s\n' "./configure --prefix=$prefix --with-ensurepip=no" 'make -j4' "make DESTDIR=$base/stage altinstall -j4" > "$base/build-commands.txt"
./configure --prefix="$prefix" --with-ensurepip=no > "$base/configure.log" 2>&1
make -j4 > "$base/make.log" 2>&1
make DESTDIR="$base/stage" altinstall -j4 > "$base/stage.log" 2>&1
sha256sum -c "$base/system-python-before.sha256" > "$base/system-python-after.txt"
test "$(readlink -f /usr/bin/python3)" = /usr/bin/python3.12
PYTHONHOME="$base/stage$prefix" "$base/stage$prefix/bin/python3.11" -s - <<'PY' > "$base/runtime-check.json"
import sys, json, platform, ssl, importlib, hashlib, pathlib, multiprocessing
assert sys.version_info[:3] == (3,11,15)
modules=['ssl','hashlib','sqlite3','bz2','lzma','ctypes','readline','zlib','uuid','dbm.gnu','dbm.ndbm','tkinter','pyexpat','multiprocessing','resource','fcntl','select','socket']
result={}
for name in modules:
    try: importlib.import_module(name); result[name]='OK'
    except Exception as exc: result[name]=repr(exc)
ctx=multiprocessing.get_context('fork')
p=ctx.Process(target=abs,args=(-1,));p.start();p.join(10)
if p.is_alive(): p.terminate();p.join();raise RuntimeError('own smoke process timed out')
assert p.exitcode == 0
print(json.dumps(dict(version=sys.version,executable=sys.executable,sha256=hashlib.sha256(pathlib.Path(sys.executable).read_bytes()).hexdigest(),glibc=platform.libc_ver(),openssl=ssl.OPENSSL_VERSION,modules=result,multiprocessing_fork_exit=p.exitcode,scope='UNPRIVILEGED_RELOCATABLE_STAGE_NOT_GUEST_INSTALL'),indent=2))
assert all(v=='OK' for v in result.values()),result
PY
ldd "$base/stage$prefix/bin/python3.11" > "$base/interpreter-ldd.txt"
tar -C "$base/stage" --sort=name --owner=0 --group=0 --numeric-owner -czf "$base/cpython-3.11.15-guest-stage.tar.gz" opt
sha256sum "$base/cpython-3.11.15-guest-stage.tar.gz" > "$base/archive.sha256"
mkdir "$record/runtime-stage"
cp "$base"/*.txt "$base"/*.json "$base"/*.tsv "$base"/*.sha256 "$base"/*.log "$record/runtime-stage/"
cp "$base/cpython-3.11.15-guest-stage.tar.gz" "$record/runtime-stage/"
printf '%s\n' 'STAGING_BUILD_COMPLETE_NO_SYSTEM_INSTALL'
