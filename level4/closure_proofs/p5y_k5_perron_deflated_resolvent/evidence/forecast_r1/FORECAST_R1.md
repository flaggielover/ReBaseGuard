# Forecast r1 — NON-CERTIFIED (float operator constants)

Label: **FORECAST**. The operator constants are float values (`OPERATOR_FLOAT_PROFILE_deg20.json`) with margins, not
certificates. Everything else is exact: the registered consumer (`code/deflated_consume.py` @ f0231499) applied the
theorem AD rule to the manifest-bound K1 records (manifest `29ad1f9b`, 310 records) on vultr-02, intersected with the
adopted T-EXT C2 channel, and ran the frozen `k5b_literal`. No model evaluation, no R value computed, nothing sealed.

## Open front cells after deflation, by constant scale s (C_T and τ multiplied by s)

| s | m = 1 | m = 2 | m = 3 | m = 5 |
|---|---|---|---|---|
| 1.0 | 11–32 | 11–39 | 11–40 | 11–41 |
| 1.3 | 11–38 | 11–45 | 11–46 | 11–48 |
| 2.0 | 11–54 | 11–61 | 11–62 | 11–63 |
| 3.0 | 11–95 | 11–100 | 11–97 | 11–97 |
| 5.0 | 11–119 | 11–135 | 11–136 | 11–140 |
| 10 | 11–132 (no change) | 11–144 | 11–145 | 11–148 |

The m = 5 tail 305–309 is untouched in every run (outside the deflation domain; different mechanism).
s ≈ 1.3 is the expected certification loss (the adopted R3 atom-taboo certificate is 20.43 against a float 15.8).

## What binds on the remaining lower front (s = 1.3)

| m = 1 cell | e0 | g centre | g half-width | R half-width | R' half-width | ρ·x·M | Γ |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 11 | 0.0060 | −1.6e-4 | 3.1e-3 | 2.5e-3 | 0.095 | 4.8e-4 | +3.4e-3 |
| 25 | 0.0137 | −1.9e-3 | 3.8e-3 | 2.5e-3 | 0.098 | 1.4e-3 | +3.3e-3 |
| 38 | 0.0213 | −7.2e-3 | 4.6e-3 | 2.5e-3 | 0.099 | 2.6e-3 | +6.6e-5 |
| 39 | 0.0219 | −7.8e-3 | 4.7e-3 | 2.5e-3 | 0.099 | 2.7e-3 | −3.8e-4 (direct) |

- The R half-width is the order-0 floor E_a[τ]·‖residual‖ (Lemma SM(d)), at most ≈ 1.3× the sharp value. It is
  larger than |g| up to e ≈ 0.014 (m = 1) and e ≈ 0.023 (m = 5, where five F objects add). No deflation can move this.
- The whole-cell R'' radius (≈ 270 at cell 11 to ≈ 700 at cell 130; K1 had 4000–16700) sets M and keeps H.lo < 0, so
  the K5-B chain cannot carry from the T-EXT cell 10 through the lower front.
- Compared with K1: R' half-width 3.7–9 → ≈ 0.1 (×40–90), R'' radius ×15–25, R half-width ×2.6.

## Consequence for the gates (frozen in `config/FEASIBILITY_GATES.json` before any certified computation)

STRONG is unattainable by this route; USEFUL needs the certified constants within s ≤ 2.4 of the float profile; the
lower front (about 22–38 cells per m) needs order-3 information beyond e = 0, which is a different route.
