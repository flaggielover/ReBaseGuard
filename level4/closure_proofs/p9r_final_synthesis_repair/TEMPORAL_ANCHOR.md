# P9R temporal anchor

> **This is the only P9R document written twice.** At Checkpoint A it is
> committed with `ANCHOR_COMMIT = PENDING_THIS_COMMIT`, because a commit cannot
> contain its own hash; the hash is filled in immediately afterwards.
>
> That update is not a loophole, and nothing in this campaign trusts this
> file's prose. `TEMPORAL_ANCHOR.md` is deliberately **excluded** from
> `PROTOCOL_DIGEST.json`'s frozen set, and every assertion below is checked
> against git rather than against this document:
>
> * gate `I1` runs `git ls-tree` on the named commit and fails if any
>   production result is present in it;
> * gates `I3` and `I4` run `git show <anchor>:<path>` and compare bytes;
> * `tests/test_temporal_and_protection.py` additionally requires the anchor to
>   be an ancestor of `HEAD` and requires every result artifact's recorded
>   `git_commit` to descend from it.
>
> An adjudicator should not take the hash below on trust. Check it — see
> `CODEX_HANDOFF.md` attack 1.

---

## 1. The anchor

```text
ANCHOR_COMMIT    = PENDING_THIS_COMMIT
ANCHOR_PARENT    = dc8516732c2c5672987a6a5a22c1ce023c77f68f
ANCHOR_TIMESTAMP = 2026-09-02T15:22:41+09:00
ANCHOR_BRANCH    = main
ANCHOR_SUBJECT   = P9R Checkpoint A: pre-result temporal anchor for the
                   Level-4 Priority-9 final-synthesis repair
```

The parent is the authoritative P8R integration commit, whose subject is
`adjudicate Level-4 Priority 8 repair as closed`. At that commit
`HEAD == origin/main == dc85167`, the worktree was clean, and
`level4/closure_proofs/p9r_final_synthesis_repair/` did not exist anywhere in
history.

## 2. What the anchor commit contains

| present | absent |
|---|---|
| `README.md`, `DEFINITION_AUDIT.md`, `REPAIR_RATIONALE.md` | every production result |
| `FROZEN_PROTOCOL.md`, `FROZEN_GATES.md` | `results/sr_recurrence_check.json` |
| `CLAIM_LANGUAGE_FIREWALL.md`, `DISCREPANCY_REGISTER.md` | `results/reproduction.json` |
| `THEORY.md` — lemmas, `P9R-T2a`, `P9R-T2b`, `P9R-T3`, the SR algebra | `results/burnin_sensitivity.json` |
| `COMMAND_MANIFEST.json` — the exact production commands | `results/response_grid.json` |
| the complete `src/rebaseguard_p9r/` library | `results/claim_ledger.json`, `results/dependency_graph.json` |
| the complete `experiments/` generators, including the claim schema and the source-derived node table | `results/integrity/gate_report.json` |
| the complete `scripts/` and `tests/` | `RESULTS.md`, `REPRODUCTION.md`, `SCOPE_MAP.md`, `LIMITATIONS.md`, `CLAIM_LEDGER.md`, `CODEX_HANDOFF.md` |
| `SOURCE_MANIFEST.json`, `PROTOCOL_DIGEST.json` | |
| `results/integrity/protected_tree_manifest_pre.json` | |

The pre-campaign protected-tree manifest is the single permitted `results/`
file at the anchor: by definition it must be taken *before* the campaign runs,
and gate `I1` names it as the one exception. Everything else under `results/`
being absent is what makes this a real anchor rather than a narrative one.

## 3. Digests recorded at the anchor

```text
SOURCE_DIGEST      = c1d53e2cf66e0e18b9d4599cef8b07d3151c9cf27033e682355094a6bb16b46d
                     (20 files; see SOURCE_MANIFEST.json)
PROTOCOL_DIGEST    = 446f41a3815c4cc7c76daad89d125973aeaa1f72b318cf7919ea37c0139549e3
                     (9 files; see PROTOCOL_DIGEST.json)
PROTECTED_TREE_PRE = a52a8a96698194cb9e28ce1814a276595c1612835c910364dd6737990b5598a7
                     (3428 tracked files outside the P9R namespace; see
                     results/integrity/protected_tree_manifest_pre.json)
```

Each manifest lists every constituent path with its own SHA-256, so a
disagreement can be localised to a file rather than only detected in aggregate.
The protected-tree manifest separately records a per-tree aggregate for each
protected namespace, including `level4/closure_proofs/p9_final_synthesis` and
`level4/closure_proofs/p8r_temporal_integrity_repair`.

## 4. Authoritative state verified at the anchor

```text
HEAD                     = dc8516732c2c5672987a6a5a22c1ce023c77f68f
origin/main              = dc8516732c2c5672987a6a5a22c1ce023c77f68f
worktree                 = clean
P9  verdict              = PARTIAL   (a3e3cabc30c4508b866736aeede54db17e5e1fcc)
P8  verdict              = FAIL      (5411e2c7c5ff9af2fb983a5b5a48c1e360bca2e8)
P8R verdict              = CLOSED    (dc8516732c2c5672987a6a5a22c1ce023c77f68f)
P4, P5                   = PARTIAL
P1, P2, P3, P6, P7       = CLOSED
p9_final_synthesis       = one commit only, a3e3cab; diff a3e3cab..HEAD empty
pre-existing P9R         = none in history
```

## 5. Environment

```text
python   3.14.5
numpy    2.5.2
scipy    1.18.0
platform macOS-26.5.2-arm64-arm-64bit-Mach-O
interpreter level4/.venv/bin/python
```

## 6. Command manifest

The exact production commands are frozen in `COMMAND_MANIFEST.json` and are not
repeated here, so that there is one place to change and gate `I4` guards it.

## 7. What would invalidate this anchor

* a production result present in the anchor commit (gate `I1`);
* any byte of `SOURCE_MANIFEST.json`'s or `PROTOCOL_DIGEST.json`'s files
  differing between the anchor and `HEAD` (gates `I3`, `I4`);
* a result artifact whose recorded `git_commit` does not descend from the
  anchor (focused test);
* the anchor not being an ancestor of `HEAD`, or being squashed away.

Checkpoint A is never squashed.
