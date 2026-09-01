"""Literal reconstruction of the declared BH families, in particular F3 (G6A).

The frozen declaration, ``p6r_safe_rebaselining_confirmation/REPAIRED_PROTOCOL.md``:

* section 6, families table:
    **F3** -- the `Delta`-scope family: **the primary metric** at
    `Delta in {0.5, 2}`; BH `q = 0.10`; sub-floor cells are **excluded** from the
    family and labelled.
* section 6, tail-event floor:
    a `Dtail` estimate is reportable only if **both** arms carry at least 200
    exceedances; below that it is labelled `INSUFFICIENT_TAIL_EVENTS`, carries
    no resolved claim, and is **excluded from its BH family**.
* section 7, `Delta = 2` row:
    `Dtail(100)` is inferentially unresolved unless the floor is met in both
    arms; **`Dq95` is the declared fallback metric**.

The adjudication found the implementation added an **undeclared extra
`Dq95@Delta=0.5` test** while the primary metric was eligible there.  The literal
rule, applied per `Delta` cell, is:

```text
primary = Dtail(100)
if both arms clear the 200-event floor:
        INCLUDE primary;  do NOT include the fallback
else:
        EXCLUDE primary, labelled INSUFFICIENT_TAIL_EVENTS;
        INCLUDE the declared fallback Dq95 in its place
```

Nothing else may enter F3.
"""
from __future__ import annotations

import numpy as np

PRIMARY_METRIC = "Dtail100"
FALLBACK_METRIC = "Dq95"
TAIL_EVENT_FLOOR = 200
BH_Q = 0.10
F3_DELTAS = (0.5, 2.0)


def f3_membership(events_by_delta: dict, floor: int = TAIL_EVENT_FLOOR) -> dict:
    """Decide, per `Delta`, which single test enters F3 and why.

    ``events_by_delta[delta] = (n_events_method, n_events_control)`` for the
    PRIMARY metric.  Returns one entry per declared `Delta`, each naming exactly
    one included test and, where applicable, one excluded test with its reason.
    """
    out = {}
    for d in F3_DELTAS:
        nm, nc = events_by_delta[d]
        eligible = min(int(nm), int(nc)) >= floor
        if eligible:
            out[d] = {
                "delta": float(d),
                "included_metric": PRIMARY_METRIC,
                "included_key": f"{PRIMARY_METRIC}@{d}",
                "excluded": [],
                "reason": (f"primary metric eligible: min(events) = "
                           f"{min(int(nm), int(nc))} >= floor {floor}; the "
                           f"declared fallback {FALLBACK_METRIC} is therefore "
                           f"NOT included"),
                "n_events_method": int(nm), "n_events_control": int(nc),
            }
        else:
            out[d] = {
                "delta": float(d),
                "included_metric": FALLBACK_METRIC,
                "included_key": f"{FALLBACK_METRIC}@{d}",
                "excluded": [{"key": f"{PRIMARY_METRIC}@{d}",
                              "label": "INSUFFICIENT_TAIL_EVENTS",
                              "reason": (f"min(events) = {min(int(nm), int(nc))} "
                                         f"< floor {floor}; excluded from the "
                                         f"family and carries no claim")}],
                "reason": (f"primary metric sub-floor, so the DECLARED fallback "
                           f"{FALLBACK_METRIC} takes its place"),
                "n_events_method": int(nm), "n_events_control": int(nc),
            }
    return out


def benjamini_hochberg(pvals, q: float = BH_Q):
    """BH step-up.  Returns ``(reject, adjusted_p)``, aligned to the input."""
    p = np.asarray(pvals, float)
    n = p.size
    if n == 0:
        return np.zeros(0, bool), np.zeros(0, float)
    order = np.argsort(p)
    ranked = p[order]
    adj_sorted = np.minimum.accumulate(
        (ranked * n / np.arange(1, n + 1))[::-1])[::-1]
    adj_sorted = np.clip(adj_sorted, 0.0, 1.0)
    adj = np.empty(n, float)
    adj[order] = adj_sorted
    return adj <= q, adj


def bh_over_defined(records: dict, q: float = BH_Q) -> dict:
    """BH over a family, EXCLUDING undefined and sub-floor records.

    An undefined comparison (``status == UNDEFINED_ZERO_DENOMINATOR``) and a
    sub-floor tail estimate carry no claim, so they neither consume nor receive
    false-discovery budget.
    """
    from .undefined import STATUS_UNDEFINED
    keys, excluded = [], {}
    for k, r in records.items():
        if r.get("status") == STATUS_UNDEFINED:
            excluded[k] = "UNDEFINED_ZERO_DENOMINATOR"
        elif r.get("tail_flag") == "INSUFFICIENT_TAIL_EVENTS":
            excluded[k] = "INSUFFICIENT_TAIL_EVENTS"
        elif r.get("p_value") is None:
            excluded[k] = "NO_P_VALUE"
        else:
            keys.append(k)
    if not keys:
        return {"q": q, "n_tests": 0, "family": [], "excluded": excluded,
                "reject": {}, "p_adjusted": {}}
    rej, adj = benjamini_hochberg([records[k]["p_value"] for k in keys], q)
    return {"q": q, "n_tests": len(keys), "family": keys, "excluded": excluded,
            "reject": {k: bool(v) for k, v in zip(keys, rej)},
            "p_adjusted": {k: float(v) for k, v in zip(keys, adj)}}
