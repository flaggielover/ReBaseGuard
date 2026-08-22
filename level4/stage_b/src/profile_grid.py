"""Build adaptive grids from a non-rigorous float profile of G.

Grid choice is a *presentation* decision, not a soundness one: the monotone
interval iteration is valid on any partition.  Using a float solve to place
cells therefore does not import its error into the certificate.  The profile
and the resulting edges are persisted so the choice can be audited and rerun.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "level_4_theory_numerics"))


def axis_profiles(e: float, n_solver: int = 200):
    """(p, G(p,0)), (m, G(0,m)) from the Stage A Claude Science Bellman solver."""
    import scipy.sparse as sp
    import scipy.sparse.linalg as spla
    from bellman_solver import Grid, build

    g = Grid(n_solver)
    K, rG, _, _, _ = build(g, e)
    n = g.n
    G = spla.splu((sp.eye(n, format="csc") - K).tocsc()).solve(rG)
    ip = np.array([g.idx[(i, 0)] for i in range(g.N + 1)])
    im = np.array([g.idx[(0, j)] for j in range(g.N + 1)])
    x = np.concatenate([[0.0], (np.arange(1, g.N + 1) - 0.5) * g.D])
    return (x, G[ip]), (x, G[im]), float(G[g.idx[(0, 0)]])
