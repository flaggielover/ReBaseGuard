# Stream B_307 — progress log

| utc | step | state |
|---|---|---|
| 2026-09-27T18:18Z | VALIDATION_DECLARATION_B307.json written (rules for FX_A, FX_B, lower front, Gaussian identity) before any run | done |
| 2026-09-27T18:25Z | code: b307_lib.py (fixtures, point objects, ladders, cell bounds, TC arithmetic), b307_cellpipe.py, b307_order3.py, b307_run_fixtures.py | written, lib selftest PASS |
| 2026-09-27T18:40Z | deliverable skeletons created | done |
| 2026-09-27T18:50Z | b307_lower_front.py run: exact TC reproduction 136/136, planted 2^-60 perturbation detected; 170 objects compared (real G vs zero-candidate surrogate) -> validation/B307_LOWER_FRONT_ORDER3.json | done |
| 2026-09-27T18:52Z | coordinator suggestion ADLR (atom-direct LR Taylor enclosure) received; to be added to b307_order3 as an extra route family on fixtures | in progress |
| 2026-09-27T18:58Z | first fixture run (no ADLR) PASS: P1 identities 7/7 + NCs detected; ladders 0 rung failures; 64 cells x 5 objects x 4 routes, 0 identity/soundness failures; NC flip 328/640, NC E10 146/320 detected; props RO3-E/RO3-F hold | superseded by run 2 (same code + ADLR) |
| 2026-09-27T19:00Z | run 2 launched (ADLR added: G certified / PM / true / oracle variants) | running |
| 2026-09-27T19:10Z | b307_hermite_check.py: Hermite/LR identity one-step 240 cases worst rel err 1.6e-15, j-step 100 pts 4.4e-13; NCs 112/120 and 225/300 detected (undetected = odd derivatives vanishing by symmetry, and n = 1 where the variance rescaling is the identity) -> validation/B307_HERMITE_IDENTITY.json | done |
| 2026-09-27T19:12Z | b307_tower_fixture.py: J/h tower sound on FX_B; tower/true at n=3: h_2 3.1-3.8, h_3 9-12, h_4 24-38, S_4 47-77; NC (binomials dropped) detected 6/54 -> validation/B307_TOWER_FIXTURE.json | done |
| 2026-09-27T19:15Z | HIGHER_ORDER_AUDIT_307.md sections 0-2 written | done |
| 2026-09-27T19:20Z | run 2 (with ADLR) PASS, 362 s: P1 7/7 + 7/7 NC; P2 42 points 0 rung failures, SM exact, NC A0:=tau_a 42/42; P3 64 cells/320 objects/4 routes/17 grid pts: 0 identity, 0 soundness, premises hold, 0 Env4 failures; NC flip 328/640, NC E10 146/320; O3: F''' atom identity exact, all direct levels sound, RO3-E and RO3-F hold; ADLR-G 0 failures, NC B3-dropped 247/320 | done (supersedes run 1) |
| 2026-09-27T19:22Z | b307_scaling.py: FX_B slopes vs Lambda at e=0: true A1 1.50, A2 2.00, A3 2.49 vs G/PM 2, 3, 4 (Dv' 1.91, 2.83); at e=1/4, 1/2 true A1 1.37/1.23, A2 1.85/1.57 vs G 2/3, Dv' 2.16-2.18/3.37-3.42 | done |
| 2026-09-27T19:23Z | FX_B structural degeneracy found and kept: F_r'''(e0)(a) = 0 exactly for 56/80 FX_B objects (F_0(a) = 1 and F_1(a) = 1 - p_0(e) identically; all r at e0 = 0) -> FX_B alpha statistics are degenerate; FX_A is the representative class for alpha | recorded |
| 2026-09-27T19:24Z | ov_quarantine --scan: 8 B_307 files scanned, 0 findings in B_307, planted control detected (one finding elsewhere: streams/A_306/audit/a306_reproduce_A.py TARGET_INPUT_PATH, not this stream) | done |
| 2026-09-27T19:35Z | HIGHER_ORDER_AUDIT_307.md complete (sections 0-7) | done |
| 2026-09-27T19:45Z | REAL_ORDER3_THEORY.md sections 1-2 written | in progress |
| 2026-09-27T19:47Z | REAL_ORDER3_THEORY.md section 2 done (stray heredoc lines removed) | in progress |
| 2026-09-27T19:55Z | REAL_ORDER3_THEORY.md sections 3-4 written | in progress |
| 2026-09-27T20:05Z | REAL_ORDER3_THEORY.md complete (sections 1-7) | done |
| 2026-09-27T20:10Z | B_307_ROUTE_SUMMARY.md written (registry rows, gate table, 307 per-cell deliverable) | done |
| 2026-09-27T20:20Z | incident-01 correction (coordinator, binding): tail-cell shares removed from every place adjacent to route/synthetic factors (audit sections 2-6, REAL_ORDER3 section 4c, summary per-cell section); ranking now structural only; history kept in separate sections; correction notes added to all three documents | done |
