# SRK certificate specification (for independent verification from the mathematics, not from the producer code)

A certificate claims one inequality, and it must be checkable **without trusting the producer**. This document plus
`theory/THEOREM_SRK.md` (sections 1, 2, 9) and the operator definition (`p5y_k5_perron_deflated_resolvent/theorem/
OPERATOR_AUDIT.md` §1) are the complete specification. An independent verifier must not import or read
`impl/srk_*.py` or the overnight `c1b_*` modules.

## 1. The model (geometry (h, k), c := h + k; frozen real geometry h = 5, k = 1/2)

* **State space.** X = {(p, m) ∈ [0, h]² : p = 0 or m = 0 or p + m ≤ h − 2k}. This is the closure of the reachable
  set; it includes the atom a = (0, 0).
* **Kernel.** For f ∈ B(X), x = (p, m) ∈ X and drift e ∈ ℝ, the whole kernel is

      (K_e f)(p, m) = ∫_{m−c}^{c−p} f( max(0, p + z − k), max(0, m − z − k) ) φ(z + e) dz,

  with φ the standard normal density. The integration window is e-free, and so is the update map.
* **Hermite weights.** He_0 = 1, He_1 = v, He_{n+1} = v He_n − n He_{n−1}.
* **State-resolved norms.** k_i(x; e) := ∫_{m−c+e}^{c−p+e} |He_i(v)| φ(v) dv, and κ̄_i^E(x) := sup_{e∈E} k_i(x; e).

## 2. Certificate JSON (schema `SRK_CERT/1`)

| key | meaning |
|---|---|
| `geometry` | {"h": "p/q", "k": "p/q"} |
| `block` | ["e_lo", "e_hi"]: the drift set E = [e_lo, e_hi], exact rationals |
| `e_c` | (e_lo + e_hi)/2, exact |
| `hermite_index` | i ∈ {0, 1, 2, 3, 4} |
| `weight_block` | ["w_lo", "w_hi"] ⊇ block: the weight is κ̄_i over the WEIGHT block (default equal to `block`) |
| `V0`, `V1`, `W0`, `W1` | bivariate polynomials in (p, m): {"a,b": "num/den"} meaning Σ c_ab p^a m^b, exact rationals |
| `lam`, `eta_W` | informational (already folded into V0/V1/W0/W1) |
| `Gamma` | claimed value "num/den" |
| `W_at_atom_max` | informational |
| `sha256` | sha256 of the canonical JSON (sort_keys, default separators) of every other key |

For e ∈ E define V_e := V0 + (e − e_c)·V1 and W_e := W0 + (e − e_c)·W1.

## 3. What the certificate claims (and the verifier must decide)

For **every** e ∈ E and **every** x ∈ X:

    (C1)  W_e(x) ≥ 0
    (C2)  W_e(x) − (K_e W_e)(x) ≥ 1
    (C3)  V_e(x) − (K_e V_e)(x) ≥ κ̄_i^{Ew}(x),   Ew = weight_block (⊇ E)
    (C4)  Gamma ≥ max( V_{e_lo}(a), V_{e_hi}(a) )     (exact rational comparison)

and `sha256` must match the body.

(C1)–(C3) are statements about all (x, e) ∈ X × E. A verifier must prove them with a rigorous method, for example:
* interval arithmetic with rational endpoints on a cover of X × E by boxes, with outward-rounded rigorous enclosures of
  φ and Φ;
* or any other method whose soundness it can state.

Failing to prove (C1)–(C3) is a REJECT: a rejection is never a false acceptance. The certificates are produced with a
margin (the μ-term of THEOREM_SRK §7), so that a sound but somewhat looser method can still accept a valid certificate
with enough subdivision.

**Closed form for (K_e P)(x) with P a polynomial.** Split the window at the clipping kinks z = k − p (p + z − k = 0) and
z = m − k (m − z − k = 0). On each piece the image state is affine in z, so P(image) is a polynomial in z. With
u = z + e,

    ∫_A^B u^n φ(u) du = M_n(A, B),
    M_0 = Φ(B) − Φ(A),  M_1 = φ(A) − φ(B),  M_n = (n−1) M_{n−2} + A^{n−1}φ(A) − B^{n−1}φ(B).

The pieces are:
* p + m ≥ 2k:
  * z ∈ [m − c, k − p]: image (0, m − z − k);
  * z ∈ [k − p, m − k]: image (p + z − k, m − z − k);
  * z ∈ [m − k, c − p]: image (p + z − k, 0).
* p + m ≤ 2k:
  * z ∈ [m − c, m − k]: image (0, m − z − k);
  * z ∈ [m − k, k − p]: image (0, 0), the atom;
  * z ∈ [k − p, c − p]: image (p + z − k, 0).

The verifier should derive and check this itself.

## 4. What the certificate is used for

By THEOREM_SRK Lemma SV′, (C1)–(C4) imply sup_{e∈E} (R_e κ̄_i^E)(a) ≤ Gamma, where R_e = (I − K_e)⁻¹. That value
enters `impl/srk_assemble.py` as Γ̄_i.

## 5. Required rejections (verifier self-tests)

The verifier must REJECT each of the following:
1. The certificate with `Gamma` decreased by 1/10⁶.
2. V0 scaled by 1 − 2⁻⁸.
3. V0 := V0 − (lam)·W0, i.e. the additive repair removed (when lam > 0).
4. The block widened by 1/8 on either side (with e_c recomputed), unless the widened claim is also true. The verifier
   reports which.
5. The hermite_index increased by one (a larger weight: the claim should then generally fail).
6. The sha256 altered.
7. Malformed input: a missing key, a non-rational string, e_lo > e_hi, or a non-dyadic drift if the method needs
   dyadics (it must refuse, not crash).

The verifier must ACCEPT the genuine certificates, or report the specific (x, e) box where its method could not prove
the claim.
