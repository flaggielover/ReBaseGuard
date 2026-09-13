# K3 adjudication: binding requirement on `M_2 = sup_e E_e[Rbar²]` (additive closure packet, 2026-09-13)

Separate pass, re-traced from the frozen sources. The same agent wrote the prior back-solve, so a countersignature is recommended. Nothing historical is rewritten.

## 1. Every frozen consumer, with temporal provenance

| date (commit) | record | text concerning `M_2` | requirement |
|---|---|---|---|
| 2026-08-31 (`bb03c0ea`) | P5 THEOREM/PROOF T4, T5 | "`E[Rbar^{2p}\|e] ≤ (2p−1)!! C_D`", with `C_CUSUM ≤ 9.8959e8` and `C_SR ≤ 1.4054e11` | source of the discharge; the P5 independent adjudication lists T4/T5 as authoritative exact premises (P6 handoff item 3) |
| 2026-09-02 (`db0781ed`, P5X anchor) | FROZEN_THEOREM §7 P5X-T6 | "with certified … `M_2 = sup_e E_e[Rbar^2] < infinity`, … `E_π[e²] ≤ ρ²M_2 + (1−ρ)²/m`" | finiteness |
| same | FROZEN_THEOREM §10 P5X-T9(4) | "`E_π[e²] ≤ ρ²M_2 + (1−ρ)²/m`" | finiteness |
| same | FROZEN_GATES G4 | "`s_min > 0` and `M_2 < infinity` are certified … two-sided bound … stated" | finiteness |
| same | EMPIRICAL_PLAN E3 / G9 | measured `E_π[e²]` inside the certified bracket | any valid bound; no tightness |
| same | THEOREM_CANDIDATES Level B; FEASIBILITY_AUDIT §7 | "`M_2 < infinity` certified"; "Crucially the **lower** end is what carries the science" | finiteness; tightness only described |
| same | LEAN_COMPATIBILITY X2 | `g_max` hypothesis | finiteness |
| 2026-09-05 01:54 (`8e888255`) | K1 checkpoint §1 | "`K3` (finite / useful `M_2`)", listed as **out of scope** | "useful" undefined |
| 2026-09-05 11:45 (`17eb58b2`) | FORWARD_AUDIT | "what is open is only whether anything downstream needs a non-vacuous `M2`" | poses the question |
| 2026-09-05 11:54 (`45a82473`) | THEOREM_ADJUDICATION (binding) | `K3_FINITE_BUT_TIGHT_BOUND_STILL_REQUIRED`, reasoning from intent ("named the primary target … to deliver a quantitative sandwich") | tight, with **no consumer, inequality or threshold cited** |

## 2. Ruling

- Every theorem, gate, empirical test and Lean declaration frozen **before** any P5Y label uses `M_2` only through a finite upper bound.
- The "useful/tight" language appears later, first as an undefined adjective inside a P5Y out-of-scope list, then as TA's intent-based reading. Neither defines a criterion, and neither cites a consumer.
- A requirement with no criterion cannot be adjudicated mechanically. Supplying one now would manufacture a new obligation.
- TA's own finding that "finiteness is closed by P5-T5" stands. Its "tight bound still required" clause is superseded for lack of a binding consumer. It is not deleted.
- `M_2 ≤ 100·s_min` is **not** adopted: no binding consumer requires it.

## 3. Discharge (independently re-verified)

P5-T4 (block argument; `E_e[τ] ≤ C_D` uniformly in `e`) and P5-T5 (Jensen, `Rbar² ≤ Σ_{t≤τ} raw_t²`, then Wald/Tonelli) give, exactly and for every `D, m, e`:

```text
E_e[Rbar²] ≤ C_D,   so   M_2(D,m) ≤ C_D < ∞,   C_CUSUM ≤ 10/Φ(−1)^10 = 9.8959e8,   C_SR ≤ 1/Φ(−(log A + 1/2)) = 1.4054e11.
```

The certification semantics are the same as in K2 §4: an exact theorem with explicit constants, and the same G4 precedent.

```text
K3_BINDING_REQUIREMENT                     = FINITENESS_ONLY
K3_EXISTING_THEOREM_DISCHARGES_REQUIREMENT = YES  (M_2 ≤ C_D; P5-T4/P5-T5, exact, adjudicated premises)
K3_FINAL                                   = CLOSED
```

Consequence, not a claim: P5X-T6's upper arm with `M_2 = C_D` is numerically vacuous. This is recorded as a property of the theorem, not as an open obligation.
