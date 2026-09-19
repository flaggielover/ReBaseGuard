# Disposition of pre-freeze review r1 (verdict NOT_READY)

| id | severity | disposition |
|---|---|---|
| B1 | BLOCKING | Fixed in `code/tc_consume.py`: `check_index` (exactly the 34 addresses under this protocol; reproduction flags 11 and 44 true; reproduction file bytes equal the first run), `crosscheck` (tc_crosscheck loaded from the protocol pin must equal tc_rule on every TC cell and m, else refusal), evidence files must be committed (`committed_bytes`). `tc_run` still writes the index when the reproduction differs (for the record), but the consumer refuses it. Qualification S08(f)(h) exercises each refusal. |
| B2 | BLOCKING | Fixed: `tc_consume.py` takes `--protocol-sha256`, loads tc_rule / tc_crosscheck from the protocol's pins (no CLI sha), compares the index's protocol sha, checks every record's binding (freeze commit from git, committed AUTHORIZATION sha, a committed ALLOW version of GUARD, run head in this history) and the K1 record sha against the protocol (`check_binding`). Qualification S08(g) exercises each refusal. |
| N1 | NOTE (load-bearing) | `G_at_a` (an uncertified order-3 candidate value) is no longer recorded; only δ_mid(G_r) and the upper bound \|Ĝ_r(a)\| are. The parallel channel (Order3Certifier called directly; its registry stays empty) is declared in the protocol (`producer.parallel_channel`) and spec §7a, for explicit acceptance by the authorization review. AUTHORIZATION must carry the committed QUALIFICATION_RESULT sha; GUARD must carry the AUTHORIZATION sha; the producer enforces commit order qualification → authorization → guard (`merge-base --is-ancestor`). |
| N2 | NOTE | Mode real now checks, before computing: runtime equal to the protocol, order-3 producer manifest, Aux5 `manifest_v3.verify()`, pre-registered K1 record sha, and no repository module loaded outside the frozen list (`runtime_checks`); flint threads pinned to 1. |
| N3 | NOTE | Protocol `producer.identity_gate` text states the 53-bit rule for the Aux3 fields. |
| N4 | NOTE | Budget unified: forecast 16.3 CPU-h from the measured dev replays (`evidence/forecast_r1/COST_NOTE.md`), protocol cap 24 CPU-h, 4 workers; `tc_run` reads the worker count from the protocol. |
| N5 | NOTE | Double counting of the r = 0 order-3 truncation allowance kept (conservative), disclosed here. |
| N6 | NOTE | Replay-mode wording corrected (the order-3 right-hand side is evaluated in memory with a synthetic G; only a shape summary is written). |
| N7 | NOTE | Added fixture families SRC0, SRC1, SRC3 (tight: 0.99996, 0.999996, 0.9991) and mutants M15–M20; the mutant harness now also runs the tc_crosscheck equality on 80 synthetic all-m records. Dev result: 48 fixtures, 0 violations, 20/20 mutants detected (source-error drops by containment; h-tower and W mutants by the cross-check). |
| N8 | NOTE | Covered by N2's loaded-module check (before computing); lazily imported frozen modules are covered by the two frozen producer manifests. |
| N9 | NOTE | Accepted (forecast W radius 0.01 is conservative vs measured ≈ 0.002). |
| N10 | NOTE | Consumer now enforces exactly-once per address (index = address set). |
| N11 | NOTE | The float diagnostic (least-squares fit of adopted K1 midpoints) is explicitly labelled non-evidence in the Phase A audit; it is not an input of any gate. README updated. |
