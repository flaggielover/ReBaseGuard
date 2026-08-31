# Handoff note for Priority 5 (nonlinear / global dynamics)

Priority 4 is a **local, first-order** campaign and deliberately proves nothing
about global or nonlinear behaviour.  The following observations fell out of it
and may save Priority 5 some work.  None of them is a result, and none is
supported by evidence collected for that purpose.

1. **The map is genuinely nonlinear in `e` for every family.**  Route Q
   evaluates `g_m(e)` exactly at any `e`, at negligible cost, for the
   memoryless detector.  That gives Priority 5 a cheap, non-Monte-Carlo
   playground in which the full map — not just its derivative at a point — is
   available to machine precision, including for asymmetric families.

2. **Theorem G1' already gives the multiplier at any base point.**  Priority 5
   needs `F'_{rho,m}(e*)` at a nonzero fixed point, and G1' supplies it as
   `rho(1 - E_{e*}[A_m sum psi(eps_t)])`.  The hypotheses are the same ones,
   re-centred.  Nothing new has to be proved to *linearise* at a period-2
   point; what has to be proved is that the point exists.

3. **Asymmetric families move the fixed point off the origin.**  For the
   standardised skew-normal, `E_0[A_1]` is of order one, so the
   conditional-mean map has a nonzero fixed point even in control.  Priority 5
   should expect the whole orbit structure to be shifted, not merely tilted,
   and should not reuse any centring that assumes an even innovation law.

4. **The Laplace closed form may extend.**  `g_1(e) = -(c+b) tanh(e/b)` for the
   memoryless detector is a bounded, odd, sigmoidal map.  Iterating
   `rho(e + g_1(e))` is a one-line exercise, and it is a genuinely non-Gaussian
   analytic example in which period-2 behaviour can be studied in closed form.
   Whether the same tractability survives the CUSUM is unknown.

5. **`Gamma - 1` is a selection effect (Corollary G2).**  If Priority 5 wants a
   mechanism for the instability rather than a number, the deterministic-
   stopping control shows the entire multiplier comes from the stopping rule's
   selection of which residuals get reused, not from the reuse rule or the
   innovation law.

6. **The short-window correction can have either sign.**  Any Priority-5
   argument that relies on the truncated window making things *worse* is a
   Gaussian argument and will not port.

None of the above is scoped, sized or evidenced here.  Priority 5 should treat
every line as a hypothesis to be designed against, not as an inherited result.
