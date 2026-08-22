"""
Deterministic Bellman/Fredholm solver for the frozen ReBaseGuard CUSUM model.

FROZEN MODEL (Level 1-3, not modified here)
------------------------------------------
Cycle j: X_t ~ N(mu_j, 1); reference R_j; reference error e = R_j - mu_j.
Monitored innovation      z_t = X_t - R_j = Z_t - e,  Z_t ~ iid N(0,1)
   => under reference error e,  z_t ~ iid N(-e, 1).
Two-sided CUSUM, shared innovation, slack k, boundary h:
   S+_t = (S+_{t-1} + z_t - k)^+ ,   S-_t = (S-_{t-1} - z_t - k)^+ ,  S+_0 = S-_0 = 0
   tau  = inf{ t >= 1 : max(S+_t, S-_t) >= h }        (inclusive threshold, tested POST-update)
Reuse (m = 1, terminal block includes the alarm observation):
   R_{j+1} = X_tau   =>  e_{j+1} = X_tau - mu = z_tau + e.
Conditional-mean skeleton (full reuse):
   F_1(e) = e + E_e[z_tau].
Mixed reuse (frozen Level-3 theorem): F_rho(e) = rho * F_1(e).

LIVE-STATE ENCLOSURE (proved in this module's docstring, used to shrink the grid)
--------------------------------------------------------------------------------
Claim. For every live (pre-alarm) state, either min(S+,S-) = 0 with max(S+,S-) < h,
or both arms are strictly positive and S+ + S- < h - 2k.

Proof. From (0,0) one step gives S+ = (z-k)^+, S- = (-z-k)^+; since k > 0 at most one
is positive. So a maximal run of "both arms positive" starts at some time t0 whose
predecessor t0-1 had exactly one arm zero. Say S-_{t0-1} = 0 (the other case is the
arm-swap mirror). Both arms positive at t0 forces the (.)^+ to be inactive, so
   S+_{t0} = S+_{t0-1} + z - k ,  S-_{t0} = -z - k ,
hence S+_{t0} + S-_{t0} = S+_{t0-1} - 2k < h - 2k because the state at t0-1 was live.
Within the run both (.)^+ stay inactive, so each further step maps
(S+,S-) -> (S+ + z - k, S- - z - k) and the sum drops by exactly 2k; it therefore stays
< h - 2k. If instead one arm is zero, liveness of the other gives max < h.       QED

Corollary (forward invariance). If both new arms are positive the new sum is
old_sum - 2k < h - 2k; if one new arm is zero the other is < h or the step alarmed.
So the region above is closed under the continuation dynamics.

DISCRETIZATION
--------------
Per arm: an exact atom at 0 (created by the (.)^+ reset) plus N cells
(0,D], (D,2D], ..., ((N-1)D, h], D = h/N, collocated at cell midpoints.
Nystrom / Brook-Evans style midpoint collocation.  For each state the continuation
z-interval is split at EVERY z where either arm crosses a cell boundary, so the
destination cell is constant on each sub-interval and the Gaussian mass of each
sub-interval is evaluated in closed form (Phi differences).  No Monte Carlo anywhere.

QUANTITIES SOLVED  (K_e = killed/sub-Markov continuation operator at drift -e)
-----------------------------------------------------------------------------
  A_e   = 1 + K_e A_e                       A_e(0,0) = E_e[tau]           (ARL)
  G_e   = K_e G_e + rG_e                    G_e(0,0) = E_e[z_tau]
  a     = K_0 a + ra                        a(s)     = E_s[Z_tau]
  b     = K_0 b + Kz a + rb                 b(0,0)   = E_0[Z_tau T_tau] = Gamma
The (a,b) pair is the independent route to Gamma from the frozen baseline's
affine-in-T Bellman reduction; it must agree with dG/de at e = 0 up to sign,
since the frozen score identity is F_1'(0) = 1 - Gamma, i.e. G'(0) = -Gamma.
"""

import numpy as np
from scipy.stats import norm
import scipy.sparse as sp
import scipy.sparse.linalg as spla

SQRT2PI = np.sqrt(2.0 * np.pi)


def phi(x):
    return np.exp(-0.5 * np.asarray(x, dtype=float) ** 2) / SQRT2PI


def Phi(x):
    return norm.cdf(x)


class Grid:
    """State space for the two-sided CUSUM under the proved live-state enclosure."""

    def __init__(self, N, h=5.0, k=0.5):
        self.N, self.h, self.k = N, h, k
        self.D = D = h / N
        # arm coordinate: index 0 = atom at exactly 0; index i>=1 = cell ((i-1)D, iD]
        self.arm = np.concatenate([[0.0], (np.arange(1, N + 1) - 0.5) * D])
        idx = {}
        states = []
        lim = h - 2.0 * k + D  # enclosure + one cell of slack
        for i in range(N + 1):
            for j in range(N + 1):
                p, m = self.arm[i], self.arm[j]
                if i == 0 or j == 0 or (p + m) < lim:
                    idx[(i, j)] = len(states)
                    states.append((i, j))
        self.states = states
        self.idx = idx
        self.n = len(states)
        self.p = np.array([self.arm[i] for i, _ in states])
        self.m = np.array([self.arm[j] for _, j in states])

    def cell(self, x):
        """Destination arm index for an arm value x >= 0 (x < h assumed)."""
        if x <= 0.0:
            return 0
        i = int(np.ceil(x / self.D - 1e-12))
        return min(max(i, 1), self.N)


def build(grid, e):
    """Assemble K_e (dense), the reward vectors, and the z-weighted operator Kz (e=0 use).

    Returns K, rG, ra, rb, Kz  with K[s, s'] = P(step from s lands in cell s').
    """
    N, h, k, D = grid.N, grid.h, grid.k, grid.D
    n = grid.n
    rows, cols, kv, kzv = [], [], [], []
    rG = np.zeros(n)
    ra = np.zeros(n)
    rb = np.zeros(n)

    # candidate breakpoint offsets (arm value crosses a cell boundary)
    lev = np.arange(1, N) * D  # interior cell boundaries D, 2D, ..., (N-1)D

    for s, (i, j) in enumerate(grid.states):
        p, m = grid.arm[i], grid.arm[j]
        u = h + k - p          # z >= u  => plus-arm alarm
        v = h + k - m          # z <= -v => minus-arm alarm
        # ---- breakpoints inside the open continuation interval (-v, u) ----
        bpts = [k - p, m - k]                    # arm hits 0
        bpts += list(k - p + lev)                # plus arm crosses cell boundaries
        bpts += list(m - k - lev)                # minus arm crosses cell boundaries
        b = np.array(bpts)
        b = b[(b > -v) & (b < u)]
        edges = np.unique(np.concatenate([[-v], b, [u]]))
        lo, hi = edges[:-1], edges[1:]
        mid = 0.5 * (lo + hi)
        # exact Gaussian mass / first moment of z on each sub-interval, z ~ N(-e,1)
        Plo, Phi_ = Phi(lo + e), Phi(hi + e)
        mass = Phi_ - Plo
        # E[z 1{z in (lo,hi)}] with z = w - e, w ~ N(0,1):
        zmom = (phi(lo + e) - phi(hi + e)) - e * mass
        for a_, b_, mm, zz in zip(lo, hi, mass, zmom):
            if mm <= 0.0:
                continue
            zc = 0.5 * (a_ + b_)
            ip = grid.cell(p + zc - k)
            jm = grid.cell(m - zc - k)
            t = grid.idx.get((ip, jm))
            if t is None:
                raise RuntimeError(f"escaped enclosure: {(i,j)} -> {(ip,jm)}")
            rows.append(s); cols.append(t); kv.append(mm); kzv.append(zz)
        # ---- terminal rewards ----
        aa, bb = e - v, u + e   # w-thresholds for the two alarm tails
        # E[z 1{alarm}] with z = w - e
        rG[s] = (-phi(aa) - e * Phi(aa)) + (phi(bb) - e * (1.0 - Phi(bb)))
        ra[s] = phi(u) - phi(v)                                   # e = 0
        rb[s] = u * phi(u) + (1.0 - Phi(u)) + v * phi(v) + (1.0 - Phi(v))
    K = sp.coo_matrix((kv, (rows, cols)), shape=(n, n)).tocsr()
    Kz = sp.coo_matrix((kzv, (rows, cols)), shape=(n, n)).tocsr()
    return K, rG, ra, rb, Kz


def solve_at(grid, e, want_gamma=False):
    """Solve the killed systems at reference error e. Returns a dict of scalars."""
    K, rG, ra, rb, Kz = build(grid, e)
    n = grid.n
    M = (sp.eye(n, format="csc") - K).tocsc()
    lu = spla.splu(M)
    A = lu.solve(np.ones(n))
    G = lu.solve(rG)
    s0 = grid.idx[(0, 0)]
    out = {"e": e, "N": grid.N, "n": n, "ARL": A[s0], "Ez_tau": G[s0]}
    out["F1"] = e + G[s0]
    if want_gamma:
        a = lu.solve(ra)
        b = lu.solve(rb + Kz @ a)
        out["Gamma_bellman"] = b[s0]
    return out
