# External validation V3 results

All values are generated from `results/summary.json`; no cross-task estimate is
pooled. Null and unfavorable routes remain visible.

| Task | E1 P1/P2 ratio [97.5% bounds] | E1 P1/P0 ratio [97.5% bounds] | E2 P1/P2 ratio [97.5% bounds] | E2 P1/P0 ratio [97.5% bounds] | H3-1 | H3-2 | H3-3 | H3-4 |
|---|---:|---:|---:|---:|---|---|---|---|
| MetroPT-3 compressor | 1.308610 [1.158103, 1.481725] | 1.327520 [1.181889, 1.501185] | 1.242105 [1.077670, 1.442862] | 1.282609 [1.117008, 1.486486] | YES | YES | YES | YES |
| Online Retail II | 2.211168 [1.924711, 2.536847] | 2.205489 [1.910373, 2.533894] | 1.183908 [1.084337, 1.291672] | 1.163842 [1.064865, 1.271605] | YES | YES | YES | YES |

## Operational-route audit

H3-2 is supported on both tasks through frozen Route A only. The prespecified
Route B result is unfavorable and is not reclassified:

- **MetroPT-3 compressor:** Route A alert burden=YES; Route B medium-step response=NO; P1/P2=0.774461 [0.607607, 1.000017], P1/P0=0.779893 [0.611082, 0.994590].
- **Online Retail II:** Route A alert burden=YES; Route B medium-step response=NO; P1/P2=0.949921 [0.809278, 1.147217], P1/P0=0.945158 [0.805396, 1.136308].

## Simultaneous P2 non-inferiority

The primary rule requires every upper simultaneous one-sided 99% excess bound
to be at most 0.10:

- **MetroPT-3 compressor:** upper 99% excess bounds: GRADUAL_1.0=0.012077, RECURRING_1.0=0.053597, STEP_0.5=0.047038, STEP_1.0=0.053358, STEP_2.0=-0.000106.
- **Online Retail II:** upper 99% excess bounds: GRADUAL_1.0=0.023169, RECURRING_1.0=0.028986, STEP_0.5=0.026714, STEP_1.0=0.026317, STEP_2.0=0.063651.

Both tasks support H3-1, H3-2, H3-3, and therefore H3-4. V3 joint support is
2/2. The scientific scoped result is `EXTERNAL-VALIDATION-V3-CLOSED`.

MetroPT limitation: the administrative cap is 32 observed hours, shorter than
the 48-hour recurring on-phase. Consequently its recurring and step-1 delays
are identical within the frozen scoring window; this limitation is retained.
