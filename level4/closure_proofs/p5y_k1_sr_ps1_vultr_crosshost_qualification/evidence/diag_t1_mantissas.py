"""POST-HOC DIAGNOSTIC (not predeclared; cannot alter any predeclared verdict).
Frozen-cell-150 T1 candidate construction on this host vs the COMMITTED AWS candidate set."""
import json, sys
import sr_o9_candidates as T
ref = json.load(open(sys.argv[1]))
ref = ref.get("scientific", ref)
got = T.build_cell_candidates(150)
got = got.get("scientific", got)
rc = {c["node"]: c for c in ref["candidates"]}
gc = {c["node"]: c for c in got["candidates"]}
rows, maxd = {}, 0
for n in rc:
    a, b = rc[n]["mantissas"], gc[n]["mantissas"]
    d = max(abs(x - y) for ra, rb in zip(a, b) for x, y in zip(ra, rb))
    maxd = max(maxd, d)
    rows[n] = {"mantissas_equal": a == b, "max_abs_mantissa_diff_units_2^-50": d,
               "identity_hash_equal": rc[n]["identity_hash"] == gc[n]["identity_hash"]}
rb_ref, rb_got = ref.get("runtime_binding", {}), got.get("runtime_binding", {})
print(json.dumps({"nodes": len(rows), "mantissas_equal_nodes": sum(r["mantissas_equal"] for r in rows.values()),
                  "identity_equal_nodes": sum(r["identity_hash_equal"] for r in rows.values()),
                  "max_abs_mantissa_diff_units_2^-50": maxd,
                  "runtime_binding_differing_keys": sorted(k for k in set(rb_ref) | set(rb_got) if rb_ref.get(k) != rb_got.get(k)),
                  "producer_hash_equal": ref.get("producer", {}).get("producer_hash") == got.get("producer", {}).get("producer_hash"),
                  "construction_spec_equal": ref.get("construction") == got.get("construction"),
                  "sample_nodes": dict(list(rows.items())[:6])}, indent=1))
