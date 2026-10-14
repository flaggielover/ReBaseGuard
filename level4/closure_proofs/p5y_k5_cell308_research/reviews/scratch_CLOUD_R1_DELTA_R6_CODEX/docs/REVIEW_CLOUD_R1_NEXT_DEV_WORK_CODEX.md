# Cell308 bounded next-work assessment

Reviewed immutable input: `13047bbebe509c1c04cd25ea90651c853cc61b03`.
Checkout: `/Users/suzhe/.codex/worktrees/cell308-review61/ReBaseGuard`.
Namespace: `level4/closure_proofs/p5y_k5_cell308_research` (paths below are relative to it).
Assessment is source-only; no workloads, host probes, repository edits, commits, or worker calls were made.

## Finding

Meaningful target-free development remains without changing an accepted decision: implement and review a **DEV_ONLY trusted-boundary wrapper prototype** for the existing platform helpers. Do this after the pending revision-5 baseline/mutation evidence and fresh review have been adjudicated; any fresh concrete defect takes priority.

The owner authorization explicitly permits useful development, isolated tests and fresh independent review while unresolved host facts block dependent official steps (`USER_AUTHORIZATION_20261014.md`, authorization and delivery rows). The earlier preparation-only phase does not negate that later extension.

This recommendation is an expressly identified integration gap, not a new measurement policy:

* Amendment r4 §3 and §12 A1 require a wrapper deriving `root_cgroup_is_real` from the verified committed attestation and current-host binding. `lx_platform.memory_readings` still accepts a raw strict boolean and explicitly leaves provenance to that wrapper (lines 549–567).
* r4 §12 A2 requires a reviewed wrapper to restrict observer/checker/reading/configuration seams. Current `preflight` exposes `readings`, `decided`, `attestation_check`, and `launch_observer` (lines 1036–1079). Those are development seams; choosing a favorable callback or decision set cannot establish authority.
* `attestation_valid` already provides a mechanical building block: committed blob/hash, strict review/acceptance fields, current hardware identity and committed acceptance-line checks (lines 972–1005). The proposed wrapper can compose this mechanism without choosing any host or asserting a genuine attestation exists.

## One bounded recommended action

Prepare a small reviewable change confined to `streams/CLOUD_R1_LINUX_DEV/`, implementing an infrastructure-only wrapper prototype and synthetic refusal/provenance regressions. Preserve the existing low-level test seams; keep them out of the wrapper's public interface.

Required behavior:

1. The public prototype accepts an attestation reference rather than caller-supplied attestation facts or `root_attested=True`. It invokes the canonical `attestation_valid` with default current-machine observation and derives the memory flag only from a verified record whose `root_cgroup_is_real is True`.
2. Missing, malformed, uncommitted, unaccepted, wrong-hash or wrong-host references, and non-boolean root claims, cannot supply the root flag. A caller cannot redirect verification to a favorable checker, machine identity or alternate repository through the public interface.
3. Live preflight composition uses the canonical readers and live launch observer. No public caller can pass injected readings, observer/checker callbacks, or a `decided` set. The canonical development decision set remains empty; no open gate becomes PASS through this work.
4. Output continues to label Linux memory quantities RAW, never R-FREE/R-MEM rule outputs or an operational allowance. Verification of a synthetic fixture demonstrates composition only; it does not establish owner/reviewer acceptance of a real host.
5. The prototype imports and executes no science, candidate, evaluator or qualification code, launches no campaign, and leaves complete science pin-point binding explicitly unmet. Its documentation and return status must not advertise operational readiness.

Meaningful regressions should show that only a genuinely verified committed synthetic fixture supplies the raw root contract, that the rejected cases above withhold it, that caller attempts to supply public seams are refused, and that all D-* blockers remain. Bind evidence to immutable source/test inputs and obtain a fresh narrow development review. A Linux synthetic runner can check the composition; its success supplies no actual-host guarantee. Local fixture tests do not require reconnecting either unavailable SSH worker.

This prototype reduces A1/A2 integration work. It does **not** discharge them for operation: the eventual accepted contract and independent implementation review still have to cover the complete operational wrapper.

## Work that cannot be completed from these sources

| Remaining condition | What is missing | Can the prototype proceed without it? |
|---|---|---|
| A5 complete static science import list and pin point in every computing mode | The permitted sources contain no canonical complete list or computing-mode import paths. `pin_point(modules)` only checks that caller-chosen names are in `sys.modules` (lines 903–911). Completeness requires a separately scoped non-holder static review of the intended science/build paths, a fixed list in accepted text, and wrapper implementation review. Do not guess names or use an empty/placeholder list as proof. | Yes; keep A5 unmet and import no science. |
| D-* measurement/policy semantics | All 20 decisions remain undecided (r4 §4; erratum E1 §1/§5). R-FREE equivalence, wired memory, CPU window, pause/awake time, interpreter, S15 mechanism and the other choices require the designated owner/reviewer process. | Yes; preserve the blockers. |
| Official host and H1–H8 | Actual machine selection/access, positive inventories and owner attestations for lifetime, update control, storage durability, hidden cgroup ancestors and machine identity; independent acceptance. Hosted synthetic validation cannot establish these. | Yes; synthetic fixtures only. |
| Formal route/S12/implementation acceptance and later sequence gates | r4/E1 remains PROPOSED; owner brief r4 OD-1/OD-2/OD-3 are unresolved. Reference records and serializer/strip digests are not supplied by these allowed sources. | Yes; no formal operational step is implied. |

Worker unreachability and use of hosted Linux for synthetic validation are task-supplied context, not new findings from this assessment. No host was investigated or selected here. Actual-host dependent steps remain blocked even if every development test passes.

## Sources read and byte bindings

| Source | SHA256 |
|---|---|
| `governance/new_host_route_cloud_r1/PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R4.md` | `0a9d720f2b715cda0f247d1500a807613a2e6f2a1265578fdada0ab2d85baa9b` |
| `governance/new_host_route_cloud_r1/PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R4_ERRATUM_E1.md` | `b73ecabf0dbf7fe2dda650b6f8c98808b03137faaa4cc69d8e1a4c35bc237e84` |
| `governance/new_host_route_cloud_r1/OWNER_DECISION_BRIEF_CLOUD_R1_R4.md` | `7dc0322dd341477f008cbd5f7957eae7e3ee1fbc2d8d28c99ebc485602715c4c` |
| `governance/new_host_route_cloud_r1/ROUTE_PREPARATION.md` | `80c9f5a07191592b0d606cc713708ababd62acd4e8fd7b481ec08411f4b3be99` |
| `governance/new_host_route_cloud_r1/USER_AUTHORIZATION_20261014.md` | `a202596d3ac2e417565b437bb3791ed479dd230e7abaee1e2ee0a0636bc650b9` |
| `streams/CLOUD_R1_LINUX_DEV/README_DEV_ONLY.md` | `4362a1d675a4ce19ee93258faca00b2e750813f5d39cabde9a322d704d0a635d` |
| `streams/CLOUD_R1_LINUX_DEV/lx_platform.py` | `e4f30c816a31a2f36fe7fab88fb4af957457d817b88fc2a8b75324cdb7ef705e` |
| `streams/CLOUD_R1_LINUX_DEV/lx_inventory.py` | `8ea74ed3621e805066727a4ca3f20253f9a85c90857aca8d8e41e02607cfa597` |

Only the enumerated Cell308 sources were read. No excluded incident/audit/disclosure/postexecution/target-record sources or separate-cell material were opened. No target, decoy, qualification, freeze, grant or scientific adoption is authorized by this assessment.
