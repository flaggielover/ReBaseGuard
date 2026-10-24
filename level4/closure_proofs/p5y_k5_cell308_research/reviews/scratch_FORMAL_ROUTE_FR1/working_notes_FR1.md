# Formal route / governance review FR1 — Cell-308 MB-S new-host route, Cloud r1

- Reviewer: reviewerFR1 (fresh agent, brief FR1)
- Date: 2026-10-16
- Pinned commit: 29d79e7045e36c71fa1f30c03d83e92be8a58006 (detached worktree tree_29d79e70)
- Status: IN PROGRESS (written incrementally)

## Working notes (to be replaced by final sections)
- Scope sha256 values: all eight match the brief at 29d79e70.
- USER_AUTHORIZATION_20261016_OD2.md (named in brief line 2) is NOT present in governance/new_host_route_cloud_r1/ at 29d79e70.
- Accepted-source sha256 at 29d79e70 match packet §2 prefixes (governance, A1, A1 E1, route A1, E1, ratification, brief R2); route E2 = 620bfbb9...a5c1.
- Quotes checked verbatim so far: route A1 §1 RC2, §2 HOST row, §3 MBR1_REPRO; route E1 DR2; governance S5, S7, S10; A1 S12, S13, S15; A1 E1 D2, D3; ratification R-FREE, R-MEM 1/5, item 15, rows 24/25; brief R2 §6 EVAL_CAP, §9 rows, MBS-5(b).
- Brief R2 is a user decision brief (briefer2); its §9 rows describe the MB-S protocol DRAFT's gates (line 402). [ACCEPTED] for brief-R2 §9 "Thermal pressure level 0" etc. overstates the source class.
- R-ALLOW (b) literal path list includes /usr/sbin/ and /sbin/ (ratification line 75), which exist on Linux: D-ALLOW-PATHS "none" is an amendment (stricter), not "amends nothing".
- Full clone (blob:none, scratch/fullclone): five reference blobs introduced at 7eb057bb (subject: official qualification at freeze r3 c46434a3: PASS); same paths held r1-qualification blobs (3a05aef7, deleted 29b68d5e) and r2-qualification blobs (d031dad8, deleted by freeze r3 c46434a3). Addendum omits the earlier generations. Ancestry c46434a3 < 7eb057bb < 142d97a9 and < 21e99cf0 confirmed; no change to the paths in 7eb057bb..142d97a9. sha256 of all 5 blobs + 2 code blobs recomputed: equal.
- source_sha256 of all 16 pinned definitions recomputed with ast.get_source_segment (CPython 3.13.16): equal. fs grammar: f"{numerator}/{denominator}" of a normalised Fraction (always contains "/").
- a40211cc, 9ad632c9, e451e634 (S14) are not objects of this repository (not in the full clone): S14 MET is UNVERIFIED here.
