# Level-4 Priority 2: SR derivative closure

This independent package targets the ordinary Stage-D truncated-window map for
the authoritative reset symmetric two-chart Shiryaev--Roberts detector:

```text
F'_{rho,m}(0)=rho(1-E_0[A_mT_tau]),
w_m=min(m,tau).
```

Start with `THEOREM.md`, `PROOF.md`, and `SR_HISTORY_AUDIT.md`. Run the complete
campaign with:

```bash
bash level4/closure_proofs/sr_derivative_priority2/reproduce.sh
```

Evidence classes remain separate. Frozen infinite-horizon Gaussian SR values
are empirical. Rigorous Arb intervals apply only to the exact finite-support
SR-compatible witness. The historical 52-file guard rejection and later
README archive-hash drift are reported as `HISTORICAL_DIAGNOSTICS`, not hidden.
