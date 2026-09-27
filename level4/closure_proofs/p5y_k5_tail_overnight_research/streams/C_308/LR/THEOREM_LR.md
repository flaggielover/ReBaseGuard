# THEOREM LR — likelihood-ratio / score representation of the atom constants A0, A1, A2

Status: theory complete (self-checked, not independently reviewed); VALIDATED_NON_TARGET on exact synthetic fixtures
(§7). Stream C1a. No target-cell quantity and no tail-cell constant appears or is computed in this document (rule S8
checked). Under floor r2 any supply built from it is CLOSURE-ONLY.

## §0 Setting and notation

X is a measurable state space, B(X) the bounded measurable functions with the sup norm, a ∈ X the evaluation point
(the atom), E ⊂ ℝ a drift set (a point or a block [e_lo, e_hi]). The consumer (TC / TC-T radius
rad = A0 p2 + 2 A1 p1 + A2 p0, see SCR/graph_B_operators.md §a.2) needs, uniformly on E,

    A0 ≥ sup_e ‖δ_a R_e‖,   A1 ≥ sup_e ‖δ_a ∂_e R_e‖,   A2 ≥ sup_e ‖δ_a ∂²_e R_e‖,

where ‖δ_a L‖ := sup_{‖f‖≤1} |(Lf)(a)| is the functional norm, R_e = (I − K_e)⁻¹, ∂R = R K' R, ∂²R = 2RK'RK'R + RK''R.

**Driven killed chain (standing form).** A killed Markov family is given by
* a noise space (Z, ν) and, for each x ∈ X, a *probability* density q_e(x, ·) w.r.t. ν (so ∫ q_e(x,z) ν(dz) = 1);
* a measurable update map T : X × Z → X, and a survival set A(x) ⊂ Z, both **independent of e**;
* the sub-Markov kernel  (K_e f)(x) = ∫_{A(x)} f(T(x,z)) q_e(x,z) ν(dz).

Path: X_0 = x, Z_k ~ q_e(X_{k−1}, ·), X_k = T(X_{k−1}, Z_k) while Z_k ∈ A(X_{k−1}); the chain is killed at the first k
with Z_k ∉ A(X_{k−1}); τ := that k (so X_0, …, X_{τ−1} are alive, and Σ_{n<τ} f(X_n) = Σ_{n≥0} f(X_n)1{n<τ}).
Then (K_e^n f)(x) = E_x^e[f(X_n); n < τ] and, when the series converges, (R_e f)(x) = E_x^e[Σ_{n<τ} f(X_n)].

Scores (defined where q_e > 0; set to 0 where q_e = 0):

    s_e(x,z) := ∂_e log q_e(x,z),    t_e(x,z) := ∂²_e log q_e(x,z),    so  ∂_e q = s q,  ∂²_e q = (s² + t) q,

    M_n := Σ_{k=1}^{n} s_e(X_{k−1}, Z_k),   N_n := Σ_{k=1}^{n} t_e(X_{k−1}, Z_k)   (M_0 = N_0 = 0).

Derivative kernels (K'f)(x) = ∫_A f(T) s q dν, (K''f)(x) = ∫_A f(T)(s² + t) q dν, and positive majorant kernels
(|K'| f)(x) := ∫_A f(T) |s| q dν, (|K''| f)(x) := ∫_A f(T) |s² + t| q dν. Also the *moment kernels*
(K^{(j)} f)(x) := ∫_A f(T) s^j q dν (so K^{(0)} = K, K^{(1)} = K').

**Two instances.**
* *CUSUM (noise level).* Z = ℝ, ν = Lebesgue, q_e(x,z) = φ(z + e), T = the CUSUM update, A(x) = the e-free
  non-alarm window (THEOREM_AD Lemma K). Then s = −(z + e), t = −1.
* *State level / finite fixtures.* Z = X ⊔ {†}, T(x,y) = y, A(x) = X, q_e(x,y) = K_e[x][y] for y ∈ X and
  q_e(x,†) = 1 − Σ_y K_e[x][y]. Then s(x,y) = K1[x][y]/K0[x][y], t(x,y) = K2[x][y]/K0[x][y] − s(x,y)² on living
  transitions. Any sub-Markov kernel with density p_e(x,y) μ(dy) is of this form (T = id); e-dependence of the
  killing mass is allowed because only living transitions enter the scores.

## §1 General LR (score) representation (item a)

**Hypotheses (H) on a drift set E.**
* (H1) *Resolvent.* There is W ∈ B(X) with W ≥ 1 + K_e W on X for every e ∈ E (whole-kernel supersolution).
* (H2) *Differentiability.* For each x, e ↦ q_e(x,z) is C² for ν-a.e. z, and e ↦ K_e is C² in operator norm on B(X)
  with derivatives K', K'' given by the kernels above (for CUSUM: Lemma K; for polynomial fixtures: trivially).
* (H3) *Score moments.* m_j := sup_{e∈E, x∈X} ∫_{A(x)} |s_e|^j q_e dν < ∞ for j = 1, 2, 4, and
  m'_j := sup ∫_A |t_e|^j q_e dν < ∞ for j = 1, 2. (CUSUM: s ~ N(0,1) restricted, t = −1; fixtures: finite.)

**Theorem LR-1 (score representation).** Under (H), for every e ∈ E, f ∈ B(X), x ∈ X:

    (∂_e R_e f)(x)  = (R K' R f)(x)                 = E_x[ Σ_{n<τ} f(X_n) M_n ],
    (∂²_e R_e f)(x) = (2RK'RK'R f + RK''R f)(x)    = E_x[ Σ_{n<τ} f(X_n) (M_n² + N_n) ],

and both random series converge absolutely in L¹(P_x):

    E_x[ Σ_{n<τ} |f(X_n)| Σ_{k≤n} |s_k| ] = (R|K'|R|f|)(x) < ∞,
    E_x[ Σ_{n<τ} |f(X_n)| ( Σ_{k≤n}|s_k²+t_k| + 2Σ_{j<k≤n}|s_j||s_k| ) ] = (R|K''|R|f| + 2R|K'|R|K'|R|f|)(x) < ∞.

*Proof.* (i) *Operator series.* By Lemma TL (§2), ‖K_e^n‖ ≤ θ^n ‖W‖ with θ = 1 − 1/‖W‖ < 1, so R_e = Σ_n K_e^n
converges in operator norm and ‖R_e‖ ≤ ‖W‖. By (H2) and the standard resolvent calculus, e ↦ R_e is C² with
∂R = RK'R and ∂²R = 2RK'RK'R + RK''R. Expanding the Neumann series,

    R K' R = Σ_{n≥1} Σ_{k=1}^{n} K^{k−1} K' K^{n−k},
    R K' R K' R = Σ_{n≥2} Σ_{1≤j<k≤n} K^{j−1} K' K^{k−j−1} K' K^{n−k},   R K'' R = Σ_{n≥1} Σ_{k=1}^{n} K^{k−1} K'' K^{n−k}.

(ii) *One term.* For 1 ≤ k ≤ n, by the Markov property at times k−1 and k and the definition of K',

    (K^{k−1} K' K^{n−k} f)(x) = E_x[ 1{k−1<τ} ∫_{A(X_{k−1})} s(X_{k−1},z) q(X_{k−1},z) (K^{n−k}f)(T(X_{k−1},z)) ν(dz) ]
                               = E_x[ f(X_n) s(X_{k−1}, Z_k) ; n < τ ].

Likewise (K^{k−1}K''K^{n−k}f)(x) = E_x[f(X_n)(s_k² + t_k); n<τ] (because ∂²q = (s²+t)q) and, applying the Markov
property twice, (K^{j−1}K'K^{k−j−1}K'K^{n−k}f)(x) = E_x[f(X_n) s_j s_k; n<τ] for j < k.
(iii) *Absolute convergence.* The same computation with |s|, |s²+t| and |f| in place of s, s²+t, f gives the two
displayed majorant identities; they are finite because ‖R‖ ≤ ‖W‖ and ‖|K'|‖ ≤ m_1, ‖|K''|‖ ≤ m_2 + m'_1.
(iv) *Summation.* By (iii) and Fubini, Σ_n Σ_k E[f(X_n)s_k; n<τ] = E[Σ_{n<τ} f(X_n) M_n]; the second identity uses
M_n² + N_n = Σ_{k≤n}(s_k² + t_k) + 2Σ_{j<k≤n} s_j s_k. ∎

**Remarks.** (1) No differentiation under an infinite expectation is performed: the identity is the Neumann expansion
of RK'R read path-wise, and the only analytic input is (H2) for the single-step kernel. (2) The killing never contributes a
score term: only living transitions carry a density, so e-dependent killing mass (fixtures) is allowed, while for the
noise form the survival set must be e-free (else ∂_e K picks up boundary terms — the CUSUM window is e-free, Lemma K).
(3) *Rao–Blackwell ordering of score levels.* If two representations of the same K_e are related by a coarsening
(the state-level density of the noise-level form: p_e(x,dy) = T(x,·)_#(q_e 1_A ν)), then the state-level score is the
conditional expectation of the noise-level score given (X_{k−1}, X_k); since {n<τ} and X_{0..n} are functions of the
X-path, E[|M_n^{state}|; n<τ] ≤ E[|M_n^{noise}|; n<τ] (conditional Jensen). For CUSUM, T(x,·) is injective off the atom
window, so the two scores differ only on transitions into a (state score there = E[S | Z ∈ window]).

## §2 Geometric tail lemma for τ from a supersolution

**Lemma TL.** Let W ∈ B(X) satisfy W ≥ 1 + K_e W on X for every e ∈ E, and put C_W := sup_X W, θ := 1 − 1/C_W.
Then for every e ∈ E, x ∈ X, n ≥ 0:

  (a) P_x(τ > n) = (K_e^n 1)(x) ≤ θ^n W(x) ≤ θ^n C_W;
  (b) E_x[τ] = (R_e 1)(x) ≤ W(x), and E_x[τ^p] < ∞ for every p ≥ 1, with E_x[Σ_{n<τ} n^p] ≤ C_W Σ_n n^p θ^n;
  (c) under (H3), for p ∈ {1, 2, 4} and 1 ≤ k ≤ n:  E_x[|s_k|^p ; n < τ] ≤ m_p C_W² θ^{n−1}, hence
      E_x[|M_n|^p ; n<τ] ≤ n^p m_p C_W² θ^{n−1}  and  E_x[Σ_{n<τ} |M_n|^p] ≤ m_p C_W² Σ_{n≥1} n^p θ^{n−1} < ∞;
      the same holds for N_n with m'_p (p = 1, 2);
  (d) (polynomial growth vanishing) if g(x, μ, ν) is measurable with |g| ≤ G (1 + μ⁴ + ν²), then for the augmented chain
      Y_n := (X_n, μ + M_n, ν + N_n): E[|g(Y_n)|; n<τ] → 0 as n → ∞.

*Proof.* (a) W ≥ 1 and W − 1 ≥ KW give KW ≤ W − 1 ≤ (1 − 1/C_W) W = θW (since W ≤ C_W ⇒ 1 ≥ W/C_W). By positivity of
K, K^n 1 ≤ K^n W ≤ θ^n W. (b) R1 = Σ K^n 1; the partial sums satisfy Σ_{j<n}K^j1 ≤ W by induction
(Σ_{j<n+1}K^j 1 = 1 + K Σ_{j<n}K^j 1 ≤ 1 + KW ≤ W); moments from (a) since P(τ > n) ≤ C_Wθ^n.
(c) By the Markov property at k−1 and at k:
E_x[|s_k|^p; n<τ] = E_x[ 1{k−1<τ} ∫_{A(X_{k−1})} |s|^p q (K^{n−k}1)(T) dν ] ≤ P_x(τ>k−1) · m_p · sup_y P_y(τ>n−k)
≤ C_W θ^{k−1} m_p C_W θ^{n−k}. Then |M_n|^p ≤ n^{p−1} Σ_{k≤n}|s_k|^p (power-mean) gives the stated bound.
(d) |g(Y_n)| ≤ G(1 + 8μ⁴ + 8M_n⁴ + 2ν² + 2N_n²) and each term's expectation on {n<τ} is ≤ poly(n) θ^{n−1} by (a), (c). ∎

For CUSUM: W is the whole-kernel supersolution of THEOREM_AD §4 ("Whole-kernel supersolution"); m_p ≤ E|Y|^p for
Y ~ N(0,1) (m_1 = √(2/π), m_2 = 1, m_4 = 3), m'_1 = m'_2 = 1 (t ≡ −1 on the surviving set, integrated against a
sub-probability). For the taboo (excursion) chain of §5.3 the same lemma holds with K̂ and the taboo supersolution w of
THEOREM_AD Lemma T (C_W = C_T).

## §3 CUSUM specialisation (item b)

For the two-sided CUSUM kernel (THEOREM_AD Lemma K): q_e(x,z) = φ(z + e) does not depend on x, the update map and the
alarm window are e-free, so the standing form applies with

    s_e(z) = ∂_e log φ(z+e) = −(z+e) =: S,     t_e ≡ −1,     N_n = −n.

Under P^e the S_k = −(Z_k + e) are i.i.d. N(0,1) and S_k is independent of F_{k−1} = σ(Z_1..Z_{k−1}); M_n is a standard
Gaussian random walk and τ is a stopping time of its filtration (X_n is a function of Z_1..Z_n). Theorem LR-1 reads

    (∂R f)(a)  = E_a[ Σ_{n<τ} f(X_n) M_n ],          (∂²R f)(a) = E_a[ Σ_{n<τ} f(X_n) (M_n² − n) ].

The kernels, written as weights on the noise: K^{(1)} = K' has weight S, K'' has weight S² − 1 = He_2(S), and
K^{(2)} = K'' + K has weight S². (H3): m_1 = √(2/π), m_2 = 1, m_4 = 3, m'_1 = m'_2 = 1. (H2) is Lemma K. (H1) is the whole-kernel
supersolution; for the excursion chain, Lemma T.

*Useful exact identities (not needed for the bounds, used as validation handles).* Taking f = 1:
∂_e E_a[τ] = E_a[Σ_{n<τ} M_n], where path-wise Σ_{n<τ} M_n = Σ_{1≤k<τ} S_k (τ − k) (these are the ARL
sensitivities; they are exact, finite by Lemma TL, and give the *lower* bounds A1_true ≥ |∂_eΛ(e)|,
A2_true ≥ |∂²_eΛ(e)| used as sanity checks).

## §4 Consequences for A0, A1, A2 (item c)

Let Λ(e) := E_a^e[τ] = (R_e 1)(a). Define, for each e,

    A1^LR(e) := E_a^e[ Σ_{n<τ} |M_n| ],        A2^LR(e) := E_a^e[ Σ_{n<τ} |M_n² + N_n| ]   (CUSUM: |M_n² − n|).

**Corollary LR-2.** Under (H), for every e ∈ E:

  (A0)  ‖δ_a R_e‖ = Λ(e)  exactly (R_e ≥ 0, so sup_{‖f‖≤1}|(R_e f)(a)| is attained at f = 1);
  (A1)  A1_true(e) := ‖δ_a ∂R_e‖ ≤ A1^LR(e);
  (A2)  A2_true(e) := ‖δ_a ∂²R_e‖ ≤ A2^LR(e).

Hence A0 := sup_E Λ, A1 := sup_E A1^LR, A2 := sup_E A2^LR (or any certified upper bounds of them) are admissible
atom constants for TC / TC-T on the block E.

*Proof.* (A0): |(R f)(a)| ≤ (R|f|)(a) ≤ ‖f‖ (R1)(a), equality at f = 1. (A1): for ‖f‖ ≤ 1, by Theorem LR-1 and
|E[Σ f(X_n) M_n]| ≤ E[Σ |f(X_n)||M_n|] ≤ E[Σ |M_n|]. (A2) identical with M_n² + N_n. ∎

Exact form of the true constants (for comparison): A1_true(e) = |u_1|(X) where u_1(dy) := Σ_n E_a[M_n; X_n ∈ dy, n<τ]
is the signed "score occupation measure" (total variation norm); similarly A2_true = |u_2|(X) with weight M_n² + N_n.
The loss true → LR is exactly the cancellation *between different paths ending in the same y* (and across n); the loss
LR → PM (§5) is the cancellation *within one path* (inside M_n).

## §5 Orderings: true ≤ LR ≤ PM ≤ Lemma G; relation to Dv′ (item d)

Positive majorants (PM), at the score level used for LR:

    PM1(e) := (R|K'|R1)(a),      PM2(e) := (R|K''|R1)(a) + 2(R|K'|R|K'|R1)(a).

**Proposition LR-4 (ordering chain).** Under (H), for every e ∈ E, and for either score level:

    Λ(e) = A0_true(e) ≤ ‖R_e‖ ≤ C,
    A1_true ≤ A1^LR ≤ PM1 ≤ ‖R‖² ‖|K'|‖ ≤ k1 C²                     (Lemma G A1),
    A2_true ≤ A2^LR ≤ PM2 ≤ ‖R‖²‖|K''|‖ + 2‖R‖³‖|K'|‖² ≤ k2 C² + 2k1² C³   (Lemma G A2),

where the last inequality in each line requires C ≥ ‖R_e‖ and k_i ≥ ‖|K^{(i)}_e|‖ at the *same* score level.

*Proof.* First inequalities: Corollary LR-2. Second: |M_n| ≤ Σ_{k≤n}|s_k| and |M_n² + N_n| ≤ Σ_k|s_k² + t_k| +
2Σ_{j<k}|s_j||s_k|, then the majorant identities of Theorem LR-1(iii) with f = 1. Third: for positive operators
(P_1 P_2 P_3 1)(a) ≤ ‖P_1‖‖P_2‖‖P_3‖. Fourth: monotonicity in the inputs. ∎

*Score-level caveat.* At the state level ‖|K'|‖ = ‖K'‖ (the sup-norm operator norm of a kernel with a density is the sup
of the total variation of its rows), so the chain closes whenever Lemma G's k1 bounds ‖K'‖. At the noise level
‖|K'|_noise‖ = sup_x ∫_A |s| q dν can exceed ‖K'‖; the chain then closes if k1 ≥ that noise norm (true for the CUSUM
κ-type bound k1 = E|Y| = √(2/π), not automatically for sharper drift-aware state norms). LR_state ≤ LR_noise always
(§1 Remark 3), and PM_state ≤ PM_noise (|E[s|y]| ≤ E[|s| | y]).

### 5.2 Plain (whole-kernel) LR versus Dv′: neither dominates

**Example E1 (Dv′ exact, noise-level LR loses by an unbounded factor).** One state X = {a}, T(a,z) = a, q_e = φ(z+e),
survival window A = {z ≤ c} (e-free), so K_e = π(e) := Φ(c+e), Λ = 1/Φ̄(c+e) (Φ̄ = 1 − Φ), writing h := c + e.
* true: A1_true = |∂_eΛ| = φ(h)/Φ̄(h)² = Λ² φ(h).
* Dv′ with exact inputs: every living transition enters a, so K̂ = 0, Ĝ = I, τ_a = C_T = 1, κ_n = 0, D = Φ̄(h),
  D' = −φ(h), δ1 = φ(h)/Φ̄(h); A1^{Dv′} = Λ δ1 = Λ² φ(h) = A1_true (exact).
* state-level LR: the state score is the deterministic ∂_e log π(e) = φ(h)/Φ(h); A1^LR_state = Σ_n π^n n φ/Φ
  = Λ²φ(h) = A1_true.
* noise-level LR: on {n<τ} the S_k (k ≤ n) are i.i.d. with the law of ξ := S | S ≥ −h (mean μ_h = φ(h)/Φ(h),
  variance σ_h² ∈ (0,1], σ_h → 1 as h → ∞), and P(n<τ) = π^n. Put Y_n := M_n − nμ_h (centred i.i.d. sum). Hölder,
  E Y² ≤ (E|Y|)^{2/3}(E Y⁴)^{1/3}, with E Y_n⁴ ≤ 3n²σ_h⁴ + n E(ξ−μ_h)⁴, gives E|Y_n| ≥ √n σ_h/2 for
  n ≥ n_h := ⌈E(ξ−μ_h)⁴/σ_h⁴⌉; and |M_n| ≥ |Y_n| − nμ_h. Hence

      A1^LR_noise ≥ (σ_h/2) Σ_{n≥n_h} π^n √n − μ_h π/(1−π)² ≥ (σ_h/2) Σ_{n≥n_h} π^n √n − A1_true/Φ(h).

  As Λ → ∞ (h → ∞): σ_h → 1, n_h → 3, Σ_n π^n √n ~ Γ(3/2) Λ^{3/2}, and A1_true = Λ²φ(h) = Λ·φ(h)/Φ̄(h) ~ Λ h
  ~ Λ√(2 log Λ) (Mills ratio). So A1^LR_noise ≥ (√π/4 − o(1)) Λ^{3/2} while A1^{Dv′} = A1_true = O(Λ √log Λ):
  **the ratio LR_noise / Dv′ → ∞** (rigorous in order; explicit constants on the finite analogue in lr_fsm.py).

**Example E2 (state-level LR loses to Dv′).** Two states {a, b}: a → a w.p. α(e), a → b w.p. β(e), b → a w.p. r
(e-free), everything else killed. The atom recurs every one or two steps, the state scores s(a,a) = α'/α and
s(a,b) = β'/β differ in sign if α' β' < 0, so M_n is a genuine random walk: A1^LR_state ≳ c Λ^{3/2}, while
Dv′ has C_T = 1 + β, κ1 = |β'| and δ1 = |D'|/D bounded as the killing → 0 with bounded |∂ log D|, i.e.
A1^{Dv′} = O(Λ). lr_fsm.py computes a rigorous *lower* bound on A1^LR (per-(n,y) Hölder, §cert (iv)) and the exact
Dv′ value for a declared ε-ladder, exhibiting A1^LR > A1^{Dv′} once Λ is large.

**Conversely (LR can beat Dv′).** Dv′'s cross factor κ1 C_T multiplies the worst-case excursion length C_T = sup_x
E_x[σ] by the full-noise norm κ1, while LR only pays E|M_n| = O(√n) along the actual excursion from a. When C_T is
large compared with the typical excursion from the atom and Λ is moderate, LR is smaller (observed on fixtures, §7).

**Heuristic asymptotic orders (HEURISTIC, not used by any bound).** If τ is approximately exponential with mean Λ and
M is approximately diffusive and weakly correlated with τ: A1^LR ≈ √(2/π)·E[Σ_{n<τ}√n] ≈ (2/3)√(2/π)E[τ^{3/2}]
≈ Λ^{3/2}/√2 and A2^LR ≈ E|Y²−1|·E[Σ_{n<τ} n] = 4φ(1)·E[τ(τ−1)/2] ≈ 4φ(1)Λ² = O(Λ²); true A1 ≥ |Λ'| = Λ|∂ log Λ| and
true A2 ≥ |Λ''|, typically O(Λ·polylog Λ); Dv′ A1 = Λ(κ1C_T + δ1) = O(Λ C_T), A2 = O(Λ C_T²); Lemma G A1 = k1C² ≥ k1Λ²,
A2 ≥ 2k1²Λ³. So plain LR beats Lemma G by order but not Dv′ when Λ ≫ C_T².

### 5.3 Regenerative LR (RLR): LR inside the atom excursion — dominates Dv′

Taboo kernel K̂_e (THEOREM_AD Lemma K): the standing form with survival set Â(x) := A(x) \ {z : T(x,z) = a}, which is
e-free (CUSUM: the atom window [β, α] is e-free). Its chain is killed at σ := first time of alarm *or* of entering a at
a time ≥ 1; Ĝ = (I − K̂)⁻¹, ν_e(f) = (Ĝf)(a) = E_a[Σ_{n<σ} f(X_n)], τ_a = ν(1) = E_a[σ], D = 1 − (Ĝk_a)(a) > 0,
Λ = τ_a/D (Lemma SM). Define the *excursion LR constants*

    L1(e) := E_a[Σ_{n<σ} |M_n|],   L2(e) := E_a[Σ_{n<σ} |M_n² + N_n|],   ρ_j ≥ sup_{e∈E} L_j(e)/τ_a(e)  (j = 1, 2).

**Theorem LR-3 (RLR constants).** Assume the Dv′ hypotheses on E (Ā ≥ sup E_a[τ], τ ≥ τ_a, D ≥ D_lo > 0,
|D'| ≤ D1, |D''| ≤ D2; δ_j := D_j/D_lo), a taboo supersolution w ≥ 1 + K̂_e w (Lemma T), and (H2)-(H3) for K̂. Then

    A0 = Ā_eff,   A1^RLR = Ā_eff (ρ1 + δ1),   A2^RLR = Ā_eff (ρ2 + 2ρ1δ1 + 2δ1² + δ2),   Ā_eff = min(Ā, τ/D_lo),

are admissible atom constants on E. Moreover the exact excursion ratios satisfy, for every e,

    L1/τ_a ≤ (Ĝ|K̂'|Ĝ1)(a)/τ_a ≤ ‖|K̂'|‖ C_T,     L2/τ_a ≤ [(Ĝ|K̂''|Ĝ1)(a) + 2(Ĝ|K̂'|Ĝ|K̂'|Ĝ1)(a)]/τ_a ≤ ‖|K̂''|‖C_T + 2‖|K̂'|‖²C_T²,

so with ρ_j equal to the exact suprema (or with ρ_j := min(certified ρ_j, the Dv′ factor)), A^RLR ≤ A^{Dv′}
componentwise, for the same (Ā, τ, D_lo, δ1, δ2) and κ_1 ≥ ‖|K̂'|‖, κ_2 ≥ ‖|K̂''|‖.

*Proof.* Theorem LR-1 applied to K̂ (with Lemma TL for w): ν'(f) = E_a[Σ_{n<σ} f(X_n)M_n] and
ν''(f) = E_a[Σ_{n<σ} f(X_n)(M_n² + N_n)], so |ν'(f)| ≤ L1‖f‖ ≤ τ_a ρ1 ‖f‖ and |ν''(f)| ≤ τ_a ρ2 ‖f‖. By Lemma SM(c),
(R f)(a) = ν(f)/D, and the quotient rule gives (ν/D)' = ν'/D − νD'/D², (ν/D)'' = ν''/D − 2ν'D'/D² + ν(2D'²/D³ − D''/D²).
Each term is (τ_a/D)·(factor) with τ_a/D = Λ ≤ Ā_eff (Lemma SM(d) and τ_a ≤ τ, D ≥ D_lo) and the factors bounded by
ρ1, δ1 (|ν| ≤ τ_a‖f‖, |D'|/D ≤ D1/D_lo) etc. — exactly the proof of Lemma Dv′ with κ1C replaced by ρ1 and
2κ1²C² + κ2C by ρ2. The domination: Proposition LR-4 applied to Ĝ (L1 ≤ PM1-hat, L2 ≤ PM2-hat), then
Ĝ1 ≤ C_T and |K̂'|1 ≤ ‖|K̂'|‖ pointwise give (Ĝ|K̂'|Ĝ1)(a) ≤ C_T‖|K̂'|‖ τ_a, and similarly for the second order. ∎

*Note on score levels.* For CUSUM, K̂ has no atom column, T(x,·) is injective on Â(x), so noise-level and
state-level scores coincide for the excursion chain; the Λ^{3/2} penalty of §5.2 cannot arise inside RLR because M is
reset at every return to a. (HEURISTIC order: ρ1 ≈ E_a[σ^{3/2}]/E_a[σ], independent of Λ, versus κ1C_T with
C_T = sup_x E_x[σ].)

## §6 Block uniformity over [e_lo, e_hi] (item e)

All constants must hold for every e in the block E = [e_lo, e_hi].
* **A0.** sup_E Λ(e) ≤ W(a) for any e-free whole-kernel supersolution W ≥ 1 + K_e W (∀e ∈ E) — the existing Ā of
  THEOREM_AD §4; nothing new.
* **A1, A2 (plain LR) — e-free certificate (U1).** Every certificate of §cert is an inequality w ≥ g + 𝒫_e w that is
  *affine in the kernel*; if one e-free w satisfies it for every e ∈ E, Lemma C0 gives V_e ≤ w for every e, hence
  sup_E A1^LR(e) ≤ w(a, 0). The e-dependent quantities to enclose over E are, for the quadratic certificate,
  K_e a, K_e b, K_e^{(2)} b (all ≥ 0 for a, b ≥ 0: upper enclosures suffice) and |K_e^{(1)} b| (upper enclosure of an
  absolute value). For CUSUM these are Gaussian-moment kernel applications with an interval drift — the same
  interval-drift evaluation that I1/I2 already perform for K_e (weights 1, S, S² in place of 1).
* **Sign subtlety.** The cross term 2μK^{(1)}_e b has no fixed sign in e; U1 must enclose |K^{(1)}_e b| over the whole
  block (not K^{(1)} at an endpoint). The full-quadratic certificate (i′) with b1 ≠ 0 needs a *two-sided* enclosure of
  K^{(1)}_e b2 and K_e b1 (b1 has no sign) and the discriminant condition B_x² ≤ 4A_xC_x with the worst-case B_x; that is
  why the δ-form (b1 = 0) is the robust default for blocks.
* **RLR ratios.** ρ_j ≥ sup_E L_j(e) / inf_E τ_a(e). Use an e-free excursion certificate for sup L_j and the trivial
  τ_a ≥ 1 (or a certified lower bound). Alternatively use the non-ratio form |ν'(f)/D| ≤ (sup_E L1)/D_lo‖f‖:
  A1 = sup_E L1 / D_lo + Ā_eff δ1 (and similarly for A2); both forms are valid, take the smaller.
* **Validation (fixtures).** lr_fsm.py builds an e-free δ-certificate on the declared block [0, 1/4] from an entrywise
  upper kernel over sub-intervals (interval Horner, exact rationals) and checks it against the *exact interval
  enclosures*; the pointwise values on a grid of E must lie below the block bound (a check that can fail).

## §cert Certification theory

Augmented chain for A1: Y_n = (X_n, μ + M_n) on X × ℝ with the same killing; augmented sub-Markov kernel

    (𝒫_e w)(x, μ) = ∫_{A(x)} w(T(x,z), μ + s_e(x,z)) q_e(x,z) ν(dz),

and V1(x, μ) := E_x[Σ_{n<τ} |μ + M_n|] = Σ_n 𝒫^n g with g(x,μ) = |μ|; A1^LR = V1(a, 0). (For A2 add ν + N_n.)

**Lemma C0 (comparison / minimal solution).** Let g ≥ 0 and let w be measurable with w ≥ g + 𝒫w pointwise. If either
(i) w ≥ 0, or (ii) |w| ≤ G(1 + μ⁴ + ν²) and the hypotheses of Lemma TL hold, then Σ_n 𝒫^n g ≤ w.
*Proof.* Iterating, w ≥ Σ_{n<N} 𝒫^n g + 𝒫^N w for every N (𝒫 is positive). In case (i) 𝒫^N w ≥ 0; in case (ii)
𝒫^N w → 0 pointwise by Lemma TL(d). Let N → ∞ (monotone convergence on the left). ∎

**(i) Quadratic δ-certificate (Proposition C1).** Let a, b ∈ B(X), c > 0 and δ : X → (0, ∞). If, on X and for every e ∈ E,

    (C1-b)  b ≥ 1/(2c) + δ + K_e b,
    (C1-a)  a ≥ c/2 + K_e a + K_e^{(2)} b + (K_e^{(1)} b)² / δ,

then w(x,μ) := a(x) + b(x)μ² satisfies w ≥ |μ| + 𝒫_e w, hence A1^LR(e) ≤ a(a) for all e ∈ E.
*Proof.* Expand: (𝒫w)(x,μ) = (Ka)(x) + μ²(Kb)(x) + 2μ(K^{(1)}b)(x) + (K^{(2)}b)(x), because
∫_A b(T)(μ + s)² q dν = μ²Kb + 2μK^{(1)}b + K^{(2)}b. Use |μ| ≤ c/2 + μ²/(2c) ((√c − |μ|/√c)² ≥ 0) and
2μ(K^{(1)}b) ≤ 2|μ||K^{(1)}b| ≤ δμ² + (K^{(1)}b)²/δ ((√δ|μ| − |K^{(1)}b|/√δ)² ≥ 0). Then
|μ| + 𝒫w ≤ [c/2 + Ka + K^{(2)}b + (K^{(1)}b)²/δ] + μ²[1/(2c) + δ + Kb] ≤ a + bμ² by (C1-a), (C1-b). Since
b ≥ 1/(2c) > 0 and a ≥ c/2 > 0 (K^{(2)} ≥ 0 because its weight s² ≥ 0 and b ≥ 0; K ≥ 0), w ≥ 0 and Lemma C0(i) applies.
Killing: 𝒫 integrates only over the survival set, i.e. dead paths contribute 0 to both sides, consistent with V1. ∎

*Reduction to linear supersolution inequalities on the original state.* (C1-b) is a Lemma-T inequality for K_e with
constant forcing β := 1/(2c) + δ (for constant δ: b = βW with any whole-kernel supersolution W works, and the minimal
b is βR1). (C1-a) is a Lemma-T inequality for K_e with the forcing c/2 + K^{(2)}b + (K^{(1)}b)²/δ, computed from b
by one application of the moment kernels K^{(1)}, K^{(2)} (CUSUM: Gaussian moments of order 1 and 2 of the increment).
With the minimal solutions (δ constant) the bound is

    B1(c, δ) = (c/2)Λ + β (R K^{(2)} R1)(a) + (β²/δ) (R (K^{(1)}R1)²)(a),   β = 1/(2c) + δ.

**(i′) Full quadratic certificate (linear term allowed).** w = a + b1 μ + b2 μ² (b1 of any sign). With g_c :=
c/2 + μ²/(2c) ≥ |μ|, w ≥ g_c + 𝒫w holds iff for every x the quadratic A_xμ² + B_xμ + C_x ≥ 0 for all μ, where

    A_x = b2 − 1/(2c) − K b2,   B_x = b1 − K b1 − 2K^{(1)} b2,   C_x = a − c/2 − K a − K^{(1)} b1 − K^{(2)} b2,

i.e. A_x ≥ 0, C_x ≥ 0, B_x² ≤ 4A_xC_x. (Expansion: ∫ w(T, μ+s) q = Ka + μKb1 + K^{(1)}b1 + μ²Kb2 + 2μK^{(1)}b2 + K^{(2)}b2.)
Then V1 ≤ w by Lemma C0(ii) (w is quadratic with bounded coefficients). The exact solution A = B = C = 0 is
b2 = R1/(2c), b1 = (1/c) R K^{(1)} R1, a = R[c/2 + K^{(1)} b1 + K^{(2)} b2], and w_exact(a, 0) = cΛ/2 + S2/(2c) with
S2 := E_a[Σ_{n<τ} M_n²] (w_exact = Σ𝒫^n g_c). Optimising c: **√(Λ S2)** (global Cauchy–Schwarz).
*Dominance:* every δ-certificate of (i) is feasible for (i′) (A_x ≥ δ-slack, B_x = −2K^{(1)}b, C_x ≥ (K^{(1)}b)²/δ,
so B² ≤ 4AC), hence ≥ the minimal g_c-supersolution w_exact: **(i′)-exact ≤ (i) at the same c**.
*State-dependent c.* With c = c(x) the forcing becomes c(x)/2 + μ²/(2c(x)) and the exact value is
Σ_y [c(y)U0(y)/2 + U2(y)/(2c(y))], U0(y) := E_a Σ_{n<τ} 1{X_n = y}, U2(y) := E_a Σ_{n<τ} M_n² 1{X_n = y}; the optimum
is **Σ_y √(U0(y) U2(y))** (per-state Cauchy–Schwarz) ≤ √(Λ S2).

**(ii) A2 certificates.** Target V2(x, μ, ν) = E_x Σ_{n<τ}|(μ+M_n)² + ν + N_n|, A2^LR = V2(a, 0, 0).
* (ii-a) *Triangle / linear:* |M² + N| ≤ M² + |N| gives A2^LR ≤ S2 + T_N with T_N := E_a Σ_{n<τ} Σ_{k≤n} |t_k|
  = (R|K_t|R1)(a) (|K_t| has weight |t|; CUSUM: T_N = E_a[τ(τ−1)/2]). Both are *exact linear* functionals (quadratic
  ansatz with polynomial forcing μ², no absolute value) — certified by Lemma-T inequalities with Lemma C0(ii).
* (ii-b) *Quartic Cauchy–Schwarz:* |y| ≤ c/2 + y²/(2c) with y = (μ+M)² + ν + N. The ansatz
  w = Σ_{i+2j≤4} b_{ij}(x) μ^i ν^j is mapped into itself by 𝒫 (weights s^i t^j), giving a triangular linear system
  (ordered by i + 2j); the exact value is cΛ/2 + Q4/(2c), Q4 := E_a Σ_{n<τ}(M_n² + N_n)², optimum √(Λ Q4); per-state
  version Σ_y √(U0(y) Q4(y)). A block certificate needs the discriminant-type positivity of a quartic in μ at each x
  (sum-of-squares or the δ-splitting of each odd cross term, exactly as in (i)).
* (ii-c) Per-(n, y) Cauchy–Schwarz (below) with the quartic moment.

**(iii) Alternative: finite horizon + certified tail.** For a horizon H,

    A1^LR = Σ_{n<H} E_a[|M_n|; n<τ] + E_a[V1(X_H, M_H); H < τ].

Head: E_a[|M_n|; X_n = y, n<τ] ≤ √(u0_n(y) u2_n(y)), where u_j,n(y) := E_a[M_n^j; X_n = y, n<τ] obey the *linear
forward recursion* u_{j,n+1}(dy) = Σ_{i≤j} C(j,i) ∫ u_{i,n}(dx) K^{(j−i)}(x, dy) (u_{0,0} = δ_a, u_{j,0} = 0 for j ≥ 1).
Tail: by Lemma C0 and any certificate w = a + b1μ + b2μ² of (i)/(i′),
E_a[V1(X_H, M_H); H<τ] ≤ Σ_y [a(y)u_{0,H}(y) + b1(y)u_{1,H}(y) + b2(y)u_{2,H}(y)] (an exact linear functional of the
time-H moments). A fully a-priori tail is Σ_{n≥H} √(P(n<τ) E[M_n²; n<τ]) ≤ Σ_{n≥H} √(C_Wθ^n · n² m_2 C_W² θ^{n−1})
(Lemma TL), a geometric series. The per-(n,y) CS head is always ≤ the per-state CS on the same horizon.
For A2 the same with u over (M, N)-moments up to weighted degree 4.

**(iv) Rigorous lower bound (validation handle, not a certificate).** Hölder on each (n, y):
E[|M_n|; X_n = y] ≥ u_{2,n}(y)^{3/2} / u_{4,n}(y)^{1/2}; summing over n < H gives a rigorous lower bound on A1^LR.
Used only to (a) measure certificate slack and (b) prove LR > Dv′ in Example E2.

**Regenerative versions.** Every item applies verbatim with K̂ (taboo kernel, killed on entering a) and the taboo
supersolution, giving certified L1, L2 and hence ρ1, ρ2 for Theorem LR-3.

**Cost for CUSUM (expectation, not measured).** (i): two Lemma-T-type solves on the 2-D state (b is βW, so one new
solve for a) plus one application each of K^{(1)} and K^{(2)} (Gaussian first/second moments over the same cells as
kernel_apply) — O(1)× the cost of the existing whole-kernel ARL supersolution. (i′): three solves. (ii-a): two
solves. (iii): H forward density propagations of 3 (A1) or 6–9 (A2) moment densities. Block uniformity: the same
with interval-drift enclosures.

## §7 Exact finite-state validation (pointer to lr_fsm.py and C1LR_*.json)

Producer: `lr_fsm.py` (this directory; stdlib fractions only, import guard installed, guard_drift at every entry,
ledger entries class SYNTHETIC_VALIDATION, cells_touched = []). Outputs: `NS/validation/C1LR_FSM_VALIDATION.json`
(`--sets`), `NS/validation/C1LR_EXAMPLES.json` (`--examples`, `--example-e1dp`), `NS/validation/C1LR_BLOCK.json`
(`--block`). Every number quoted below is a field of those files (path given); re-running the flag regenerates it.

**Declared sets (PROGRESS.md, before running).** V1: `random_family(n = 6 + seed%4, seed, e_range=(0,1/4),
kill=1/20)`, seeds 1..12; V2: same with kill = 1/5; e = 1/8. Examples: ε-ladder {1/10,…,1/160} at e = 0. Block: V1
seeds 1..8 on [0, 1/4].

**What is computed exactly (per seed; code line refs are function names in lr_fsm.py).**
* `Chain.moment_totals`: U_{ij}(y) = E_a Σ_{n<τ} M_n^i N_n^j 1{X_n = y} by the row-vector triangular system
  U_{ij}(I − K) = δ_a 1{ij=00} + Σ_{(i',j')<(i,j)} C(i,i')C(j,j') U_{i'j'} K_{s^{i−i'}t^{j−j'}} (the moment
  recursion of §cert (iii), summed over n).
* `identity_checks`: Theorem LR-1 as *exact vector equalities* U_{10} = (RK1R)[a,·] and U_{20} + U_{01} = (∂²R)[a,·];
  independent checks — (1) symmetric difference quotients of e ↦ R_e (h = 10⁻⁵, exact rationals), (2) brute-force path
  enumeration to horizon 3–4 against the forward recursion `Chain.forward_moments`; negative controls — first-order
  score sign flipped, and t sign flipped, must break the equalities.
* `truth_pm_g`: A1_true = ‖(RK1R)[a,·]‖₁, A2_true = ‖(∂²R)[a,·]‖₁, PM1, PM2 (state level, |K1|, |K2| entrywise),
  Lemma G with C = ‖R‖, k_i = ‖K_i‖ at the point.
* `lr_bounds_A1`: (i) δ-certificate over the declared (c, δ) grid; (i′) full quadratic, global c; (i′) per-state c(y);
  (iii) horizon-12 per-(n,y) CS head + certified tail; (iv) per-(n,y) Hölder lower bound (horizon 80). Every
  certificate is checked by `check_quadratic_cert` (exact coefficient test A ≥ 0, C ≥ 0, B² ≤ 4AC per state).
  Checker negative controls: a scaled by (1 − 10⁻³); constant term c/4 instead of c/2; certificate scaled below the
  rigorous LR lower bound; b1 perturbed by 10⁻⁶ at the atom — each must be rejected.
* `lr_bounds_A2`: (ii-a) triangle S2 + T_N and (ii-b) per-state quartic Cauchy–Schwarz (exact values of the minimal
  solutions); Jensen lower bound Σ_{n,y}|E[M_n² + N_n; X_n = y]|.
* `rlr_and_dv`: taboo chain (atom column removed), τ_a, C_T = ‖Ĝ‖, κ_i = ‖K̂_i‖, D, D′, D″ exactly (h = Ĝk_a and
  its e-derivatives); Dv′ **with exact point inputs** (Ā = Λ, τ = τ_a, D_lo = D, δ_i = |D^{(i)}|/D — the most
  favourable possible Dv′); RLR (Theorem LR-3) with certified L1, L2; checks Λ = τ_a/D, the regenerative quotient
  identities for ∂R and ∂²R rows (exact), ν′ = (ĜK̂1Ĝ)[a,·], and PM-hat ≤ Dv′ factors.

**Results (C1LR_FSM_VALIDATION.json, `V1.summary`, `V2.summary`).**
* 24/24 seeds: both identities exact; difference-quotient and path-enumeration checks agree; both sign-flip negative
  controls detected (`identity_counts`).
* 24/24: every certificate passes the exact checker; all four planted non-supersolutions rejected, for the whole-kernel
  and the excursion chain (`checker_negative_controls_detected*`); closed-form values match the solved certificates
  (`formula_matches`); regenerative identities exact (`regenerative_checks`); PM-hat ≤ Dv′ factor (`PMhat_le_Dv_counts`).
* Chain true ≤ LR_cert ≤ PM ≤ G: 24/24 for A1 and for A2 (`chain_A1_holds`, `chain_A2_holds`).
* Ratios to the truth (`A1_ratios`, `A2_ratios`; Λ ∈ [2.7, 8.4] on these fixtures): PM/LR_cert ≈ 1.5–2.4 (A1) and
  1.2–3.5 (A2); the rigorous LR lower bound itself is ≈ 1–7.6× (median ≈ 2×) above A1_true — **about half of the
  true-vs-PM slack is between-path cancellation that no |M_n|-type bound can recover**; RLR beats exact-input Dv′ on
  24/24 seeds (A1 by 1.7–3.0×, A2 by 1.4–3.1×); at these small Λ the whole-kernel LR certificate is also below Dv′
  24/24, and RLR is below the whole-kernel LR certificate for A1 on 24/24.

**Examples (C1LR_EXAMPLES.json).** E2 (state-level, two states): the rigorous LR lower bound ≈ 0.40 Λ^{3/2}, exact
Dv′ ≈ 1.07 Λ, ratio 1.33 → 4.69 over Λ = 10 … 160; RLR stays below Dv′. E1d (declared) showed *no* separation — a
design error: its killing derivative is O(1), so δ1 ∝ Λ and Dv′ = true ∝ Λ²; the theory predicts ratio ∝ √Λ/δ1, so this
is the correct outcome (preserved, `E1d_note`). E1d′ (faithful analogue, δ1 = 1, declared before running): Dv′ = true
= Λ exactly, noise-level LR lower bound ≈ 0.40 Λ^{3/2}, ratio up to 5.10 at Λ = 160 (`E1d_prime`).

**Block uniformity (C1LR_BLOCK.json).** Setup:
* block [0, 1/4] on V1 seeds 1..8;
* each certificate is a single e-free (a, b1, b2, c), with per-state c from the midpoint;
* b2 = (1+η)R_up[1/(2c)], b1 = the exact midpoint solution, and a with the discriminant slack;
* the checker `check_block_cert` tests A ≥ 0, C ≥ 0 and B² ≤ 4AC per state on each of m sub-intervals, using exact
  interval-Horner enclosures.

Results:
* **Baseline (η = 1/100, m = 8, `records`).** All 8 pass. LB(e) ≤ block bound on the grid e = k/32. The overhead over
  the largest pointwise certificate is 1.55–3.43×, and for seed 1 the block LR exceeds the block PM.
* **Declared variants (η ∈ {1/100, 1/10, 1/2, 2} × m ∈ {8, 32}, `variant_records`).** All 64 pass. The best variant has
  overhead 1.44–1.94×, and block LR ≤ block PM ≤ block G holds 8/8. The Λ-envelope inflation is 1.05–1.10×.
* **Negative controls.**
  * The "slack = 0" control turned out *not* to be guaranteed invalid: it passed, legitimately, in 2 of the 64 variants
    (seed 7, η = 2). That was a design error, and it is preserved.
  * The guaranteed-invalid control is a certificate scaled below the rigorous LR lower bound (`guaranteed_invalid_controls`).
    It is rejected 8/8.
