set -euo pipefail
export LC_ALL=C
record=/mnt/d/ReBaseGuard-309/records/p309-local-control-package-preparation-20261016-01
src=/mnt/d/ReBaseGuard-309/workspace/p309-local-vm-diagnostic-dev-20261016/level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/guest
test ! -e "$record/guest-adapter-tests-v2.txt"
cd "$src"
/home/suzhe/p309/runtime/cpython-3.11.15/bin/python3.11 -B -m unittest -v test_owned_instance > "$record/guest-adapter-tests-v2.txt" 2>&1
gcc -std=c11 -O2 -Wall -Wextra -Werror -D_FORTIFY_SOURCE=2 -fstack-protector-strong -fPIE -pie -Wl,-z,relro,-z,now stop_guard.c -o "$record/stop-guard-v2" > "$record/guest-guardian-build-v2.txt" 2>&1
sha256sum owned_instance.py test_owned_instance.py stop_guard.c "$record/stop-guard-v2" > "$record/guest-source-bindings-v2.sha256"
cat "$record/guest-adapter-tests-v2.txt"
