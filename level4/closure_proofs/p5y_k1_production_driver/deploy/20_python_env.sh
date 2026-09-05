#!/usr/bin/env bash
# Pinned Python environment. Versions must match the qualification record.
set -euo pipefail
: "${WORKDIR:=$HOME/rebaseguard}"
cd "$WORKDIR"
python3 -m venv level4/.venv
./level4/.venv/bin/pip install --upgrade pip
./level4/.venv/bin/pip install "python-flint==0.9.0" "numpy>=2,<3"
./level4/.venv/bin/python -c "import flint,numpy;print('flint',flint.__version__,'numpy',numpy.__version__)"
