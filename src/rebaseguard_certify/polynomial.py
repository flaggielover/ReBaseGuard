"""Small Arb polynomial algebra used by the continuum residual certificate."""

from __future__ import annotations

from collections.abc import Mapping

from flint import arb


BiPoly = dict[tuple[int, int], arb]
TriPoly = dict[tuple[int, int, int], arb]


def bi_constant(value: arb) -> BiPoly:
    return {(0, 0): value}


def bi_add(left: Mapping[tuple[int, int], arb], right: Mapping[tuple[int, int], arb]) -> BiPoly:
    result = {key: arb(value) for key, value in left.items()}
    for key, value in right.items():
        result[key] = result.get(key, arb(0)) + value
    return result


def bi_scale(poly: Mapping[tuple[int, int], arb], scalar: arb) -> BiPoly:
    return {key: value * scalar for key, value in poly.items()}


def bi_mul(left: Mapping[tuple[int, int], arb], right: Mapping[tuple[int, int], arb]) -> BiPoly:
    result: BiPoly = {}
    for (i, j), a in left.items():
        for (k, ell), b in right.items():
            key = (i + k, j + ell)
            result[key] = result.get(key, arb(0)) + a * b
    return result


def bi_pow(poly: Mapping[tuple[int, int], arb], exponent: int) -> BiPoly:
    if exponent < 0:
        raise ValueError("negative polynomial exponent")
    result = bi_constant(arb(1))
    base = dict(poly)
    power = exponent
    while power:
        if power & 1:
            result = bi_mul(result, base)
        power >>= 1
        if power:
            base = bi_mul(base, base)
    return result


def bi_shift_monomial(poly: Mapping[tuple[int, int], arb], di: int, dj: int) -> BiPoly:
    return {(i + di, j + dj): value for (i, j), value in poly.items()}


def bi_eval(poly: Mapping[tuple[int, int], arb], p: arb, m: arb) -> arb:
    if not poly:
        return arb(0)
    max_i = max(i for i, _ in poly)
    max_j = max(j for _, j in poly)
    rows: list[arb] = []
    for i in range(max_i + 1):
        value = arb(0)
        for j in range(max_j, -1, -1):
            value = value * m + poly.get((i, j), arb(0))
        rows.append(value)
    result = arb(0)
    for i in range(max_i, -1, -1):
        result = result * p + rows[i]
    return result


def tri_add(left: Mapping[tuple[int, int, int], arb], right: Mapping[tuple[int, int, int], arb]) -> TriPoly:
    result = {key: arb(value) for key, value in left.items()}
    for key, value in right.items():
        result[key] = result.get(key, arb(0)) + value
    return result


def tri_mul(left: Mapping[tuple[int, int, int], arb], right: Mapping[tuple[int, int, int], arb]) -> TriPoly:
    result: TriPoly = {}
    for (i, j, r), a in left.items():
        for (k, ell, s), b in right.items():
            key = (i + k, j + ell, r + s)
            result[key] = result.get(key, arb(0)) + a * b
    return result


def tri_pow(poly: Mapping[tuple[int, int, int], arb], exponent: int) -> TriPoly:
    if exponent < 0:
        raise ValueError("negative polynomial exponent")
    result: TriPoly = {(0, 0, 0): arb(1)}
    base = dict(poly)
    power = exponent
    while power:
        if power & 1:
            result = tri_mul(result, base)
        power >>= 1
        if power:
            base = tri_mul(base, base)
    return result


def chebyshev_payload_to_power(payload: Mapping[str, object]) -> BiPoly:
    degree = int(payload["degree"])
    scale = arb(2) ** int(payload["scale_bits"])
    h = arb(int(payload["h_num"])) / arb(int(payload["h_den"]))
    numerators = payload["numerators"]
    x: BiPoly = {(0, 0): -arb(1), (1, 0): arb(2) / h}
    y: BiPoly = {(0, 0): -arb(1), (0, 1): arb(2) / h}

    def chebyshev_basis(variable: BiPoly) -> list[BiPoly]:
        basis = [bi_constant(arb(1))]
        if degree == 0:
            return basis
        basis.append(variable)
        for _ in range(2, degree + 1):
            basis.append(
                bi_add(bi_scale(bi_mul(variable, basis[-1]), arb(2)), bi_scale(basis[-2], -arb(1)))
            )
        return basis

    basis_x = chebyshev_basis(x)
    basis_y = chebyshev_basis(y)
    result: BiPoly = {}
    for i in range(degree + 1):
        for j in range(degree + 1):
            coefficient = arb(int(numerators[i][j])) / scale
            result = bi_add(result, bi_scale(bi_mul(basis_x[i], basis_y[j]), coefficient))
    return result
