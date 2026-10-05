import json

EV = "/tmp/claude-0/-home-user-ReBaseGuard/ede4e097-f9ec-54f5-9e84-81294f8ad688/scratchpad/t3/ev/"
c = {x["id"]: x for x in json.load(open(EV + "MATRIX_CANDIDATE.json"))["cases"]}
b = {x["id"]: x for x in json.load(open(EV + "MATRIX_BASELINE.json"))["cases"]}
keys = set()
for x in list(c.values()) + list(b.values()):
    keys |= set(x)
print("keys:", sorted(keys))


def short(x):
    if x is None:
        return "-"
    r = x.get("restart") or {}
    return (f"st={x.get('status_after_crash')} rc={x.get('rc')} notrace={x.get('no_trace')} "
            f"fresh={x.get('fresh_start_allowed_after')} restart.ok={r.get('ok')} refused={r.get('refused')} "
            f"unch={r.get('unchanged')} " + " ".join(f"{k}={x[k]}" for k in sorted(x) if k not in (
                "id", "desc", "risk", "crash", "status_after_crash", "rc", "no_trace", "fresh_start_allowed_after",
                "restart") and not isinstance(x[k], (dict, list))))


for k in sorted(set(c) | set(b)):
    x = c.get(k) or b.get(k)
    print(f"{k} [{x.get('crash')}] {x.get('desc')}")
    print("   CAND:", short(c.get(k)))
    print("   BASE:", short(b.get(k)))
    for lab, y in (("CAND", c.get(k)), ("BASE", b.get(k))):
        if y:
            extra = {kk: v for kk, v in y.items() if isinstance(v, (dict, list)) and kk != "restart"}
            if extra:
                print("   ", lab, "extra:", json.dumps(extra)[:600])
            rt = (y.get("restart") or {}).get("refusal_texts")
            if rt:
                print("   ", lab, "refusals:", [t[:110] for t in rt])
