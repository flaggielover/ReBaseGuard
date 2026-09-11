# PS1 temporal anchor

This is the only PS1 document written twice (P8R pattern). At Checkpoint A it is committed with
`ANCHOR_COMMIT = PENDING_THIS_COMMIT`; immediately afterwards the hash is filled in. It is excluded from
`config/PROTOCOL_DIGEST.json`, and nothing trusts its prose: `code/temporal_integrity.py` checks every claim
against git (`git ls-tree` of the anchor, byte comparison of every frozen file at the anchor, ancestry of HEAD,
and ancestry of every certified run manifest's recorded commit).

ANCHOR_COMMIT = PENDING_THIS_COMMIT

At the anchor: the protocol, the deterministic partition generator and its table, the complete successor executable
surface (identity layer, T1, T3 midpoint producer, T3 aggregation with the mean-value cell mode, generated T4/T5,
stage runner, region driver), the tests and their output, and the NON-CERTIFYING pre-result feasibility evidence.
Absent at the anchor: every successor certified result (nothing under evidence/certified/).
