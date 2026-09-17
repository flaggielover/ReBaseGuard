# Governance status of the first real-probe preregistration (after four independent static reviews)

## What is frozen and stable

**The science preregistration.** It is identical in content from r1 (`dbbd405a`) through r4 (`852b2d65`); only
governance text changed:
- the cell: K1 CUSUM cell 0 = theorem cell C₁ = [0, 5083/10⁷];
- m ∈ {1, 2, 3, 5};
- the object: `I₀ = [L0, U0] ∋ R'''(0)`, `M5 ≥ sup_[0,x₁] |R⁽⁵⁾|`, `L1 = L0 − (x₁²/2)·M5`, `U1 = U0 + (x₁²/2)·M5`;
- the three-way verdict, plus POINT_NEGATIVE ⇒ H3a false;
- the K5-B consumption map keyed on the H3a consequence;
- negative-result handling;
- the single 256-bit rung;
- the cost basis and CPU ceilings;
- the per-m addresses, which carry no attempt id.

All four reviews passed these elements. The frozen rule code `probe_rules.py` implements them and is tested on
hypothetical inputs only. No real `R'''` or `R⁽⁵⁾` value exists anywhere in the lineage, and no execution has been
authorized or attempted.

## What is not sound yet

**The launch-governance machinery** (`prelaunch_verify.py`, the ledger and the authorization procedure). r1–r4 each
closed the previous reviewer's bypasses, and each next review found deeper ones. The r4 findings show a structural
limit rather than patchable slips:
- An operator who can write the repository or host environment can rewrite the commit graph the verifier consults
  (git replace or grafts), the git environment, the mirror path, or even the Python bytecode that runs.
- No verifier that runs inside that same repository and environment can be made sound against that operator by adding
  local checks.

## Repair direction (REPAIR_PROTOCOL_BEFORE_AUTHORIZATION)

1. **Make the binding authorization control external and server-side.**
   - Before launch, an independent session on a machine other than the execution host verifies the freeze,
     amendment, authorization and launch-notice commits through the GitHub API: server-side commit objects, the
     branch head and ancestry, with no local refs.
   - It writes a signed or committed pre-launch attestation naming the host, slot and authorization sha256.
   - The on-host verifier becomes a fail-closed consistency check. It runs with a clean git environment
     (`GIT_NO_REPLACE_OBJECTS=1`, no inherited `GIT_*`, isolated config) and `python -I -B`, and refuses replace refs,
     grafts, shallow clones, alternates, symlinked mirrors, and untracked or ignored code.
2. **Make ledger semantics exact.**
   - The ledger is read from the published tip.
   - Parsing is strict (duplicate keys rejected; events and keys allow-listed).
   - A single-use `SLOT_OPENED` event is recorded before arithmetic.
   - The ordering is fixed: verify, then open the slot, then launch.
3. **Strengthen amendment review.**
   - Every pin is checked against its blob at the amendment commit.
   - A second independent review, committed after the amendment, names the amendment sha256 (sources and evidence).
   - Template comparison uses canonical bytes; timestamps must carry `Z`.
4. **Build and qualify the executor** (E1–E7, still PENDING) and the consumption adapter (E6). Then re-freeze the
   governance files once in a successor, leaving the science preregistration unchanged, and obtain an independent
   review before any authorization.

Until then, `EXECUTION_AUTHORIZED` must remain false and no real-cell computation may run.
