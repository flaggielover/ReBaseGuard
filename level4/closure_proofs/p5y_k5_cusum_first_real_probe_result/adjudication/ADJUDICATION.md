# Independent adjudication: K5 CUSUM first real probe, slot-1

**Final status: `ADOPTED`**

I got this status from the frozen `probe_rules.adoption_status(sealed=True, science_usable_=True, independent_replay_pass=True, independent_review_pass=True)`.

- **Subject.** The sealed record `/root/work/k5-first-real-probe/slot-1/SCIENTIFIC_RECORD_SEALED.json` on rebaseguard-vultr-02:
  - sha256 `cf90f1ea577c09d718adddab9698f8f03995722dae51f68d1fd767e4339f73ae`
  - `scientific_hash` `199867e310f7c95c32fc958aa60252578da6df9b3a872d35a4eca691d54ec090`
  - attempt_uid `86e310e4d9c38723eed1ce9472babbd2`
- **Rule.** `SCIENCE_PREREGISTRATION_R4.json` key `independent_adjudication.rule`:
  - prereg sha256 `9ace6896...`
  - `probe_rules.py` sha256 `5ce87758...`
  - Both files are byte-equal at the tip to their blobs at the freeze commit 852b2d65.
- **Date.** 2026-09-19.

## Method

1. **Fresh clones.** I made two fresh GitHub clones of `p5y-postk1-frontier` at tip `44088f14`:
   - one on the host, in `/var/tmp/adj-k5-1789753125/clone`;
   - one on the Mac, in `scratchpad/adj-clone`.

   I imported every frozen module from my own clone (`probe_rules`, `lifecycle`, `qualification_gates`, `consumer`, `authorization_interface`, `consumption_adapter`), never from the launch checkout.
2. **Evidence.** I read the four slot files read-only and copied them into `/var/tmp/adj-k5-1789753125/evidence` and `slotcopy/slot-1`. The copies are byte-equal to the originals. I also copied these operator logs: LAUNCH_ARGV, LAUNCH_UTC, PREFLIGHT_*, supervisor.stdout/stderr, SUPERVISOR_PID and REAL_INPUT_GUARD.before. I did not open `STAGE_*` or `post_run_stage_*.py`.
3. **Host replay.** My own script (`/var/tmp/adj-k5-1789753125/work/replay.py`, sha256 `a94ccae1...`) ran in the contract venv and made 72 checks, with 0 failures. It covered:
   - integrity;
   - Q07 and Q11, recomputed with exact `Fraction` arithmetic and by the frozen rules;
   - all verdicts, compared with the frozen `consumer.interpret`;
   - gates and logs;
   - temporal order and publication;
   - E6.

   It wrote output only into `/var/tmp/adj-k5-1789753125/work/`.
4. **Mac cross-check.** On a second machine and interpreter (Mac arm64, Python 3.14.5, second clone) I repeated Q07, the verdicts, the aggregate and the per-m address hashes. Before that I checked the transcribed per-m values by hash: `e06b3955...` = sha256(canonical(per_m)).
5. **GitHub push times.** I read GitHub's server-side push times for the frontier branch from the repository activity API. There were no force-pushes since the freeze.
6. **Address inputs.** I did not take the address inputs from the record. I derived them from committed files:
   - the K1 record file hash;
   - the prereg `producer_identity_sha256`;
   - the sha256 of the committed `EXECUTION_BINDING_AMENDMENT.json`;
   - the sha256 of the committed prereg;
   - 256 bits.

## Per-check result

| # | Check | Result |
|---|---|---|
| 1 | Record integrity | PASS |
| 2 | Q07, recomputed per m | PASS (m = 1, 2, 3, 5) |
| 3 | Q11, recomputed | PASS |
| 4 | Verdicts, recomputed, and frozen `consumer.interpret` | PASS, identical |
| 5 | Gate and attempt-log review | PASS |
| 6 | Publication anchor | PASS |
| 7 | E6 consumption | PASS (ran; baseline equals frozen acceptance) |
| 8 | Adoption status | `ADOPTED` |

### 1. Record integrity (PASS)

- **Ledger match.** The sha256 of the sealed record is `cf90f1ea...`. At the tip, the ledger's `OUTCOME.sealed_record_sha256` and its `SCIENTIFIC_RECORD_SEALED.sha256` both equal it.
- **Ledger history.**
  - Only two commits touch the ledger: 93a73313 (1 line) and 44088f14 (3 lines). Each version is a byte-prefix of the next, so the ledger is append-only.
  - The ledger has exactly one LAUNCH_NOTICE, for slot-1.
  - The first version containing an OUTCOME is 44088f14. The ledger at the launch head 69a162d0 has no OUTCOME.
- **RUN_COMPLETE.** It agrees with the record on all of these:
  - `sealed_record` and `sealed_record_sha256`;
  - `scientific_hash`;
  - `qualification_gates`;
  - `addresses_sha256`, which equals the sorted address hashes;
  - `attempt_uid`, pid, slot, protocol, executor identity and authorization;
  - `recovered=false`.

  There is no RUN_FAILED file and no VOID seal.
- **Frozen lifecycle checks.**
  - `lifecycle.reconcile` returns `[]` for both the host slot and my copy.
  - `lifecycle.outcome_entry` equals the ledger OUTCOME.
  - `lifecycle.classify` gives class C with no problems.
  - `seal_valid` is ok.
- **File state.**
  - The record bytes are exactly the frozen writer format (`json.dumps(indent=1, sort_keys=True)+"\n"`).
  - The slot holds exactly the four expected files.
  - Every file's ctime equals its mtime, so nothing was touched after it was written.

### 2. Q07 (PASS)

- x1 = 5083/10^7, taken from the prereg. It also equals the record's `context.x1` and `binding.right`.
- The transport factor is x1^2/2 = 25836889/200000000000000 for every m.

For each m, all of the following hold:
- every value is an exact, reduced rational string;
- L0 <= U0;
- M5 >= 0 and is finite;
- L1 <= L0 <= U0 <= U1;
- the frozen `probe_rules.transport(L0, U0, M5)`, with and without `x1=`, returns exactly the sealed (L1, U1);
- my own arithmetic L0 - (x1^2/2)·M5 and U0 + (x1^2/2)·M5 gives the same values.

The Mac replay agrees.

### 3. Q11 (PASS)

- `canonical(scientific)` is stable under a round-trip.
- sha256(canonical(scientific)) = `199867e3...`. This equals the record's `scientific_hash`, RUN_COMPLETE's `scientific_hash` and the ATTEMPT_LOG SEALED event.
- For each m, `probe_rules.scientific_address` and my hand-built address dict (fields exactly as the frozen schema lists them) reproduce the sealed address and its hash:

  | m | Address hash |
  |---|---|
  | 1 | `c8103545...` |
  | 2 | `bf92080d...` |
  | 3 | `cc0ec18a...` |
  | 5 | `c33c7a1e...` |

  The four hashes are distinct, and sorted they equal RUN_COMPLETE's `addresses_sha256`.
- The record context (producer, protocol, executor binding, runtime identity, K1 record, manifest and cells hashes) equals the inputs I derived independently.

### 4. Verdicts (PASS)

Each verdict came from the frozen `scientific_verdict`, `point_sign`, `h3a_consequence`, `consumption_key`, `k5b_consumption` and `aggregate`. They match my own reading of the preregistered definitions and the frozen `consumer.interpret(record)`:
- REAL_PRODUCER_QUALIFICATION PASS;
- SCIENCE_USABLE true;
- identical per-m verdicts and aggregate.

### 5. Gate and attempt-log review (PASS)

**ATTEMPT_LOG**
- It holds exactly three events: VALIDATED, ARITHMETIC_STARTED, SEALED.
- Each event has only gate fields. SEALED also carries the scientific hash, as the frozen code does.
- All three share the same attempt_uid, and their epochs increase.
- It is not torn.

**No numbers outside the record.** No 16-digit prefix of any numerator or denominator of L0, U0, M5, L1 or U1 appears in:
- ATTEMPT_LOG, RUN_STATE or RUN_COMPLETE;
- supervisor stdout/stderr;
- the launch argv or UTC files;
- the preflight reports.

**RUN_STATE**
- Its key set is the frozen `STATE_KEYS`.
- mode is `real` and slot is `slot-1`.
- The authorization is `17a45ffdbb34...`, which equals the sha256 of the committed `AUTHORIZATION_ACTIVE.json`.
- The protocol is `9ace6896...`, which equals the sha256 of the prereg.
- The executor identity `ef1c86e40bff...` equals `authorization_interface.executor_identity()`, recomputed both from my clone and from the launch checkout's files.
- `prelaunch_decision_sha256` recomputes.
- The argv is exactly `.../supervisor.py launch --namespace /root/work/k5-first-real-probe --slot 1 --mode real`, run by the contract venv python with `-B`. It equals the operator's LAUNCH_ARGV.txt.

**Prelaunch decision**
- The verdict is `LAUNCH_PERMITTED` and checks P01-P12 all pass (`failing_checks` is empty).
- The report digest recomputes.
- It was verified at 16:36:59.864Z. The ordering is: verified < RUN_STATE start (16:36:59.888Z) < VALIDATED (16:37:00.270Z) < ARITHMETIC_STARTED (16:37:00.272Z).
- The attempt parameters are: real binding, K1 record `4f8df44c...`, m set {1, 2, 3, 5}, e = 0, C_1, right = 5083/10^7, 256 bits.
- It derives authorization commit b2bc93d5 and freeze commit 852b2d65.
- It records ls-remote on GitHub = 69a162d0 = head.
- It binds the committed LAUNCH_NOTICE, the canonical slot slot-1 (with no pre-existing slots) and a ledger sha256 equal to the committed ledger at 93a73313 and 69a162d0.
- The record's guard binding equals the RUN_STATE decision.

**Producer gates**
- Q01-Q16 are all true, and every gate mode is REAL.
- The frozen `producer_qualification` returns PASS and `science_usable` returns true.
- The structural checks QE01-QE12 of `qualification_gates.gates` are all true, including QE09 (addresses), QE11 (M5 from the even tower) and QE12 (scientific hash).
- The gate evidence is consistent. Q01/Q16 reuse the decision's report digest and epochs. Q04 initial and final both pass with aux5 identity 3692d0fe, and final is scipy-free. The Q06 checks are all true. Q08 has no problems. Q09 has a 13-entry trace whose last entry equals M5_1 exactly and never increases. Q10 uses the RUNG_256 reference `0bb1b474...` and has no disjoint sets.
- Q15: 3026.9 CPU-s against a soft limit of 9000, and 3027.7 wall-s against a limit of 14400.

**Q16, temporal order.** The git ancestry is a strict chain: freeze → amendment → authorization → countersignature → launch notice → launch head → ledger commit.

| Event | Git commit time (UTC) | GitHub push time (server, UTC) | Host epoch (UTC) |
|---|---|---|---|
| freeze 852b2d65 | 2026-09-17 05:28:23 | 05:28:24 | |
| amendment 842d3565 | 2026-09-18 15:13:31 | 15:14:12 | |
| authorization b2bc93d5 | 15:26:49 | 15:27:20 | |
| countersignature dd750286 | 15:55:56 | 15:56:30 | |
| LAUNCH_NOTICE 93a73313 | 15:58:05 | 15:59:34 | |
| launch head 69a162d0 | 16:20:26 | 16:20:29 | |
| prelaunch verified | | | 16:36:59.864 |
| ARITHMETIC_STARTED | | | 16:37:00.272 |
| seal (SEALED event) | | | 17:27:27.998 |
| ledger OUTCOME 44088f14 | 17:31:05 | 17:31:07 | |

- AUTHORIZATION_UTC (15:26:49Z) falls inside the frozen P04 window and after the amendment.
- AUTHORIZATION_ACTIVE, the amendment, the prereg R4 and COUNTERSIGNATURE_ACTIVE were each committed exactly once, at the expected commit.

**Q04, runtime identity**
- The prelaunch report's `live_host_facts` are exactly equal to the frozen `host_runtime_contract`.
- `runtime_identity_sha256` equals the prereg's `host_runtime_identity_sha256`, which is the sha256 of canonical(contract).
- The host's live facts today also equal the contract, and the boot id is unchanged.

**Provenance**
- All 14 amendment `executor_sources_sha256` entries match both my clone and the launch checkout.
- All 279 `EXECUTOR_PINS` files match both my clone and the launch checkout.
- The launch checkout HEAD is 69a162d0.

### 6. Publication anchor (PASS)

- `git ls-remote` on GitHub `refs/heads/p5y-postk1-frontier` returns `44088f14`.
- These commits are all ancestors of that GitHub tip, in a clone fetched from GitHub: freeze 852b2d65, amendment 842d3565, authorization b2bc93d5, countersignature dd750286, launch notice 93a73313, launch head 69a162d0 and ledger 44088f14.
- The activity API shows the frontier advanced by fast-forward pushes only after the freeze.

### 7. E6 consumption (ran read-only from my clone)

- The consumption key is POSITIVE for all four m, so the adapter consumed every m. I ran `consume(L1={m: Fraction(sealed L1_m)})` against `/root/work/postk1-runs/closure-r1/COMPOSITE_EXPORT/k4_records`.
- The adapter sha256 is `fbad7d33...`, which matches the amendment pin.
- All 310 records match the manifest `29ad1f9b...`. The records sha256 is `76fc2af5...`.
- The baseline `consume(None)` equals the frozen E6 acceptance `expected_pass_ranges`, and equals the committed `acceptance_r1/ADAPTER_OUTPUT.json` in every key.

| m | Pass ranges | Pass count | Open ranges | Open count | Newly closed vs L = None | Lost |
|---|---|---|---|---|---|---|
| 1 | [0,0], [133,309] | 178 | [1,132] | 132 | {0} | none |
| 2 | [0,0], [145,309] | 166 | [1,144] | 144 | {0} | none |
| 3 | [0,0], [146,309] | 165 | [1,145] | 145 | {0} | none |
| 5 | [0,0], [149,304] | 157 | [1,148], [305,309] | 153 | {0} | none |

- sha256(canonical(output)) = **`89017388681e05ec9b8e63ef8e22305af8bd7cf76d5ab1b571a7c948afcafb6a`**. It is the same with the adapter's `canonical` and with `probe_rules.canonical`.
- The baseline (L = None) output sha256 is `773999f5b47ea4e43e4ec8ba20d54821f424829897ebfaf1f7686829524f37c4`.

This matches the preregistered downstream disclosure: a POSITIVE result closes only C_1 (cell 0) for each m. Cells 1 through 132, 144, 145 and 148 (for m = 1, 2, 3 and 5), plus 305-309 for m = 5, stay open.

## Per-m table

x1 = 5083/10^7. The penalty is (x1^2/2)·M5, with x1^2/2 = 25836889/2·10^14 ≈ 1.2918e-7.

| m | L0 | U0 | M5 | penalty | L1 | U1 | Verdict | Point sign | H3a consequence | Consumption key |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1801.434727921407 | 2790.362876472101 | 1.061360489928378e8 | 13.71112658363256 | **1787.723601337775** | 2804.074003055734 | SUPPORTS_K5B_FIRST_CELL | POINT_POSITIVE | K5B_CELL_1_PASSES_FOR_THIS_M | POSITIVE |
| 2 | 1461.592374120910 | 2410.418561002309 | 9.164814988466416e7 | 11.83951537812715 | **1449.752858742783** | 2422.258076380436 | SUPPORTS_K5B_FIRST_CELL | POINT_POSITIVE | K5B_CELL_1_PASSES_FOR_THIS_M | POSITIVE |
| 3 | 1307.107127538203 | 2200.973144783892 | 8.367296396923906e7 | 10.80924541187115 | **1296.297882126332** | 2211.782390195763 | SUPPORTS_K5B_FIRST_CELL | POINT_POSITIVE | K5B_CELL_1_PASSES_FOR_THIS_M | POSITIVE |
| 5 | 1073.994985366952 | 1930.974900715943 | 7.340440809229820e7 | 9.482707719957052 | **1064.512277646995** | 1940.457608435900 | SUPPORTS_K5B_FIRST_CELL | POINT_POSITIVE | K5B_CELL_1_PASSES_FOR_THIS_M | POSITIVE |

**Aggregate:** `FIRST_CELL_SUPPORTED_ALL_M`, with route `CONSUME_IN_FROZEN_K5B_CHECKER_THEN_PREREGISTER_NEXT_ORDER3_CELLS`.

### Exact sealed values (reduced rationals)

**m = 1**
- L0 = 407406036661476549599971184823916182780747120864150545331718204467912460684155/226156424291633194186662080095093570025917938800079226639565593765455331328
- U0 = 631058490619046620834967279758566405193716170715402866655845060059012322079877/226156424291633194186662080095093570025917938800079226639565593765455331328
- M5 = 91565511049887843577522081704274853482294634789007097183226422074630210556357/862718293348820473429344482784628181556388621521298319395315527974912
- penalty = 2365767945224225676961800920042280214913309944339114790135233729009370466191224053373/172543658669764094685868896556925636311277724304259663879063105594982400000000000000
- L1 = 2467682966920851150638817218762197053573339521813393437463330999234773551188408439994891/1380349269358112757486951172455405090490221794434077311032504844759859200000000000000
- U1 = 3870601501344060778285367745730494523419234279331341743124823691481320093611591560005109/1380349269358112757486951172455405090490221794434077311032504844759859200000000000000

**m = 2**
- L0 = 82637126275775990455427537397212896502490575282399237858510719927521077935217/56539106072908298546665520023773392506479484700019806659891398441363832832
- U0 = 136282910700616524574566936280910070462221901655190944205574855930794916397967/56539106072908298546665520023773392506479484700019806659891398441363832832
- M5 = 79066535457074363446705955133534263486091101543197727334890424006016793080445/862718293348820473429344482784628181556388621521298319395315527974912
- penalty = 408566660043798918623639835684820988677377766891865677240765942441278242991085107121/34508731733952818937173779311385127262255544860851932775812621118996480000000000000
- L1 = 100058264965771765511663288440462507073537059996488775797020811776642196852905769238883/69017463467905637874347558622770254524511089721703865551625242237992960000000000000
- U1 = 167178108296426128812060434311152442834559225327717989417927400941028694667094230761117/69017463467905637874347558622770254524511089721703865551625242237992960000000000000

**m = 3**
- L0 = 9919048263574201335264715485086853148329908674844593863014408152732867219432068934489/7588550360256754183279148073529370729071901715047420004889892225542594864082845696
- U0 = 16702195550765245728696502101578811247977758776967571425780319745558263634253486429351/7588550360256754183279148073529370729071901715047420004889892225542594864082845696
- M5 = 4511637292186204538513365097312058308852372910310253164331798934437878548843/53919893334301279589334030174039261347274288845081144962207220498432
- penalty = 116566671926475533992866039035725848887346476270292966568739448239389745461937669427/10783978666860255917866806034807852269454857769016228992441444099686400000000000000
- L1 = 60040416018126482461640558539439560776319049147935274741935992494199177789097149664751288831233/46316835694926478169428394003475163141307993866256225615783033603165251855974400000000000000
- U1 = 102442761559628931747107107394799113517550991451504210663305266650644150175292226335248711168767/46316835694926478169428394003475163141307993866256225615783033603165251855974400000000000000

**m = 5**
- L0 = 4075032516560166652875459303178684095793870970662673127399952192245279953718095431725/3794275180128377091639574036764685364535950857523710002444946112771297432041422848
- U0 = 7326650139237359111587153086050946506180617141322560708801357024280718932400600201171/3794275180128377091639574036764685364535950857523710002444946112771297432041422848
- M5 = 15831831418416962962942583383875367137693445970365611904710571460391767609967/215679573337205118357336120696157045389097155380324579848828881993728
- penalty = 409045271024351627790658640262432250570833279563833604199085611948709996252512672663/43135914667441023671467224139231409077819431076064915969765776398745600000000000000
- L1 = 24652420129503917585808661586724338623914712465274155728050613707569087997106069251910515924469/23158417847463239084714197001737581570653996933128112807891516801582625927987200000000000000
- U1 = 44937928111447777753928962859257293468214731577604468760482767740953854423051985148089484075531/23158417847463239084714197001737581570653996933128112807891516801582625927987200000000000000

## Discrepancies and observations

None of these is a failure of any check.

1. **M5 is much smaller than forecast.** The pre-result forecast for m = 1 was point radius 490.6 plus penalty 330.1. The sealed point radius is 494.5, close to forecast, but the penalty is 13.71, about 24x smaller. The forecast was declared non-scientific. The sealed M5_1 equals the final entry of the 12-iteration local_r5 trace, which starts at 6.69e11 and never increases, and QE11 ties each M5 to the even tower nodes. I did not recompute any certificate. The verdicts do not depend on this gap: L1 <= 0 would need M5 to be 131x (m = 1), 123x (m = 2), 121x (m = 3) or 113x (m = 5) larger than sealed.
2. **SUPERVISOR_PID differs.** The operator file `SUPERVISOR_PID` holds 512063, while RUN_STATE and RUN_COMPLETE record pid 512067. The file most likely holds the wrapper shell's pid. No gate uses it, and the executor's in-process `bound_decision_problems` requires RUN_STATE.pid to be its own parent.
3. **AUTHORIZATION_UTC timing.** It equals the authorization commit time to the second. This is inside the frozen P04 window [commit − 3600 s, commit + 60 s].
4. **Guard restored.** In the launch checkout, `config/REAL_INPUT_GUARD.json` is back to `DENY` and byte-equal to the committed file. It was restored at 17:29:56Z, after the seal and before the ledger commit.

## Independence limits

- **Same model family.** I am Claude Code (claude-opus-5) in a separate session and process, working from fresh clones with my own scripts. The operator packet was also prepared by claude-opus-5, so the independence is procedural (separate session and process), not institutional.
- **Same host and venv.** The main replay ran on the production host with the production venv, because `consumer.interpret` / QE11 need flint. The stdlib-only replay of Q07, the verdicts, the aggregate and the addresses was repeated on a Mac with a different interpreter. The full-record `scientific_hash` was recomputed on the host only; my attempt to move the whole record to the Mac was refused by the tool's permission classifier.
- **No certificates recomputed.** Per the hard limits, I did not recompute any certificate, R''' or R^(5) value. That L0, U0 and M5 are certified enclosures rests on the executor-evaluated gates Q02-Q10. I re-checked those only through their evidence and the structural checks QE01-QE12.
- **Clocks.** Host epochs come from the host clock. Git commit times are claimed by the committer; GitHub server push times back them up.
- **Operator material not read.** I did not read the operator's `STAGE_*` files, `post_run_stage_*.py`, the operator packet files in this directory, or any review or result markdown.
- **Read-only.** Nothing in `/root/work/k5-first-real-probe`, the launch checkout or `REAL_INPUT_GUARD.json` was modified. I did not run supervisor, executor_cli or any qualify_*. I did not commit or push, and I did not touch AWS.

## Artifacts

- **Host replay:**
  - `/var/tmp/adj-k5-1789753125/work/replay.py` (sha256 `a94ccae1fe9ff49c77384d16cb1d7edea0dac5a00e3b230b5c93a4426cd81c78`)
  - `REPLAY_RESULT.json` (sha256 `4e3a95ce...`)
  - `E6_OUTPUT.json`
  - `E6_BASELINE_L_NONE.json`
- **Mac cross-check:** `scratchpad/adj-mac/mac_crosscheck.py`, `mac_crosscheck_result.json`, `per_m_sealed.json`
- **Machine-readable result:** `ADJUDICATION.json` (this directory)
