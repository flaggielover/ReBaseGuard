# Blind Mathematical Re-Derivation Report
## Sequential monitoring with stopping-selected reference reuse

Everything below is derived from the model statement alone. Numerical values were
obtained by two mutually independent computations (crude Monte Carlo on the raw
recursion; numerical solution of the integral equations derived in §G). No prior
formula was assumed at any point.

---

## A. Exact model and assumptions

**Data.** $X_1, X_2, \dots$ iid $N(0,1)$ on $(\Omega,\mathcal F,P)$.

**Residuals.** For a fixed scalar $e$, $Z_t := X_t - e$, so under the parameter
$e$ the residuals are iid $N(-e,1)$. Write $Q_e$ for the law of $(Z_t)_{t\ge1}$ on
sequence space, $E_e$ for its expectation, $\mathcal F_t = \sigma(Z_1,\dots,Z_t)$.

**Detector.** With $k>0$, $h>0$ fixed and independent of $e$:
$$S_0^\pm = 0,\qquad S_t^+ = (S_{t-1}^+ + Z_t - k)^+,\qquad S_t^- = (S_{t-1}^- - Z_t - k)^+,$$
$$\tau = \inf\{t\ge1 : \max(S_t^+,S_t^-)\ge h\}.$$
Alarm is tested **after** the update; the threshold is attained inclusively;
overshoot is not truncated. Main case $k=1/2$, $h=5$.

**Reuse map.** $e_{\text{next}} = e + Z_\tau$ and
$$F(e) := E_e[e_{\text{next}}] = e + E_e[Z_\tau].$$

**Critical structural fact (A1).** $\tau$ is a *fixed measurable functional of the
residual path* $(Z_t)$: the map $\tau$ does not depend on $e$. The parameter $e$
enters **only** through the measure $Q_e$. This is what makes a change-of-measure
argument possible at all, and it is the single assumption most likely to be
violated by a careless reformulation (see O.4).

**(A2) $\tau<\infty$ a.s., with geometric tails, under every $Q_e$.** Proof: the
single-step event $B_j := \{Z_j > k+h\}$ has probability
$p_0 := Q_e(Z_1 > k+h) > 0$, and on $B_j$,
$$S_j^+ = (S_{j-1}^+ + Z_j - k)^+ \ge (Z_j - k)^+ > h$$
because $S_{j-1}^+\ge0$ can only increase the argument. So an alarm occurs at
step $j$ whenever $B_j$ occurs, and survival to time $t$ requires all of
$B_1,\dots,B_t$ to fail. These are independent, hence
$$Q_e(\tau > t) \le (1-p_0)^{t},$$
so $\tau$ has geometric tails and all moments, uniformly for $e$ in compacts. *(Verified numerically: at $h=5$, $k=0.5$ the
empirical ratios $P(\tau>t+200)/P(\tau>t)$ are constant at $0.649$ — clean
geometric decay.)*

---

## B. Stopped likelihood ratio

On $\mathcal F_t$, the density of $Q_e$ w.r.t. $Q_0$ is obtained from the Gaussian
product density. With $\varphi$ the standard normal density,
$$\frac{dQ_e}{dQ_0}\Big|_{\mathcal F_t} = \prod_{s=1}^t \frac{\varphi(z_s+e)}{\varphi(z_s)}
= \exp\Big(-e\sum_{s=1}^t z_s - \tfrac{t e^2}{2}\Big).$$
Define
$$M_t(e) := \exp\big(-e\,T_t - \tfrac{t e^2}{2}\big),\qquad T_t := \sum_{s=1}^t Z_s .$$
$(M_t(e))_t$ is a positive $Q_0$-martingale with $E_0[M_t(e)]=1$.

**Sign check (O.5).** Under $Q_e$ the residuals have mean $-e$. The exponent
carries $-e\,T_t$, *not* $+e\,T_t$: differentiating at $e=0$ gives score
$-T_t$, and indeed $E_e[T_t] = -et \Rightarrow \partial_e E_e[T_t]|_0 = -t$,
consistent with $E_0[T_t\cdot(-T_t)] = -t$. The opposite sign would flip the
final answer's sign, so this is worth stating explicitly.

**Stopped identity.** For any $\mathcal F_\tau$-measurable $G$ with the
integrability below,
$$\boxed{\;E_e[G] = E_0[G\,M_\tau(e)]\;}\tag{B1}$$
Justification, in the only form that is actually safe: for each $t$, the
restriction of $Q_e$ to $\mathcal F_t$ has density $M_t(e)$, so for $G$
$\mathcal F_\tau$-measurable,
$$E_e[G\mathbf 1_{\tau=t}] = E_0[G\mathbf 1_{\tau=t} M_t(e)]
= E_0[G\mathbf 1_{\tau=t}M_\tau(e)],$$
using $\{\tau=t\}\in\mathcal F_t$ and $M_\tau = M_t$ there. Summing over
$t\ge1$ and invoking $\tau<\infty$ a.s. (A2) plus dominated convergence /
Fubini for the sum gives (B1). **No optional-stopping theorem is invoked** —
this is a decomposition over $\{\tau=t\}$, which is why it is legitimate. In
particular taking $G\equiv1$ gives $E_0[M_\tau(e)]=1$ (stopped normalization)
as a *consequence*, not an assumption.

Sufficient conditions used: (i) $\tau<\infty$ a.s. under $Q_0$ — (A2);
(ii) $E_0[|G|M_\tau(e)]<\infty$; (iii) for the *differentiation* step, local
uniform integrability of the difference quotients, supplied in C below.

---

## C. The derivative identity

Take $G = Z_\tau$ in (B1):
$$F(e) = e + E_0\!\big[Z_\tau\,e^{-eT_\tau - \tau e^2/2}\big] =: e + g(e).$$

**Differentiability.** Let $\psi(e,\omega) := Z_\tau e^{-eT_\tau - \tau e^2/2}$.
Then $\partial_e\psi = Z_\tau(-T_\tau - \tau e)e^{-eT_\tau-\tau e^2/2}$. For
$|e|\le\delta$,
$$|\partial_e\psi| \le |Z_\tau|\,(|T_\tau| + \delta\tau)\,e^{\delta|T_\tau|+\tau\delta^2/2}.$$
Since $|Z_\tau|\le |T_\tau| + |T_{\tau-1}|$, and $\tau$ has geometric tails with
$Z_t$ Gaussian, all of $\tau$, $T_\tau$, $Z_\tau$ have finite exponential
moments of small order (Wald/Cramér-type bound: $E_0 e^{\lambda|T_\tau|}<\infty$
for $\lambda$ small, since $|T_\tau|\le \sum_{t\le\tau}|Z_t|$ and $\tau$ is
geometrically bounded). Hence for $\delta$ small the bound is an integrable
dominating function, and **dominated convergence justifies differentiating under
the expectation** on $(-\delta,\delta)$. This is the step that must not be waved
through (O.1, O.3).

Evaluating at $e=0$ ($M_\tau(0)=1$):
$$g'(0) = E_0[Z_\tau\cdot(-T_\tau)] = -E_0[Z_\tau T_\tau],$$
so
$$\boxed{\;F'(0) = 1 - E_0[Z_\tau T_\tau]\;}\tag{C1}$$

**Covariance versus raw product (O.9).** The general identity produced by the
score argument is
$$F'(0) = 1 - \mathrm{Cov}_0(Z_\tau, T_\tau) - E_0[Z_\tau]\,E_0[T_\tau]\cdot 0
\quad\text{— more precisely:}$$
differentiating gives $-E_0[Z_\tau T_\tau]$ *raw*. Since
$$\mathrm{Cov}_0(Z_\tau,T_\tau) = E_0[Z_\tau T_\tau] - E_0[Z_\tau]E_0[T_\tau],$$
the raw product equals the covariance **iff** $E_0[Z_\tau]E_0[T_\tau]=0$.

Now:
* $E_0[T_\tau]=0$ is **not** free from Wald's identity in the naive form
  $E_0[T_\tau]=E_0[\tau]\cdot E_0[Z_1]$ — that *is* valid here because
  $E_0[Z_1]=0$ and $E_0\tau<\infty$ (Wald applies: $\tau$ is a stopping time for
  an iid sequence with finite mean, $E\tau<\infty$). So $E_0[T_\tau]=0$ follows
  from **optional stopping / Wald**, requiring only $E_0\tau<\infty$ — no
  symmetry.
* $E_0[Z_\tau]=0$ does **not** follow from Wald (it is a single terminal
  increment, size-biased by the alarm event). It follows from **reflection
  symmetry** (§D). Without symmetry it is generically nonzero — demonstrated
  below.

So $\Gamma := E_0[Z_\tau T_\tau] = \mathrm{Cov}_0(Z_\tau,T_\tau)$ here, but the
coincidence rests on $E_0[T_\tau]=0$ (Wald), and each vanishing moment has a
*different* source. **The derivative identity (C1) itself needs neither.**

**Numerical confirmation of (C1) — independent of all later machinery.** Direct
Monte Carlo with common random numbers, $h=1.5$, $k=0.5$, $N=2\times10^6$ per
value of $e$:

| $e$ | $-0.02$ | $-0.01$ | $0$ | $+0.01$ | $+0.02$ |
|---|---|---|---|---|---|
| $F(e)$ | $+0.076325$ | $+0.038413$ | $-0.000106$ | $-0.038340$ | $-0.076756$ |

Central difference at $\pm0.01$: $-3.8376$; at $\pm0.02$: $-3.8270$; Richardson
extrapolation: $-3.8411$. Prediction from (C1) with $\Gamma$ from the *independent*
integral-equation solve: $1-\Gamma = -3.8343$. Agreement to $\approx0.1\%$
(residual is Monte Carlo noise, s.e. $\approx0.002$ on each $F$).

---

## D. Reflection symmetry

Consider the involution $R:(z_t)\mapsto(-z_t)$. Under $Q_0$, $R$ is
**measure-preserving** (the $Z_t$ are iid $N(0,1)$, symmetric). Under $Q_e$ with
$e\ne0$ it is *not*.

Applying $R$ to the recursions: with $\tilde Z_t = -Z_t$,
$$\tilde S_t^+ = (\tilde S_{t-1}^+ + \tilde Z_t - k)^+ = (\tilde S_{t-1}^+ - Z_t - k)^+,$$
which is exactly the recursion for $S_t^-$. By induction from $S_0^\pm=0$,
$$\tilde S_t^+ = S_t^-,\qquad \tilde S_t^- = S_t^+ \quad\text{for all }t.$$
Hence $\max(\tilde S_t^+,\tilde S_t^-) = \max(S_t^+,S_t^-)$ and therefore
$$\tau\circ R = \tau .$$
The two-sided rule is **reflection-equivariant** (indeed $\tau$ is
reflection-*invariant*, while the arms swap). This uses: both arms share the same
$k$ and the same $h$, both start at $0$, and both use the same innovation $z$.

Consequences, under $Q_0$ only:
* $Z_\tau\circ R = -Z_{\tau}$ and $\tau\circ R=\tau$, so $Z_\tau
  \stackrel{d}{=} -Z_\tau$, giving $E_0[Z_\tau]=0$ and hence
  $$F(0) = 0 + E_0[Z_\tau] = 0 .$$
* Likewise $T_\tau \stackrel d= -T_\tau$ ($E_0[T_\tau]=0$, consistent with Wald),
  while $Z_\tau T_\tau$ is $R$-**invariant** — so $\Gamma$ is not forced to vanish,
  and generically does not.

**Numerical check** ($h=1.5$, $N=2\times10^6$): $E_0[Z_\tau] = -0.0001 \pm
0.0014$, $E_0[T_\tau] = -0.0002\pm0.0023$ — both zero to precision.

**Stochastic recursion vs. mean skeleton (O.14).** $e=0$ is a fixed point of the
**deterministic map** $F$, i.e. $F(0)=0$. It is emphatically *not* a fixed point
of the stochastic recursion $e_{j+1}=e_j+Z_{\tau_j}$: starting from $e_0=0$,
$e_1=Z_{\tau_1}$ is a nondegenerate random variable with (at $h=5$) second moment
$E_0[Z_\tau^2]\approx4.05$. The stochastic recursion has *no* fixed point; it has
at best an invariant law. Conflating the two is the single most tempting error in
this problem.

**Falsification of the symmetry claim by counterexample.** Replace the detector
by the **one-sided** CUSUM $\tau=\inf\{t: S_t^+\ge h\}$ (all else identical,
$h=1.5$). Reflection equivariance is destroyed. Simulation ($N=10^6$):
$$E_0[Z_\tau] = +1.8664,\qquad F(0) = +1.8664 \ne 0,$$
so $F(0)=0$ **fails** without symmetry — as predicted. Meanwhile the derivative
identity (C1) still holds: the integral-equation solve gives
$\Gamma_{\text{raw}} = E_0[Z_\tau T_\tau] = -0.0377$, predicting
$F'(0) = 1-\Gamma = +1.0377$, versus finite-difference $+1.0295$ (Richardson
$+1.0309$). Note here $E_0[Z_\tau]E_0[T_\tau]\neq0$ and indeed
$\mathrm{Cov} = -0.0373 \ne -0.0377 = \Gamma_{\text{raw}}$ — the raw/covariance
distinction becomes *numerically visible* exactly when symmetry is absent. This
is a clean confirmation that (C1) is the raw-product form and that the
covariance form is the symmetric special case.

---

## E. Mixed reuse

Let $e_{\text{next}} = \rho(e+Z_\tau) + (1-\rho)W$, with $W\perp$ cycle data,
$E[W]=0$, $E|W|<\infty$, and — **crucially** — the law of $W$ not depending on
$e$. Then
$$F_\rho(e) = \rho\big(e+E_e[Z_\tau]\big) + (1-\rho)E[W] = \rho\,F_1(e).$$
Because the identity holds *as functions of $e$* (not merely at $e=0$),
differentiating gives
$$\boxed{\;F_\rho'(0) = \rho\,F_1'(0) = \rho(1-\Gamma)\;}$$
**exactly**, and also $F_\rho(0) = \rho F_1(0) = 0$. Assumptions actually needed:
$E[W]=0$; $W$ independent of the alarm cycle; **the law of $W$ is
$e$-independent**; $\rho$ constant (not a function of $e$ or of the data);
$F_1$ differentiable at $0$ (§C). If instead $W$'s law drifted with $e$ — e.g.
$W$ drawn from a recent-history pool — an extra $(1-\rho)\partial_e E_e[W]$ term
appears and the clean scaling fails. That is the only realistic way this
statement breaks.

---

## F. Local stability theorem

**Theorem.** Let $F$ be $C^1$ near $0$ with $F(0)=0$ and $\lambda:=F'(0)$.
For the deterministic scalar iteration $e_{j+1}=F(e_j)$:
$|\lambda|<1 \Rightarrow 0$ locally asymptotically stable (attracting);
$|\lambda|>1 \Rightarrow 0$ unstable (repelling) — there is a neighbourhood
$U$ such that every $e_0\in U\setminus\{0\}$ eventually leaves $U$.
Proof: standard, from $|F(e)| = |\lambda||e|(1+o(1))$.

Hence $F_1'(0) < -1$ implies **exactly** this: $e=0$ is a repelling fixed point
of the mean skeleton, with the local expansion being *orientation-reversing*
(trajectories alternate sign while growing in modulus). Nothing more.

**What does NOT follow** (O.15), and why:
* *Period-2 orbits.* Not implied. $F'(0)<-1$ makes $F\circ F$ have derivative
  $\lambda^2>1$ at $0$, so $0$ repels under $F^2$ too — but existence of a
  genuine 2-cycle requires a **global** argument (e.g. $F$ continuous with a
  trapping interval, or a sign/monotonicity condition giving a fixed point of
  $F^2$ away from $0$). Local data cannot produce it.
* *Period doubling.* A bifurcation statement, requiring a *parameter family*
  crossing $\lambda=-1$ with transversality plus a nondegenerate third-order
  (Schwarzian-type) coefficient. Not available from $F'(0)$ alone.
* *Bimodality of the invariant law*, *ARL degradation*: statements about the
  **stochastic** recursion, whose behaviour is governed by the whole random map
  $e\mapsto e+Z_\tau$, not by $F$. The mean skeleton neither implies nor
  precludes them. Note in particular that $\mathrm{Var}(Z_\tau)$ is large
  ($\approx4.05$ at $h=5$) compared with the local scale on which the linearization
  is valid, so *the mean skeleton is a poor proxy for the stochastic dynamics
  here* — this is a substantive caveat, not a formality.

**Mixed-reuse critical $\rho$.** With $F_\rho'(0)=\rho(1-\Gamma)$ and
$\Gamma>1$, the map is locally stable iff $|\rho(1-\Gamma)|<1$, i.e.
$$\boxed{\;0\le\rho<\rho_c := \frac1{\Gamma-1}\;}$$
At $h=5$, $\Gamma\approx15.885 \Rightarrow \rho_c\approx0.0672$: only very weak
reuse is locally stable. (If $\Gamma<2$, $\rho_c>1$ and all $\rho\in[0,1]$ are
stable.)

---

## G. Independent Bellman/Fredholm reduction

**State.** After the update at time $t$ (no alarm), the pair $s=(p,m)=(S_t^+,S_t^-)$
with $x=T_t$ is sufficient: the future depends on the past only through $(s,x)$,
because the recursions are Markov in $(S^+,S^-)$ and the reward involves $T$ only
additively. Define, for $s$ in the continuation region $C:=[0,h)^2$,
$$H(s,x) := E_0\big[Z_\tau T_\tau \mid S^+=p, S^-=m, T=x\big].$$

**Affinity in $x$.** Write $T_\tau = x + \sum_{t>{\rm now}} Z_t$; the future
increments and $\tau$'s residual law depend on $s$ only. So
$H(s,x) = E[Z_\tau(x + \Delta)] = x\,E[Z_\tau] + E[Z_\tau\Delta]$ where
$\Delta$ is the future partial sum up to alarm — both expectations functions of
$s$ alone. Hence **$H$ is affine in $x$**:
$$H(s,x) = a(s)\,x + b(s),\qquad a(s)=E_s[Z_\tau],\quad b(s)=E_s[Z_\tau\Delta_s].$$

**Continuation geometry (§9).** From $s=(p,m)$ with innovation $z$, the updated
arms are $p'=(p+z-k)^+$, $m'=(m-z-k)^+$. Alarm iff $p'\ge h$ or $m'\ge h$, i.e.
$$p+z-k\ge h \iff z \ge u(s):= h+k-p, \qquad m-z-k\ge h \iff z \le -v(s),\ v(s):=h+k-m.$$
Since $p,m\in[0,h)$ we have $u,v\in(k, h+k]$, both $>0$, so the continuation set is
the nonempty interval
$$\boxed{\;z\in\big(-v(s),\,u(s)\big) = \big(-(h+k-m),\ h+k-p\big)\;}$$
For $k=1/2,h=5$: $z\in(m-5.5,\ 5.5-p)$. Checks: threshold inclusive (alarm at
$\ge h$, so continuation is the *open* interval); alarm tested after update;
both arms driven by the same $z$ (the two alarm events are the two tails of one
scalar); the $(\cdot)^+$ resets are *interior* kinks at $z=k-p$ and $z=m-k$
which do **not** affect the alarm boundary (a reset sends an arm to $0$, never
above $h$); overshoot is retained since we do not truncate $z$.

**Absorbing reward (§10).** If alarm fires with innovation $z$, then
$Z_\tau = z$, $T_\tau = x+z$, so the terminal reward is $z(x+z) = zx + z^2$ —
affine in $x$ with slope $z$, plus the **$z^2$ term** which is easy to lose.

**First-step conditioning.** With $\varphi$ standard normal, and writing
$q(s,z)=\big((p+z-k)^+,(m-z-k)^+\big)$:
$$H(s,x) = \int_{-v}^{u} H\big(q(s,z),\,x+z\big)\varphi(z)\,dz
+ \Big(\int_{-\infty}^{-v}+\int_u^{\infty}\Big) \big(zx+z^2\big)\varphi(z)\,dz .$$
Substituting $H=a x + b$ and matching powers of $x$ (legitimate since the
identity holds for all $x\in\mathbb R$):

*Coefficient of $x$:*
$$a(s) = \int_{-v}^{u} a(q(s,z))\varphi(z)dz + \underbrace{\Big(\int_{-\infty}^{-v}+\int_u^\infty\Big) z\,\varphi(z)dz}_{=:r_a(s)} .$$
Using $\int_u^\infty z\varphi = \varphi(u)$ and $\int_{-\infty}^{-v} z\varphi = -\varphi(v)$:
$$\boxed{\,r_a(s) = \varphi(u)-\varphi(v)\,}$$

*Constant term:*
$$b(s) = \int_{-v}^{u}\big[b(q(s,z)) + z\,a(q(s,z))\big]\varphi(z)dz + \underbrace{\Big(\int_{-\infty}^{-v}+\int_u^\infty\Big) z^2\varphi(z)dz}_{=:r_b(s)}$$
Using $\int_u^\infty z^2\varphi = u\varphi(u)+\bar\Phi(u)$ (with $\bar\Phi=1-\Phi$)
and the mirrored expression on the left tail:
$$\boxed{\,r_b(s) = u\varphi(u)+\bar\Phi(u) + v\varphi(v)+\bar\Phi(v)\,}$$

Defining the killed (sub-Markov) operators
$$(K f)(s) := \int_{-v(s)}^{u(s)} f(q(s,z))\varphi(z)dz,\qquad
(K_z f)(s) := \int_{-v(s)}^{u(s)} z\,f(q(s,z))\varphi(z)dz,$$
the equations are exactly the claimed triangular structure
$$\boxed{\;a = Ka + r_a,\qquad b = Kb + K_z a + r_b\;}$$
— derived, not assumed. The coupling term is $K_z a$ (not $K a$ or $a$), and
$r_b$ contains **both** a density term and a tail-probability term.

---

## I. Reset value: $\Gamma = b(0,0)$

At the start of a fresh cycle $s=(0,0)$, $x=T_0=0$. By definition
$H((0,0),0) = E_0[Z_\tau T_\tau] = \Gamma$ and $H(s,x)=a(s)x+b(s)$ gives
$$\Gamma = a(0,0)\cdot 0 + b(0,0) = b(0,0).$$
**Exact, with no missing term** — provided the convention is respected that
$(s,x)=((0,0),0)$ is the state *before the first innovation*, and that $H$ is
defined by conditioning on the post-update state. The one genuine hazard is an
off-by-one: if the initial state were treated as *post-update* after $Z_1$, one
would be computing $E[Z_\tau T_{\tau}]$ for a path started one step in, which is
not $\Gamma$.

**Off-by-one, quantified (O.7).** If $T_\tau$ were mistakenly replaced by
$T_{\tau-1}$ (dropping the terminal increment), the answer changes by exactly
$E_0[Z_\tau^2]$:
$$E_0[Z_\tau T_{\tau-1}] = \Gamma - E_0[Z_\tau^2] = 15.885 - 4.051 = 11.834
\quad (h=5),$$
a $25\%$ error. Both variants were computed; the reported $\Gamma$ is the one
matching the finite-difference slope in §C.

**Structural checks that the solution satisfies (all verified numerically at
$h=5$, grid $251^2$):**
* $a(0,0) = E_0[Z_\tau] = 0$ — obtained as $1.6\times10^{-18}$, i.e. exactly zero
  in floating point. This is *predicted* by §D and is a nontrivial validation of
  the operator equations.
* $a(p,m) = -a(m,p)$ (antisymmetric): $\max|a+a^{\!\top}| = 6.7\times10^{-16}$.
* $b(p,m) = b(m,p)$ (symmetric): $\max|b-b^{\!\top}| = 3.4\times10^{-14}$.
* $a\not\equiv0$ ($\max|a| = 0.601$) — so the $K_z a$ coupling is genuinely
  load-bearing away from the diagonal, even though $a$ vanishes at the reset state.

**Each derived term is necessary** (recomputing $\Gamma$ at $h=5$ with one term
deleted): omitting the $K_za$ coupling gives $4.050$ (error $-11.835$); omitting
the $\bar\Phi(u)+\bar\Phi(v)$ tail piece of $r_b$ gives $14.885$ (error exactly
$-1.0000$); the off-by-one gives error $-4.051$. The middle result is a further
internal consistency check: deleting that piece subtracts
$(I-K)^{-1}[P_s(\text{alarm next step})]$, and the answer is exactly $-1$
because $(I-K)^{-1}p_{\text{alarm}} \equiv 1$ — the killed process stops with
probability one.

---

## J. Existence and uniqueness

Let $B(C)$ be bounded measurable functions on $C=[0,h)^2$ with sup norm. $K$ is
a positive linear operator with
$$(K\mathbf 1)(s) = \Phi(u(s)) - \Phi(-v(s)) = P_s(\text{no alarm next step}) < 1 .$$
Pointwise $<1$ is **not** enough for a contraction (the sup over $C$ can equal
$1$: indeed numerically $\sup_s (K\mathbf 1)(s) = 0.99953$ at $h=5$ — close to,
but strictly below, $1$). Two valid routes:

1. **Uniform sub-stochasticity.** Since $p,m\in[0,h)$ we have $u(s)=h+k-p\le h+k$
   and $v(s)=h+k-m\le h+k$, so
   $$(K\mathbf 1)(s) = \Phi(u(s))-\Phi(-v(s)) \le \Phi(h+k)-\Phi(-(h+k)) =: \theta < 1$$
   uniformly in $s$, strictly because the Gaussian puts positive mass outside
   $[-(h+k),\,h+k]$. Hence $\|K\|_{\infty}\le\theta<1$, $K$ is a strict contraction on $B(C)$, and
   Banach's fixed point theorem gives a unique bounded $a$; then the second
   equation, with $K_za + r_b$ a fixed bounded function, gives a unique bounded
   $b$. **The triangular structure is what makes this work: no simultaneous
   fixed point is needed.**
2. **Geometric tail / resolvent.** Equivalently $\|K^n\|\le\theta^n$, so
   $(I-K)^{-1}=\sum_{n\ge0}K^n$ converges in operator norm; this is the
   probabilistic statement that the killed process survives $n$ steps with
   probability $\le\theta^n$ (the geometric tail of §A2). The Neumann series
   *is* $E_s[\sum_{t<\tau}\cdots]$, giving both existence and the interpretation.

Sufficient conditions: $r_a, r_b$ bounded (they are: $|r_a|\le2\varphi(0)$,
$0\le r_b\le 2[(h+k)\varphi(k)+\bar\Phi(k)]$); $K$ maps $B(C)\to B(C)$
(dominated by $\theta$); $\theta<1$, which holds for any finite $h$, $k>0$.
Note "because the process eventually stops" alone is *insufficient* — a.s.
finiteness without a uniform bound would not give norm contraction, only
pointwise convergence. Numerically, GMRES converged to $10^{-12}$ for every
case, and grid refinement ($n=150,250,350$ at $h=5$) gives
$15.8824,\ 15.8851,\ 15.8860$ — Richardson limit $\approx15.8868$, consistent
with the Monte Carlo $15.814\pm0.064$.

---

## K. Arbitrary-stopping-time Gaussian theorem

Inspecting §B–C: **the CUSUM recursion was never used.** Only (A1) parameter-
invariance of $\tau$ and integrability entered. Hence:

**Theorem K.** Let $Z_t$ iid $N(-e,1)$, let $\tau$ be a stopping time that is a
fixed functional of the residual path (independent of $e$), and let
$W_{\tau,m} := \frac1m\sum_{r=0}^{m-1}Z_{\tau-r}$ (with the convention that
indices $\le0$ are handled by a fixed rule, e.g. $\tau\ge m$ a.s. or padding).
Assume: (i) $\tau<\infty$ $Q_0$-a.s. with $E_0\tau<\infty$; (ii) for some
$\delta>0$, $E_0\big[|W_{\tau,m}|(|T_\tau|+\tau)e^{\delta|T_\tau|+\delta^2\tau/2}\big]<\infty$.
Then $e\mapsto e+E_e[W_{\tau,m}]$ is differentiable at $0$ and
$$\frac{d}{de}\Big(e+E_e[W_{\tau,m}]\Big)\Big|_{0} = 1 - E_0[W_{\tau,m}T_\tau]
= 1 - \mathrm{Cov}_0(W_{\tau,m},T_\tau),$$
the last equality using $E_0[T_\tau]=0$ (Wald, needs only $E_0\tau<\infty$).

*Assumptions replacing CUSUM structure:* parameter-invariance of $\tau$ +
integrability, nothing else. **Numerical check at $m=2$, $h=1.5$:**
$\mathrm{Cov}_0(W_{\tau,2},T_\tau) = 3.4614$, predicting slope $-2.4614$;
finite differences on simulated $e+E_e[W_{\tau,2}]$ give $-2.4686$ (Richardson
$-2.4708$). Confirmed.

---

## L. Exponential-family extension

Let $\{f_\theta\}$ be a regular family, $\ell(z)=\partial_\theta\log f_\theta(z)|_{\theta_0}$,
$L_\tau=\sum_{t\le\tau}\ell(Z_t)$. Let $G_\theta$ be $\mathcal F_\tau$-measurable
and possibly $\theta$-dependent, with $\dot G := \partial_\theta G_\theta|_{\theta_0}$.
The same $\{\tau=t\}$-decomposition gives
$E_\theta[G_\theta]=E_{\theta_0}[G_\theta \Lambda_\tau(\theta)]$ with
$\Lambda_\tau(\theta)=\prod_{t\le\tau}f_\theta(Z_t)/f_{\theta_0}(Z_t)$ and
$\partial_\theta\Lambda_\tau|_{\theta_0}=L_\tau$. Then
$$\frac{d}{d\theta}E_\theta[G_\theta]\Big|_{\theta_0}
= E[\dot G] + E[G\,L_\tau] = E[\dot G] + \mathrm{Cov}(G,L_\tau) + E[G]\,E[L_\tau].$$
Since $E_{\theta_0}[\ell(Z_1)]=0$ and $E\tau<\infty$, Wald gives
$E[L_\tau]=0$, so
$$\boxed{\;\partial_\theta E_\theta[G_\theta]\big|_{\theta_0} = E[\dot G] + \mathrm{Cov}(G,L_\tau)\;}$$
**Conditions:** (a) $\tau$ parameter-invariant; (b) $\theta\mapsto f_\theta$
differentiable in quadratic mean at $\theta_0$ with finite Fisher information;
(c) $\tau<\infty$ a.s., $E\tau<\infty$; (d) a local dominating function for
$\partial_\theta(G_\theta\Lambda_\tau)$ near $\theta_0$ (as in §C — for
non-Gaussian families this is a genuine restriction requiring local exponential
moments of $L_\tau$, available for exponential families with $\theta_0$ interior
to the natural parameter space); (e) $G_\theta$ differentiable in $\theta$ with
integrable derivative.

**Caveat on parameterization.** The Gaussian result $1-\Gamma$ arose because the
reuse map contributed $\partial_e(e)=1$ *and* the score was $-T_\tau$ under the
specific parameterization $Z\sim N(-e,1)$. In a general family the "$1$" is
$E[\dot G]$ and is parameterization-dependent; the score term likewise carries a
factor from $d\theta/de$. Forcing the answer into the shape $1-\Gamma$ is
illegitimate unless $\dot G$ genuinely equals $1$ and the score is exactly
$-T_\tau$.

---

## O. Proof-attack checklist — every item investigated

1. **Illegitimate differentiation through a stopping time.** Avoided: $\tau$ is
   never differentiated. It cannot be — $\tau$ is integer-valued. The parameter
   sits entirely in the measure. Dominating function supplied (§C).
2. **Optional-stopping misuse.** (B1) is proved by decomposition over
   $\{\tau=t\}$, not by an optional-stopping theorem. Optional stopping/Wald is
   used only for $E_0[T_\tau]=0$, where $E_0\tau<\infty$ is verified.
3. **Uniform integrability.** Supplied via geometric tails of $\tau$ +
   Gaussian increments ⇒ local exponential moments of $(T_\tau,\tau)$ ⇒
   dominated convergence on $|e|<\delta$. **Not** merely asserted.
4. **Parameter dependence of the stopping rule.** Checked: $k,h$ fixed, both
   arms start at $0$, and $\tau$ is a functional of $(Z_t)$ alone. If the
   detector were re-tuned per cycle as a function of $e$, (B1) and hence
   everything downstream would fail.
5. **Wrong likelihood-ratio sign.** Checked explicitly (§B): mean is $-e$,
   exponent is $-eT_t-te^2/2$, score $-T_\tau$. Cross-validated by the sign of
   the finite-difference slope (negative, as $1-\Gamma<0$).
6. **Missing terminal increment.** The absorbing reward is $z(x+z)$, retaining
   $z^2$. Deleting it shifts $\Gamma$ by $-1.000$ exactly (tail piece) or
   $-4.051$ (full off-by-one); both quantified.
7. **Off-by-one in $T_\tau$.** Quantified: $E[Z_\tau T_{\tau-1}] = \Gamma -
   E[Z_\tau^2]$, a $25\%$ error at $h=5$. The reported value is the one matching
   the independent finite-difference slope.
8. **Incorrect use of reflection symmetry.** Symmetry is used *only* under
   $Q_0$ (where it is exact), *only* for $E_0[Z_\tau]=0$ and $F(0)=0$, and never
   for $\Gamma$ (which is $R$-invariant, not $R$-odd). Falsified against a
   one-sided detector where $F(0)=1.866\ne0$.
9. **Covariance vs raw moments.** Distinguished throughout; the identity is raw,
   the covariance form requires $E_0[T_\tau]=0$. Difference made numerically
   visible in the asymmetric counterexample.
10. **Continuation interval.** Derived from scratch as $(-(h+k-m),\,h+k-p)$;
    inclusivity, post-update testing, shared innovation, resets-as-interior-kinks,
    and overshoot all checked (§G).
11. **Missing $z^2$ absorbing reward.** See 6.
12. **Incorrect Bellman state.** $(p,m,x)$ with affinity in $x$ proved, not
    assumed. Affinity verified implicitly by the agreement of the operator solve
    with Monte Carlo at three thresholds.
13. **Nonunique Fredholm solution.** Uniqueness proved by uniform
    sub-stochasticity $\theta<1$ (not by "it stops eventually"); triangular
    structure means no simultaneous fixed point is required.
14. **Mixing the stochastic recursion with its mean skeleton.** Explicitly
    separated (§D): the stochastic recursion has no fixed point; $F(0)=0$ is a
    statement about the mean map only.
15. **Claiming more than local instability.** §F states only repulsion, and
    enumerates what is *not* implied.

**Cross-validation summary** (two independent methods):

| $h$ | $\Gamma$ (integral eqn) | $\Gamma$ (Monte Carlo) | $F_1'(0)$ | $\rho_c$ |
|---|---|---|---|---|
| 1.5 | 4.8343 | $4.8309\pm0.0029$ | $-3.834$ | 0.261 |
| 3.0 | 9.1328 | $9.1370\pm0.0087$ | $-8.133$ | 0.123 |
| 5.0 | 15.8851 | $15.814\pm0.064$ | $-14.885$ | 0.0672 |

---

## P. Final verdict (comparison-free)

The mathematical core survives a hostile check. The derivative identity is
correct **as a raw-product formula** and its covariance form is correct given
$E_0[T_\tau]=0$; the two vanishing moments have genuinely different origins
(Wald vs. reflection symmetry), and only $F(0)=0$ depends on symmetry. The
Bellman/Fredholm reduction is correct with the stated $r_a,r_b$, and
$\Gamma=b(0,0)$ is exact. The stability claim is correct **only** as a local
repulsion statement; the listed dynamical corollaries are not implied by the
local data and are not established here. The one substantive caveat is that
because $\mathrm{Var}(Z_\tau)$ is large relative to the linearization scale, the
mean skeleton is a weak guide to the stochastic system's actual behaviour.

---

BLIND DERIVATION VERDICT:
PASS WITH CONDITIONS

GAUSSIAN STOPPED-SCORE IDENTITY:
PROVED

CUSUM-SPECIFIC STRUCTURE REQUIRED FOR DERIVATIVE:
NO — (for the derivative identity; PARTIAL for the overall package, since
$F(0)=0$ requires reflection symmetry and the numerical evaluation of $\Gamma$
requires the CUSUM state recursion)

REFLECTION SYMMETRY:
CORRECT

MIXED-REUSE SCALING:
CORRECT

LOCAL INSTABILITY IMPLICATION:
REQUIRES MODIFICATION — local repulsion only; period-2 / period-doubling /
bimodality / ARL degradation are not implied

BELLMAN/FREDHOLM REDUCTION:
CORRECT

ABSORBING REWARD:
CORRECT

GAMMA_EQUALS_b00:
CORRECT

EXISTENCE/UNIQUENESS:
PROVED

EXPONENTIAL-FAMILY EXTENSION:
CONDITIONAL — proved under quadratic-mean differentiability, $E\tau<\infty$, and
a local dominating function; parameterization caveat applies

FATAL FLAWS FOUND:
None.

NONFATAL CONDITIONS / CAVEATS:
1. $\tau$ must be parameter-invariant ($k,h$ not retuned with $e$); this is the
   load-bearing structural assumption.
2. Differentiation under the expectation needs local exponential moments of
   $(T_\tau,\tau)$; supplied here by geometric tails of $\tau$, but it must be
   stated, not assumed.
3. The identity is a **raw** product $E_0[Z_\tau T_\tau]$; the covariance form
   requires $E_0[T_\tau]=0$ (Wald, $E_0\tau<\infty$).
4. $E_0[Z_\tau]=0$ and $F(0)=0$ require reflection symmetry (equal $k$, equal
   $h$, both arms from $0$); they fail for a one-sided detector.
5. Mixed-reuse exact scaling requires $W$'s law to be $e$-independent and
   $\rho$ constant.
6. Stability conclusion is local only; $\mathrm{Var}(Z_\tau)\approx4.05$ at $h=5$
   means the mean skeleton is a poor proxy for the stochastic dynamics.
7. Reported $\Gamma$ values are numerical (grid discretization + interpolation);
   digits beyond ~4 significant figures are not certified.

STRONGEST THEOREM THAT SURVIVES:
Let $Z_t$ be iid $N(-e,1)$ and let $\tau$ be a stopping time that is a fixed
path functional independent of $e$, with $\tau<\infty$ a.s., $E_0\tau<\infty$,
and a local dominating function for the differentiated stopped likelihood. Let
$G$ be $\mathcal F_\tau$-measurable and $e$-free. Then
$\partial_e E_e[G]|_{e=0} = -E_0[G\,T_\tau] = -\mathrm{Cov}_0(G,T_\tau)$.
Specializing to $G=W_{\tau,m}$ and adding the reuse term gives
$F'(0)=1-\mathrm{Cov}_0(W_{\tau,m},T_\tau)$; for $m=1$ and the two-sided CUSUM
this is $1-\Gamma$ with $\Gamma=E_0[Z_\tau T_\tau]=b(0,0)$, where $(a,b)$ solve
$a=Ka+r_a$, $b=Kb+K_za+r_b$ on $[0,h)^2$ with
$r_a=\varphi(u)-\varphi(v)$, $r_b=u\varphi(u)+\bar\Phi(u)+v\varphi(v)+\bar\Phi(v)$,
$u=h+k-p$, $v=h+k-m$; these have a unique bounded solution because
$\|K\|_\infty<1$. Reflection symmetry additionally gives $F(0)=0$ and
$a(0,0)=0$, and affine mixed reuse gives $F_\rho'(0)=\rho(1-\Gamma)$ exactly,
with local stability iff $\rho<1/(\Gamma-1)$. At $k=1/2,h=5$:
$\Gamma\approx15.89$, $F_1'(0)\approx-14.89$, $\rho_c\approx0.067$.

TOP 5 PLACES A HUMAN REFEREE SHOULD CHECK:
1. The dominating-function argument in §C — that local exponential moments of
   $(T_\tau,\tau)$ really do justify differentiating under $E_0$ on a
   neighbourhood of $e=0$, uniformly. This is the only analytically delicate step.
2. The raw-vs-covariance bookkeeping and the *separate* provenance of
   $E_0[T_\tau]=0$ (Wald) and $E_0[Z_\tau]=0$ (symmetry) — conflating them makes
   the result look more robust than it is.
3. The continuation interval endpoints $u=h+k-p$, $v=h+k-m$ together with
   inclusive thresholding, and the claim that the $(\cdot)^+$ resets never
   trigger an alarm — i.e. that the interior kinks are irrelevant to absorption.
4. The $z^2$ term in the absorbing reward and the $\bar\Phi(u)+\bar\Phi(v)$ piece
   of $r_b$, plus the $T_\tau$ vs $T_{\tau-1}$ convention. These are the
   quantitatively largest failure modes (25% and 6% at $h=5$).
5. The stability section: confirm that nothing beyond local repulsion is claimed,
   and in particular that no period-2 / bimodality / ARL statement is smuggled in
   from the sign of $F'(0)$.

CONFIDENCE:
HIGH — for the derivative identity, the symmetry analysis, the mixed-reuse
scaling, the Bellman/Fredholm structure with its terminal terms, and
$\Gamma=b(0,0)$ (each independently cross-validated numerically by two
unrelated methods and by deliberate falsification tests).
MEDIUM — for the 4th–5th significant figures of $\Gamma$, and for the
exponential-family extension in full generality (regularity conditions stated
but not stress-tested beyond the Gaussian case).
