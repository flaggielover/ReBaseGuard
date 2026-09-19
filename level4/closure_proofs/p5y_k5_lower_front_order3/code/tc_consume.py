"""Theorem-TC consumption: adopted Perron-deflated state + Taylor-cell R'' enclosures -> frozen K5-B.

Composition only (theorem/THEOREM_TC.md section 6). Every adopted component is executed from its pinned bytes:
    consumption adapter (fbad7d33) + frozen loader k5_minimality (3a54f0fb) + frozen K5-B k5b_check (ddd54dc4)
    adopted Perron consumer deflated_consume (ef5d0474): its pure rule functions apply_deflation / block_for /
        atom_constants_r2 with the adopted certified registry r1 (1b7f5da7) on the adopted domain [0, 148]
    adopted T-EXT channel derivation text_consume.text_objects (657458ad) on TEXT_RESULT (cb97cabc), slot-1 (cf90f1ea)
    tc_rule (this namespace, frozen with the protocol)

Replay gate: with an EMPTY TC set the composition must reproduce the sealed, adopted DEFLATED_CONSUMPTION (5dcc9b7d)
exactly — per m the rows sha256, the pass and open ranges, and every recorded per-cell R, D, H, M and via (cells
0..159). Otherwise it refuses. With the TC set, for every TC cell k and m: H_k <- H_k ∩ H_TC,m(k) (refuse if empty),
M_k <- min(M_k, mag(H_k)); then k5b_literal per m on cells 0..309.

    python -B tc_consume.py --protocol-sha256 SHA --out OUT.json [--records DIR] [--replay-only]
(run in a clean checkout at the seal commit; the sealed evidence is read from evidence/tc_r1/ and must be committed)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import types
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
CP = "level4/closure_proofs/"
PINS = {
    "adapter": (CP + "p5y_k5b_consumption_adapter/code/consumption_adapter.py",
                "fbad7d33261fd47fc56c034d6a016f8427b81b51f9199f0e3a8f3e74df35973d"),
    "deflated": (CP + "p5y_k5_perron_deflated_resolvent/code/deflated_consume.py",
                 "ef5d0474183053bb7cde3075bda66f99211706a9bf7bf27e31fe994ff8b87e72"),
    "text_consume": (CP + "p5y_k5_remaining_cell_closure/transport_extension/code/text_consume.py",
                     "657458ade03c4283ae6d5bd97e5567603380bf0e6281d8483f9c1fd45a62d0ea"),
    "registry": (CP + "p5y_k5_perron_deflated_resolvent/evidence/registry_r1/REGISTRY.json",
                 "1b7f5da743a2ce0d7f557c2dae054ab358a9175212eaa1fa29dea63a25780cb5"),
    "text_result": (CP + "p5y_k5_remaining_cell_closure/transport_extension/evidence/qualification_r1/TEXT_RESULT.json",
                    "cb97cabcc3b5848665584e33ad4207c6d36ce835729725265d585dc8f3ee4f87"),
    "slot1": (CP + "p5y_k5_cusum_first_real_probe_protocol/evidence/slot-1/SCIENTIFIC_RECORD_SEALED.json",
              "cf90f1ea577c09d718adddab9698f8f03995722dae51f68d1fd767e4339f73ae"),
    "sealed_deflated": (CP + "p5y_k5_perron_deflated_resolvent/evidence/successor_r1/DEFLATED_CONSUMPTION.json",
                        "5dcc9b7d26c92babbf1b19ad064b29969ea7bd829ea9629004e312520123274a"),
    "tc_rule": (CP + "p5y_k5_lower_front_order3/code/tc_rule.py", None),
    "tc_crosscheck": (CP + "p5y_k5_lower_front_order3/code/tc_crosscheck.py", None),
}
NS_REL = "level4/closure_proofs/p5y_k5_lower_front_order3"
PROTOCOL_REL = NS_REL + "/config/TC_PROTOCOL.json"
EVID_REL = NS_REL + "/evidence/tc_r1"
MS = ("1", "2", "3", "5")
ADOPTED_DOMAIN = (0, 148)
TEXT_CHANNEL = tuple(range(1, 41))
TEXT_CURVATURE = tuple(range(0, 41))
SCHEMA = "rebaseguard.p5y.k5.lower-front-order3.tc-consumption.v1"


class TCConsumeRefusal(RuntimeError):
    pass


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical(o) -> bytes:
    return json.dumps(o, sort_keys=True, separators=(",", ":")).encode()


def pinned(key: str, pin_override: dict | None = None) -> bytes:
    rel, pin = PINS[key]
    if pin is None and pin_override:
        pin = pin_override.get(rel)
    raw = (REPO / rel).read_bytes()
    if pin is None or sha(raw) != pin:
        raise TCConsumeRefusal(f"{rel} does not match its pin")
    return raw


def module(key: str, name: str, pin_override=None):
    raw = pinned(key, pin_override)
    mod = types.ModuleType(name)
    mod.__file__ = str(REPO / PINS[key][0])
    exec(compile(raw, mod.__file__, "exec"), mod.__dict__)
    return mod


def load_protocol(protocol_sha256: str) -> dict:
    """The COMMITTED protocol, equal to its bytes at the freeze commit, with the namespace unchanged since the freeze
    outside evidence/tc_r1/ (no uncommitted or untracked change either) and every pin matching (review r2 B-R2-1)."""
    raw = committed_bytes(PROTOCOL_REL)
    if sha(raw) != protocol_sha256:
        raise TCConsumeRefusal("TC protocol does not match the given sha256")
    added = _git("log", "--diff-filter=A", "--format=%H", "--", PROTOCOL_REL).split()
    if not added:
        raise TCConsumeRefusal("no freeze commit")
    freeze = added[-1]
    import subprocess
    at_freeze = subprocess.run(["git", "-C", str(REPO), "show", f"{freeze}:{PROTOCOL_REL}"], check=True,
                               capture_output=True).stdout
    if at_freeze != raw:
        raise TCConsumeRefusal("protocol differs from its bytes at the freeze commit")
    if _git("status", "--porcelain", "--untracked-files=all", "--", NS_REL).strip():
        raise TCConsumeRefusal("namespace has uncommitted or untracked changes")
    changed = _git("diff", "--name-only", freeze, "HEAD", "--", NS_REL).split()
    extra = [c for c in changed if not c.startswith(EVID_REL + "/")]
    if extra:
        raise TCConsumeRefusal(f"namespace changed after the freeze outside {EVID_REL}: {extra[:5]}")
    proto = json.loads(raw)
    bad = [rel for rel, h in proto["pins"].items() if sha((REPO / rel).read_bytes()) != h]
    if bad:
        raise TCConsumeRefusal(f"protocol pins do not match: {bad[:5]}")
    for key in ("tc_rule", "tc_crosscheck"):
        if PINS[key][0] not in proto["pins"]:
            raise TCConsumeRefusal(f"protocol does not pin {PINS[key][0]}")
    proto["_freeze_commit"] = freeze
    return proto


def rule_modules(proto: dict):
    pov = {PINS[k][0]: proto["pins"][PINS[k][0]] for k in ("tc_rule", "tc_crosscheck")}      # frozen pins
    return module("tc_rule", "tc_rule_frozen", pov), module("tc_crosscheck", "tc_crosscheck_frozen", pov)


def check_index(index: dict, proto: dict, protocol_sha256: str, tc_cells: dict, repro_sha: dict) -> None:
    """Acceptance items 1 and 2 of the frozen spec."""
    want = sorted(proto["addresses"]["cells"])
    if index.get("protocol_sha256") != protocol_sha256:
        raise TCConsumeRefusal("TC index was not produced under this protocol")
    if sorted(int(k) for k in index.get("cells", {})) != want or sorted(tc_cells) != want:
        raise TCConsumeRefusal("TC index does not list exactly the pre-registered addresses")
    rep = index.get("reproduction", {})
    if sorted(rep) != ["11", "44"] or not all(v is True for v in rep.values()):
        raise TCConsumeRefusal("the pre-registered reproduction is missing or not byte-identical")
    for k, h in repro_sha.items():
        if h != index["cells"][k]:
            raise TCConsumeRefusal(f"reproduction file of cell {k} differs from the first run")


def check_binding(rec: dict, k: int, proto: dict, ctx: dict) -> None:
    """Every record was produced by the gated real mode under this protocol, freeze, authorization and ALLOW guard,
    at a run head that descends from the authorization commit (review r2 B-R2-1, N-R2-5)."""
    b = rec.get("binding")
    if not isinstance(b, dict):
        raise TCConsumeRefusal(f"TC record {k}: no governance binding")
    if rec.get("k1_record_sha256") != proto["k1_record_sha256"].get(str(k)):
        raise TCConsumeRefusal(f"TC record {k}: K1 record sha differs from the protocol")
    if b.get("protocol_sha256") != ctx["protocol_sha256"]:
        raise TCConsumeRefusal(f"TC record {k}: protocol sha differs")
    if b.get("freeze_commit") != ctx["freeze_commit"]:
        raise TCConsumeRefusal(f"TC record {k}: freeze commit differs")
    if b.get("authorization_sha256") != ctx["authorization_sha256"]:
        raise TCConsumeRefusal(f"TC record {k}: authorization differs")
    head = b.get("head")
    if head not in ctx["run_heads"]:
        raise TCConsumeRefusal(f"TC record {k}: run head is not a valid run head (after the authorization)")
    if b.get("guard_sha256") != ctx["guard_sha_at"].get(head):
        raise TCConsumeRefusal(f"TC record {k}: guard at the run head is not the bound ALLOW guard")


def crosscheck(R, X, rec: dict, Ak: dict, m: int, lohi: tuple) -> None:
    """Acceptance item 3: the independent implementation gives the identical enclosure."""
    if X.enclosure(rec, {j: Ak[j] for j in ("A0", "A1", "A2")}, m) != lohi:
        raise TCConsumeRefusal(f"tc_crosscheck disagrees with tc_rule on cell {rec.get('cell')} m {m}")


def compose(records_dir: Path, tc_cells: dict, proto: dict) -> dict:
    R, X = rule_modules(proto)
    A = module("adapter", "tc_adapter")
    DC = module("deflated", "tc_deflated")
    TCm = module("text_consume", "tc_text_consume")
    registry = json.loads(pinned("registry"))
    text = json.loads(pinned("text_result"))
    per = json.loads(pinned("slot1"))["scientific"]["per_m"]
    sealed = json.loads(pinned("sealed_deflated"))
    L1 = {m: F(per[m]["L1"]) for m in MS}
    lam, m2 = TCm.text_objects(text, {m: per[m]["L1"] for m in MS})
    comp = A.frozen_components(REPO)
    KM, KB = comp["loader"], comp["theorem"]
    A.bound_file(REPO / A.CELLS_JSON, A.CELLS_SHA256, "cells.json")
    manifest = json.loads(A.bound_file(REPO / A.MANIFEST, A.MANIFEST_SHA256, "record manifest"))
    cover = KM.load_cells(REPO / A.CELLS_JSON, A.DETECTOR)
    if [c["index"] for c in cover] != list(range(310)):
        raise TCConsumeRefusal("cover universe mismatch")
    records, hashes = A.read_records(KM, Path(records_dir), cover, manifest)
    if registry.get("certified") is not True or registry.get("rule") != "r2":
        raise TCConsumeRefusal("adopted registry must be the certified r2 registry")
    out, tc_audit, n_cross = {}, {}, [0]
    for m in MS:
        cells = A.cells_for_m(KM, cover, records, m, L1[m])
        audit = DC.apply_deflation(cells, records, registry, m, cover, ADOPTED_DOMAIN)
        for k in TEXT_CHANNEL:
            if cells[k]["L"] is not None:
                raise TCConsumeRefusal("unexpected order-3 channel before T-EXT assignment")
            cells[k]["L"] = lam[m][k]
        for k in TEXT_CURVATURE:
            b = m2[m][k]
            lo, hi = cells[k]["H"]
            if max(lo, -b) > min(hi, b):
                raise TCConsumeRefusal(f"empty curvature enclosure cell {k} m {m}")
            cells[k]["H"] = (max(lo, -b), min(hi, b))
            cells[k]["M"] = min(cells[k]["M"], b)
        adopted_state = {k: (cells[k]["R"], cells[k]["D"], cells[k]["H"], cells[k]["M"]) for k in range(160)}
        rows0 = KB.k5b_literal(cells)
        # ---- replay gate against the sealed adopted consumption
        s = sealed["consumptions"][m]
        passed0 = [cover[i]["index"] for i, r in enumerate(rows0) if r["pass"] is True]
        if KM.ranges(passed0) != s["pass_ranges"] or sha(canonical(A.row_json(rows0))) != s["rows_sha256"]:
            raise TCConsumeRefusal(f"replay of the adopted deflated consumption differs for m={m}")
        for k in range(160):
            R_, D_, H_, M_ = adopted_state[k]
            sc = s["cells"][str(k)]
            if ([str(x) for x in R_], [str(x) for x in D_], [str(x) for x in H_], str(M_)) != \
                    (sc["R"], sc["D"], sc["H"], sc["M"]) or rows0[k]["via"] != s["via"][str(k)]:
                raise TCConsumeRefusal(f"replayed cell {k} m={m} differs from the sealed consumption")
        # ---- theorem TC
        for k in sorted(tc_cells):
            rec = tc_cells[k]
            c = cover[k]
            if rec.get("mode") != "real" or rec.get("cell") != k or not rec.get("identity_gate", {}).get("identical"):
                raise TCConsumeRefusal(f"TC record for cell {k} is not a gated real record of that cell")
            if F(rec["e0"]) != KM.rat(c["e0"]) or F(rec["rho"]) != KM.rat(c["rho"]):
                raise TCConsumeRefusal(f"TC record for cell {k}: geometry differs from the frozen cover")
            if rec.get("k1_record_sha256") != hashes[str(k)]:
                raise TCConsumeRefusal(f"TC record for cell {k} was not computed against the adopted K1 record")
            cons = DC.block_for(registry, cells[k]["x_lo"], cells[k]["x_hi"])
            if cons is None:
                raise TCConsumeRefusal(f"cell {k} not covered by the adopted registry")
            Ak = DC.atom_constants_r2(cons["Abar"], cons["tau"], cons["C"], cons["Dlo"], cons["D1"], cons["D2"])
            if k not in audit or any(str(Ak[j]) != audit[k][j] for j in ("A0", "A1", "A2")) \
                    or any(str(Ak[j]) != s["audit"][str(k)][j] for j in ("A0", "A1", "A2")):
                raise TCConsumeRefusal(f"A-constants of cell {k} differ from the adopted audit")
            lo, hi = R.cell_enclosure(rec, Ak, int(m))
            crosscheck(R, X, rec, Ak, int(m), (lo, hi))
            n_cross[0] += 1
            a, b = max(cells[k]["H"][0], lo), min(cells[k]["H"][1], hi)
            if a > b:
                raise TCConsumeRefusal(f"empty TC intersection cell {k} m {m} (evidence of unsoundness)")
            cells[k]["H"] = (a, b)
            cells[k]["M"] = min(cells[k]["M"], max(abs(a), abs(b)))
            tc_audit.setdefault(str(k), {})[m] = {"H_TC": [str(lo), str(hi)], "H_final": [str(a), str(b)],
                                                  "A": {j: str(Ak[j]) for j in ("A0", "A1", "A2")}}
        rows = KB.k5b_literal(cells)
        passed = [cover[i]["index"] for i, r in enumerate(rows) if r["pass"] is True]
        if not set(passed0) <= set(passed):
            raise TCConsumeRefusal(f"a previously passing cell regressed for m={m} (monotonicity violated)")
        opened = [k for k in range(310) if k not in set(passed)]
        out[m] = {"pass_ranges": KM.ranges(passed), "pass_count": len(passed), "open_ranges": KM.ranges(opened),
                  "open_count": len(opened), "rows_sha256": sha(canonical(A.row_json(rows))),
                  "newly_passing": KM.ranges(sorted(set(passed) - set(passed0))),
                  "via": {str(i): rows[i]["via"] for i in range(160)},
                  "cells": {str(i): {"R": [str(x) for x in cells[i]["R"]], "D": [str(x) for x in cells[i]["D"]],
                                     "H": [str(x) for x in cells[i]["H"]], "M": str(cells[i]["M"])}
                            for i in range(160)}}
    return {"schema": SCHEMA, "consumptions": out, "tc_audit": tc_audit, "tc_cells": sorted(tc_cells),
            "crosscheck_comparisons": n_cross[0],
            "replay_gate": "PASS (empty-TC composition reproduced the sealed adopted consumption exactly)",
            "inputs": {k: {"path": v[0], "sha256": v[1] if v[1] else proto["pins"][v[0]]} for k, v in PINS.items()}
            | {"records_sha256": sha(canonical(hashes)), "record_count": len(hashes)}}


def _git(*args) -> str:
    import subprocess
    return subprocess.run(["git", "-C", str(REPO), *args], check=True, capture_output=True, text=True).stdout


def committed_bytes(rel: str) -> bytes:
    """The file must be tracked and its working-tree bytes equal to HEAD (the sealed evidence)."""
    try:
        _git("ls-files", "--error-unmatch", rel)
    except Exception:
        raise TCConsumeRefusal(f"{rel} is not committed")
    disk = (REPO / rel).read_bytes()
    import subprocess
    head = subprocess.run(["git", "-C", str(REPO), "show", f"HEAD:{rel}"], check=True, capture_output=True).stdout
    if disk != head:
        raise TCConsumeRefusal(f"{rel} differs from its committed bytes")
    return disk


def _show(commit: str, rel: str) -> bytes:
    import subprocess
    return subprocess.run(["git", "-C", str(REPO), "show", f"{commit}:{rel}"], capture_output=True).stdout


def _ancestor(x: str, y: str) -> bool:
    import subprocess
    return subprocess.run(["git", "-C", str(REPO), "merge-base", "--is-ancestor", x, y]).returncode == 0


def governance_context(proto: dict, protocol_sha256: str) -> dict:
    """Freeze, qualification -> authorization -> guard chain, the valid run heads and the guard at each of them."""
    qual = committed_bytes(EVID_REL + "/QUALIFICATION_RESULT.json")
    q = json.loads(qual)
    if q.get("QUALIFIED") is not True or q.get("protocol_sha256") != protocol_sha256 \
            or q.get("S00", {}).get("head") != proto["_freeze_commit"]:
        raise TCConsumeRefusal("no QUALIFIED qualification at the freeze commit for this protocol")
    auth = committed_bytes(EVID_REL + "/AUTHORIZATION.json")
    a = json.loads(auth)
    if a.get("verdict") != "AUTHORIZED" or a.get("protocol_sha256") != protocol_sha256 \
            or a.get("addresses") != proto["addresses"]["cells"] or a.get("qualification_result_sha256") != sha(qual):
        raise TCConsumeRefusal("AUTHORIZATION is not bound to this protocol, its addresses and its qualification")
    a_add = _git("log", "--diff-filter=A", "--format=%H", "--", EVID_REL + "/AUTHORIZATION.json").split()[-1]
    if len(_git("log", "--format=%H", "--", EVID_REL + "/AUTHORIZATION.json").split()) != 1:
        raise TCConsumeRefusal("AUTHORIZATION was modified after it was committed")
    guard_now = json.loads(committed_bytes(EVID_REL + "/GUARD.json"))
    if guard_now.get("state") != "DENY":
        raise TCConsumeRefusal("GUARD must be DENY again at consumption")
    heads, guard_at = set(), {}
    for c in [a_add] + _git("rev-list", "--ancestry-path", f"{a_add}..HEAD").split():
        g = _show(c, EVID_REL + "/GUARD.json")
        if g and json.loads(g).get("state") == "ALLOW" and json.loads(g).get("authorization_sha256") == sha(auth) \
                and _show(c, EVID_REL + "/AUTHORIZATION.json") == auth:
            heads.add(c)
            guard_at[c] = sha(g)
    return {"protocol_sha256": protocol_sha256, "freeze_commit": proto["_freeze_commit"],
            "qualification_sha256": sha(qual), "authorization_sha256": sha(auth), "authorization_commit": a_add,
            "run_heads": heads, "guard_sha_at": guard_at}


def sealed_once(rel: str) -> bytes:
    """A sealed file: committed, and added in exactly one commit and never modified afterwards."""
    data = committed_bytes(rel)
    if len(_git("log", "--format=%H", "--", rel).split()) != 1:
        raise TCConsumeRefusal(f"sealed file {rel} was modified after it was committed")
    return data


def load_sealed_tc(proto: dict, protocol_sha256: str) -> tuple[dict, dict]:
    idx_raw = sealed_once(EVID_REL + "/TC_INDEX.json")
    index = json.loads(idx_raw)
    cells, repro = {}, {}
    for k, want in index.get("cells", {}).items():
        raw = sealed_once(f"{EVID_REL}/cells/TC_CELL_{int(k)}.json")
        if sha(raw) != want:
            raise TCConsumeRefusal(f"TC cell {k} does not match the sealed index")
        cells[int(k)] = json.loads(raw)
    for k in index.get("reproduction", {}):
        repro[k] = sha(sealed_once(f"{EVID_REL}/repro/TC_CELL_{int(k)}.json"))
    check_index(index, proto, protocol_sha256, cells, repro)
    ledger = [json.loads(x) for x in sealed_once(EVID_REL + "/RUN_LEDGER.jsonl").decode().splitlines() if x.strip()]
    outs = {str(x["cell"]): x for x in ledger if x.get("event") == "OUTPUT"}
    if sorted(outs) != sorted(index["cells"]) or any(not outs[k].get("ok") or outs[k].get("sha256") != v
                                                     for k, v in index["cells"].items()):
        raise TCConsumeRefusal("RUN_LEDGER OUTPUT lines do not match the sealed index")
    if not any(x.get("event") == "RUN_END" and x.get("reproduction_identical") is True for x in ledger) \
            or any(x.get("event") in ("RUN_VOID", "CAP_STOP") for x in ledger):
        raise TCConsumeRefusal("RUN_LEDGER does not record a complete, non-void run")
    if len([x for x in ledger if x.get("event") == "START"]) != len(index["cells"]):
        raise TCConsumeRefusal("RUN_LEDGER does not record exactly one invocation per address")
    ctx = governance_context(proto, protocol_sha256)
    for k, rec in cells.items():
        check_binding(rec, k, proto, ctx)
    audit = {"tc_index_sha256": sha(idx_raw), "governance": {k: (sorted(v) if isinstance(v, set) else v)
                                                              for k, v in ctx.items()},
             "acceptance": {"addresses": len(cells), "reproduction": index["reproduction"],
                            "ledger_outputs": len(outs)}}
    return cells, audit


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", default="/root/work/postk1-runs/closure-r1/COMPOSITE_EXPORT/k4_records")
    ap.add_argument("--protocol-sha256", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--replay-only", action="store_true")
    a = ap.parse_args()
    proto = load_protocol(a.protocol_sha256)
    if a.replay_only:
        tc, audit = {}, {"mode": "replay-only"}
    else:
        tc, audit = load_sealed_tc(proto, a.protocol_sha256)
    res = compose(Path(a.records), tc, proto)
    res["protocol_sha256"] = a.protocol_sha256
    res["freeze_commit"] = proto["_freeze_commit"]
    res["verified"] = audit
    data = json.dumps(res, sort_keys=True, indent=1).encode() + b"\n"
    Path(a.out).write_bytes(data)
    print({m: v["open_ranges"] for m, v in res["consumptions"].items()}, "sha256", sha(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
