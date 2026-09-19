# Independent adjudication — brief (sealed theorem-TC successor, CUSUM K5 lower front)

You are a fresh-context adjudicator. You did not write the successor, did not review it before the freeze and did not
authorize it. Verdict: ADOPTED or NOT_ADOPTED. Only an ADOPTED result may change the authoritative coverage map.

Repository: the worktree /Users/suzhe/ReBaseGuard-k5lf (branch p5y-postk1-frontier history); namespace
`level4/closure_proofs/p5y_k5_lower_front_order3/`. Commits: gates e89b33f2, freeze (adds `config/TC_PROTOCOL.json`),
qualification, authorization, guard ALLOW, seal (evidence under `evidence/tc_r1/`, GUARD back to DENY), consumption.
Their hashes are listed in `evidence/tc_r1/` (QUALIFICATION_RESULT, AUTHORIZATION, SEAL.json).

Reproduce rather than trust. You may run pure-Python code locally (python3). The sealed K1 records needed by the
consumer live only on the compute host; you may NOT run anything remote. Where a check needs the host, say so and
check what you can locally (the consumption output records the index sha, governance context and acceptance counts).

Check at least:
1. Commit order and confinement: gates → freeze → qualification → authorization → guard → seal → consumption, each an
   ancestor of the next (`git merge-base --is-ancestor`); after the freeze nothing outside `evidence/tc_r1/` changes;
   the adopted namespaces (Perron, T-EXT, slot-1, K1 closure, coverage map r3) are byte-unchanged since 7cb01e38.
2. Protocol pins and runtime: every pin matches at the seal; the qualification ran at the freeze commit and passed S00–S09.
3. Seal integrity: every cell file sha equals TC_INDEX; the reproduction files equal the first run for cells 11 and 44;
   the ledger has one START/ok OUTPUT per address and a RUN_END with identical reproduction; each record's binding
   (protocol sha, freeze, authorization sha, run head with ALLOW guard, K1 record sha) is consistent with the history.
4. Theorem usage: recompute, INDEPENDENTLY of `tc_rule.py` and `tc_crosscheck.py` (write your own code from
   `theorem/THEOREM_TC.md`), the enclosure H_TC,m(k) for every cell 11–44 and m ∈ {1,2,3,5} from the sealed records and
   the A-constants (from the adopted registry r1 with the adopted block rule, or the values recorded in the consumption's
   `tc_audit`, which must equal the adopted `DEFLATED_CONSUMPTION.json` audit values). Compare exactly with the sealed
   consumption's `tc_audit`.
5. Pass/open derivation: run the frozen K5-B (`p5y_k5b_independent_countersignature/code/k5b_check.py`, pinned
   ddd54dc4) yourself on the adopted cells 0–159 (`DEFLATED_CONSUMPTION.json`) with H_k ← H_k ∩ H_TC,m(k) on cells
   11–44 and the adopted T-EXT channel, and compare the pass sets and `via` with the sealed consumption for cells 0–159.
   Confirm that no previously passing cell regresses.
6. Cell and m mapping: geometry (e0, ρ) of each record equals `cells.json`; the assembly coefficients equal the frozen
   table.
7. Mutation/falsification evidence: the qualification's manufactured suite (0 violations, 20/20 mutants) — read it and
   judge whether it is capable of failing.
8. Historical immutability and scope: K5 status wording (PARTIAL unless every cell of every m passes, including the m5
   tail 305–309, which this successor does not touch).

Write `evidence/tc_r1/adjudication_r1/ADJUDICATION_R1.md` (checklist table with PASS/FAIL and evidence, notes, verdict line
`ADJUDICATION = ADOPTED` or `ADJUDICATION = NOT_ADOPTED`) and `ADJUDICATION_R1.json` (machine-readable). Do not modify
any other file; do not commit.
