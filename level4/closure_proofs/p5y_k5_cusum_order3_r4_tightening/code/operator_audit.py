"""R4-B architecture audit for C_o0: FLOAT diagnostics on the frozen Chebyshev grid (NOT evidence of any bound).

Supports the comparison table in R4_DESIGN.md section B. Every number here is a float estimate on a degree-12
collocation of the continuous operator; none is promoted to a certificate.
  full K_0 (R3 matrices), odd block K_o (R4 reflected positive kernel on H), and the rank-one Perron picture.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

NS = Path(__file__).resolve().parents[1]
CP = NS.parents[0]
for _p in (str(NS / "code"), str(CP / "p5y_k5_cusum_order3_r3_infrastructure/code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def audit() -> dict:
    import odd_block_certificate as OB
    import resolvent_certificate as R3C
    K, Khat, n = R3C.kernel_matrices()
    M, _ = OB.odd_matrix()
    N = n * n
    I = np.eye(N)
    one = np.ones(N)
    ev = np.linalg.eigvals(K)
    perron = float(np.max(np.abs(ev)))
    evo = np.linalg.eigvals(M)
    rho_o = float(np.max(np.abs(evo)))
    full_res = np.linalg.solve(I - K, one)
    odd_res = np.linalg.solve(I - M, one)
    coupling = np.linalg.solve(I - Khat, one)
    # Neumann terms needed for ||K_o^k||_inf <= 1/2 (preconditioned-Neumann / power-series architectures)
    P, k = I.copy(), 0
    while np.abs(P).sum(axis=1).max() > 0.5 and k < 2000:
        P, k = P @ M, k + 1
    A = np.linalg.inv(I - M)
    defect = float(np.abs(I - A @ (I - M)).sum(axis=1).max())
    cond_odd = float(np.linalg.cond(I - M, np.inf))
    cond_full = float(np.linalg.cond(I - K, np.inf))
    return {
        "non_evidence": True, "grid": f"{n}x{n} Chebyshev (degree {n - 1}), float64",
        "full_space": {"perron_eigenvalue": perron, "sup_resolvent_of_one": float(full_res.max()),
                       "condition_inf": cond_full},
        "coupling_R3": {"sup_E_tau_wedge_T0": float(coupling.max())},
        "odd_block": {"spectral_radius": rho_o, "row_sum_norm": float(np.abs(M).sum(axis=1).max()),
                      "sup_resolvent_of_one": float(odd_res.max()), "condition_inf": cond_odd,
                      "neumann_terms_for_half": k, "matrix_defect_of_float_inverse": defect},
        "notes": {
            "direct_odd_solve": "float odd-block solve = sup_resolvent_of_one; a certificate needs a sup-norm "
                                "discretisation error bound for the continuous operator, which the supersolution avoids",
            "interval_inverse_krawczyk_newton": "certify the MATRIX inverse only; the operator-to-matrix error in the sup "
                                                 "norm is the missing load-bearing term",
            "preconditioned_neumann": "||I - A(I - K_o)|| < 1 for the continuous operator needs the same projection error; "
                                      "matrix_defect_of_float_inverse is the (non-load-bearing) matrix part",
            "schur_parity_block": "exact: sigma is a permutation symmetry, the odd block decouples at e = 0 (R4 reduction)",
            "perron_separation": "Perron mode is even (R2); irrelevant for the odd block, dominant for C_e0",
            "spectral_gap": "spectral radius < 1 does not bound the sup-norm resolvent of a non-normal operator",
            "componentwise": "for a POSITIVE operator the sup-norm resolvent norm equals sup of the resolvent of 1; the "
                             "reflected odd kernel is positive, so the componentwise supersolution is exact in the limit"}}


if __name__ == "__main__":
    import json
    print(json.dumps(audit(), indent=1))
