"""fsync ordering of one crash-matrix fsync log: every link of a record must be preceded (since the previous link) by
an fsync of its own temp file and followed (before the next link) by an fsync of a directory.

usage: fsync_order.py <C15.fsync.jsonl> <out.json>
"""
import json
import sys
from pathlib import Path

ops = [json.loads(l) for l in Path(sys.argv[1]).read_text().splitlines() if l.strip()]
links = [i for i, o in enumerate(ops) if o["op"] == "link"]
rows = []
prev = -1
for k, i in enumerate(links):
    name = ops[i]["name"]
    nxt = links[k + 1] if k + 1 < len(links) else len(ops)
    before = [o["name"] for o in ops[prev + 1:i] if o["op"] == "fsync"]
    after = [o["name"] for o in ops[i + 1:nxt] if o["op"] == "fsync"]
    tmp_ok = any(b.startswith("." + name + ".tmp-") for b in before)
    dir_ok = any("." not in a for a in after)                      # directory names carry no extension here
    rows.append({"link": name, "temp_fsynced_before": tmp_ok, "dir_fsynced_after": dir_ok})
    prev = i
ledger_fsyncs = sum(1 for o in ops if o["op"] == "fsync" and o["name"].endswith(".jsonl"))
res = {"log": sys.argv[1], "ops": len(ops), "links": len(links),
       "links_ordered": sum(r["temp_fsynced_before"] and r["dir_fsynced_after"] for r in rows),
       "ledger_fsyncs": ledger_fsyncs, "rows": rows}
res["all_ordered"] = res["links_ordered"] == res["links"] and res["links"] > 0
Path(sys.argv[2]).write_text(json.dumps(res, indent=1) + "\n")
print({k: v for k, v in res.items() if k != "rows"})
