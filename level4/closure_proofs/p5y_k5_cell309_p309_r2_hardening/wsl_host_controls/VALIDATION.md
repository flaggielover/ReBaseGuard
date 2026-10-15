# Development validation, 2026-10-15

This is a local preparation result, not an accepted route or qualification proof.
Base commit: `657ec3da602b396835b17b93d9235d7ed18e2cb7`.

* CPython 3.11.15: 18 Python synthetic tests passed.
* PowerShell sampler: 8 synthetic checks passed, including PID reuse and counter
  regression. Tests extract pure function definitions and do not start sampling.
* 57 standard-library imports (explicit requirements plus static r2 import
  inventory) passed, as did compression/hash/SSL/SQLite/ctypes checks.
* Multiprocessing fork, spawn, forkserver, locks and shared memory passed.
* Original r2 source hashes and threshold constants remain unchanged.
* Live 60-second process sample, guest facts and offline diagnostic completed.
  Observed resources passed the preparation floors. Visibility, start CPU
  quietness, pending reboot, power policy and update/window coverage did not pass.
* All results, including synthetic all-green input, retain formal admission
  BLOCKED and execution/qualification authorization false.

Evidence directory on this preparation host:
`D:\ReBaseGuard-309\records\p309-runtime-hostdev-20261015-183413`.
The runtime verifier and diagnostic JSON, dependency plans/install logs,
configure/make/altinstall logs, source digest evidence and preservation manifest
are retained there. Earlier migration/readiness records were not overwritten.
An early diagnostic attempt ran before the Windows sample file was ready and
failed with FileNotFoundError; its log is retained. The subsequent completed
sample and diagnostic passed freshness checks. A supplemental Python 3.12 test
run preceded the authoritative 3.11.15 run and is not a version substitute.

## Private runtime provenance

Official source: https://www.python.org/ftp/python/3.11.15/Python-3.11.15.tar.xz

Published digest source: https://www.python.org/downloads/release/python-31115/

SHA-256: `272179ddd9a2e41a0fc8e42e33dfbdca0b3711aa5abf372d3f2d51543d09b625`.
Archive hash matched the official HTTPS release page. Signature verification was
not performed; no claim of verified GPG or Sigstore provenance is made.

Build source tree on ext4:
`/home/suzhe/p309/builds/cpython-3.11.15-20261015/Python-3.11.15`.

Commands (ordinary Ubuntu user):

```sh
./configure --prefix=/home/suzhe/p309/runtime/cpython-3.11.15 --with-ensurepip=no
make -j4
make altinstall -j4
```

Interpreter: `/home/suzhe/p309/runtime/cpython-3.11.15/bin/python3.11`.
SHA-256: `b21d680e5061c20ee39c75f0c6edf8db4220f327de45e52ab2040e15ca0cf194`.
glibc: 2.39; Ubuntu package 2.39-0ubuntu8.9. No PGO or pip bootstrap was run.
System Python remains `/usr/bin/python3.12`, version 3.12.3, SHA-256
`e1efa562c2cc2e35521a5c9c9b9939921001ff8ca9708a13ef15ace68cc2ccd7`.
No system Python symlink or global PATH was changed.

Initially missing build packages: build-essential, gcc, g++, make, pkg-config,
libc6-dev, zlib1g-dev, libbz2-dev, liblzma-dev, libssl-dev, libffi-dev,
libsqlite3-dev, libreadline-dev, libncurses-dev, libgdbm-dev, libgdbm-compat-dev,
uuid-dev, tk-dev, libexpat1-dev. The stale-index first install failed with 404s;
after an Ubuntu apt index refresh, the reviewed install added 85 packages and
upgraded 32 dependencies, including libc6 from 2.39-0ubuntu8.7 to 2.39-0ubuntu8.9.
No Python package was replaced. Exact package versions and transactions are in
build-dependencies-final.tsv and dependency-install-current.stdout.txt. No required
build dependency or checked standard-library extension remains missing.

## Outstanding acceptance work

Authenticated host/guest bridge, protected and short-lived process accounting,
workload attribution, durable baseline and sequence protection, continuous monitor
and explicit review of AWS/container replacements remain outstanding. This
prototype does not implement those mechanisms. Power interpretation and unknown
process handling are proposed semantics as documented in DESIGN.md. Existing
Linux isolation/load/NTP/unit controls and exactly-once mechanisms still apply.
No launch, freeze, grant, drill, qualification or target evaluation was run.
