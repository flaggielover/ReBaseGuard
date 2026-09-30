# FC2 specification, revision 2: band-scoped admission for the guard and the verifier variant

**Supersedes** `fc2/FC2_SPEC.md` (revision 1, commit 2f1b6073). Revision 1 stays unchanged as the record. It had an
error: its test band [3/2, 7/4] lies **inside** the quarantine band [6/5, 13/5], and the inherited quarantine applies
that band to every geometry. Nothing was ever run under revision 1. This revision incorporates the owner's rulings 2
(`governance/OWNER_RULINGS_2_P309_VERBATIM.md`): FC2 test band; quarantine scanner; sandbox marker; grant-admission
code. It implements protocol rev. 2b §7 (a)–(d).

**This specification authorizes writing and testing the mechanism only.** It issues no grant and lifts no quarantine.
Until the owner's later explicit grant exists, every real-band item is refused. No production marker is created
anywhere, and no real in-band quantity is computed.

## 0. Roles (kept separate, per the reviewed package)

| component | file | author |
|---|---|---|
| verifier variant | `verify/srk_verify_indep_scoped.py` | the **independent verifier's author** (owner ruling: "IS authorized to implement the grant-scoped admission mechanism"). The original `RNS/verify/srk_verify_indep.py` is not modified |
| its harness and tests | `verify/run_verify_all_scoped.py`, `tests/test_verify_scoped.py` | the verifier's author |
| producer-side guard | `code/p309_guard.py` | the coordinator (producer side) |
| its tests | `tests/test_p309_guard.py` | the coordinator |
| the independent review of both against this spec | `reviews/REVIEW_FC2_P309.md` | a reviewer who wrote neither |

Neither implementation reads the other's code. Both build their own sandbox helper from §6. The file names avoid the
word `GRANT`, because the formal push procedure refuses any path containing it (check 7).

## 1. Band tables (compiled constants in each file; never read from input)

| band | drift ranges | geometries it applies to | admissible only under |
|---|---|---|---|
| **REAL** | [6/5, 13/5] and [−13/5, −6/5] | **every** geometry. This is geometry-blind, as `TARGET_QUARANTINE_309.json` is; the original verifier only checks (5, 1/2) | the **production** context, and only for geometry (5, 1/2) |
| **TEST** | [341/1024, 201/512] and [−201/512, −341/1024] | geometry (3, 1/2) only | a **test** context |

* **TEST band.** It is the drift hull Ew of the **declared synthetic decoy cell** (h = 3, k = 1/2, C = [1/3, 20/51];
  `RNS/config/SRK_DECOY_DECLARATION_A2.json`, cell family): the outward 2⁻¹⁰ dyadic hull of C.
  * Its committed certificates (`RNS/evidence/srk_decoys_cell/cell_h3_k1_2_C1_3_20_51_S0..S3.json`) are the
    positive-path fixtures. No new producer run is needed.
  * It is disjoint from the REAL band and its mirror, from every real-geometry decoy, and from the cell-309 target.
    It uses a synthetic geometry.
  * It exposes and approximates nothing about the target.
* **Meets a band.** A certificate (block **or** weight block) or a guarded interval meets a band if it intersects one
  of the band's ranges, for a geometry the band applies to.
* **No other band exists.** A geometry or drift outside both bands is handled exactly as by the original verifier and
  the research guard.

## 2. Contexts

### 2.1 Production context (a module-level singleton; no parameters; not constructible by callers)

| field | value (hard-coded) |
|---|---|
| repository | the repository containing the implementing file (resolved from `__file__` with `git rev-parse --show-toplevel`) |
| grant path | `level4/closure_proofs/p5y_k5_cell309_p309_r1/authorization/P309_GRANT.json`, read with `git show <commit>:<path>` |
| schema | `P309_GRANT/1` |
| campaign | `p5y_k5_cell309_p309_r1` |
| cell | the integer 309 |
| geometry | h = 5, k = 1/2 |
| marker ref | `PRODUCTION_MARKER = "refs/p5y-k5-cell309-p309-r1/target-consumed"` (the only occurrence of this literal in the file; §7) |
| ref namespace | `refs/p5y-k5-cell309-p309-r1/` |
| frozen manifest path | `level4/closure_proofs/p5y_k5_cell309_p309_r1/freeze/P309_FREEZE_MANIFEST.json` |
| sealed result path (review mode) | `level4/closure_proofs/p5y_k5_cell309_p309_r1/evidence/execution/P309_RESULT.json` |

### 2.2 Test context (`TestContext(sandbox_root)`)

| field | value |
|---|---|
| repository | `sandbox_root`, supplied by the caller |
| grant path | `TEST_ONLY/P309_TEST_GRANT.json` |
| schema | `P309_TEST_GRANT/1` |
| campaign | `TEST_ONLY_DO_NOT_EXECUTE` |
| cell | the string `TEST_ONLY_DO_NOT_EXECUTE` |
| geometry | h = 3, k = 1/2 |
| marker ref | `TEST_MARKER = "refs/p309-test/TEST_ONLY_DO_NOT_EXECUTE_P309_MARKER"` |
| ref namespace | `refs/p309-test/` |
| frozen manifest path | `TEST_ONLY/P309_TEST_FREEZE_MANIFEST.json` |
| sealed result path | `TEST_ONLY/P309_TEST_RESULT.json` |

Everything in 2.2 is fixed in code except `sandbox_root`. **The constructor refuses** (raises; nothing is admitted) if
any of these holds:
* the sandbox's resolved top-level equals the implementing file's repository;
* its `git rev-parse --git-common-dir` resolves to the implementing file's repository's common dir (a worktree of it);
* it has any ref under `refs/p5y-k5-cell309-p309-r1/`.

**Structural separation.**
* The production context is never built from parameters, and the test context can never carry a production value.
* A test context can only admit TEST-band items. The production context can only admit REAL-band items of geometry
  (5, 1/2).
* The production path never reads a sandbox, a test ref or a test path.

## 3. Admission (`admission_decision(item, *, ctx=PRODUCTION, mode="official") -> (decision, reason)`)

* **item.** One of:
  * a certificate descriptor: geometry, block, weight block, sha256;
  * an interval: geometry, lo, hi (for the guard).
* **decision.** `ADMIT` or `REFUSE`. Every REFUSE reason starts with `quarantine:`.
* **Fail closed.** The function evaluates only parsing, git metadata, hashes and exact rational comparisons. **Any
  exception inside it is caught and returned as REFUSE.** There is no default ADMIT, no implicit grant and no embedded
  valid grant.

**Order of checks (official mode).** An item meeting no band is not an admission question (§4). For a band-meeting
item, **all** of the following must hold:
1. **Band ↔ context.**
   * A REAL-band item needs `ctx is PRODUCTION` and geometry (5, 1/2).
   * A TEST-band item needs a `TestContext` and geometry (3, 1/2).

   Anything else is refused. So test authorization cannot admit the production band, and the production context
   cannot admit the test band.
2. **Grant present and well formed.** The grant file exists at HEAD (`git show HEAD:<grant path>`) and parses as a JSON
   object with:
   * `schema`, `campaign` and `cell` equal to the context's (exact type: the integer 309, or the TEST string);
   * `geometry` = {"h": "5", "k": "1/2"} (or "3", "1/2");
   * `cell_interval` and `drift_hull_Ew`: pairs of exact rational strings with lo < hi;
   * `frozen_commit` (40 hex digits);
   * `frozen_manifest_sha256` (64 hex digits);
   * `verifier_id` and `guard_id` (`sha256:` + 64 hex digits);
   * `execution_host.host_id_sha256` (64 hex digits);
   * `runtime.python` (a string);
   * `marker_ref` (equal to the context's marker ref);
   * `not_after_utc` (ISO-8601 UTC).

   A missing field, a wrong type, or an unknown `schema` is a refusal.
3. **Ew binding.** `drift_hull_Ew` equals the outward 2⁻¹⁰ dyadic hull of `cell_interval`:
   [⌊lo·2¹⁰⌋/2¹⁰, ⌈hi·2¹⁰⌉/2¹⁰]. Each implementation computes this itself.
4. **Grant commit.**
   * Exactly one commit in HEAD's history adds the grant path.
   * That commit changes **only** the grant path (`git diff-tree --no-commit-id --name-only -r`).
   * HEAD **equals** that commit.
5. **Frozen identity.**
   * `frozen_commit` is an ancestor of the grant commit.
   * `sha256(git show <frozen_commit>:<frozen manifest path>)` = `frozen_manifest_sha256`.
   * That manifest's `code_pins` list the implementing file's repository-relative path, with sha256 equal to the
     sha256 of the implementing file's own bytes.
6. **Own identity.** `sha256:` + sha256(own file bytes) equals `verifier_id` (for the verifier) or `guard_id` (for the
   guard).
7. **Marker binding.**
   * `git rev-parse --verify --quiet <marker ref>^{commit}` equals the grant commit.
   * The marker ref is the only ref under the context's ref namespace. Any other ref there means recording has begun
     or the target is consumed, and the item is refused.
   * No ref other than the marker and the current branch points to a descendant of the grant commit.
8. **Expiry.** Now (UTC) ≤ `not_after_utc`.
9. **Host and runtime.**
   * `sha256(b"machine-id:" + /etc/machine-id bytes stripped + b"\nhostname:" + socket.gethostname().encode())`
     equals `execution_host.host_id_sha256`.
   * `platform.python_version()` equals `runtime.python`.
10. **Item inside Ew.** The block (or interval) **and** the weight block lie inside `drift_hull_Ew`. For a
    certificate, the weight block **equals** `drift_hull_Ew`.

**Review mode** (verifier only; post-seal re-verification) replaces 4 and 7–9 by the checks below. It keeps 1–3, 5, 6
and 10, evaluated against the grant **as committed at the grant commit**.
* The marker names a commit G that adds the grant path. That grant is the one used.
* There is exactly one commit S whose **only** parent is G.
  * S changes only the sealed result path.
  * The sealed result at HEAD is byte-identical to that at S.
* The sealed result parses. Its `stage1a.certificates` lists the certificate's sha256, as a string or as an object's
  `sha256` field.

Review mode admits nothing else, and it never admits a guard interval.

## 4. Verifier variant behaviour

* **Meets no band:** it behaves bit-for-bit as the original verifier, in verdict and reason.
* **Meets a band and is not admitted:** REFUSE at parse time. The reason is `quarantine: <the admission reason>` and
  nothing is evaluated.
* **Meets a band and is admitted:** it is verified exactly like any other certificate, with the same mathematics.
* **Entry point.** `verify_cert(raw, file_kernel, N, max_depth, procs, log, *, ctx=PRODUCTION, mode="official")`.
  Without keyword arguments it is the production context in official mode.
* **Probes (protocol §7(c)).** The harness's probe-construction guard uses its **own** compiled copy of §1:
  * Any probe that meets the REAL band must come back REFUSE with nothing evaluated.
  * A TEST-band probe may be evaluated only when a test context admits it.

## 5. Guard behaviour (`code/p309_guard.py`)

* **`guard_interval(geometry, lo, hi, *, ctx=PRODUCTION)`.**
  * Meets no band: allowed (it is still subject to the research guard's other rules).
  * Meets a band: allowed iff `admission_decision` returns ADMIT. Otherwise it raises `QuarantineRefusal`.
* **`producer_adapter(ctx=PRODUCTION)`.** It returns an object with the `q309_guard` API the pinned producer uses at
  run time:
  * `guard_drift(e_lo, e_hi=None)`: calls `guard_interval` with the real geometry (5, 1/2);
  * `log_execution(...)`: writes to the formal ledger;
  * `install_import_guard()`: delegates to the research guard.

  The driver installs it in place of `srk_certify.Q` **in execute mode only, after check_grant**. Everywhere else the
  research `q309_guard` stays in force.
* **Without a grant**, every REAL-band interval is refused. In this stage no grant exists.

## 6. Sandbox for tests (each author builds their own helper from this section)

* **Location and remote.**
  * The sandbox is a `git clone --shared --no-checkout` of this repository, under the scratchpad
    (`…/scratchpad/fc2_sandbox_<author>/`), with `origin` removed.
  * It is never pushed, and no other remote is ever added.
* **Test fixtures,** committed inside the sandbox only:
  * `TEST_ONLY/P309_TEST_FREEZE_MANIFEST.json`, whose `code_pins` list the implementing file's path and sha256;
  * then a test grant commit adding `TEST_ONLY/P309_TEST_GRANT.json`, with the §3 fields for the TEST context:
    cell_interval ["1/3", "20/51"], Ew ["341/1024", "201/512"];
  * then `git update-ref refs/p309-test/TEST_ONLY_DO_NOT_EXECUTE_P309_MARKER <grant commit>`.
* **Forbidden names.**
  * **The production marker name, and any ref under `refs/p5y-k5-cell309-p309-r1/`, is never created anywhere**,
    including sandboxes, temporary namespaces and mock repositories (owner ruling).
  * The production grant path is never written anywhere.
* **Host binding in tests.** Tests write the local host id into test grants. A wrong-host control writes a different id.

## 7. Scanner allowance (owner ruling "QUARANTINE SCANNER"; `code/p309_scan.py`)

* **What is allowed.** The research scanner's TARGET_PATH finding for the literal
  `refs/p5y-k5-cell309-p309-r1/target-consumed` is allowed in exactly these files:
  * `verify/srk_verify_indep_scoped.py`;
  * `code/p309_guard.py`;
  * later, the driver, if FC6 adds it by a reviewed amendment of `config/SCANNER_ALLOWANCE_P309.json`.
* **Conditions per file.** The finding is allowed only when **all** of these hold:
  * (a) the literal occurs exactly once among the file's string constants;
  * (b) that occurrence is the value of a module-level assignment to the single name `PRODUCTION_MARKER`;
  * (c) `PRODUCTION_MARKER` is never re-bound;
  * (d) no call anywhere in the file passes `PRODUCTION_MARKER` (or the literal) together with a ref-mutating git verb
    (`update-ref`, `push`, `tag`, `branch`, `symbolic-ref`, `replace`, `notes`, `fetch`, `-d`, `--delete`);
  * (e) the file is listed with its path in `config/SCANNER_ALLOWANCE_P309.json`.
* **Not a whitelist.** Every other finding stands: CELL_LITERAL and BAND_LITERAL keep the research `literal-ok`
  mechanism, which is listed and never silently dropped. The allowance permits no creation, mutation or consumption of
  the marker, no construction of a production grant, no quarantine bypass and no evaluation.
* **New scanner rules, formal namespace:**
  * **MARKER_MUTATION**: a ref-mutating git call naming `PRODUCTION_MARKER`, the literal, or the ref namespace.
  * **GRANT_WRITE**: any write call (`write_text`, `write_bytes`, `open(..., "w"/"a"/"x")`, `git add`, `git commit`)
    whose arguments include the production grant path or the name `P309_GRANT.json`.
  * Both are findings everywhere in the formal namespace, with no allowance in this stage.
* **Controls** (`tests/test_p309_scan_allowance.py`). Each of these must be flagged, in a temporary copy:
  * a second occurrence of the literal;
  * the literal outside the `PRODUCTION_MARKER` assignment;
  * a re-binding;
  * an `update-ref` with the constant;
  * a `push` with the literal;
  * an unlisted file;
  * a grant write.

  A correctly formed allowed file must pass.

## 7a. Grant-write and marker-creation hygiene in tests

Tests may construct **test** grants in a sandbox only. Neither implementation's code contains a routine that writes a
production grant or creates the production marker (the §7 rules enforce this).

## 8. Mandatory tests (both implementations; each against its own code)

| id | control | expected |
|---|---|---|
| N1 | no grant: production context, REAL-band item (dry); test context with no test grant, TEST-band item | REFUSE |
| N2 | malformed grant: invalid JSON; a missing field; a wrong type; an unknown schema; Ew lo ≥ hi; a non-rational | REFUSE |
| N3 | wrong cell (TEST grant with another cell string; a cell of the wrong type) | REFUSE |
| N4 | wrong Ew: block outside Ew; weight block ≠ Ew; Ew not the outward hull of cell_interval | REFUSE |
| N5 | wrong verifier_id (verifier) / wrong guard_id (guard) | REFUSE |
| N6 | wrong frozen identity: manifest sha mismatch; frozen_commit not an ancestor; own file missing from the manifest or with another sha | REFUSE |
| N7 | marker: absent; pointing elsewhere; an extra ref in the namespace (consumed / recording); HEAD ≠ grant commit; the grant commit touching another file; two commits adding the grant; grant expired | REFUSE |
| N8 | wrong host id; wrong runtime | REFUSE |
| N9 | **test authorization cannot authorize the production band:** a valid test context with a REAL-band item of geometry (5, 1/2) (dry), and of geometry (3, 1/2) | REFUSE |
| N10 | **production authorization cannot be synthesized from test artifacts:** (a) a sandbox whose **test** grant path holds a production-shaped file (schema `P309_GRANT/1`, cell 309, geometry (5, 1/2)), used with the production context (which reads only its own repository) and with the test context; (b) a REAL-band item of geometry (5, 1/2) presented with that sandbox's test context; (c) a TestContext pointed at this repository or a worktree of it. Nothing is ever written at the production grant path, in any repository | REFUSE; (c) raises at construction |
| N11 | **synthetic marker substituted for production:** a sandbox where the TEST marker points at the commit adding the production-shaped file of N10(a), used with the production context and with the test context; and a production-context call made while the only marker present anywhere is the TEST marker | REFUSE |
| N12 | review mode: sha not listed; the seal commit's parent is not G, or it has two parents; the seal commit touches another file; the result changed after the seal | REFUSE |
| N13 | fail-closed: an exception raised inside a check (e.g. an unreadable git) | REFUSE |
| P1 | TEST positive path: a valid sandbox (manifest, test grant, TEST marker at the grant commit, HEAD = grant commit) | every committed h3 decoy-cell certificate: ADMIT, then a verdict and reason **identical** to the original verifier's committed result (verifier); `guard_interval` allowed for sub-intervals of Ew (guard) |
| P2 | TEST review mode: a seal commit listing a subset of the shas | listed ⇒ ADMIT; unlisted ⇒ REFUSE |
| I1 | identity outside every band: full decoy suite, v2 batteries, 21 self-tests (verifier) | identical verdicts and reasons; any band-meeting probe is REFUSE with nothing evaluated |
| D1 | REAL band, production context, dry (this repository has no grant) | REFUSE `quarantine: …no grant…` |

Every test execution is ledgered (`p309_env.log`). No REAL-band certificate is ever evaluated. No production marker
or production grant exists at any point.

## 9. Evidence of independence (protocol §7(b); R3 N18)

For the verifier variant, the author's report records:
* its session identifier;
* the sources it read;
* a statement that no producer or guard code was consulted;
* the variant's sha256.

The FC2 independent review assesses independence procedurally.
