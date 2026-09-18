# K5 CUSUM first real probe: external-authorization packet records

This namespace holds the review and verification records for the governed external authorization of the first real
CUSUM signed-R''' point probe:
- frozen protocol `p5y_k5_cusum_first_real_probe_protocol` r4 (science sha256 `9ace6896…`, freeze `852b2d65`);
- executor `p5y_k5_cusum_real_point_executor` r5 (freeze `a16d22b5`, identity `ef1c86e4…`, qualification `f83cd182`,
  review `43767695`);
- accepted E6 K5-B consumption adapter `p5y_k5b_consumption_adapter` (`ff3b6a4a`, adapter `fbad7d33…`).

It adds records only. It changes no frozen file, no executor source, no adapter, no K1 record and no scientific rule.

## The packet

The frozen verifier fixes where the packet lives and the order of its commits:

| step | object | path |
|---|---|---|
| 1 | independent amendment review | `review/AMENDMENT_REVIEW.md` (this namespace) |
| 2 | execution binding amendment | `p5y_k5_cusum_first_real_probe_protocol/protocol/EXECUTION_BINDING_AMENDMENT.json` |
| 3 | amended-packet check (E5) | `review/` and `evidence/` of this namespace |
| 4 | protocol authorization | `p5y_k5_cusum_first_real_probe_protocol/protocol/AUTHORIZATION_ACTIVE.json` |
| 5 | external countersignature | `p5y_k5_cusum_real_point_executor/authorization/COUNTERSIGNATURE_ACTIVE.json` |
| 6 | LAUNCH_NOTICE for `slot-1` | `p5y_k5_cusum_first_real_probe_protocol/ledger/ATTEMPT_LEDGER.jsonl` |

Each step is a separate commit, and each is published on `origin/p5y-postk1-frontier` before the next one.

## Not part of this packet

These steps belong to a later, separate task:
- the host guard transition (`config/REAL_INPUT_GUARD.json` set to `EXTERNAL_AUTHORIZATION` on the execution host only);
- the final launch preflight;
- the launch itself, which may only be `code/supervisor.py launch --mode real`.

Until then, `REAL_INPUT_ARITHMETIC_GUARD = DENY`. No slot exists, and no real R''' or R^(5) has been computed.
