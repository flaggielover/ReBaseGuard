# I1-only: mirrors `rehearse --cell 306` in-process to see which modules get imported lazily after load_consumer.
import importlib.util, sys
p = "/Users/suzhe/ReBaseGuard-k5c11rd/level4/closure_proofs/p5y_k5_tail_c12r1_cell306_adoption/code/c12r1_cell306.py"
spec = importlib.util.spec_from_file_location("d_probe", p); D = importlib.util.module_from_spec(spec); spec.loader.exec_module(D)
D.check_not_evaluated(); D.check_bindings(); D.check_governance_state()
con = D.load_consumer()
print("sys.path[:3] after load_consumer:", [s.replace('/Users/suzhe/ReBaseGuard-k5c11rd/','') for s in sys.path[:3]])
before = set(sys.modules)
ctl = D.control(con, 306)
import json, tempfile, os
json.dumps({"a": 1}); D.utc()
after = set(sys.modules)
print("reproduces:", ctl["reproduces_C2_exactly"], "| modules newly imported during control:", sorted(after - before))
