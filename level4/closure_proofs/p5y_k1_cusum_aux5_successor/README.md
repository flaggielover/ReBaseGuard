# P5Y K1 CUSUM Aux5 successor (rebaseguard-vultr-02)

This is the governed successor of `p5y_k1_cusum_aux4_fullcover` (commit `f0954a9d`). It follows the NEW_SUCCESSOR route frozen in `p5y_postk1_precompute_resolution/CUSUM_SUCCESSOR_PREFREEZE.md`.

**NON-PRODUCTION.** This namespace freezes a producer and runs only the qualification protocol. No production cell is authorized here: the 326-cell campaign needs a separate frozen production checkpoint.

## What changes (identity layer only)

| Aux4 module | Aux5 module | Change |
|---|---|---|
| `runtime_identity.py` | `runtime_identity5.py` | **External-venv repair.** Backend libraries are bound by absolute resolved path from the site-packages that actually holds numpy and python-flint, and a missing family fails closed. Aux4 globbed repository-relative paths and bound `{}` for a venv outside the tree. numpy's OpenBLAS is selected explicitly. The contract also binds host name, venv prefix, interpreter and site-packages. |
| `tcb.py` | `tcb5.py` | Aux5 modules, plus the reused Aux4 modules by exact path; the Aux4 manifest v2 is bound as an artifact. |
| `manifest_v2.py` | `manifest_v3.py` | Schema v3. `verify()` also requires every Aux4 science input to be byte-identical to the Aux4 manifest v2. |
| `identity4.py` | `identity5.py` | Identity kind v3; the Aux4 commit and manifest hash are added to the rejected identities. |
| `qualify4.py` | `qualify5.py` | Imports the successor layer; campaign name and change list. |

These five modules are **generated** by `code/make_aux5.py`, using anchored substitutions over the Aux4 sources, which are verified first. `config/GENERATION_REPORT.json` records the source and output hashes.

## What does not change

The following are imported in place and byte-identical, each by exact path in the TCB:
- every scientific module and frozen input;
- `schema.py` and `hash_v2.py`, which define the **scientific hash semantics**;
- `scipy_guard.py` and `ancestry4.py`.

Frozen K1 thresholds and universes are untouched.

## Frozen objects

- `manifests/producer_manifest_v3.json`: producer manifest and runtime contract, generated on the bound host.
- `config/HOST_QUALIFICATION.json`
- `config/COST_CAP_FORMULA.json`: the **formula** is binding; the numeric cap is always derived.
- `config/QUALIFICATION_PROTOCOL.json`: cells 318 and 323, two fresh isolated repeats each, P1–P5; transition to production is **not** authorized.

Qualification runs are launched by `code/run_qualification.sh` and analyzed by `code/analyze_qualification.py`. Neither script certifies.
