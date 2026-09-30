# Owner ratification request D5: the two scanner extensions (blocks the freeze)

**Source.** Delta review condition D5 (`reviews/REVIEW_DELTA_INCIDENT_P309.md` §7, commit e53a678c):

> The owner must ratify the two scanner extensions: A10's pending-ref NAME, and A19's sanctioned marker-mutating
> exactly-once sites. Independent review can confirm that they are narrow, but it cannot supply the owner's authority.
> If the owner refuses, the design must change before the freeze.

**Why the owner must decide.** Owner rulings 2 (quarantine scanner) permit an allowance for the production marker
**NAME** only, as inert metadata. They state that the allowance "must NOT permit":
* creation of the marker ref;
* mutation of the marker;
* consumption of the marker;
* construction of a production grant;
* bypass of quarantine;
* hidden evaluation.

Two parts of the frozen design go beyond that allowance. The coordinator **cannot** resolve this by reinterpreting the
ruling. The freeze waits for the owner's decision.

## Extension 1 (rev. 2c A10): the pending-ref NAME

| item | value |
|---|---|
| literal | `refs/p5y-k5-cell309-p309-r1/pending-result` |
| constant | `PENDING_REF`, defined once in `code/p309_guard.py` |
| allowed in | `code/p309_guard.py` **only**, as the inert definition. Conditions (a)–(e) are the same as for the marker name |
| purpose | package §E, recording from memory. Right after the marker, the result blob is persisted under this second ref before the seal commit. A crash between the marker and the seal then leaves recoverable evidence for `seal-only`, rather than CONSUMED_UNRECORDED |
| never created before | the owner's grant and `execute`. It is created only after the marker, by site 2 below |

## Extension 2 (rev. 2c A10/A19): two sanctioned exactly-once sites

The scanner's formal rule MARKER_MUTATION flags any ref mutation of a production name. It is sanctioned **only** inside
these two functions, each identified by file, name and the sha256 of its `ast.dump`.

| site | file | what it does | AST sha256 (current; the freeze pins this value unless the function changes before then) |
|---|---|---|---|
| `_arm_marker` | `code/p309_driver.py` | the single compare-and-swap `git update-ref <marker> <grant commit> 0000…` that **creates the production marker, which consumes the single evaluation** | `1ee764b7b1cfca7b2fbda9b394e8af235239a2d308905a9f07f521b39b80be0c` |
| `_persist_pending` | `code/p309_driver.py` | the compare-and-swap that creates the pending ref (extension 1) after the marker | `13ee3ec3b7ba4c3ff80103c16671d4697967bfb177f4ae964084c95ab2fbbaaf` |

**Constraints on both sites** (each is checked mechanically):
* The first statement is `_assert_execute_context`. It refuses unless the process is in `execute` or `seal-only` mode
  and the context's names are exactly the guard's names for its kind (production or sandbox).
* The only callers are `run_execute`, `after_marker` and `run_seal_only` (QC12 T4, scanner).
* `run_execute` reaches `_arm_marker` only after `check_grant` accepts the owner's grant commit. The chain must be
  freeze → qualification → accepted qualification review → grant, with every binding checked: cell, geometry, Ew,
  verifier, frozen hash, host, expiry and marker identity.
* Any change to either function changes its AST hash, which makes the scan fail. The allowance cannot silently widen.
* In every test (QC11, FC2 controls), the sites run only in sandboxes with the synthetic names
  `refs/p309-test/TEST_ONLY_DO_NOT_EXECUTE_P309_MARKER` / `…_PENDING`. The production names are never created
  anywhere (flow `Z_no_production_ref_anywhere`).

**What ratification would and would not do.** Ratification allows this code to exist in the frozen tree and the scanner
to accept it. It does **not** authorize creating either ref. Creation happens only when `execute` is run after the
owner's separate final execution grant. It remains FORBIDDEN until then, and the coordinator will not run `execute`.

## Decision requested

1. **RATIFY both extensions.** The freeze proceeds with the design as reviewed.
2. **RATIFY extension 2 only; REFUSE extension 1.** The pending ref is removed, which is a design change before the
   freeze: recording would rely on the emergency file and the direct seal only, with a larger CONSUMED_UNRECORDED
   window. The change needs re-implementation, QC11 re-runs and a delta review.
3. **REFUSE extension 2.** The package cannot create its marker, so it cannot execute under any grant. The design would
   have to be replaced before the freeze, for example by an owner-operated marker procedure. That needs a new
   amendment and new reviews.

Until the owner rules, the campaign stops before the freeze. No freeze commit, no qualification run.
