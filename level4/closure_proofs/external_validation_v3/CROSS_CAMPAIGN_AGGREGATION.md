# Frozen cross-campaign aggregation

This is a decision-counting audit, not a meta-analysis. Each task retains its
own frozen protocol and task-level inference; estimates and samples are never
pooled.

| Campaign | Task | Usability | Minimum effective blocks | Reference distortion | Operational consequence | P2 safety | Joint support | Counts |
|---|---|---|---:|---|---|---|---|---|
| Stage E | Electricity / Elec2 (OpenML 151) | USABLE | 23 | YES | NO | NO | NO | NO |
| Stage E | UCI Air Quality (id 360) | USABLE | 5 | NO | NO | YES | NO | NO |
| Stage E | UCI Bike Sharing (id 275) | PARTIALLY USABLE AFTER FREEZE | 2 | NA | YES | YES | NO | NO |
| V2 | Beijing PM2.5 | USABLE | 20 | YES | YES | NO | NO | NO |
| V2 | Household power | USABLE | 20 | YES | YES | YES | YES | YES |
| V2 | Metro traffic | USABLE | 20 | YES | NO | NO | NO | NO |
| V3 | MetroPT-3 compressor | USABLE | 40 | YES | YES | YES | YES | YES |
| V3 | Online Retail II | USABLE | 40 | YES | YES | YES | YES | YES |

## Mechanical aggregation

- Stage E remains 0/3 and `STAGE-E-PARTIAL`.
- V2 remains 1/3 and `EXTERNAL-VALIDATION-V2-PARTIAL`; Household power is its
  sole joint-support success.
- V3 contributes MetroPT-3 and Online Retail II, both independently gated and
  jointly supportive.
- Cross-campaign success count: 3; frozen requirement: 2.
- Original Level-4 requirement L4R-15, semi-real external validation: `CLOSED`.

The historical negative Stage-E and V2 tasks remain visible above. This later
closure neither modifies their verdicts nor performs a global Level-4 re-audit.
