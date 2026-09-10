import os
import sys
from pathlib import Path

# the frozen one-thread numerical contract must hold BEFORE numpy is imported
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"
_CODE = Path(__file__).resolve().parents[1] / "code"
if str(_CODE) not in sys.path:
    sys.path.insert(0, str(_CODE))
