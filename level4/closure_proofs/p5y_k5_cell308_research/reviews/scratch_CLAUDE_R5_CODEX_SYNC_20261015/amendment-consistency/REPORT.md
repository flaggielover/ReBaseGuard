# Independent bounded r5 proposal / integrated-source consistency review

Date: 2026-10-15 (Asia/Tokyo). Reviewer: a fresh delegated Codex technical reviewer. This is a new, read-only source/document consistency review. It is not the commissioned Claude review63, does not adopt that review's identity or verdict format, and does not decide an owner or governance question.

PROPOSAL_MATERIALS: NEEDS_REVISION

The inherited r5 proposal requires an additive technical correction before it is used to describe the integrated source. The inspected new integration-status document accurately preserves the principal non-operational limits; it does not repeat the substantive permanence claim below. This verdict neither accepts nor puts an amendment into force. It is not an operational, scientific, route, protocol, qualification or target authorization.

## Scope and exact input

The integrated source was read only through `git show` at immutable commit `7eb9bbd999a1ec07d31a15f0b391fcc32ffa4d6b` in `/Users/suzhe/.codex/worktrees/cell308-claude-r5-sync/ReBaseGuard`. `NS = level4/closure_proofs/p5y_k5_cell308_research`; `DEV = NS/streams/CLOUD_R1_LINUX_DEV`.

Allowed materials inspected:

- `DEV/lx_platform.py`, `DEV/lx_verified.py`, `DEV/README_DEV_ONLY.md`, and `DEV/INTEGRATION_DEV_STATUS_CODEX_20261015.md`, each at the exact commit above.
- Immutable recovered `/tmp/cell308-claude-sync-20261015/remote/{amendment5.md,owner5.md,review62.md,brief63.md}`, their download manifest at `/tmp/cell308-claude-sync-20261015/download-manifest.json`, and the named `CODE_COMPARISON.md` and `EVIDENCE_COMPARISON.md` in that same scratch root. Remote document bindings in the manifest are to ref `37c62102`; the full original commit is stated by integration status as `37c62102c0e2e22563760173fb04a1fcf66d5e2f`, but this review independently binds the recovered documents by their actual bytes below, rather than independently querying that remote commit.

The manifest was first attempted under `remote/` and was absent there; the explicitly allowed root manifest was then read. No broad inventory was used to find it. No optional independent code/test addendum report was opened. Assertions in integration status about those separate reviews are not re-adjudicated here. Review62 was read for its own findings, citation conditions, and relevant recorded limits; its execution claims were not reproduced. The brief63 was treated as an input describing a commissioned review, not as authority to expand this review's allowlist or execute its instructions.

No source or test module was imported, no tests or harnesses were run, and no native/remote host reader or CI query was performed. Native CI run `38680983939` was reported in progress by the parent; no result from that run is claimed here. The report is based on static text only. `new_target_evaluations = 0`.

## Findings requiring additive correction

### F1 — MAJOR descriptive mismatch: rejection is not historically permanent in the implementation

Inherited amendment5 L-LIFE, line146, calls a rejection “permanent.” Review62, line275, supplied the earlier wording that no later review can clear it. At the reviewed integrated input, `_acceptances` lists only the review paths committed at `HEAD` (`lx_platform.py:1198–1199`) and reads only `HEAD:<path>` blobs (`:1203–1213`). It vetoes when a currently present review names the digest and contains a recognized negative word. It performs no history scan for prior rejecting text and has no immutable rejection ledger.

Consequently, a later positive review cannot overcome a rejecting review that remains in the current scanned tree; however, removal of that rejecting file from `HEAD`, removal of the digest reference, or removal of all matching negative words removes this implementation veto. This conclusion follows directly from the scan's inputs; no synthetic repository or execution was needed. Blob/accepting-line ordering in `_ordered` (`:1227–1238`) does not preserve a historical negative review.

Required correction: retain the original r5 unchanged as history and add a precisely bound correction describing the veto as applying to complete review evidence at `HEAD`. State that historical rejection permanence, deletion, withdrawal and any revocation semantics are unimplemented/unresolved under the already-open D-HOST-LIFETIME question. Do not choose a policy in this correction. The new integration-status document does not repeat the permanence claim, so this is an inherited draft mismatch, not a new false implementation assertion in that status.

### F2 — MINOR inherited evidence overstatement: “killing tests” is stronger than the supplied historical record

Amendment5 §12 P4, line364, describes Y01–Y09 as being in the harness “with killing tests.” Other disposition rows also use unqualified “killed” or “killing” wording. The permitted evidence comparison, lines25–36, records that Claude's historical classifier used any nonzero suite exit and that Y09's stored result was `FAILED (errors=1)`; M29, N04 and Z09 likewise have error-only tails. That record cannot establish an intended-property assertion kill for Y09, regardless of its KILLED label. The comparison also states that the remaining109 failure-only tails lack the complete names/traces needed for per-property attribution. This review did not open or re-adjudicate the raw historical records; it relies on the explicitly permitted comparison for this evidence limit.

Required correction: distinguish historical classifier labels from independently attributed assertion kills and bind each historical count to its source. The original draft's disposition wording must not be transferred as proof for the new integrated input. Integration status, line9, already makes the correct distinction: 87 historical passing tests, 113 historical nonzero-exit outcomes, four error-only tails, and no inherited total validating the combination. It makes no combined passing-count or mutation-result claim at line25. The 136/80 Codex-line totals also remain evidence for their named earlier input only.

### F3 — MINOR interface omission: the supposedly exhaustive caller-input list omits `repo_path`

Amendment5's Caller inputs paragraph, lines109–114, calls mode, other_job_running, launched and attestation_ref the “only” preflight caller inputs. The exact integrated function signature additionally takes positional `repo_path` (`lx_platform.py:1319–1320`) and passes that location to `free_disk_bytes` (`:1333`). The reading is live, but the caller chooses which location's filesystem is measured by this low-level interface. The code's own prose at lines38–39 and1325–1327 repeats the incomplete enumeration.

Required correction: include `repo_path` as a location input and state that a reviewed operational caller must bind it to the intended repository/store filesystem. The restricted observer already obtains its canonical repository with `_repository_root()` and passes that path (`lx_verified.py:26–37`); its only public arguments remain attestation_ref and mode. No code change is required to describe that existing restricted boundary accurately. This is an inherited low-level interface description issue, not evidence that the restricted observer accepts arbitrary repository or machine assertions.

## Source mechanisms that match the bounded non-operational claims

| Topic | Source evidence at 7eb9 | Bounded disposition |
|---|---|---|
| All 21 decision IDs | `lx_platform.py:86–109` holds the same 21 IDs as amendment5 §4, lines164–184; `DECIDED = frozenset()` at79; `_decided` at1299–1303 validates known IDs | Aligned. None is decided. Recognition of an ID is not a policy implementation or an accepted ruling. |
| Fixed science list / pin point | `PIN_POINT_MODULES = None` at81; parameterless `pin_point` refuses absent/empty list at1082–1093 | Aligned with D-PIN-POINT and A5 unmet. No complete science import list, operational pin-point composition or science execution is established. |
| Reviewed journal | `JOURNAL_READER_REVIEWED = False` at80; `assess` adds the unreviewed-reader ambiguity at369–374 | Aligned. An interval cannot become CLEAN with the shipped guard, regardless of a supplied empty journal list. Full-sequence clock/counter schema and checks do not replace the missing reader. |
| Raw development memory | `lx_verified.py:29–32,49–59` removes effective_limit and cgroup_min_headroom and labels remaining observations RAW_LINUX_READINGS; visible_limit_upper_bound is described as an upper bound by `lx_platform.py:553–561` | Aligned. Numeric raw readings/upper bounds must not be cited as R-FREE/R-MEM quantities or an operational allowance. |
| Root provenance | `root_attestation` at614–627 requires initial cgroup namespace, D-HOST-LIFETIME in validated DECIDED, canonical attestation verification and strict-True root_cgroup_is_real; called inside memory_readings at630–647 | Aligned with H6/L-FREE's internal provenance mechanism. Empty DECIDED blocks this contract. A record's field alone is not root authority; hidden-ancestor/lifetime facts remain actual-host and review obligations. |
| Fixed accepting set | `_acceptances` at1189–1224 accepts direct `REVIEW_HOST_ATTESTATION_*.md` children only, exact acceptance line and a single exact accepting verdict; recursive review scan supplies the current-tree negative veto | Mechanically aligned, subject to F1 and the completeness/availability condition below. Fixed filenames and verdict text do not establish reviewer identity or authority. |
| Commit order | `_ordered` at1227–1238 uses attested blob identity, repository-wide first accepting-line introduction and strict ancestry | Aligned with the stated mechanical ordering. It supplies neither a ledger REVIEW binding nor independence; source docstring explicitly says so. Shallow history can refuse. |
| Update units | `unit_enabled` at839–882 uses13 UNIT_ROOTS, active and enablement states, file/link checks and file-mode wants/requires detection; `auto_update_settings` at885–915 refuses enabled or unknown units as disabled evidence | Preserve the integrated stricter branches: recognized inactive/failed activity is required before disabled/masked/not-found can yield False; unknown PID-1 status yields None. The original r5 L-UPD should be qualified to this stricter current behavior. |
| Live observations / caller trust | `preflight` at1319–1369 reads host values itself and compares fresh launch data; `busy_processes` at726–786 reads fresh proc completeness but still receives snapshots, duration, threshold, own-set and optional hz | Aligned only with the named caller obligations. Reader injection parameters and mutable module seams are development/test mechanisms, not trusted operational inputs. The observer passes canonical readers and unknown other-job status. |
| Permanently blocked observer | `lx_verified.py:40–60` fixes development_only True, operational_ready False and A1/A2/A5 unmet; supplies other_job_running None at36 | Aligned. Per-gate observation statuses cannot turn this observer into readiness, permission or a campaign launcher. |

## Conditions to carry with any corrected prospective proposal mapping

1. Preserve all 21 open D-* items and empty DECIDED. Do not interpret a technical source comparison as owner decisions, acceptance of Linux/macOS equivalence, or satisfaction of a D-* policy. Some preflight gates are hard-wired OPEN_DECISION even if a development constant were changed; vocabulary alone does not implement those policies.
2. Carry D-HOST-LIFETIME's existing unresolved ledger REVIEW binding and reviewer identity distinct from the attestation coordinator (amendment5 line175; owner5 lines55–58). Current exact-verdict discovery and commit ordering are only mechanical checks. “Verified” in the restricted observer is bounded to those checks and current-machine equality, not formal reviewer authority, independent acceptance or host-lifetime truth.
3. Include the current verifier's completeness/availability boundary. Both direct and recursive NUL-delimited listings and all scanned review blobs must be readable, recognized UTF-8 evidence; unreadable/malformed evidence returns an explicit unavailable sentinel (`lx_platform.py:1176–1223`). A direct directory named like an accepting review cannot be found among recursive blob records and refuses. Integration status line31 already states these conservative availability limits. They are not a guarantee that the local repository contains every authoritative external review, and F1's HEAD-only scope still applies.
4. Preserve the unit-state third value: failed/unrecognized supervision or activity readings cannot count as a disabled unit. Preserve both listed unimplemented update-unit limits in inherited L-UPD: no parsing of Wants=/Requires= inside another unit and no runtime-start detection in file mode. “Full search path” describes the declared13 roots, not proof that every actual-host update vector is disabled. H3 still needs actual-host evidence, owner action and provider-image assurance; provider-image checks stay OPEN_DECISION while lifetime is open.
5. Preserve the canonical observer's restrictions and describe low-level seams honestly (F3). The preflight other_job_running input still depends on a reviewed caller; the restricted observer deliberately supplies None. busy_processes accepts caller snapshots, timing/threshold/own parameters and hz; a fresh proc-view reading validates visibility, not those observations' provenance or choice of window/policy. A reviewed operational caller and D-EXCL/ALLOW policies remain unmet.
6. Keep the complete fixed science list/pin point undefined and A5 unmet; keep the journal reader unreviewed; keep RAW memory classification and no operational allowance. Platform hashes, mapped libc/libm/loader objects, package versions, livepatch and the declared PIN_KEYS are concrete proposed observations, not proof of deterministic equivalence, full microcode/CPU pinning or coverage of modules imported after a future pin point. CPU model/vCPU count are recorded rather than PIN_KEYS members.
7. Preserve evidence lineage and citation limits. Review62 concerns revision4 at `cd86c326b573c631749585a46638674e6d8417f4`; its E1 requires repaired source plus fresh confirming review for L-LIFE/L-UPD/L-PIN pin-point citation. Brief63 commissions a review and supplies no completed output. This report is neither that output nor a full E1 repair/kill verification. Any new integrated-result claim requires completed evidence bound to its exact input and an appropriately scoped independent audit. No native CI outcome is available in this review.
8. Carry actual-host H1–H8, storage durability, complete visibility, pending formal route/governance review, fresh S12, owner design/host/other decisions and the governing sequence as unmet. Synthetic/static evidence cannot establish these facts. Do not promote this descriptive correction into designation, qualification, freeze, grant, target execution or scientific adoption authority.

## Authority and citation limitation

The allowed set does not include the original authority texts behind the amendment's [ACCEPTED] quotations, the owner authorization, provider documentation, the route preparation or all historical source artifacts. Their verbatim fidelity, binding status, freshness and external rule compliance are UNVERIFIED here. Review62 records its own earlier quotation checks, but that is neither direct access to those authority texts nor this review's independent validation of r5 against them. No false quotation or accepted-rule compliance finding is inferred from missing inputs. No arbitrary linked reference in brief63 or another allowed document was followed.

Owner5 accurately says that the reviews recorded at its authorship run through review62 of revision4 and that revision5's own delta review was not yet recorded (lines27–30). Its OD-2 correctly carries formal review, fresh S12, decisions and owner design approval as requirements rather than completed authority (lines49–58). Whether review63 has since been published is outside this supplied set. The integrated README and status explicitly remain DEV_ONLY, proposed and non-operational. Assertions there about historical branch preservation or separate independent reviews are not independently established by the four allowed exact source files; no contrary evidence is asserted.

## Byte bindings

SHA256 values below were recomputed locally from the inspected bytes. Integrated Git blob IDs were recomputed by hashing the exact `git show` bytes. Remote document Git blob IDs are their manifest identities; their SHA256 values match the independently recomputed document bytes.

| Integrated path relative to DEV at 7eb9 | Git blob | SHA256 |
|---|---|---|
| lx_platform.py | a9bf5d88498bcbc137e1f442114f16b50e66add0 | 2f0489d376a7129ce4416004c37d1cf66f2bcfbede5a653ed068e382919fae15 |
| lx_verified.py | a803134f98c6c6cd339ab412e2ab522b920be199 | b78756eb377e91c4877b5bf0f96557257da64d4ac464ae339080e9f9e0ca29a9 |
| README_DEV_ONLY.md | 6dfd31e34cde7484071742553679e351f77d1e4e | ed7fc679e95e60cb9bc9f242da8cd5a4a344d2f5da51c1f8291c12414fa233d9 |
| INTEGRATION_DEV_STATUS_CODEX_20261015.md | a1bffefbc8982a62b6133aea07776276849275ff | 03831cb8853d03c727436e002d2e9708e5f7d934d547830c80350305484c06a7 |

| Recovered document at ref 37c62102 | Manifest Git blob | SHA256 |
|---|---|---|
| amendment5.md | 427656fcb22bb8b883747e4d461685213062dcb9 | d0963b110baab7beb86fa80184b9ebf2aab21362d7c7e35745fc10b06f9ba933 |
| owner5.md | 8d72bbf89b344fdfe46fae85bbc2cc3297176403 | a0142eb09576b46367bda03b85f794104a7c2a0b280ec84c8d890e1cd597fbee |
| review62.md | 635a0a964f8dc16ba8c452badf59dfbb99bb4c7d | 0a54a549345354a76da73bdae421244d0f0ecf10ebf6f7eb7525f362848203aa |
| brief63.md | f3c0a26522b76eebbf1ea89eab026bcdf544d3e1 | d4f4902947f5c637a67163060134181d79723606b824f278576507c41434ca79 |

| Other allowed input | SHA256 |
|---|---|
| download-manifest.json | 9f5f0db496ac23e28ca223cc0545c3a10d2b0e20f0deb988e70c30bb748ed41e |
| CODE_COMPARISON.md | 425ee69d2d8ab740ffe5b98dbddef73d6d1d7ad90fffb7c5c24b130c64918ef6 |
| EVIDENCE_COMPARISON.md | 9610b652cb23487250cb5902807d9d97682e3adad85cd6970c25bda21fc10549 |

## Exposure and artifact preservation

Only the explicit allowed documents/source blobs above and the startup `using-superpowers` skill (whose subagent instruction says to skip it) were read. No optional review addendum was read; no other current-agent report was opened. No forbidden audit/interruption/exposure-disclosure document, MB-r1 postexecution or target-run record, or Cell309 content was opened, searched or executed. No broad NS inventory, quarantine CLI, candidate source, science/decoy/qualification/drift/certificate/evaluator source, host/settings query, secret or credential was accessed. Names and quotations inside permitted inputs were treated as permitted embedded source material and were not followed. The only authored artifact is this report under `/tmp/cell308-claude-sync-20261015/amendment-consistency/`; no repository edit, commit or push occurred.

This original report and verdict are to be preserved verbatim. Any later review of an additive supplement is a separately bound delta and cannot silently replace these original findings or convert them into approval.
