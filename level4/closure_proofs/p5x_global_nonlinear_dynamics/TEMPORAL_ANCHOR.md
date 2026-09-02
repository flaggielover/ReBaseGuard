# P5X temporal anchor

> **This is the only P5X document written twice.** At Checkpoint A it is
> committed with `ANCHOR_COMMIT = PENDING_THIS_COMMIT`, because a commit cannot
> contain its own hash; the hash is recorded immediately afterwards in a
> follow-up commit that touches this file only.
>
> Nothing in this campaign trusts this file's prose. `TEMPORAL_ANCHOR.md` is
> deliberately **excluded** from `PROTOCOL_DIGEST.json`'s frozen set, and every
> assertion below is checkable against git rather than against this document:
>
> * gate `G1` runs `git ls-tree` on the anchor and fails if any production
>   result is present in it, and compares every `PROTOCOL_DIGEST.json` path byte
>   for byte against the anchor;
> * gate `G11` re-derives the protected tree from
>   `results/integrity/protected_tree_manifest_pre.json` and from
>   `git rev-parse bb03c0e:<p5 path>`;
> * `tests/test_anchor_and_protection.py` requires that no production artifact
>   exists in the anchor and that the two pre-existing untracked audit
>   namespaces were not swept into git.
>
> Do not take the hash below on trust. Check it — `CODEX_HANDOFF.md` §5.

---

## 1. The anchor

```text
ANCHOR_COMMIT    = db0781ed79851ca55af788731a47a0f4dda1d9c6
ANCHOR_PARENT    = eea2bfb43803e853a1bc84d10410fd9f3984d849
ANCHOR_TIMESTAMP = 2026-09-02T18:16:55+09:00
ANCHOR_BRANCH    = main
ANCHOR_PUSHED_TO = origin/main (github.com/flaggielover/ReBaseGuard)
ANCHOR_SUBJECT   = P5X Checkpoint A: pre-result temporal anchor for the
                   Level-4 successor campaign on global nonlinear dynamics
```

The parent is `eea2bfb`, "P9R Checkpoint B: completed final-synthesis repair
campaign, CLOSED_CANDIDATE awaiting adjudication". At that commit
`HEAD == origin/main`, and `level4/closure_proofs/p5x_global_nonlinear_dynamics/`
did not exist anywhere in history.

## 2. What the anchor commit contains

| present | absent |
|---|---|
| `README.md`, `FEASIBILITY_AUDIT.md`, `THEOREM_CANDIDATES.md`, `FAILURE_ANALYSIS.md` | every production result |
| `FROZEN_THEOREM.md` — `P5X-T1` … `P5X-T9`, with tiers | `PROOF.md` (the human proofs of `L1`–`L8`) |
| `FROZEN_SCOPE.md`, `FROZEN_GATES.md`, `PROOF_OBLIGATIONS.md` | any Arb certificate or enclosure |
| `CERTIFICATE_PLAN.md`, `LEAN_PLAN.md`, `EMPIRICAL_PLAN.md`, `LIMITATIONS.md` | any Lean source |
| `CODEX_HANDOFF.md` | any Monte Carlo production run |
| `PROTOCOL_DIGEST.json`, `SOURCE_MANIFEST.json` | `RESULTS.md`, `CERTIFICATE_REPORT.md`, `NUMERICAL_CORRESPONDENCE.md` |
| `feasibility/` — the probe and its non-authoritative output | any `results/` file other than the pre-campaign protected-tree manifest |
| `scripts/`, `tests/` | — |
| `results/integrity/protected_tree_manifest_pre.json` | — |

The presence of `feasibility/results/reduction_probe.json` in the anchor is
deliberate and is what makes the feasibility verdict itself auditable: it is
marked `FEASIBILITY_PROBE_NON_AUTHORITATIVE`, it is floating point, and gate
`G8` forbids any proof path from citing it.

## 3. What the anchor does and does not fix

It fixes P5X's own provenance: the theorem statements, the scope, the gates and
the verdict semantics all predate every P5X number.

It fixes nothing about P5. Original P5 entered git in a single commit
(`bb03c0e`) and that permanent provenance limitation is recorded in
`p5_final_disposition_audit/P5_FINAL_DISPOSITION_AUDIT.md` §10. A new anchor
cannot repair a 2026-08-31 record and is not offered as doing so.

## 4. Worktree state at the anchor

`git status --porcelain --untracked-files=all` lists, besides the P5X namespace,
exactly two untracked paths that predate this campaign:

```text
level4/closure_proofs/p4_final_disposition_audit/
level4/closure_proofs/p5_final_disposition_audit/
```

Their content digests are recorded in
`results/integrity/protected_tree_manifest_pre.json` under
`untracked_namespaces_outside_p5x`. P5X does not commit, modify or delete them.
This is recorded explicitly rather than left implicit because an unrecorded
worktree-scope conjunct is precisely what failed P5's gate `G20`.
