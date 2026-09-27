# STREAM C2a PROGRESS — cell 308 exclusion question (THEORY + PROTOCOL ONLY)

Scope: no computation at any drift; no new quantity for cells 305-309 (Q1/Q2).
Sibling C2b owns A0X/gen/ — not touched by C2a.

## Log
- step 0: skeletons created (EXCLUSION_308.md, FREEZE_308_EXCLUSION_PROTOCOL_DRAFT.md, C2A_ROUTE_SUMMARY.md).
- step 1: read PREAMBLE, NS README, quarantine + amendment, graph_C §1.4/§5, THEOREM_AD §3, C4_TARGET_RECONSTRUCTION (full),
  ADJUDICATION_C8:262-275/376-386, C7 README + ledger ceiling, P5X R1 PROOF M2, P5X DEFECT_REGISTER D3, P5 LIMITATIONS §3.
- KEY FINDING (theory, to be written as Theorem M): from the atom, the two-sided CUSUM is an exact V-mask:
  tau>n iff |S_t-S_s| <= H+K(t-s) for all 0<=s<t<=n (S_t=sum z_i, S_0=0). Survival set A_n is a centrally symmetric convex
  polytope; S = R - e*(1..n) with R Gaussian (symmetric, log-concave). Anderson (1955) => P_e(tau>n) nonincreasing in |e|
  for every n => E_a[tau](e) even and nonincreasing in |e|. Resolves C4's caveat (Lambda_k = E_a[tau](e_lo) for e_lo>=0)
  and P5's open claim sup_e E[tau|e]=E[tau|0] (ATOM START ONLY; D3/L4's sup_x version NOT implied).
- Quantifier: A0 admissible iff A0 >= sup_{e in cell} E_a[tau](e) (C4_TARGET_RECONSTRUCTION.md:10-16). Prove X308 needs one
  point; refute needs sup => without Theorem M one drift does NOT suffice; with Theorem M the single drift e_lo suffices.
- E2 family ceiling 4.679910340 was evaluated at e = 19839101/10000000 = right endpoint of cell 308 (C7_LEDGER.json).
- step 2: EXCLUSION_308.md §0 (facts F1-F17 with file:line) and §(a) (X308 exact, sup quantifier, negation) WRITTEN.
- step 3 (plan): write §(c) Theorem M (Lemma V V-mask, Lemma S survival set, Anderson), corollaries, NOT-implied list,
  analytic negative control (non-atom start: one-step survival d/de at e=0 = phi(C-p0)-phi(C) > 0 for 0<p0<2C),
  proxy prohibition (Theorem M turns every drift into a one-sided bound on Lambda_308 -> quarantine-policy flag).
- step 4: §(c) WRITTEN: Theorem M proved (V-mask Lemma V + symmetric convex survival set + Anderson 1955; Prekopa
  alternative), corollaries M1-M4, not-implied list with analytic negative control, proxy prohibition c.9, validation c.10.
- step 5: §(b) WRITTEN (proof/refute certificates, family ceilings table, one-drift question, completeness, b.4 comparator not certified).
- step 6: §(d) WRITTEN (D1-D8 consistent; wording issue: C8 R3 'closes 308' is conditional on not-X308).
- step 7: §(e) WRITTEN. EXCLUSION_308.md complete (pending self-review).
- step 8: read C2b gen/ skeleton (read-only): P1 family on anti-diagonal triangulation, exact vertex margins, structural
  lemma K_e w(p,m) = Psi_w(p+m, p-K-e) => block-uniform check possible. Read C8_DECISION.json 308 block:
  max_admissible_A0 (A1,A2 at committed operator-mixed) = 3.270701093 < floor 3.512733596 => under committed A1/A2 NO
  admissible A0 closes 308 => a certified U carries no new Gamma-sign info under committed supplies (leakage analysis).
- step 9: writing FREEZE_308_EXCLUSION_PROTOCOL_DRAFT.md.
- step 10: FREEZE_308_EXCLUSION_PROTOCOL_DRAFT.md WRITTEN (DRAFT ONLY banner; P1-P5; variants P/B; two-sided enclosure; A0* bracket stage; decision table; C12-R2 mechanics; leakage: U is a Gamma INPUT, not proxy; no sign info under committed A1/A2 since C8 max_admissible_A0 3.2707 < floor 3.5127; risk MEDIUM).
- step 11: C2A_ROUTE_SUMMARY.md WRITTEN. Self-review of citations done (line numbers re-verified by grep/sed).
- DONE. Files: EXCLUSION_308.md, FREEZE_308_EXCLUSION_PROTOCOL_DRAFT.md, C2A_ROUTE_SUMMARY.md, PROGRESS.md.
  No code written or run; no ledger entries (no substantive executions); gen/ (C2b) not touched (read-only listing).
- step 12: coordinator S8 received (no new-route result next to/combined with committed tail-cell factors/margins; no outcome estimate). Auditing all files.
- step 13: S8 corrections applied in all three deliverables, each marked [S8-corrected], with a correction notice at
  the top of each file and a table in C2A_ROUTE_SUMMARY.md §6. Withdrawn: outcome estimates for X308 (Theorem M + MC + A0*),
  use of 306-309 committed MC/diagnostics as Theorem-M evidence (old c.10, D3), the entailed 308 floor from C7's 309
  number, committed tail factors in own reasoning (C4 Cond. 3 factor, C5-T consumed-margin share, C8 A1 figure, A1/A2 values).
  Classification is now outcome-neutral: BOUNDABLE now; DECIDABLE in principle (either direction); L/R4 cannot prove it.
