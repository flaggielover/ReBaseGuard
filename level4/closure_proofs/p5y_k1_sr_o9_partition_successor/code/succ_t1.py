"""Successor T1: the frozen O9 candidate construction for a successor cell.

Identical construction to sr_o9_candidates.build_cell_candidates (same NodalSystem, construct_nodal, quantize,
construction spec, producer and runtime binding, census); only the geometry/identity layer is the successor's.
"""
import time

import sr_o9_candidates as T
import succ_cells as SC

SCHEMA = "k1.sr.o9.partition-successor.candidate.v1"
CELL_SET_SCHEMA = "k1.sr.o9.partition-successor.cell-candidate-set.v1"


def build(rec: dict) -> dict:
    T.check_bits(T.FROZEN_BITS)
    T.check_bidegree(T.FROZEN_BIDEGREE)
    T.check_threads()
    want = list(T.BASIS_ORDER)
    census = T.verify_census()
    t_cpu = time.process_time()
    with T.scientific_precision():
        geo = SC.geometry(rec)
        b_f, c_f, e_f = T.float_inputs(geo)
    sysn = T.NodalSystem(b_f, c_f, e_f)
    values, _node_cpu = T.construct_nodal(sysn)
    prod, rt = T.producer_identity(), T.runtime_binding()
    cid = SC.identity(rec)
    cspec = T.construction_spec(b_f, c_f, e_f)
    cands = []
    with T.scientific_precision():
        for nid in want:
            if nid == "const:1":
                mant, diag = [row[:] for row in T.EXACT_ONE], {"exact": True}
            else:
                mant, diag = T.quantize(values[nid])
            T.to_arb_matrix(mant)
            ident = {"schema": SCHEMA, "cell": cid, "node": nid, "node_class": T.node_class(nid), "construction": cspec,
                     "producer_hash": prod["producer_hash"], "runtime_binding": rt}
            ih = T.sha256(T.canonical(ident))
            ch = T.sha256(T.canonical({"identity_hash": ih, "mantissas": mant, "scale_bits": T.SCALE_BITS}))
            cands.append({"node": nid, "node_class": T.node_class(nid), "identity_hash": ih, "content_hash": ch,
                          "mantissas": mant, "construction_diagnostics": diag})
    if len({c["identity_hash"] for c in cands}) != len(cands):
        raise T.ConstructionFailure("candidate identities are not unique")
    sci = {"schema": CELL_SET_SCHEMA, "cell": cid, "construction": cspec, "producer": prod, "runtime_binding": rt,
           "census": {k: census[k] for k in ("distinct_candidates", "certified_contracts", "by_moment_shift")},
           "node_order": [c["node"] for c in cands], "candidates": cands}
    sci["cell_scientific_hash"] = T.sha256(T.canonical([[c["node"], c["identity_hash"], c["content_hash"]] for c in cands]))
    return {"scientific": sci, "measurement": {"cpu_s": time.process_time() - t_cpu}}
