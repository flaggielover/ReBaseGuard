# P7 provenance

Machine-readable copy: `PROVENANCE.json` (53 campaign files hashed).

* Python 3.14.5, numpy 2.5.2
* Seed family `20260831` (Stage D uses `20261001`; no overlap)
* Detector codes `{'cusum': 11, 'sr': 13}` — fixed integers, because Python salts `hash(str)` per process

## Seed derivation

* stage `2`: `chain sweep  [SEED_FAMILY, 2, detector_code, m, round(rho*1e7)]`
* stage `3`: `response curves  [SEED_FAMILY, 3, detector_code, sign, round(|x|*1e6)]`
* stage `5`: `delay validation  [SEED_FAMILY, 5, detector_code, m, round(rho*1e7), round(Delta*1000)]`
* stage `7`: `gain correspondence  [SEED_FAMILY, 7, detector_code, batch]`
* stage `adversarial replication`: `seed family 20260901, stage 2 (deliberately outside the production family)`
* stage `independent adjudication`: `seed family 20260917, stages 71/72`

## Read-only inputs (never modified)

| path | sha256 |
|---|---|
| `level4/closure_proofs/m_rho_stability_priority3/results/boundary_table.json` | `f59d85070c76b53f...` |
| `level4/closure_proofs/m_rho_stability_priority3/THEOREM.md` | `88f0544d294e919d...` |
| `level4/closure_proofs/m_gt_1_priority1/THEOREM.md` | `c630051d710361b4...` |
| `level4/closure_proofs/sr_derivative_priority2/THEOREM.md` | `4af4e721375e8462...` |
| `level4/stage_d/STAGE_D_PROTOCOL.md` | `925adecf08c72343...` |
| `level4/stage_d/src/chain.py` | `84d354a67d23c33e...` |
| `level4/stage_d/src/stopped.py` | `7224bfec8bf0473c...` |
| `level4/src/rebaseguard_level4/frozen.py` | `777681ea32842ff4...` |
| `level4/stage_d/results/calibration_d1.json` | `f623fcc8a140387f...` |
| `level4/stage_d/results/d2_5_verdict.json` | `1da3f04401cf9eaf...` |

## P4

P4 remains **PARTIAL** and is not a premise. Its adjudicated 1.6-million-path SR replay is used only as supplementary diagnosis; P7 closure rests on the closed P1--P3 artifacts.

## Sample sizes

| experiment | size |
|---|---|
| chain sweep | 104 cells x 5,000 replicates x 50 cycles (38 post burn-in) |
| response curves | 4x10^5 paths for `|x| <= 0.15`, 2x10^5 to `0.5`, 10^5 beyond; 34 grid points per detector |
| delay validation | 8 cells x 40,000 replicates, shift at cycle 25 |
| gain correspondence | 20 batches x 100,000 cycles per detector |
| adversarial replication | 6 cells x 5,000 replicates, independent seed family |
| independent adjudication | 16 in-control cells x 2,500 replicates; 2 delay cells x 30,000 replicates |
