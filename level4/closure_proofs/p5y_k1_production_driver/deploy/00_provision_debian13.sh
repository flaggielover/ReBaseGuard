#!/usr/bin/env bash
# K1 successor production -- fresh Debian 13 provisioning. No secrets here.
set -euo pipefail
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
  git ca-certificates build-essential pkg-config \
  python3 python3-venv python3-dev \
  libflint-dev libarb-dev libgmp-dev libmpfr-dev \
  tmux jq
python3 -c 'import sys; print("system python", sys.version)'
