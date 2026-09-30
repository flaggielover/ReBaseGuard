# FC2 spec rev. 2, erratum 1 (pre-freeze; from comparing the two independent implementations)

`fc2/FC2_SPEC_R2.md` stays unchanged. This erratum governs where the two differ. It is part of the rev. 2c amendments
(`governance/P309_REV2C_AMENDMENTS.md`, A2) for the independent pre-freeze review.

| id | point | ruling | why |
|---|---|---|---|
| E1-1 | §3 check 7: "No ref other than the marker and the current branch points to a descendant of the grant commit" | **strict descendant.** A ref pointing at the grant commit **itself** is allowed; for example the remote-tracking ref after the owner's grant commit is pushed and fetched. A ref pointing at a commit that has the grant commit as a **proper** ancestor is refused. Both implementations must use this reading | the verifier variant counted refs equal to G as descendants. In production the remote-tracking ref of the branch equals G, so the variant would refuse every in-band Stage-1a certificate. Every verdict would then be REFUSE and fall back (protocol §2.5): SRK would silently contribute nothing, and the single evaluation would be spent. The guard already used the strict reading |
| E1-2 | §3: what `admission_decision` returns for an item that meets no band | both conventions are acceptable, and each is recorded: the guard returns `NOT_BANDED`, and the variant returns `ADMIT` with "meets no band". An item that meets no band is not an admission question. Neither implementation's callers treat the value as a band admission | a documented difference, not a defect |
| E1-3 | grant `geometry` strings | the proposed grant uses **exactly** `{"h": "5", "k": "1/2"}`. The variant requires these exact strings, and the guard accepts any rationally equal strings | the stricter reading governs the grant text |
| E1-4 | `frozen_commit` versus the grant commit | the variant requires a proper ancestor, and the guard allows equality. The rev. 2c chain (freeze → qualification → review → grant) makes them always different | no conflict in practice |
| E1-5 | outputs during qualification | the variant's harness gains `--out PATH` (default unchanged), so that qualification writes under `qualification/` and never modifies the frozen `verify/` directory | rev. 2c A8 |
