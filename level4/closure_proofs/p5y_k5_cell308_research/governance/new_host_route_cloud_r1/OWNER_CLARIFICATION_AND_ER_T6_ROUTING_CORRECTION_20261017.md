# Owner factual clarification, and author correction of the ER-T6 r2 routing (Cell-308 Cloud route r1), 2026-10-17

**Status: OWNER STATEMENT (recorded verbatim) · AUTHOR CORRECTION (coordinator side; not independently confirmed).**
This record makes no eligibility ruling. It adopts no rule, grants no S1 or OD-3, and authorizes no execution. The B3
round stays closed, and every unresolved finding (YC1–YC4; rows A6b, A14a, A14b, A14p) is retained.
`new_target_evaluations = 0` · `cell309_activity = none`.

## 1. The owner's factual clarification (verbatim)

> "I, the owner, have never personally seen the actual MB r1 target-run runtime or host observations named by E1″. Do
> not ask me to attest otherwise or read those observations merely to establish eligibility."

## 2. The statements in play, kept apart

| source | class | what it says | what it does **not** establish |
|---|---|---|---|
| governance A1 **S13** (`SUCCESSOR_GOVERNANCE_308_ADDENDUM_A1.md`, line 148 onward) | **ACCEPTED** | E1″ "names, never values, the MB r1 target-run runtime and host observations, where they are recorded, and who holds them". The successor's route, implementation and caps agents have not seen them | any rule on who may read the register. Whether the register's actual bytes match that description is **unverified** |
| governance A1 erratum E1 **D3** (lines 40–48) | **ACCEPTED** | adds reviewGOV and reviewADJ as holders, and bars them from successor route, implementation and caps roles | any reader requirement |
| route-audit addendum A1, item **9(e)** (`registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1.md`, lines 98–100) | **ACCEPTED** (a risk statement) | the go / no-go decisions "are taken with the lost run's runtime-only observations in view" | that the owner personally read them, the owner's actual exposure history, or a requirement that every register reader be a prior holder |
| ER-T6 r2 §4 (`EVIDENCE_REQUEST_ER_T6_ROLE_HOLDER_CHECK_R2_20261017.md`, lines 63–65) | **AUTHOR-PREPARED**, not adopted | "the owner personally, **or** an existing listed holder whom the owner specifically authorizes"; "must already be eligible … under the governing rule" | that a governing rule exists. None has been identified |
| the coordinator side's routing reply of 2026-10-17 (in chat) | **coordinator interpretation** | read A1 9(e) as making the owner an existing holder, and told the owner to confirm prior exposure or stop | — (withdrawn below) |

## 3. Author correction

1. **No binding provision found.** Among the accepted texts available to the coordinator side, none makes prior
   exposure to the E1″-named observations a condition for reading the E1″ register. The texts searched were the
   governance text, addendum A1 and erratum E1, the conditions register, brief R2, and route-audit addendum A1.
   The register exclusion applied to earlier reviewers came from **coordinator-authored brief restrictions**, not
   from an accepted provision.
2. **Withdrawn.** The routing reply's instruction that the owner "must confirm prior observation exposure", and its
   reading of A1 9(e) as establishing the owner's holder status, are both withdrawn. ER-T6 r2 §4's two alternatives
   stand as written, with no added holder requirement on the owner alternative.
3. **The narrower conclusion that replaces them:** "Owner non-holder status has not been shown to be independently
   disqualifying. Overall eligibility and other access requirements remain unresolved."
4. **ER-T6 r2 §4's phrase "under the governing rule"** is read as: *no governing rule has been identified; the owner
   alternative rests on the owner's own authority, recorded in the owner's record.*

## 4. Remaining prerequisites for an owner-personal, bounded register-metadata lookup

| dimension | status |
|---|---|
| **reader authority** | the owner, acting personally. An AI acting for the owner is not the owner personally. No accepted bar has been found. The authority is the owner's own recorded decision to perform the lookup. That decision is not yet recorded |
| **exact source bindings** | register path, from S13: `level4/closure_proofs/p5y_k5_cell308_research/ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`. Commit pin: **MISSING**. Blob id and sha256: **MISSING**. MBS-1 location list: path **MISSING**, and whether it is part of the same file is **unknown**. The request's commit (`58769a0f`) is the request's pin, **not** a source pin |
| **identity matching** | per ER-T6 r2 §3, row by row. R1b and R3c are CANNOT_TELL by construction. The other rows are labels only |
| **actual exposure** | S13 describes the register as names only, but its bytes are unverified. If, on reading, the register shows any observation value, time or figure, the owner stops at once and records that the description did not hold. The consequences for the owner's roles are then an open question, not decided here |

## 5. How the bindings can be fixed without viewing any content

These commands are run by the owner personally, in the owner's own clone. They print only commit ids and digests; no
file content is shown.

```
P=level4/closure_proofs/p5y_k5_cell308_research/ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md
C=$(git log -1 --format=%H origin/codex/cell308-claude-r5-integration -- "$P")   # last commit that changed it
git rev-parse "$C:$P"                                                           # blob id
git cat-file blob "$C:$P" | wc -c                                               # length
git cat-file blob "$C:$P" | sha256sum                                           # digest
```

* The owner records `C`, the blob id, the length and the sha256 in the owner's own record. That binding is then fixed
  before any reading.
* The MBS-1 location list is bound **after** this step. Whether it is contained in the bound file is learned during the
  authorized reading of that file. If it points to a separate record, the owner binds that record the same way before
  reading it.
* The coordinator side does not run these commands. Its own exclusion (no read, grep, hash or list of the register) is
  unchanged.
