# ReBaseGuard Step 3 — Proof-to-Code Correspondence Audit

**Date:** 2026-08-19  
**Scope:** Frozen Level-3 CUSUM certificate (`k=0.5`, `h=5`, `m=1`)  
**Audit objective:** Verify that the mathematical objects used in the Level-3 proof correspond to the actual source implementation, proof artifacts, certificate fields, and replay auditor.  
**Verdict:** **PASS WITH NONFATAL ENVIRONMENT QUALIFICATION**

---

## 1. Executive verdict

The source-level correspondence chain is intact:

\[
\text{CUSUM model}
\leftrightarrow
\text{stopped reward }Z_\tau T_\tau
\leftrightarrow
(K,K_z,r_a,r_b)
\leftrightarrow
(a,b)\text{ Bellman/Fredholm residuals}
\leftrightarrow
\text{continuum residual certificate}
\leftrightarrow
\text{block contraction/resolvent}
\leftrightarrow
\Gamma=b(0,0)
\leftrightarrow
\Gamma>2.
\]

I found **no source-level mismatch** of the dangerous form “the mathematics proves one quantity while the program certifies another.”

The uploaded certificate also hashes exactly to all five proof artifacts named inside it.

The only qualification is environmental: this ChatGPT sandbox does not currently have `python-flint` installed, so I could not perform another live Arb replay here. That is **not a correspondence failure**. A fresh executable replay had already been independently performed on the same repository in the prior external audit, and the present Step-3 task is specifically the proof-to-code mapping audit.

---

## 2. Mathematical model ↔ pathwise source

### Mathematical object

For state \(s=(p,m)\),

\[
p'=\max(0,p+z-k),\qquad
m'=\max(0,m-z-k),
\]

with an inclusive post-update alarm at \(p'\ge h\) or \(m'\ge h\).

For the stopped score functional,

\[
T_t=\sum_{i=1}^t Z_i,
\qquad
\Gamma=E[Z_\tau T_\tau].
\]

The firing increment must be included in both the CUSUM update and \(T_\tau\), so the terminal reward is

\[
Z_\tau T_\tau=z(T_{t-1}+z).
\]

### Source correspondence

`src/rebaseguard_certify/model.py`

- `step`, lines 54–62:
  - `plus = max(0.0, state.plus + z - k)`
  - `minus = max(0.0, state.minus - z - k)`
  - inclusive alarm checks use `>= h`.
- `oracle_step`, lines 65–79:
  - updates the detector first;
  - sets `next_t_sum = t_sum + z`;
  - terminal reward is `z * next_t_sum`.

**Assessment:** PASS.

This is the exact convention required by the derivation. No off-by-one terminal indexing mismatch was found.

---

## 3. Continuation thresholds ↔ source

The derivation defines

\[
\ell=m-h-k,\qquad
u=h+k-p,
\]

and continuation is exactly

\[
\ell<z<u.
\]

`model.py:48–51` implements

```python
return state.minus - h - k, h + k - state.plus
```

For the frozen values \(k=1/2,h=5\), the proof-critical residual code independently specializes these to

\[
\ell=m-\frac{11}{2},\qquad
u=\frac{11}{2}-p.
\]

`residual.py:147–152` constructs precisely these affine endpoints.

**Assessment:** PASS.

---

## 4. Transition map \(q(s,z)\) ↔ diagnostic and proof code

The mathematical transition is

\[
q(s,z)=
\left(
\max(0,p+z-\tfrac12),
\max(0,m-z-\tfrac12)
\right).
\]

`equations.py:24–28` implements this directly.

The rigorous residual code does not numerically call the floating transition. Instead, it symbolically splits the integration domain according to which reflected CUSUM coordinates are active:

- active plus: \(p+z-\frac12\);
- active minus: \(m-z-\frac12\);
- reset coordinate: \(0\).

`residual.py:70–97` constructs these symbolic substitutions, and
`residual.py:144–173` partitions the continuation integral into the correct reset/one-arm/both-arm pieces.

**Assessment:** PASS.

This is an important correspondence point: the proof-critical path is not silently using a different discretized CUSUM transition.

---

## 5. \(K\) and \(K_z\) ↔ implementation

The derivation defines

\[
(Kf)(s)=\int_\ell^u f(q(s,z))\phi(z)\,dz,
\]

\[
(K_zf)(s)=\int_\ell^u zf(q(s,z))\phi(z)\,dz.
\]

The ordinary diagnostic implementation is:

- `equations.py:43–56`: `apply_k_float`
- `equations.py:59–72`: `apply_kz_float`

The proof-critical symbolic implementation uses the same kernel construction with a `z_weight` switch:

- `residual.py:130–141`: `_kernel_piece`
- `residual.py:144–173`: `_kernel_polynomials`
- `residual.py:350–352`:
  - `z_weight=0` for \(K\hat a,K\hat b\);
  - `z_weight=1` for \(K_z\hat a\).

**Assessment:** PASS.

---

## 6. Absorbing rewards \(r_a,r_b\) ↔ implementation

The mathematical terminal reward decomposition gives

\[
r_a(s)=E[Z;Z\notin(\ell,u)]
      =\phi(u)-\phi(\ell),
\]

and

\[
r_b(s)=E[Z^2;Z\notin(\ell,u)]
=u\phi(u)+1-\Phi(u)+\Phi(\ell)-\ell\phi(\ell).
\]

The floating diagnostic version appears in `equations.py:31–40`.

The proof-critical polynomial construction appears in
`residual.py:176–190`:

- `reward_a = phi_upper - phi_ell`;
- `reward_b` is assembled as
  \(u\phi(u)+1-\Phi(u)+\Phi(\ell)-\ell\phi(\ell)\).

**Assessment:** PASS.

Crucially, the \(z^2\) terminal term is present. The implementation is not certifying only \(Z_\tau T_{\tau-1}\).

---

## 7. Bellman/Fredholm system ↔ residual code

The audited mathematical system is

\[
a=Ka+r_a,
\]

\[
b=Kb+K_z a+r_b.
\]

The rigorous residual code constructs:

`residual.py:355–360`

\[
\hat a-K\hat a-r_a
\]

and

\[
\hat b-K\hat b-K_z\hat a-r_b.
\]

The signs in source match the theorem exactly.

**Assessment:** PASS.

No missing \(K_z a\), sign reversal, or reward omission was found.

---

## 8. Reachable continuum ↔ proof coverage

The derivation states that continuing states consist of the axes together with the interior triangle

\[
p>0,\quad m>0,\quad p+m<h-2k=4.
\]

`geometry.py:12–20` encodes this reachable closure.

The proof-critical residual range checker uses

\[
p=rt,\qquad m=r(1-t)
\]

and covers:

- \(0\le r\le1\);
- \(1\le r\le4\);
- plus-axis tail \(4\le p\le5\);
- minus-axis tail \(4\le m\le5\).

See `residual.py:293–325` and the returned coverage metadata at
`residual.py:398–404`.

**Assessment:** PASS.

The residual bound is therefore over the claimed reachable continuum rather than merely over sampled states.

---

## 9. Exact candidate ↔ residual proof role

`residual.py:24–38` constructs floating spectral candidates and then serializes them as exact dyadic coefficients.

The artifact explicitly labels their role:

> `EXACT DYADIC CANDIDATE; VALID ONLY AFTER RESIDUAL CERTIFICATION`

The proof does not infer correctness from the candidate solve itself. The candidate is accepted only after its continuum residual is rigorously bounded.

**Assessment:** PASS.

This correctly separates heuristic candidate construction from proof evidence.

---

## 10. Continuum residual bounds ↔ artifacts

`certify_continuum_residuals` (`residual.py:337–405`) reconstructs the exact dyadic candidates, symbolically forms the Bellman residuals, bounds them over the reachable continuum using Bernstein range bounds, and adds the rigorous Gaussian-density approximation remainder.

The stored artifact reports

\[
\delta_a
\approx 8.46346\times10^{-6},
\]

\[
\delta_b
\approx 2.06165\times10^{-4}.
\]

These values are exactly the quantities consumed by the enclosure propagation.

**Assessment:** PASS.

---

## 11. Block contraction ↔ resolvent

The final certificate uses the sharper monotone contraction artifact, not the older coarse Gaussian block-sum bound.

`contraction.py:49–126` constructs a one-sided CUSUM hitting-probability lower envelope with Arb arithmetic.

The mathematical logic encoded in the artifact is:

1. one-sided upper-chart hitting probability is nondecreasing in the starting chart state;
2. left-cell values therefore form a continuum lower envelope, rather than a sampled approximation;
3. an upper-chart hit forces absorption of the two-sided CUSUM;
4. hence
   \[
   \sup_s K^n1(s)\le1-q_{\rm safe};
   \]
5. consequently
   \[
   \|(I-K)^{-1}\|_\infty\le n/q_{\rm safe}.
   \]

The stored artifact gives

\[
C=1315.7894736842\ldots
\]

and the certificate reads this exact contraction artifact.

**Assessment:** PASS for proof-to-code correspondence.

The validity of the monotonicity argument belongs to the mathematical audit layer; the present audit confirms that the code and certificate implement the argument that the derivation claims.

---

## 12. Residual propagation ↔ \(\Gamma\) enclosure

The derivation uses

\[
E_a=C\delta_a,
\]

\[
E_b=C(\delta_b+\mu E_a),
\qquad
\mu=\sqrt{2/\pi},
\]

then

\[
\Gamma\in
\hat b(0,0)+[-E_b,E_b].
\]

`enclosure.py:14–47` implements exactly this chain:

- loads `delta_a`;
- loads `delta_b`;
- loads `b_hat_origin`;
- reconstructs \(C=n/q_{\rm safe}\);
- sets `mu = sqrt(2/pi)`;
- computes `e_a`;
- computes `e_b`;
- forms `gamma = b_origin + [-E_b,E_b]`;
- requires `gamma > 2`.

The stored values are

\[
E_a\approx0.01113613,
\]

\[
E_b\approx11.96251691,
\]

and

\[
\Gamma\in
[3.924348200582897\ldots,\,
27.849382127546703\ldots].
\]

**Assessment:** PASS.

---

## 13. \(\Gamma=b(0,0)\) ↔ certificate target

The derivation explicitly defines

\[
H(s,x)=a(s)x+b(s)
\]

for

\[
H(s,x)=E[Z_\tau T_\tau\mid S_t=s,T_t=x].
\]

At the initial state \(s=(0,0),x=0\),

\[
\Gamma=E[Z_\tau T_\tau]=b(0,0).
\]

The certificate records:

- `"target": "E[Z_tau*T_tau]"`
- `"state_reduction": "...=a(p,m)*x+b(p,m)"`
- `"target_state": "Gamma=b(0,0)"`

and obtains its center from the residual artifact's `b_hat_origin`.

**Assessment:** PASS.

There is no target substitution such as certifying an ARL, \(E[Z_\tau^2]\), or a finite-grid Bellman value and relabeling it as \(\Gamma\).

---

## 14. Certificate assembly ↔ proof artifacts

`certificate.py:15–21` freezes five required artifacts:

1. `candidates.json`
2. `contraction_monotone.json`
3. `residual.json`
4. `enclosure.json`
5. `bellman_crosscheck.json`

`certificate.py:32–47` refuses assembly if an artifact is absent and refuses the result if the enclosure does not prove `gamma_lower_gt_2`.

The uploaded `certificate.json` reports:

```text
Gamma_lower =
3.924348200582897128185777546605095267...

Gamma_upper =
27.849382127546703280529527546605095267...

result = Gamma_lower > 2
proof_status = CERTIFIED
```

I independently recomputed SHA-256 hashes of all five referenced artifacts from the uploaded ZIP. **All five hashes exactly match the certificate.**

**Assessment:** PASS.

---

## 15. Replay auditor ↔ certificate

`audit.py:30–110` does not merely read the stored final inequality.

It:

1. validates schema/model/target;
2. rehashes every proof artifact;
3. recomputes the monotone contraction;
4. in full mode reconstructs the continuum residual from the exact candidate;
5. redoes residual-to-resolvent propagation;
6. requires the replayed lower endpoint to exceed two;
7. checks the finite Bellman result lies inside the certified interval.

The final certificate's `proof_status="CERTIFIED"` and independent-audit metadata are therefore downstream of a replay mechanism that is source-connected to the same proof objects.

**Assessment:** PASS.

---

## 16. Hash integrity check performed in this audit

All certificate-declared artifact hashes matched the uploaded files:

| Artifact | SHA-256 match |
|---|---|
| `bellman_crosscheck.json` | PASS |
| `candidates.json` | PASS |
| `contraction_monotone.json` | PASS |
| `enclosure.json` | PASS |
| `residual.json` | PASS |

This rules out a simple artifact/certificate substitution inside the supplied archive.

---

## 17. Environment qualification

I attempted to launch the repository's replay auditor in the present ChatGPT execution environment.

It stopped immediately because this sandbox does not have the `flint` Python module installed:

```text
ModuleNotFoundError: No module named 'flint'
```

I did **not** install or modify the uploaded repository during this Step-3 audit.

This does not change the source-correspondence verdict. It only means this specific environment did not provide a second fresh Arb execution.

The earlier independent external check already reported a fresh installation of `python-flint`, 90 passing tests, stored-audit replay, and fresh certificate regeneration reproducing the certified lower endpoint.

---

## 18. Hostile mismatch checklist

| Failure mode | Result |
|---|---|
| Wrong CUSUM recursion | NOT FOUND |
| Pre-update vs post-update alarm mismatch | NOT FOUND |
| Strict vs inclusive threshold mismatch affecting the implemented convention | NOT FOUND |
| Terminal increment omitted from \(T_\tau\) | NOT FOUND |
| Terminal reward implemented as \(Z_\tau T_{\tau-1}\) | NOT FOUND |
| Wrong continuation endpoints | NOT FOUND |
| Wrong sign in reflected minus chart | NOT FOUND |
| \(K_z a\) missing | NOT FOUND |
| \(r_b\) missing \(z^2\) absorption | NOT FOUND |
| Candidate numerical solve treated as proof | NOT FOUND |
| Residual checked only on sampled grid | NOT FOUND |
| Certificate target differs from \(E[Z_\tau T_\tau]\) | NOT FOUND |
| \(\Gamma\) taken from finite Bellman cross-check | NOT FOUND |
| Stored artifact hashes inconsistent with certificate | NOT FOUND |
| Auditor only trusts stored final interval | NOT FOUND |

---

# 19. Final Step-3 decision

\[
\boxed{\textbf{PROOF-TO-CODE CORRESPONDENCE: PASS}}
\]

with the narrow environmental qualification that no new Arb execution was possible inside this sandbox because `python-flint` is absent.

No source-level defect was found that threatens the frozen CUSUM Level-3 theorem.

Combining the evidence currently available:

\[
\boxed{
\begin{aligned}
\text{Blind re-derivation} &:\ \mathrm{PASS}\\
\text{Hostile mathematical audit} &:\ \mathrm{PASS\ with\ nonfatal\ corrections}\\
\text{Proof-to-code correspondence} &:\ \mathrm{PASS}\\
\text{Fresh executable certificate replay} &:\ \mathrm{PASS\ (external\ independent\ run)}
\end{aligned}}
\]

Therefore the CUSUM core is now strong enough to designate:

\[
\boxed{\textbf{LEVEL-3 MATHEMATICAL BASELINE: FROZEN}}
\]

for the specific theorem actually established:

> For the frozen Gaussian two-sided CUSUM configuration \(k=0.5\), \(h=5\), \(m=1\), the audited computer-assisted continuum certificate establishes \(\Gamma>2\). Together with the separately audited stopped-score identity \(F_1'(0)=1-\Gamma\), this yields \(F_1'(0)<-1\) and hence local instability of the centered reference fixed point under full stopping-selected reuse. The exact mixed-reuse derivative scaling then yields a nontrivial local critical reuse fraction.

This freeze **does not** promote any broader claim about arbitrary \(m\), arbitrary \((k,h)\), global nonlinear bifurcation, rigorous period-2 existence, or universal detector independence.

Those remain Level-4 extension questions.

---

## 20. Recommended repository record

Preserve this audit beside the other mathematical verification records and do not silently rewrite it after future Level-4 work. If a later audit discovers a shared defect, supersede the baseline explicitly with a dated amendment rather than editing the historical PASS record.
