#!/usr/bin/env python3
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

from rebaseguard_novelty.generate import main

raise SystemExit(main())
