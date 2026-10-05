"""fsync ordering of one crash-matrix fsync log (v2, task 4: the S1 probe's own operations are reported apart).

usage: fsync_order.py <C15.fsync.jsonl> <out.json>
Record links: every link of a record must be preceded (since the previous record link) by an fsync of its own temp file
and followed (before the next record link) by an fsync of a directory.  Probe operations (names probe.a / probe.b and
the probe directory .p309-fsprobe-*) are the S1 probe's; they must all precede the first record link (the probe runs
before the start line) and are listed separately.
"""
import json
import sys
from pathlib import Path

ops = [json.loads(l) for l in Path(sys.argv[1]).read_text().splitlines() if l.strip()]
is_probe = lambda o: o["name"] in ("probe.a", "probe.b") or o["name"].startswith(".p309-fsprobe-")  # noqa: E731
probe_idx = [i for i, o in enumerate(ops) if is_probe(o)]
links = [i for i, o in enumerate(ops) if o["op"] == "link" and not is_probe(o)]
rows, prev = [], -1
for k, i in enumerate(links):
    name = ops[i]["name"]
    nxt = links[k + 1] if k + 1 < len(links) else len(ops)
    before = [o["name"] for o in ops[prev + 1:i] if o["op"] == "fsync"]
    after = [o["name"] for o in ops[i + 1:nxt] if o["op"] == "fsync"]
    rows.append({"link": name, "temp_fsynced_before": any(b.startswith("." + name + ".tmp-") for b in before),
                 "dir_fsynced_after": any("." not in a for a in after)})
    prev = i
res = {"log": sys.argv[1], "ops": len(ops), "record_links": len(links),
       "record_links_ordered": sum(r["temp_fsynced_before"] and r["dir_fsynced_after"] for r in rows),
       "ledger_fsyncs": sum(1 for o in ops if o["op"] == "fsync" and o["name"].endswith(".jsonl")),
       "probe_ops": [ops[i] for i in probe_idx],
       "probe_ops_all_before_first_record_link": all(i < links[0] for i in probe_idx) if links else True,
       "rows": rows}
res["all_ordered"] = res["record_links_ordered"] == res["record_links"] > 0 and res["probe_ops_all_before_first_record_link"]
Path(sys.argv[2]).write_text(json.dumps(res, indent=1) + "\n")
print({k: v for k, v in res.items() if k != "rows"})
