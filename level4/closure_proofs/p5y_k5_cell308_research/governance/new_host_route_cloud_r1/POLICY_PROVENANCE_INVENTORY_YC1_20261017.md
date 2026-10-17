# Policy-provenance inventory for YC1 (Cell-308 Cloud route r1): what must be traced before the D-* decision, and what is a later artifact

**Status: AUTHOR CORRECTION · NOT INDEPENDENTLY CONFIRMED · NOTHING ADOPTED.** This inventory answers external B3
confirmation finding **YC1 (BLOCKING)** (`reviews/external/CONFIRMATION_EXTERNAL_B3_CORRECTIONS.md`, `6a721ada…253c`,
lines 76–82).

**Withdrawal of the blanket B9-T deferral.** The earlier statement that code-level constants "do not exist yet" and
receive their M1-style trace at B9-T is **withdrawn**. It appeared in:
* provenance record §6;
* T6 disposition K-T6-2;
* matrix R4 erratum E4, row B9-T;
* owner package R4 erratum E1 §5, P1.

**The rule restored here.** Every new policy number, threshold, limit or rule needs its provenance traced **before the
owner decision that adopts it** (S12 §5 item 8; matrix R4 rows A6 and A17). A policy choice does not move into the
later-artifact category because it will appear in code. B9-T is kept only as an **additional conformance check** of
requirements already traced (matrix R4 erratum E5). It clears neither A15 nor A17.

**Late policy choices.** A policy choice first introduced after A17 is a change after the decisions. Amendment
erratum E2.5 already says: "A later change needs a fresh S12 rating and a formal review with the readings in view."

`new_target_evaluations = 0` · `cell309_activity = none`.

## 1. Sources inspected, and coverage

| source | pin / sha256 | coverage |
|---|---|---|
| route texts, as B3 traced them (package erratum E2; recommendations erratum E1; provenance record) | correction pin `b047237a` | T01–T11, N1–N2, X01–X09, Z01–Z06, O01–O30 |
| `OPERATIONAL_WRAPPER_READER_PINPOINT_REQUIREMENTS_20261016.md` | `bea16c62…6abf` (unchanged since `e9c42a97`) | **not** in any B3 allowlist |
| development layer `streams/CLOUD_R1_LINUX_DEV/lx_platform.py` | `9db01504`, sha256 `da32ce8c…6389` (unchanged at HEAD) | **not** in any B3 allowlist. Module constants were listed statically (AST; nothing imported or run). Inline numeric literals were searched for timeouts and comparison constants only |
| `lx_verified.py`, `lx_inventory.py`, `lx_portmap.py` | `9db01504` | module constants listed; none adds a policy number beyond the rows below |
| the successor build | **does not exist** | **UNKNOWN.** Any policy item it would introduce is not inventoried here and must be traced before A17, or else is a later change |

**Incompleteness, stated.** This inventory covers only the route texts, the requirements document and the development
layer, as listed. It is not a proof that no other policy choice exists. The author (the coordinator side) compiled
it, and no independent reviewer has checked it.

## 2. Category (a): policy items that need provenance before their owner decision

**Status key:**
* **B3-T**: traced by B3 at text level, with the qualifications recorded in the provenance record;
* **NT**: not traced by any eligible non-holder;
* **NV**: inherited by reference, with the value not verified.

| id | item | source and location | status | decided at |
|---|---|---|---|---|
| a1 | T01–T11 (window 30 s; PSI N = 3 / 30 s / `avg10 = 0.00`; ≤ 3 re-reads; ≥ 6 physical cores; thermal predicate; HOST-row construction; the window-bound and response-time slots; MBS-8 (ii) rule and N1 ceiling; digit limit) | package erratum E2 §E2.1 | B3-T (Y3 CONFIRMED) | A17, A18 |
| a2 | N1 = 24 h; N2 = 21 days | recommendations erratum E1 | B3-T (Y1, Y2 CONFIRMED) | A17 |
| a3 | X01–X09 (L-DET E2 / E3 rules; procedure E1.2, E1.4) | provenance record §3 | B3-T (Y4 PARTLY) | A15 |
| a4 | Z01–Z06 (procedure E2) | provenance record §4 | B3-T; author proposal (Y7) | A15 |
| a5 | O01–O30 | provenance record §5 | B3-T (Y4 PARTLY; YC4 qualifications) | A15, A17 |
| a6 | J1: journal source (`journalctl --boot=<id> --since --until -o json`; current boot; kernel and `systemd-sleep` records only; timeout) | requirements doc line 38 | **NT** | A15 (L′ rule) |
| a7 | J2: the sleep-event pattern set (`systemd-sleep` messages; kernel `PM:` entries; `systemd-logind` requests) | requirements doc line 39 | **NT** | A15 |
| a8 | J3: completeness rules (`Storage=persistent`; cursor-gap check; rotation, vacuum or "Suppressed … messages" ⇒ AMBIGUOUS) | requirements doc line 40 | **NT** | A15 |
| a9 | J4: fail-closed outcomes (parse error, unknown shape, wrong boot id, timeout ⇒ AMBIGUOUS) | requirements doc line 41 | **NT** | A15 |
| a10 | P1: composition rule for `PIN_POINT_MODULES` (the static AST import closure, with at least the S11 modules and stdlib / C-extension modules). The **rule** is policy; the computed list is (b) | requirements doc line 52 | **NT** (O08 covers pin objectives, not this rule) | A15 |
| a11 | P3: late-import consequence (invalid before the marker; close-indeterminate after it) | requirements doc line 54 | **NT** | A15 |
| a12 | A2.4: the test-seam list whose production use the lint forbids | requirements doc line 30 | **NT** | A15 |
| a13 | `SLEEP_GAP_TOL_NS = 2 000 000 000` (2 s sleep-gap tolerance) | lx_platform.py:70 | **NV**: O05 says the old tolerances are "inherited by reference, not re-derived" | A15 |
| a14 | `MAX_SAMPLE_GAP_S = 180` | lx_platform.py:71 | **NV** (as a13) | A15 |
| a15 | `MIN_FREE_DISK = 2 GiB` | lx_platform.py:72; ratification row 23 | B3-T (O12: inherited; adequacy on a new host not established) | A17 |
| a16 | `UNLIMITED_CGROUP_V1 = 2**62` (when a cgroup-v1 limit counts as "no limit") | lx_platform.py:69 | **NT** | A17 (D-MEM-FREE / D-MEM-WIRED) |
| a17 | `KNOWN_NOT_DISCHARGING` statuses (`Charging`, `Full`, `Not charging`) | lx_platform.py:75 | B3-T in part (O04 "known supply statuses"); the exact list **NT** | A17 (D-POWER-ABSENT) |
| a18 | `UNIT_ROOTS` (the systemd search roots) and `UPDATE_UNITS` | lx_platform.py:800, 805 | B3-T as a rule (O11); the primary-source list **UNTRACED** (YC4) | A17 |
| a19 | `REQUIRED_MAPPED` (`libm.so.6`, `libc.so.6`, `ld-linux`) and `PIN_KEYS` | lx_platform.py:1051, 1133 | B3-T in part (O08; L-DET E2.4 adds pins) | A15 |
| a20 | subprocess timeouts: 30 s (lines 818, 962, 1062, 1080) and 60 s (lines 793, 1181, 1223, 1238). A timeout means refusal | lx_platform.py, as listed | **NT** | A15 |
| a21 | git isolation and history-completeness set: `_GIT_ISOLATION`, `_GIT_ENV_KEEP`, `_LOCAL_CONFIG_REFUSED`; strict fsck | lx_platform.py:1159, 1166, 1188 | B3-T in part (O21 "history / fsck checks"); the exact sets **NT** | A15 |
| a22 | veto vocabulary: `_VERDICT`, `_NEGATIVE`, `_NEGATIVE_MORE` | lx_platform.py:1314–1316 | B3-T as policy (O21 "broad negative-word veto"); the exact word lists **NT** | A15 |
| a23 | integer-parse digit guard (`> 4300` in the development integer reader) | lx_platform.py:304 | **NT**. It is related to T11 but distinct: a reader guard, not the comparator setting | A15 |

## 3. Category (b): later artifacts and evidence (identity, conformance, measurement)

These cannot exist before their stage. A later stage checks them against rules already traced and decided. None of
them introduces a policy choice.

| id | artifact or evidence | stage |
|---|---|---|
| b1 | successor commit; source hashes; build provenance record; prefix manifest; libpython identity | B8–B10 |
| b2 | the computed `PIN_POINT_MODULES` list (by rule a10) | B8–B9 |
| b3 | the per-record view declaration (by rule X01) | B13 |
| b4 | the L-DET commit and its diff list | B13 |
| b5 | the attestation JSON; appointment entries; review files; ledger lines; anchor records | B6, B11 |
| b6 | host inventory readings (PSI, zones, topology, cgroup, power, DMI) | B4 onward |
| b7 | official decoy runtimes and the resulting caps values (by rule T10) | C1 |
| b8 | response-time and window compliance evidence; process lists; S15 listings | OPS-5 … OPS-10 |
| b9 | identifiers: the schema name, acceptance-line strings, unit prefix, file paths | fixed with the design (B8). They are naming, not thresholds |

## 4. What follows (the dependency is stated, not met)

* **Items a6–a14, a16 and a20–a23**, and the untraced parts of a17–a19, need an M1-style provenance trace by an
  eligible non-holder **before** A15 / A17. B3's round is final and cannot supply it. This is a new external
  requirement (dependency handoff §2, step 2).
* **The trace reviewer's own non-holder status** rests on the register check (ER-T6 r2). Without it, that review's
  standing is limited exactly as B3's is.
* **Nothing in this inventory changes a value or a rule.** Where a value has no derivation, the trace records it as a
  free choice. The value is not altered to produce one.
