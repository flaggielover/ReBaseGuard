# K1 INDEPENDENT ADJUDICATION CONTRACT  (binding, frozen at T1)

The producing script may **not** self-award `K1_CLOSED`. A verdict of
`K1_CLOSED` is valid only if an adjudicator that is **not** the producer
verifies every item below and writes `adjudication/ADJUDICATION_VERDICT.json`.
Any `NO` forces `K1_FAIL_GOVERNANCE` (or the more specific class in §24 of
`CHECKPOINT.md` when one applies).

## A. Provenance and integrity
```text
A1  the run's checkpoint SHA-256 matches manifests/CHECKPOINT_HASH.json
A2  the run's anchor commit is an ancestor of the run commit
A3  every protected input digest in manifests/protected_inputs.json is unchanged
A4  no tracked file outside {results,certificates,logs} was written
A5  no post-freeze amendment to CHECKPOINT.md or config/*.json
A6  hashes were taken from `git ls-tree` at the anchor commit, not the worktree
```

## B. Scientific scope
```text
B1  exactly 2 detectors, matching FROZEN_SCOPE.md verbatim (k, h, A, conventions)
B2  exactly m in {1,2,3,5}; all 8 (D,m) cells present; none deleted post-result
B3  the assembly used is the frozen general formula of CHECKPOINT.md 3
B4  no scope narrowing, no m-specific exclusion, no detector dropped
```

## C. Cover and splice
```text
C1  cover cell count matches manifests/cover_*.json
C2  exact tiling: no gap, no overlap, endpoints meet
C3  no adaptive splitting occurred
D1* numerics reach e_star_D EXACTLY; far-field starts exactly there
D2* B_D certified on [c_D, c_D+1] and monotone beyond; sup < 2
D3* the splice covers every m simultaneously (w = min(m,1) = 1 on {tau=1})
D4* e < 0 discharged by the exact oddness P5-T3, not by recomputation
```

## D. Budget and metric
```text
E1  the ABSOLUTE metric of CHECKPOINT.md 6 was used; the relative P2 gated nothing
E2  per-component usage <= per-component absolute budget, every cell
E3  no redistribution between components; the 0.010 reserve untouched
E4  the m=1 tightening (6.1) was applied: coefficient 1, not Gate-2E's 1/2
E5  C_D evaluated at e_lo of each cell
E6  arithmetic: sum(allocated) = 0.190 <= w_target = 0.200
```

## E. Numerical governance
```text
F1  direction audit PASS for BOTH detectors before any cell ran
F2  C is an UPPER bound; C(0) <= the certified 25000/19 cap; C non-increasing in e
F3  no use of the unproved sup_e E[tau|e] = E[tau|0] (P5X defect D3)
F4  candidate identities recorded; degrees within the frozen bidegree families
F5  complexity score <= 60000 on every composed-contraction invocation, and the
    guard fired BEFORE kernel construction
F6  working precision exactly 256 bits; P1 rule target evaluated inside
    workprec(512); no escalation, no degree adaptation
F7  P1 rule target and check threshold are DISTINCT; headroom_rel > 1e-6
```

## F. Work conservation and accounting
```text
G1  sum of shard sizes == 12255 exactly; no overlap; no omission
G2  every unit individually recomputable from its stored record
G3  aggregation identity: recomputing from per-unit artifacts reproduces the hull
G4  CPU ledger total <= 1848 CPU-h; no hidden retries, no silent substitutions
G5  no Monte Carlo value appears in any certificate or verdict path
G6  every uncomputed cell marked NOT_COMPUTED explicitly, never absent
```

## G. The theorem itself
```text
H1  for each (D,m): max( compact sup enclosure , far-field majorant ) < 2 strictly
H2  the inequality is strict and certified, not a midpoint comparison
H3  the required artifact set is complete
H4  K1_CLOSED does NOT recolour P5 or P5X (CHECKPOINT.md 17)
```

`(*)` items C/D are numbered D1..D4 within section C for the splice.
