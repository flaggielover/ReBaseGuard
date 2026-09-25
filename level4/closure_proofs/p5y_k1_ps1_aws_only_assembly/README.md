# PS1 AWS-only downstream assembly successor

Additive successor that consumes the COMPLETED P5Y K1 PS1 SR production shard
(369/369 cells, verified) on the frozen `A_AWS_ONLY` topology.

It exists because the frozen assembler cannot consume this shard:

1. `prodctl assemble` accepts only role `VULTR` (historical two-host handoff topology);
2. its accounting identity is `committed == records + settlement charges`, which has no
   term for the generation-2 imported predecessor accounting seed (92.32 CPU-h).

This namespace changes NO scientific artifact. It never re-runs a cell, never writes to a
production namespace or runtime tree, never touches either historical ledger, and never
relocates the first 16 cells' historical evidence. Its only write is
`evidence/FINAL_ASSEMBLY.json` inside this namespace.

## Routes

| topology evidence | route | implementation |
| --- | --- | --- |
| `A_AWS_ONLY`, AWS owns the complete shard, no handoff material | `AWS_ONLY` | `driver/ps1_assembly.py` (this successor) |
| handoff fingerprint present AND off-AWS ownership | `MULTI_HOST` | frozen `ops/prodctl.py assemble --role VULTR`, untouched |
| anything else | refuse | fail closed |

## Accounting

    committed_cpu_h == scientific_record_cpu_h
                     + settlement_or_operational_cpu_h
                     + imported_predecessor_cpu_h

Every term is derived from frozen or ledger evidence; there is no balancing residual.
The imported term is cross-checked four ways: the generation transition record, the
operational contract, the earliest generation-2 run's opening balance (with no completed
cells), and the hash-pinned predecessor ledger (which holds zero completed cells, so the
import can never double-count science).

## Use

    python3 ops/assemble_entry.py verify              # read-only pre-assembly verification
    python3 ops/assemble_entry.py assemble            # dry run
    python3 ops/assemble_entry.py assemble --commit   # writes evidence/FINAL_ASSEMBLY.json

`assemble` refuses unless the successor is frozen (source manifest + contract hashes).

Final assembly is NOT scientific adjudication and does not decide K1 closure.
