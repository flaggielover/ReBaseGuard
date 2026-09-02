# P8R temporal anchor

> **This file is the only P8R document that is written twice.** At Checkpoint A
> it is committed with `ANCHOR_COMMIT = PENDING_THIS_COMMIT`, because a commit
> cannot contain its own hash. Immediately afterwards the hash is filled in.
>
> That update is *not* a loophole, and nothing in the campaign trusts this
> file's claims. `TEMPORAL_ANCHOR.md` is deliberately **excluded** from
> `PROTOCOL_DIGEST.json`'s frozen set, and every assertion below is checked
> against git rather than against this prose:
>
> * `I1` runs `git ls-tree` on the named commit and fails if any production
>   result is present in it;
> * `I6` and `I7` run `git show <anchor>:<path>` and compare bytes;
> * `tests/test_temporal_anchor.py` additionally requires the anchor to be an
>   ancestor of `HEAD` and requires every result artifact's recorded
>   `git_commit` to descend from it.
>
> An adjudicator should therefore not take the hash below on trust. It should be
> checked — see `CODEX_HANDOFF.md` attack 1.

---

## 1. The anchor

```
ANCHOR_COMMIT = PENDING_THIS_COMMIT
ANCHOR_BRANCH = main
ANCHOR_SUBJECT = P8R Checkpoint A: pre-result temporal anchor for the Level-4
                 Priority-8 repair
```

## 2. What the anchor commit contains

| present | absent |
|---|---|
| `README.md`, `DEFINITION_AUDIT.md`, `REPAIR_RATIONALE.md` | every production result |
| `FROZEN_PROTOCOL.md`, `FROZEN_GATES.md` | every calibration artifact |
| `CALIBRATION_PLAN.md`, `RNG_ADDRESS_PLAN.md`, `PRODUCTION_PLAN.md`, `STATISTICAL_ANALYSIS_PLAN.md` | every `Gamma` matrix |
| `COMMAND_MANIFEST.json` — the exact production commands | every chain and drift artifact |
| the complete `src/rebaseguard_p8r/` library | the resolution record |
| the complete `experiments/` and `scripts/` drivers | the integrity audit |
| the complete `tests/` suite | the verdict |
| `SOURCE_MANIFEST.json`, `PROTOCOL_DIGEST.json` | |
| `results/integrity/protected_tree_manifest_pre.json` | |

The pre-campaign protected-tree manifest is the single permitted `results/` file
at the anchor: by definition it has to be taken *before* the campaign runs, and
`I1` names it explicitly as the one exception. Everything else under `results/`
being absent is exactly what makes this a real anchor.

## 3. Digests recorded at the anchor

```
SOURCE_DIGEST        = see SOURCE_MANIFEST.json  ("aggregate_sha256")
PROTOCOL_DIGEST      = see PROTOCOL_DIGEST.json  ("aggregate_sha256")
PROTECTED_TREE_PRE   = see results/integrity/protected_tree_manifest_pre.json
```

Each file also lists every constituent path with its own SHA-256, so a
disagreement can be localised to a file rather than only detected in aggregate.

## 4. Environment

```
python 3.14.5   numpy 2.5.2   scipy 1.18.0
interpreter: level4/.venv/bin/python
platform: darwin (macOS), arm64
```

Every result artifact records this independently in its provenance envelope, so
a result produced under a different environment is visible without consulting
this file.

## 5. Repository state entering the campaign

```
P8 authoritative verdict   FAIL
P8 adjudication commit     5411e2c7c5ff9af2fb983a5b5a48c1e360bca2e8
                           "adjudicate Level-4 Priority 8 model-class
                            robustness as failed"
commits touching the P8 namespace, whole history:  exactly one (5411e2c)
working tree at campaign start:                    clean
```

Verified independently at the start of this campaign with
`git log --all -- level4/closure_proofs/p8_model_class_robustness`.

## 6. Intended production commands

`COMMAND_MANIFEST.json`, committed at the anchor, lists all 65 verbatim.
`experiments/pipeline.sh` runs them in the frozen order. Every artifact records
its own `argv`, so the manifest and the artifacts can be compared directly.

## 7. Disclosed pre-anchor activity

Two things were done before the anchor and are disclosed because they shaped the
frozen protocol. Neither produced a production result and neither is cited as
evidence for any question.

1. **Throughput measurement.** Wall-clock cost per row block, which fixed the
   production budgets.
2. **Convergence check on the calibration update rule.** `ARL_0` is not linear in
   the SR natural threshold; the frozen update is therefore a log-log secant.
   See `CALIBRATION_PLAN.md` §3 and `REPAIR_RATIONALE.md` §5.

Both were run on a scratch copy of this tree at reduced budgets, at addresses no
P8R result uses, in `level4/closure_proofs/_p8r_smoke/`. That directory was
deleted before Checkpoint A and is not tracked; it does not appear in the anchor
commit or anywhere in the repository.

## 8. The rule this anchor exists to enforce

**No production scientific result may exist before this commit, and nothing
frozen here may change after it.**

If a legitimate, result-independent amendment ever becomes necessary, the frozen
procedure in `PRODUCTION_PLAN.md` §7 applies: stop, characterise, preserve the
old artifacts, document the amendment, **create a new temporal anchor**, and
disclose explicitly if the need was discovered by inspecting a result. The anchor
commit is never amended, rebased or rewritten.
