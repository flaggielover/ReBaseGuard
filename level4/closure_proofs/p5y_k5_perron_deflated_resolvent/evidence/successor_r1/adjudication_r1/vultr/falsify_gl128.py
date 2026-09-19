"""Adjudicator wrapper: run the frozen falsify_registry main() with the Gauss-Legendre order doubled (64 -> 128).
The frozen file is not modified; only its module globals are rebound in this process (fork start method)."""
import sys
import numpy as np
sys.path.insert(0, "/root/work/k5p-adjudication/level4/closure_proofs/p5y_k5_perron_deflated_resolvent/code")
import falsify_registry as FR
assert FR.GL_N == 64
FR.GL_N = 128
FR.GN, FR.GW = np.polynomial.legendre.leggauss(128)
sys.argv = ["falsify_registry.py"] + sys.argv[1:]
sys.exit(FR.main())
