# GUARD_DIFF: mbs308_guard.py against MB r1's mb308_guard.py

The successor guard differs from MB r1's in exactly ONE line: the marker ref constant `CONSUMED_REF` (`refs/p5y-k5-cell308-mb-r1/target-consumed` -> `refs/p5y-k5-cell308-mbs-r1/target-consumed`), so that `arm_target` enters TARGET mode only when the SUCCESSOR's marker names the grant commit at HEAD; MB r1's marker is never read for arming. Everything else (the band, the mirror, CELL308, the admitted-set rule D1/D2, DECOY by default, the reproduction context, the import guard, the forbidden paths, `log_execution`) is byte-identical. RC1 condition: the guard may differ only in namespace / ref / marker constants; asserted by `tests/test_mbs308_static.py` t_rc1_guard_diff_only_marker (the diff must be exactly this line pair).

* MB r1 sha256 `882ce3fb86f4089081104e0fdbaf31c01b16e9a80065acd4e911f3010e6e06b1`; MB-S sha256 `48903487f648e9d39bb764497ceae87941c33be73cb4b1fa285ac83bbb1e9435`.

```diff
--- mb308_guard.py (MB r1, 21e99cf0)
+++ mbs308_guard.py (MB-S)
@@ -37,7 +37,7 @@
 REPRODUCTION_CELLS = frozenset({305, 308})
 SUB_BLOCK_MAX_WIDTH = F(1, 100)          # D1 (C2's rule, as the 307 campaign)
 HULL_BITS = 20                           # D2
-CONSUMED_REF = "refs/p5y-k5-cell308-mb-r1/target-consumed"
+CONSUMED_REF = "refs/p5y-k5-cell308-mbs-r1/target-consumed"
 FORBIDDEN_MODULES = frozenset({"numpy", "scipy", "mpmath", "sympy", "flint", "gmpy2", "numba", "cython"})
 FORBIDDEN_PATHS = (re.compile(r"RLR307_CELL307_RESULT"), re.compile(r"C12R[12]_CELL306_RESULT"),
                    re.compile(r"-emergency-result\.json"))
```
