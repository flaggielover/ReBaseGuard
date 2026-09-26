# Frozen scope — P5Y-K1R4

## Inherited unchanged
Target `sup |R_D,m(e)| < 2`; m ∈ {1,2,3,5}; 256-bit precision; `B_cover` cap 1/20; SR radius cap
1/25; shared cap 150 NEW CPU-h (0.0 consumed); CUSUM bridge `(11/2, 49750555/8388608]` with its two
frozen cells; far-field endpoints `49750555/8388608` (CUSUM) and `1883835/262144` (SR); P5X-T3
unmodified; B1 inherited PASS.

## Amended (prospectively, in K1R4 only)
SR bridge lower endpoint: `3803026123175981/562949953421312` → `q_SR = 33777657/5000000`.
`SCOPE_CHANGE_CLASS = DOMAIN_ENLARGEMENT_TO_REMOVE_CERTIFICATE_GAP` — the domain only grows; no
threshold, precision, m value or previously required point changes.

## Composition
SR: `[0, c_SR] ∪ [q_SR, e_close] ∪ [e_close, ∞) = [0, ∞)`, with `[q_SR, c_SR]` a
`DECLARED_REDUNDANT_CERTIFIED_OVERLAP`. CUSUM: `[0, 11/2] ∪ (11/2, e_close] ∪ [e_close, ∞)`.
Uncovered width: 0 for both.

## SR bridge cells (indices 2000–2005, non-terminal, all affine components zero)
| cell | interval | C_upper (num/2³²) | parent |
| --- | --- | --- | --- |
| 2000–2003 | `[6.7555314, 7.0688599]` in 4 equal parts, rho 0.0391661 | 8589935033 | bridge parent 9000 |
| 2004–2005 | `[7.0688599, 1883835/262144]` in 2 equal parts, rho 0.0293501 | 6894180847 | bridge parent 9001 |

## Producer and authorization
`K1R4-SR-BRIDGE-PRODUCER`, authorization `K1R4-SR-BRIDGE-AUTH-001` (AWS only, no Vultr, no handoff,
no synthetic records; the PS1 authorization is **not** reused). The producer identity binds the
transformation manifest, all 7 generated stages, the 39 lower-level executor files, the bridge table,
universe, record schemas and runtime contract.
