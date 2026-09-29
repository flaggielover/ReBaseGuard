# Incident 309R1-03: unsanctioned in-band verifier probe, refused at parse time (nothing evaluated)

| field | value |
|---|---|
| found | 2026-09-30 ~00:1xZ, by the coordinator while closing review R2 condition C4 (`code/verifier_probe_envelope.py`) |
| what | Harness v1 of the independent verifier (`verify/run_verify_all.py`, sha 54840bf4…) built its item-7 probe "7h non-dyadic drift" by shifting `block` by +1/3 without checking the quarantine band. On the real-kernel decoy block E = [1, 33/32] this gives the probe block [4/3, 131/96], which lies inside the band [6/5, 13/5]. It affected 5 certificates (h5 E[1,33/32], indices 0–4) |
| outcome | All 5 were **REFUSED at parse time** ("malformed: weight_block does not contain block"), because v1 did not move `weight_block` with `block`. The `Cert` constructor raises before any evaluation. Had the probe passed parsing, the verifier's hard-coded quarantine refusal, which also runs before any evaluation, would have refused it too |
| information | **None.** No kernel, resolvent, certificate or Γ quantity was computed at any band drift, so no number exists. The probe relates to no cell (it is a synthetic shift of a decoy block) |
| sanctioned? | No. Only the 7q refusal probe is sanctioned to name a band drift, and only to test the refusal |
| repair | Harness v2 (3455c141…, written by the verifier author) shifts by −1/3 or +1/3, whichever exact rational comparison shows avoids the band. For [1, 33/32] it uses −1/3. v2 has no unsanctioned in-band probe (`evidence/VERIFIER_PROBE_ENVELOPE.json`) |
| liability | **NONE** (no quantity; no target information; no selection effect). Recorded for completeness under the owner's no-concealment rule |
