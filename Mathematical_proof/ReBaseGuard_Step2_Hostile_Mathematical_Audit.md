# ReBaseGuard — Step 2 Hostile Mathematical Audit

**Date:** 2026-08-19  
**Audit role:** adversarial mathematical reviewer  
**Scope:** compare the official ReBaseGuard mathematical derivation against the independent blind re-derivation, looking specifically for shared hidden assumptions, incorrect stopping-time arguments, sign/indexing mistakes, Bellman reward errors, and overclaiming.

## Executive verdict

**STEP-2 HOSTILE MATHEMATICAL AUDIT: PASS WITH CORRECTIONS**

I found **no fatal mathematical flaw** in the Level-3 CUSUM core.

The following central chain survives the hostile comparison:

\[
F_1'(0)=1-\Gamma,\qquad
\Gamma=E_0[Z_\tau T_\tau],
\]

for the symmetric two-sided Gaussian CUSUM with the stated stopping-time regularity; and independently,

\[
\Gamma=b(0,0),
\]

where \(a,b\) solve

\[
a=Ka+r_a,\qquad
b=Kb+K_z a+r_b.
\]

The certified numerical statement \(\Gamma>2\) therefore connects to the intended mathematical quantity, subject to the separate proof-to-code correspondence audit planned for Step 3.

However, the audit found **two nonfatal errors/inaccuracies in the blind report** and **one place where the official proof should be replaced by a cleaner lemma-level argument**:

1. The blind report's one-sided-CUSUM discussion incorrectly says that
   \(E_0[Z_\tau]E_0[T_\tau]\neq 0\) and therefore raw product and covariance differ.  
   Under the stated integrability conditions, **Wald gives \(E_0[T_\tau]=0\) for any such stopping time**, including the one-sided detector. Thus the exact raw product and covariance are equal even there. The simulated discrepancy is finite-sample error, not a mathematical distinction.
2. The blind report states numerically that
   \(\sup_s K\mathbf 1(s)\approx0.99953\) for \(h=5,k=0.5\).  
   Since the origin is in the state space,
   \[
   (K\mathbf 1)(0,0)=P(|Z|<5.5)\approx0.99999996,
   \]
   so that numerical value is incorrect. The **theorem \(\|K\|_\infty<1\) remains correct**, but the quoted numerical check is not.
3. The official Phase-2C change-of-measure/UI justification is directionally correct but unnecessarily compressed. I give below a direct stopped-density decomposition and an explicit exponential-domination lemma that closes the delicate differentiation step without relying on a vague optional-stopping/UI statement.

These corrections do **not** affect the Level-3 CUSUM conclusion.

---

## 1. Materials audited

The hostile comparison used the following independent sources:

### Official ReBaseGuard derivation
- `rebaseguard_phase2c.md`
  - regularity conditions
  - Gaussian stopped-score identity
  - mixed-reuse theorem
  - local-stability scope
- `rebaseguard-proof/proofs/derivation.md`
  - exact CUSUM state reduction
  - continuation geometry
  - Bellman/Fredholm equations
  - absorbing rewards
  - contraction/resolvent argument
  - residual propagation
- `rebaseguard-proof/proofs/ReBaseGuard_Certified_Lemma_Proof_Report.md`
  - theorem target
  - certified continuum interpretation
  - explicit claim boundary

### Independent blind derivation
- `blind_rederivation_report.md`

The blind report was generated from the raw model specification without being given the existing proof chain.

---

# Gate A — Probability model and parameterization

## Claim

The physical model is

\[
X_t\overset{iid}{\sim}N(0,1),\qquad
Z_t=X_t-e,
\]

so under the residual-coordinate law \(Q_e\),

\[
Z_t\overset{iid}{\sim}N(-e,1).
\]

The detector parameters \(k,h\) remain fixed while \(e\) varies, and the stopping rule is the **same measurable path functional of the residual sequence** under every \(Q_e\).

## Audit

This is the load-bearing parameterization behind the entire score argument.

The official derivation and blind derivation agree exactly here.

The distinction is important: in physical \(X\)-coordinates the detector thresholding depends on the reference \(e\), but after changing to residual coordinates the detector map itself is fixed and only the measure changes.

No hidden derivative of \(k,h\), the recursion, or \(\tau(\cdot)\) therefore appears.

## Verdict

**PROVED WITH EXPLICIT ASSUMPTION**

The paper should explicitly state:

> The local parameter \(e\) changes the law of the residual path but not the detector functional applied to that path.

If the detector were re-tuned as a function of \(e\), the clean stopped-score formula would need additional terms.

---

# Gate B — Stopped change of measure

For fixed \(t\),

\[
\frac{dQ_e}{dQ_0}\Big|_{\mathcal F_t}
=
M_t(e)
=
\exp\!\left(-eT_t-\frac{e^2t}{2}\right),
\qquad
T_t=\sum_{j=1}^t Z_j.
\]

The sign is correct because \(Q_e\) has mean \(-e\).

The official Phase-2C proof phrases the stopped identity through optional stopping and uniform integrability. The blind proof gives a cleaner route.

For any nonnegative or integrable \(\mathcal F_\tau\)-measurable \(G\),

\[
E_e[G]
=
\sum_{t\ge1}E_e[G1_{\{\tau=t\}}]
=
\sum_{t\ge1}E_0[G1_{\{\tau=t\}}M_t(e)].
\]

On \(\{\tau=t\}\), \(M_t(e)=M_\tau(e)\), so

\[
\boxed{
E_e[G]=E_0[G M_\tau(e)].
}
\]

This derivation uses the finite-time Radon–Nikodym derivative and decomposition by the disjoint events \(\{\tau=t\}\). It does **not** require invoking optional stopping of the likelihood martingale.

Taking \(G=1\) gives

\[
E_0[M_\tau(e)]=Q_e(\tau<\infty)=1
\]

once \(\tau<\infty\), \(Q_e\)-a.s.

## Verdict

**PROVED**

Recommendation: use this decomposition in the final manuscript instead of making optional stopping of \(M_t(e)\) the main route.

---

# Gate C — The analytically delicate step: differentiation under expectation

This is the strongest legitimate concern raised by the blind reviewer.

We need to justify

\[
\frac{d}{de}
E_0\!\left[
Z_\tau
e^{-eT_\tau-e^2\tau/2}
\right]
\Big|_{e=0}
=
-E_0[Z_\tau T_\tau].
\]

The earlier reports appeal to geometric tails plus Gaussian moments. That idea is correct, but it can be closed more explicitly.

## A direct domination lemma

Let

\[
H=h+k.
\]

Under \(Q_0\), define

\[
N=\inf\{t\ge1:Z_t>H\}.
\]

Because \(S_{t-1}^+\ge0\), whenever \(Z_t>h+k\),

\[
S_t^+
=
\max(0,S_{t-1}^++Z_t-k)
>
h.
\]

Therefore, pathwise,

\[
\boxed{\tau\le N.}
\]

Let \(Z\sim N(0,1)\). For \(\lambda\ge0\), define

\[
A(\lambda)
=
E[e^{\lambda|Z|}1_{\{Z\le H\}}],
\qquad
B(\lambda)
=
E[e^{\lambda|Z|}1_{\{Z>H\}}].
\]

At \(\lambda=0\),

\[
A(0)=P(Z\le H)<1.
\]

By continuity, there exists \(\lambda_0>0\) such that

\[
A(\lambda)<1
\quad
\text{for }0\le\lambda<\lambda_0.
\]

Using the definition of the first forcing time \(N\),

\[
\begin{aligned}
E\exp\!\left(
\lambda\sum_{j=1}^{N}|Z_j|
\right)
&=
\sum_{n\ge1}
A(\lambda)^{n-1}B(\lambda) \\
&=
\frac{B(\lambda)}{1-A(\lambda)}
<\infty.
\end{aligned}
\]

Since \(\tau\le N\),

\[
|T_\tau|
\le
\sum_{j=1}^{\tau}|Z_j|
\le
\sum_{j=1}^{N}|Z_j|,
\]

and likewise

\[
|Z_\tau|
\le
\sum_{j=1}^{N}|Z_j|,
\qquad
\tau\le N.
\]

Hence the random vector

\[
(|Z_\tau|,\ |T_\tau|,\ \tau)
\]

has the small exponential moments required for a local dominating function.

For sufficiently small \(\delta>0\),

\[
|Z_\tau|(|T_\tau|+\delta\tau)
e^{\delta|T_\tau|+\delta^2\tau/2}
\]

is integrable.

Therefore dominated differentiation is valid in a neighbourhood of \(e=0\).

## Consequence

\[
\boxed{
F_1'(0)
=
1-E_0[Z_\tau T_\tau].
}
\]

## Verdict

**PROVED AFTER EXPLICIT LEMMA CLOSURE**

This is not a mathematical defect. It is a presentation/rigor improvement.

The final manuscript should promote this argument to a named lemma rather than saying only “geometric tails imply UI.”

---

# Gate D — Raw product, covariance, Wald, and symmetry

This comparison exposed a useful correction.

The differentiated formula is fundamentally the **raw-product formula**

\[
F_1'(0)
=
1-E_0[Z_\tau T_\tau].
\]

For any integrable stopping time \(\tau\) of iid centered increments,

\[
E_0[T_\tau]=0
\]

by Wald's first identity.

Therefore

\[
\operatorname{Cov}(Z_\tau,T_\tau)
=
E_0[Z_\tau T_\tau]
-
E_0[Z_\tau]E_0[T_\tau]
=
E_0[Z_\tau T_\tau].
\]

Thus the covariance form does **not** require reflection symmetry.

Reflection symmetry is instead needed to establish

\[
E_0[Z_\tau]=0
\]

and consequently

\[
F(0)=0.
\]

This distinction agrees with the later Phase-4 pre-gate analysis and should be the canonical formulation.

## Error found in the blind report

The blind report's one-sided-CUSUM falsification section says that in the asymmetric example

\[
E_0[Z_\tau]E_0[T_\tau]\neq0
\]

and therefore raw product and covariance differ.

That is false at theorem level: provided \(E\tau<\infty\),

\[
E_0[T_\tau]=0
\]

still holds for the one-sided detector.

Any small observed raw/covariance discrepancy in Monte Carlo is finite-sample error.

This does **not** affect the symmetric two-sided result or the derivative theorem.

## Verdict

- Raw derivative identity: **PROVED**
- Covariance rewrite: **PROVED via Wald**
- \(E_0[Z_\tau]=0\): **PROVED via reflection**
- \(F(0)=0\): **PROVED via reflection**

---

# Gate E — Reflection symmetry and fixed-point semantics

Under \(Q_0\), the transformation

\[
Z_t\mapsto -Z_t
\]

swaps the two CUSUM arms:

\[
S_t^+\leftrightarrow S_t^-,
\]

while preserving

\[
\tau.
\]

Hence

\[
Z_\tau\mapsto-Z_\tau
\]

and therefore

\[
E_0[Z_\tau]=0.
\]

Thus

\[
F(0)=0.
\]

The blind report is also correct to distinguish the deterministic mean map from the actual stochastic recursion.

What is proved is:

\[
e=0
\]

is a fixed point of

\[
e_{j+1}=F(e_j),
\]

not that the random update

\[
e_{j+1}=e_j+Z_{\tau_j}
\]

stays at zero.

## Verdict

**PROVED**

The phrase “zero-reference fixed point” should always be qualified as the fixed point of the **mean transition map / deterministic skeleton** when there is risk of ambiguity.

---

# Gate F — Mixed reuse

For

\[
e_{\mathrm{next}}
=
\rho(e+Z_\tau)
+
(1-\rho)W,
\]

where \(W\) has

\[
E[W]=0
\]

and its distribution is independent of \(e\),

\[
F_\rho(e)
=
\rho F_1(e).
\]

Therefore

\[
\boxed{
F_\rho'(0)
=
\rho F_1'(0).
}
\]

No approximation is involved.

Required assumptions:

1. \(W\) has mean zero;
2. its law is independent of \(e\);
3. it is not adaptively coupled to the stopping-selected cycle;
4. \(\rho\) is fixed rather than data- or \(e\)-dependent.

## Verdict

**PROVED WITH EXPLICIT ASSUMPTIONS**

---

# Gate G — Local stability claim

Given

\[
F(0)=0,\qquad F'(0)<-1,
\]

standard one-dimensional local dynamics imply that the zero fixed point of the deterministic map is locally repelling and orientation reversing.

For the mixed map,

\[
F_\rho'(0)
=
\rho(1-\Gamma).
\]

When \(\Gamma>2\),

\[
|1-\Gamma|=\Gamma-1>1,
\]

so the local threshold is

\[
\boxed{
\rho_c=\frac1{\Gamma-1}.
}
\]

Then

\[
0\le\rho<\rho_c
\]

is locally stable and

\[
\rho>\rho_c
\]

is locally unstable.

At exactly \(\rho=\rho_c\), the derivative has modulus one and the linear test is inconclusive.

## What does NOT follow

The following are not consequences of \(F'(0)<-1\):

- existence of a period-2 orbit;
- period-doubling bifurcation;
- uniqueness/stability of such an orbit;
- bimodality of a stochastic invariant law;
- ARL degradation;
- stochastic oscillation theorem.

Those remain separate empirical or future-theory claims.

## Verdict

**PROVED, CLAIM SCOPE MUST REMAIN LOCAL**

---

# Gate H — Bellman/Fredholm reduction

Let the live CUSUM state be

\[
s=(p,m)=(S_t^+,S_t^-)
\]

and let

\[
x=T_t.
\]

Define

\[
H(s,x)
=
E_0[Z_\tau T_\tau\mid s,x].
\]

Because future innovations depend on the past only through \(s\), while \(x\) enters the terminal cumulative sum additively,

\[
H(s,x)=a(s)x+b(s).
\]

For one innovation \(z\),

\[
q(s,z)
=
\left(
\max(0,p+z-k),
\max(0,m-z-k)
\right).
\]

An up-alarm occurs when

\[
z\ge h+k-p=:u,
\]

and a down-alarm occurs when

\[
z\le m-h-k=:\ell.
\]

Hence continuation is exactly

\[
\boxed{\ell<z<u.}
\]

On absorption,

\[
Z_\tau=z,\qquad
T_\tau=x+z,
\]

so the exact terminal reward is

\[
\boxed{z(x+z)=zx+z^2.}
\]

First-step conditioning yields

\[
a=Ka+r_a,
\qquad
b=Kb+K_z a+r_b.
\]

with

\[
(Kf)(s)=
\int_\ell^u f(q(s,z))\phi(z)\,dz,
\]

\[
(K_zf)(s)=
\int_\ell^u zf(q(s,z))\phi(z)\,dz.
\]

The absorbing moments are

\[
\boxed{
r_a=\phi(u)-\phi(\ell)
}
\]

and

\[
\boxed{
r_b
=
u\phi(u)+1-\Phi(u)
+
\Phi(\ell)-\ell\phi(\ell).
}
\]

The blind derivation instead writes the down threshold as \(-v\), where

\[
v=h+k-m,
\qquad
\ell=-v.
\]

Its formulas

\[
r_a=\phi(u)-\phi(v)
\]

and

\[
r_b=
u\phi(u)+\bar\Phi(u)
+
v\phi(v)+\bar\Phi(v)
\]

are exactly equivalent because \(\phi\) is even and

\[
\Phi(-v)=\bar\Phi(v).
\]

## Verdict

**CORRECT**

No sign, threshold, reset, overshoot, or terminal-reward mismatch was found.

---

# Gate I — \(\Gamma=b(0,0)\)

At cycle start,

\[
s=(0,0),\qquad x=T_0=0.
\]

Therefore

\[
\Gamma
=
E_0[Z_\tau T_\tau]
=
H((0,0),0)
=
b(0,0).
\]

No additional term appears.

This agrees independently between the official derivation and the blind derivation.

## Verdict

**CORRECT**

The off-by-one warning remains important: the target is \(T_\tau\), including the alarm-causing increment.

---

# Gate J — Reachable-state geometry

The official derivation uses the reachable continuation complex consisting of:

- both coordinate axes below \(h\);
- the interior triangle
  \[
  p>0,\quad m>0,\quad p+m<h-2k.
  \]

This is valid.

If both arms remain positive through an update,

\[
p'+m'=p+m-2k.
\]

Entering the interior from an axis similarly gives a sum strictly below \(h-2k\), while resets return to an axis.

For \(k=0.5,h=5\),

\[
p+m<4
\]

in the reachable interior.

## Verdict

**CORRECT**

Using a strict superset would also be safe for a proof; under-coverage would not be.

---

# Gate K — Existence and uniqueness

The official certificate uses a rigorous block-contraction/resolvent argument.

The blind derivation independently observes that on the full square \(C=[0,h)^2\),

\[
(K\mathbf 1)(s)
=
P_s(\text{continue one step})
\le
P(|Z|<h+k)
<1.
\]

Hence

\[
\|K\|_\infty<1
\]

for finite \(h,k\), giving existence and uniqueness by a direct Neumann series.

This is mathematically correct, though numerically far too weak for a sharp proof error budget.

### Numerical error found in the blind report

The blind report quotes

\[
\sup_s(K\mathbf1)(s)\approx0.99953
\]

at \(h=5,k=0.5\).

That cannot be correct because at the origin

\[
(K\mathbf1)(0,0)
=
P(-5.5<Z<5.5)
\approx0.99999996.
\]

The theorem remains correct:

\[
P(|Z|<5.5)<1.
\]

Only the quoted numerical value is wrong.

The official stronger multi-step contraction remains the appropriate route for the certified error bound.

## Verdict

**EXISTENCE/UNIQUENESS PROVED BY TWO INDEPENDENT ROUTES**

---

# Gate L — General arbitrary-stopping-time result

For a parameter-invariant stopping time \(\tau\) with sufficient local exponential integrability and

\[
W_{\tau,m}
=
\frac1m\sum_{r=0}^{m-1}Z_{\tau-r},
\]

the same stopped-density derivation gives

\[
F'(0)
=
1-E_0[W_{\tau,m}T_\tau].
\]

Since Wald gives

\[
E_0[T_\tau]=0,
\]

this becomes

\[
\boxed{
F'(0)
=
1-\operatorname{Cov}_0(W_{\tau,m},T_\tau).
}
\]

No CUSUM recursion or reflection symmetry is needed for this derivative identity.

CUSUM-specific ingredients are instead needed to:

- establish its detector-specific regularity cheaply;
- obtain a zero fixed point through reflection symmetry;
- compute/certify the detector-specific value of \(\Gamma\).

For \(m>1\), one must additionally specify what happens if \(\tau<m\) (minimum dwell or another fixed padding/window convention).

## Verdict

**PROVED UNDER EXPLICIT REGULARITY / WINDOW-DEFINITION CONDITIONS**

---

# Gate M — Exponential-family extension

The blind report's extension

\[
\frac{d}{d\theta}E_\theta[G_\theta]\Big|_{\theta_0}
=
E[\dot G]
+
\operatorname{Cov}(G,L_\tau)
\]

is structurally correct under suitable stopped-likelihood differentiability and domination conditions, with

\[
L_\tau
=
\sum_{t\le\tau}\ell(Z_t).
\]

This is not needed for the current Level-3 CUSUM theorem.

The exact regularity assumptions depend on the family and parameterization, so the extension should remain a **conditional theorem**, not be advertised as a fully universal result.

## Verdict

**CONDITIONAL / NON-CORE**

---

# Cross-proof mismatch table

| Topic | Official derivation | Blind derivation | Hostile-audit conclusion |
|---|---|---|---|
| Residual law | \(N(-e,1)\) | same | PASS |
| Likelihood sign | \(-eT_\tau-e^2\tau/2\) | same | PASS |
| Stopped measure change | optional-stopping/UI framing | \(\{\tau=t\}\) decomposition | use blind decomposition; cleaner |
| Differentiation domination | geometric tail + moment argument | geometric tail + exponential moments | correct idea; explicit lemma supplied here |
| \(E[T_\tau]=0\) | symmetry in Phase-2C | Wald | Wald is canonical; symmetry is true but unnecessary |
| \(E[Z_\tau]=0\) | reflection | reflection | PASS |
| Raw vs covariance | covariance after centering | raw first, covariance via \(E[T]=0\) | raw-first formulation preferred |
| Mixed reuse | exact linearity | exact linearity | PASS |
| Mean fixed point | reflection | reflection | PASS |
| Stability | local threshold | local repulsion only | use narrower blind wording |
| Continuation interval | \((m-h-k,h+k-p)\) | \((-v,u)\) | exactly equivalent |
| Terminal reward | \(z(x+z)\) | same | PASS |
| \(r_a,r_b\) | \(\ell,u\) notation | \(u,v\) notation | exactly equivalent |
| Coupling | \(K_z a\) | \(K_z a\) | PASS |
| \(\Gamma=b(0,0)\) | yes | yes | PASS |
| Existence | block contraction | one-step contraction | both valid |
| General score theorem | later Phase-4 pre-gate | independently rederived | PASS with regularity |
| Period-2/bimodality | not theorem-level in current clean framing | explicitly rejected as implication | must remain empirical |

---

# Findings by severity

## Fatal errors

**None.**

## Mathematical corrections required

### Correction 1 — one-sided raw/covariance claim in blind report

Replace the claim that raw product and covariance differ for the one-sided CUSUM.

Correct statement:

\[
E_0[T_\tau]=0
\]

by Wald under finite \(E\tau\), so

\[
E_0[Z_\tau T_\tau]
=
\operatorname{Cov}_0(Z_\tau,T_\tau)
\]

even if

\[
E_0[Z_\tau]\ne0.
\]

The one-sided example correctly falsifies \(F(0)=0\), **not** the raw-to-covariance equality.

### Correction 2 — one-step continuation probability numerical value

Delete the blind report's value `0.99953` for the \(h=5\) one-step operator norm.

The exact theorem needed is only

\[
\|K\|_\infty
\le
P(|Z|<5.5)
<1.
\]

The rigorous certificate should continue to use the stronger block contraction for error propagation.

## Proof strengthening required

### Lemma — stopped Gaussian exponential domination

Insert the explicit forcing-time argument from Gate C into the mathematical appendix.

This closes the main regularity concern without relying on a hand-wavy “standard UI” statement.

---

# Canonical Level-3 theorem after this audit

A defensible theorem statement is:

> **Theorem (local instability under stopping-selected CUSUM reuse).**  
> Let \(Z_t\) be iid \(N(-e,1)\), and let \(\tau\) be the post-update inclusive alarm time of the symmetric two-sided CUSUM with fixed \(k,h\), initialized at zero. For \(m=1\) full stopping-selected reuse,
> \[
> F(e)=e+E_e[Z_\tau].
> \]
> Then \(F\) is differentiable at \(e=0\), \(F(0)=0\), and
> \[
> F'(0)=1-\Gamma,
> \qquad
> \Gamma=E_0[Z_\tau T_\tau].
> \]
> Moreover,
> \[
> \Gamma=b(0,0),
> \]
> where the unique bounded solution \((a,b)\) satisfies
> \[
> a=Ka+r_a,\qquad
> b=Kb+K_za+r_b
> \]
> with the exact CUSUM continuation operator and Gaussian tail rewards derived above.
>
> For \(k=0.5,h=5\), the separate computer-assisted continuum certificate proves
> \[
> \Gamma>2.
> \]
> Therefore
> \[
> F'(0)<-1,
> \]
> so \(e=0\) is a locally repelling, orientation-reversing fixed point of the deterministic mean transition map.
>
> Under affine mixed reuse with an \(e\)-independent mean-zero fresh component,
> \[
> F_\rho'(0)=\rho F_1'(0),
> \]
> and the local critical reuse fraction is
> \[
> \rho_c=\frac1{\Gamma-1}\in(0,1).
> \]
>
> No period-2, bifurcation, bimodality, invariant-law, or ARL theorem follows from this local result alone.

---

# Step-2 baseline decision

| Component | Status after hostile audit |
|---|---|
| Gaussian change of measure | **PASS** |
| Stopped likelihood identity | **PASS** |
| Differentiation under expectation | **PASS after explicit lemma closure** |
| Raw-product derivative | **PASS** |
| Covariance reformulation | **PASS via Wald** |
| Reflection / \(F(0)=0\) | **PASS** |
| Mixed-reuse scaling | **PASS** |
| Local instability implication | **PASS, local-only scope** |
| Bellman/Fredholm state reduction | **PASS** |
| Continuation geometry | **PASS** |
| Absorbing reward | **PASS** |
| \(\Gamma=b(0,0)\) | **PASS** |
| Existence / uniqueness | **PASS by two routes** |
| General Gaussian stopping-time theorem | **PASS with regularity conditions** |
| Exponential-family extension | **CONDITIONAL / non-core** |
| Fatal flaws | **NONE FOUND** |

## Final Step-2 verdict

\[
\boxed{\textbf{STEP 2: PASS WITH TWO NONFATAL CORRECTIONS}}
\]

The CUSUM Level-3 mathematical core survives hostile comparison of the official and blind derivations.

The only analytically delicate point — differentiation of the stopped likelihood — can be closed by the explicit forcing-time exponential-moment lemma given in this report.

The two errors found are in auxiliary numerical/one-sided commentary of the blind report and do not alter the symmetric CUSUM theorem.

**Do not freeze the final Level-3 Mathematical Baseline yet.**

Per the agreed workflow, the next required gate is:

\[
\boxed{
\text{Step 3 — proof-to-code correspondence audit}
}
\]

which must establish, line by line,

\[
\text{mathematical object}
\leftrightarrow
\text{source implementation}
\leftrightarrow
\text{certificate field}.
\]

Only after Step 3 passes, together with the already demonstrated fresh certificate replay, should the Level-3 Mathematical Baseline be frozen.

---

## Claim discipline frozen by this audit

### Theorem-level / certified
- stopped-score derivative identity under stated regularity;
- reflection-centered mean-map fixed point for symmetric two-sided CUSUM;
- exact mixed-reuse slope scaling;
- Bellman/Fredholm reduction;
- \(\Gamma=b(0,0)\);
- certified \(\Gamma>2\) at \(k=0.5,h=5,m=1\);
- local mean-map instability.

### Empirical only unless separately proved
- period-2-like behavior;
- bimodality;
- stochastic invariant-law shape;
- multi-cycle oscillation theorem;
- ARL degradation mechanism;
- robustness across arbitrary \(m,k,h\) or noise families.

---

**Archive status:** suitable to retain as the Step-2 hostile mathematical audit record.  
**Next gate:** Step 3 proof-to-code correspondence audit.
