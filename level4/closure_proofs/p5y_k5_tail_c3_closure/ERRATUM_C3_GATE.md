# Erratum — the frozen C3 gate's description of the inherited adoption floor

The C3 gate is frozen at commit `24c038ec`, sha256
`f0bd87ecaeea4485560969770c95c9d4ad20bceedf9ac7ca11fb6d8d5de53ac7`. **It is not amended.** A frozen
pre-registration is not edited after review, even to correct its prose; the correction is carried here. This is the
precedent C2 set for the same situation and C3 keeps it.

## The defect

`adoption_floor.provenance` says the floor is inherited "verbatim" from the independent C2 adjudicator. The gate's
restatement is a **condensation**, not a transcription, and it drops one clause: the adjudicator conditioned the
F1 disjunct on N9 remaining open — F1 applies *for as long as* no second, independently written certifier exists.

Source of truth is the adjudication itself, `p5y_k5_tail_c2_closure/evidence/adjudication/C2_ADJUDICATION.md`
(sha256 `f37dae47…`), which is immutable and pinned by the C3 B0 audit. Read the floor there, not here.

## Whether anything the gate decides changes

**No.** N9 is open — `p5y_k5_tail_c2_closure/OPEN_NOTES_DISPOSITION_C2.md` records that no second independently
written certifier exists and that C2 did not build one, and C3 has not built one either. The dropped clause is
therefore inert on this campaign's data: F1 applies exactly as the gate states it. The condensation would only
matter to a successor that closed N9 and then read C3's gate instead of the adjudication.

Raised by the pre-forecast review as its note N2, before any C3 forecast existed.

## The other pre-forecast notes, and where they were fixed

| note | finding | disposition |
|---|---|---|
| N1 | `C3_B0_AUDIT.json` stored the vs-**C1** figures under a field named `gap_fall_vs_C2_baseline` | fixed at source: both baselines now computed and labelled separately (`gap_fall_vs_r5_baseline` 0.204579 / 0.079220 / 0.056886; `gap_fall_vs_C1_baseline` 0.572741 / 0.305669 / 0.230323) |
| N2 | this erratum | recorded, gate not amended |
| N3 | `frozen_gate()` / `GATE_SHA` defined in `c3_selector.py` but never called on any path | wired into `c3_forecast.py`, which refuses unless the gate hashes to `f0bd87ec…` |
| N4 | the suite reported "13/13 detected" when the truth is 12 killed + 1 proved equivalent | fixed at source: `killed` and `proved_equivalent` are now separate fields |
| N5 | the tie world's docstring claimed "the registries agree on nothing"; in fact `Abar` is bit-identical between C1 and C2 on all four cells | fixed at source, with the reason the tie world is still needed (Ā is inert, so ties must be exercised on the fields that bind) |
