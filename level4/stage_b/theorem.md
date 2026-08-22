# Stage B — Theorem statement and proof skeleton

**Status of this document.** Written before the certifying code was finished, and
edited only to record what was actually proved. It states the target, the
lemmas it decomposes into, and — explicitly — which lemmas are ordinary
mathematics and which are discharged by validated numerics.

---

## 0. The frozen object

Fix the Level 1–3 frozen constants, unchanged:

```text
k = 1/2 ,   h = 5 ,   m = 1 ,   rho = 1
```

Let `e ∈ ℝ` be the reference error. Under reference error `e` the monitored
innovations are

```text
z_t = X_t − R_j ,   X_t ~ iid N(mu_j, 1) ,   e = R_j − mu_j
   ⟹  z_t ~ iid N(−e, 1) .
```

The frozen two-sided CUSUM, shared innovation, inclusive threshold tested
**after** the update, first admissible index `t = 1`:

```text
S⁺_0 = S⁻_0 = 0
S⁺_t = max(0, S⁺_{t−1} + z_t − k)
S⁻_t = max(0, S⁻_{t−1} − z_t − k)
tau  = inf{ t ≥ 1 : max(S⁺_t, S⁻_t) ≥ h }
```

With `m = 1` the re-baselining block is the single alarm-causing observation,
so `R_{j+1} = X_tau` and `e_{j+1} = z_tau + e`. The **deterministic
conditional-mean skeleton** at full reuse is therefore

```text
G(e)   := E_e[ z_tau ]
F_1(e) := e + G(e)  =  E[ e_{j+1} | e_j = e ] .
```

This is the same `F_1` as Gate 4.2 and as the Claude Science solver; the
correspondence is checked numerically in the report and structurally in
`tests/test_frozen_correspondence.py`.

---

## 1. Target theorem

> **Theorem (Stage B target).** For the frozen symmetric two-sided Gaussian
> CUSUM with `k = 1/2`, `h = 5`, `m = 1` and full reuse `rho = 1`, there is a
> real number `e*` and an interval `I` with `0 ∉ I` such that
>
> 1. `e* ∈ I` and `F_1(e*) = −e*`;
> 2. `e*` is the **unique** solution of `F_1(e) + e = 0` in `I`;
> 3. `{e*, −e*}` is a period-2 orbit of `F_1`, i.e. `F_1(F_1(e*)) = e*`
>    and `F_1(e*) ≠ e*`;
> 4. its multiplier `lambda_2 = F_1'(e*) · F_1'(−e*) = [F_1'(e*)]²` satisfies
>    `|lambda_2| < 1`, so the orbit is locally attracting.
>
> Numerically `e* ≈ 1.0367`.

**What the theorem is about.** `F_1` is the *deterministic* conditional-mean
map. The actual reference recursion is `E_{j+1} = F_1(E_j) + noise`. This
theorem says nothing about that stochastic recursion, its invariant law, or
bimodality. Those remain `OPEN`.

---

## 2. Analytic lemmas

### L0 — Well-posedness
`tau < ∞` almost surely, `E_e[tau] < ∞`, and `z_tau ∈ L¹`, so `G(e)` is a
well-defined real number and `|G(e)| ≤ E|N(−e,1)| · E_e[tau]` by Wald's
identity applied to `Σ_{t≤tau} |z_t|`.
*Discharged by L2 (which gives a geometric tail for `tau`) plus Wald.*

### L1 — Live-region enclosure
Every reachable pre-alarm state lies in

```text
L = {(p,0) : 0 ≤ p < h} ∪ {(0,m) : 0 ≤ m < h}
    ∪ {(p,m) : p > 0, m > 0, p + m < h − 2k}
```

and `L` is forward invariant under the continuation dynamics.

*Proof.* From `(0,0)` one step gives `S⁺ = (z−k)⁺`, `S⁻ = (−z−k)⁺`; since
`k > 0` at most one is positive. Hence a maximal run of "both arms positive"
begins at a time `t₀` whose predecessor had one arm zero, say `S⁻_{t₀−1} = 0`.
Both arms positive at `t₀` makes both `(·)⁺` inactive, so
`S⁺_{t₀} + S⁻_{t₀} = S⁺_{t₀−1} − 2k < h − 2k` by liveness at `t₀−1`. Inside the
run each step subtracts exactly `2k` from the sum, so the bound persists. If
instead one arm is zero, liveness of the other gives `max < h`. ∎

This is the same statement as the frozen Level 1–3 certificate's
`reachable_domain` (`certificate.json`), and as the enclosure lemma in the
Claude Science solver's module docstring.

### L2 — Uniform killing (the resolvent bound)
For every live `s` and every `n ≥ 1`,

```text
P_s(tau ≤ n) ≥ q_n(e) := P(|G_n| ≥ h + nk) ,    G_n = Σ_{t≤n} z_t ~ N(−ne, n)
```

hence `P_s(tau > jn) ≤ (1 − q_n)^j`, and

```text
sup_s E_s[tau] ≤ n / q_n(e) ,      ‖(I − K_e)^{−1}‖_∞ ≤ n / q_n(e) .
```

*Proof.* `max(0,x) ≥ x` gives `S⁺_n ≥ S⁺_0 + G_n − nk ≥ G_n − nk` and
`S⁻_n ≥ S⁻_0 − G_n − nk ≥ −G_n − nk` by induction. So `|G_n| ≥ h + nk` forces
`max(S⁺_n, S⁻_n) ≥ h`, i.e. `tau ≤ n`. The bound is uniform in the starting
state and involves no discretization. ∎

This is the drift-`−e` version of the frozen
`rebaseguard_certify.contraction.certify_block_contraction`.

### L3 — Odd symmetry (proved, not assumed)
`G(−e) = −G(e)`, hence `F_1(−e) = −F_1(e)`.

*Proof.* Let `P_e` be the law of `(z_t)_{t≥1}` iid `N(−e,1)` on `ℝ^ℕ`, and let
`R(ω) = −ω`. Then `R_* P_e = P_{−e}`. By induction on the recursion,
`S⁺_t(Rω) = S⁻_t(ω)` and `S⁻_t(Rω) = S⁺_t(ω)`: the two updates are exchanged
by `z ↦ −z`. Hence `max(S⁺_t, S⁻_t)` is `R`-invariant, so `tau(Rω) = tau(ω)`,
and `z_{tau}(Rω) = −z_{tau}(ω)`. Therefore

```text
G(−e) = E_{P_{−e}}[z_tau] = E_{P_e}[z_tau ∘ R] = E_{P_e}[−z_tau] = −G(e).
```
Integrability is L0. ∎

*The symmetric route is therefore legitimate; the general two-variable
formulation is not required.*

### L4 — Smoothness in `e`
On any compact real interval `J`, `q_n` is continuous and positive, so
`‖K_e^n‖_∞ ≤ 1 − min_J q_n < 1` uniformly and `I − K_e` is boundedly
invertible on `L^∞(L)`. The continuation limits `u(s) = h+k−p`,
`v(s) = h+k−m` do **not** depend on `e`, so `∂_e^j K_e` has kernel
`φ^{(j)}(z+e)` on the continuation set with `‖∂_e^j K_e‖_∞ ≤ ∫|φ^{(j)}| < ∞`.
Hence `e ↦ K_e` and `e ↦ r_e` are `C^∞` in operator/sup norm, and so is
`e ↦ G_e = (I−K_e)^{−1} r_e`. In particular `F_1` is `C^1` on `J`, and
differentiating L3 gives `F_1'(−e) = F_1'(e)` (`F_1'` is even).

### L5 — Fixed-point equation
`G` is the unique bounded solution of `G = T G`, where

```text
(T G)(s) = ∫_ℝ psi(s,z) φ(z+e) dz ,
psi(s,z) = z                if z ≤ −v(s) or z ≥ u(s)      [alarm]
         = G(q(s,z))        otherwise                     [continue]
q(s,z)   = ((p+z−k)⁺, (m−z−k)⁺) .
```
Equivalently `G = K_e G + r_e`. Uniqueness: a difference of two bounded
solutions is killed by `I − K_e`, which is injective by L2. `T` is **monotone**
in `G`, which is what the interval iteration uses.

### L6 — Derivative equation
By L4, differentiating `G_e = K_e G_e + r_e` in `e`:

```text
(I − K_e) G_e' = (∂_e K_e) G_e + ∂_e r_e ,
```
with `(∂_e K_e)` the continuation integral against `φ'(z+e) = −(z+e)φ(z+e)`
and `∂_e r_e` the alarm integral against the same. Then
`F_1'(e) = 1 + G_e'(0,0)`.

### L7 — Period-2 from oddness
If `F` is odd and `F(e*) = −e*`, then `F(−e*) = −F(e*) = e*`, so
`F(F(e*)) = e*`. If in addition `F` is differentiable then `F'` is even and

```text
(F∘F)'(e*) = F'(F(e*))·F'(e*) = F'(−e*)·F'(e*) = [F'(e*)]² .
```
If `e* ≠ 0` and `F(e*) = −e* ≠ e*`, the orbit has exact period 2.

### L8 — Local attraction
If `|(F∘F)'(e*)| < 1` then `e*` is a locally asymptotically stable fixed point
of `F∘F`; by symmetry so is `−e*`; hence `{e*, −e*}` is a locally attracting
period-2 orbit of `F`. (Standard hyperbolic fixed-point theorem.)

---

## 3. Computer-assisted obligations

| ID | Obligation | Method |
|---|---|---|
| C1 | rigorous enclosure of `G(e)` at a thin `e` | monotone interval iteration on `T` (L5), Arb |
| C2 | rigorous enclosure of `G_e'(0,0)` for `e` ranging over an interval | interval iteration on L6 with the C1 bracket as data |
| C3 | existence + uniqueness of a nonzero root of `H(e) = F_1(e) + e` in `I` | interval Newton / Krawczyk using C1 and C2 |
| C4 | `|lambda_2| < 1` | `lambda_2 = [1 + G'(I)]²` from C2 |

**What makes C1/C2 enclosures of the *true* map and not of a discretization.**
Three approximation sources that a naive validated-Nyström scheme would incur
are structurally absent here:

* **quadrature error — zero.** The `z` axis is cut at breakpoints and each
  piece is integrated against the Gaussian in closed form (`Φ` differences and
  `φ` differences). No quadrature rule is used.
* **domain-truncation error — zero.** The continuation set is contained in
  `(−(h+k), h+k)`, so the outer regions `|z| > z_cut > h+k` are pure-alarm and
  are integrated to `±∞` analytically.
* **iterative solve error — zero.** By monotonicity of `T`, *every* iterate of
  the interval iteration is already a valid bracket; the iteration may be
  stopped anywhere.

The remaining sources — Arb ball radii, the cell partition, and float rounding
inside the iteration — are enumerated with their bounds in
`proof_obligations.md` §4 and in the report's error budget.
