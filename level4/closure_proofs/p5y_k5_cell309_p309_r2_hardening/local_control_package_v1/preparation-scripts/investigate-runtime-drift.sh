set -eu
export LC_ALL=C
base=/home/suzhe/p309/builds/guest-runtime-stage-20261016
record=/mnt/d/ReBaseGuard-309/records/p309-local-control-package-preparation-20261016-01/runtime-drift
mkdir "$record"
cp "$base/system-python-before.sha256" "$base/system-python-after.txt" "$base/build-commands.txt" "$base/build-host-packages.tsv" "$record/"
cp /var/log/dpkg.log "$record/dpkg.log"
cp /var/log/apt/history.log "$record/apt-history.log"
sha256sum /usr/bin/python3.12 > "$record/system-python-current.sha256"
stat /usr/bin/python3.12 "$base/system-python-before.sha256" "$base/configure.log" "$base/make.log" "$base/stage.log" > "$record/file-times.txt"
dpkg-query -W -f='${Package}\t${Version}\t${Architecture}\n' > "$record/packages-after.tsv"
dpkg --verify python3.12-minimal > "$record/dpkg-python-verify.txt"
cat "$record/system-python-before.sha256" "$record/system-python-current.sha256"
sed -n '/Start-Date: 2026-10-16  08:57:2/,/End-Date:/p' "$record/apt-history.log"
grep 'python3.12' "$record/dpkg.log" | tail -20
cat "$record/file-times.txt"
