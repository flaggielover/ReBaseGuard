"""A small dense LP solver (float, stdlib only) for the family-slack study.

Problem:  minimise c.x  subject to  G x >= g  (rows),  x in R^n free.
Method:   simplex on the dual   maximise g.y  s.t.  G^T y = c,  y >= 0,  two phases with artificial
          variables, Dantzig pricing with a Bland fallback against stalling.  The primal x is read off
          as the simplex multipliers of the equality rows (the reduced costs of the artificial
          columns), then CHECKED: primal feasibility min(Gx - g) and the duality gap c.x - g.y are
          returned, so a wrong answer is visible rather than silent.
"""
from __future__ import annotations


class LPError(RuntimeError):
    pass


def solve(G: list, g: list, c: list, *, tol: float = 1e-10, maxit: int = 200000,
          perturb: float = 1e-9, seed: int = 20260928) -> dict:
    """``perturb``: the dual right-hand side c is perturbed by perturb * max|c| * U(0.5, 1) per entry
    (fixed seed) to remove the massive degeneracy of objectives such as w(a) = x_0 (one nonzero entry);
    the returned x is primal FEASIBLE, and its objective is reported with the ORIGINAL c, so the value
    is a valid (at worst very slightly suboptimal) family value on the conservative side."""
    import random
    M, n = len(G), len(c)
    c_orig = list(c)
    if perturb:
        rng = random.Random(seed)
        sc = max(abs(x) for x in c) or 1.0
        c = [x + perturb * sc * (0.5 + 0.5 * rng.random()) for x in c]
    # dual equality rows: sum_i G[i][k] y_i = c[k], k < n; flip rows with c[k] < 0
    sign = [(-1.0 if c[k] < 0 else 1.0) for k in range(n)]
    ncol = M + n
    T = []
    for k in range(n):
        row = [sign[k] * G[i][k] for i in range(M)] + [0.0] * n + [sign[k] * c[k]]
        row[M + k] = 1.0
        T.append(row)
    basis = [M + k for k in range(n)]

    def pivot(r, col):
        pr = T[r]
        pv = pr[col]
        inv = 1.0 / pv
        for j in range(ncol + 1):
            pr[j] *= inv
        for i in range(len(T)):
            if i != r:
                f = T[i][col]
                if f != 0.0:
                    ri = T[i]
                    for j in range(ncol + 1):
                        ri[j] -= f * pr[j]
        basis[r] = col

    def run(cost, allowed):
        # cost: maximise cost.y ; objective row obj[j] = reduced cost = cost_j - cB B^-1 a_j
        it, stall, best, bland = 0, 0, None, False
        while True:
            it += 1
            if it > maxit:
                raise LPError("iteration limit")
            cb = [cost[b] for b in basis]
            obj = []
            for j in range(ncol):
                if not allowed(j):
                    obj.append(-1.0)
                    continue
                s = cost[j]
                for i in range(n):
                    s -= cb[i] * T[i][j]
                obj.append(s)
            val = sum(cb[i] * T[i][ncol] for i in range(n))
            if best is None or val > best + 1e-14:
                best, stall = val, 0
            else:
                stall += 1
            if stall > 50:
                bland = True     # permanent for this phase: Bland's rule guarantees termination
            if bland:        # Bland: smallest improving index
                col = next((j for j in range(ncol) if allowed(j) and obj[j] > tol), None)
            else:
                col, bv = None, tol
                for j in range(ncol):
                    if obj[j] > bv:
                        col, bv = j, obj[j]
            if col is None:
                return val, obj, it
            r, br = None, None
            for i in range(n):
                a = T[i][col]
                if a > tol:
                    q = T[i][ncol] / a
                    if br is None or q < br - 1e-12 * (1 + abs(br)) or \
                            (abs(q - br) <= 1e-12 * (1 + abs(br)) and basis[i] < basis[r]):
                        r, br = i, q
            if r is None:
                raise LPError("dual unbounded (primal infeasible)")
            pivot(r, col)

    # phase I: maximise -sum(artificials)
    cost1 = [0.0] * M + [-1.0] * n
    v1, _, it1 = run(cost1, lambda j: True)
    if v1 < -1e-8:
        raise LPError(f"dual infeasible (primal unbounded) phase-I value {v1}")
    # drive remaining artificial basics out where possible
    for r in range(n):
        if basis[r] >= M:
            col = next((j for j in range(M) if abs(T[r][j]) > 1e-9), None)
            if col is not None:
                pivot(r, col)
    # phase II: maximise g.y over the original columns; artificials kept (cost 0) but not entering
    cost2 = list(g) + [0.0] * n
    v2, obj, it2 = run(cost2, lambda j: j < M)
    # multipliers pi_k = -(reduced cost of artificial k) * sign_k  -> primal x
    x = [-(obj_art) * sign[k] for k, obj_art in enumerate(_art_reduced(T, basis, cost2, M, n))]
    feas = min(sum(G[i][k] * x[k] for k in range(n)) - g[i] for i in range(M))
    cx_pert = sum(c[k] * x[k] for k in range(n))
    cx = sum(c_orig[k] * x[k] for k in range(n))
    return {"x": x, "primal_obj": cx, "dual_obj": v2, "gap": cx_pert - v2, "min_slack": feas,
            "iterations": it1 + it2, "perturb": perturb}


def _art_reduced(T, basis, cost, M, n):
    cb = [cost[b] for b in basis]
    out = []
    for k in range(n):
        j = M + k
        s = cost[j]
        for i in range(n):
            s -= cb[i] * T[i][j]
        out.append(s)
    return out


def _selftest():
    # min x0 + x1 s.t. x0 >= 1, x1 >= 2, x0 + x1 >= 4  -> 4
    r = solve([[1, 0], [0, 1], [1, 1]], [1, 2, 4], [1, 1])
    assert abs(r["primal_obj"] - 4) < 1e-9 and r["min_slack"] > -1e-9, r
    # min -x0 s.t. -x0 >= -3, x0 - x1 >= 0, x1 >= 1   (x0 <= 3) -> -3
    r = solve([[-1, 0], [1, -1], [0, 1]], [-3, 0, 1], [-1, 0])
    assert abs(r["primal_obj"] + 3) < 1e-9 and r["min_slack"] > -1e-9, r
    print("mech_lp selftest PASS")


if __name__ == "__main__":
    _selftest()
