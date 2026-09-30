# Formal-campaign errata (append-only; incident-review condition C6 and later corrections)

The research-namespace files stay untouched. Each entry corrects a formal or research record, and does so only
here.

## FE-1 (C6(a)): the coordinator's incident audit misattributes the budget branch and omits the 6 → 48 CPU-h change

`governance/INCIDENT_AUDIT_P309_COORDINATOR.md` has two errors:
* Rule choice 1 (lines 52–54) says the whole Stage-1a failure mapping was R3's proposal and that it **reduces** the
  chance of closure. Only the exception → EXECUTION_INDETERMINATE branch was R3's minimal fix, and only that branch
  works against closure. R3's minimal fix sent a budget overrun to EXECUTION_INDETERMINATE. The budget-exhaustion →
  fallback branch was the coordinator's choice, and it works **toward** closure: an exhausted budget still lets Stage 2
  run.
* The audit omits the budget change itself. Before rev. 2 the drafts and ce829bb4 had a 6 CPU-h cap. The coordinator
  raised it to 48 CPU-h in rev. 2 (814ff984), with mechanics settled in rev. 2b (36e672be). That change also works toward
  closure, on a target-free basis (decoy costs).

The pre-rev.-2 Stage-1b rule (CERTIFICATION_FAILED ⇒ NOT_CLOSED, in the drafts and in ce829bb4) also belongs in the
audit's timeline. It was replaced by the fallback to S_I1 in rev. 2 (814ff984) and adopted by the owner under G3.

All three rule choices carry their direction into `disclosed_liabilities` (condition C8):
* exceptions: against closure;
* budget fallback and 48 CPU-h: toward closure;
* Stage-1b fallback: toward closure.

## FE-2 (C6(b)): "found" times later than the commits recording them

* `INCIDENT_309R1_03` says "found 2026-09-30 ~00:1xZ". Its file was added in 426461c8 at 2026-09-29T23:59:53Z.
* `INCIDENT_309R1_04` says "found 2026-09-30 ~01:1xZ". Its file was added in eb3b3432 at 2026-09-30T00:46:17Z.

The stated "found" times are approximate recollections written into the files, and they are later than git's record
of the files. **Git commit order governs.** Both incidents were found no later than their recording commits.

## FE-3 (C6(c)): the overnight incidents are dated 09-27

The coordinator audit's table (lines 34–36) dates overnight incidents 01–03 "09-28". Their files were committed at:
* incident 01: 2026-09-28T04:09:10+09:00;
* incident 02: 2026-09-28T05:13:39+09:00;
* incident 03: 2026-09-28T06:06:24+09:00.

That is 2026-09-27, 19:09–21:06 UTC. Every other time in this campaign is UTC, so their date is 09-27. The "09-28" in the
audit is the committer's local date.

## FE-4 (C6(d)): qualification of "no target-equivalent proxy"

Every owner-facing statement "no target-equivalent proxy" or "target-equivalent proxies = 0" means:
* **zero computed proxies**;
* **one recorded qualitative (mental) proxy exposure**, 309R1-01 (TPT at 309; TPT is OUT);
* **one mental in-band estimate**, 309R1-02 (SRK).

The ledger counters count computed quantities only. The handoff and the proposed grant carry this qualification.

## FE-5 (C6(e)): push-record commit subjects

The checkpoint-push record commits 0e4849a7, 4754ac16 and 4a50aa7b on the formal branch carry the subject
"p5y: K5 cell-309 research r1 — ledger: checkpoint push record". They are **formal-campaign** records. The template
was fixed in 0b3cfefd, and later records say "p309 formal r1". The three commits stay as they are.

## FE-6: a duplicate retrospective ledger record

The first FC2(b) attempt (rev. 1, stopped by the permission system) is recorded twice in
`ledger/ZERO_TARGET_LEDGER.jsonl`:
* once by the coordinator's retrospective transcription (commit 78bd6a98);
* once by the verifier author's own start-of-work line.

Both describe the same read-only inspections. There was no evaluation.

## FE-7: a ledger line naming a non-existent path

The exposure line at 2026-09-30 (C6 adjudication, first attempt) names a path that did not exist, so nothing was read
under it. It was corrected append-only by the next line, and the read happened under the correct path.

## FE-8: Stage 1b could not load its certifier in `execute` (found by a QC11 development run before the freeze)

**Defect.** In `execute`, two steps run in the driver process before Stage 1b:
* the historical control (pre-marker);
* the Stage-1a gate (post-marker).

Both import the SRK side (`srk_gate`), which imports `c1b_gauss` by a plain import. Stage 1b then called the pinned
RLR307 loader, `load_certifier`. That loader refuses any certifier module it did not load itself ("already imported
from somewhere else").

**Consequence had it shipped.** Every production execution would have raised after the marker. The result would have
been EXECUTION_INDETERMINATE, and the single evaluation would have been spent.

**Why the earlier checks missed it.**
* The decoy Stage-1b runs (QC09) start in a fresh process.
* The QC14′ rehearsal does not load the RLR307 certifier in-process after the SRK side.

**How it was found.** QC11 stage flow S10, the first run in which the stage flows ran after the SRK side was imported.
That run used stubs only; nothing was evaluated for any cell.

**Fix** (driver, `_load_certifier_isolated`). For the load, the certifier's module names and `ov_quarantine` are
removed from `sys.modules`, and the previous table is restored afterwards.
* The pinned helper is unchanged.
* The loader's identity check still binds the certifier modules to each other.
* Later imports, including those of Stage 2, resolve exactly as they did for the historical control.

A new QC11 flow, `S13_stage1b_after_srk_imports_table_unchanged`, reproduces the execute order and checks that the
module table is unchanged.

**Direction.** The fix restores executability, which is toward a conclusive outcome. It is a repair of the implementation. No rule,
parameter or binding changes. It is disclosed to the pre-freeze review (R4) and carried into the disclosures.

**Other pre-freeze fixes found in the same QC11 development runs** (test fixtures and checker robustness; no driver
rule is involved):
* **Sandbox freeze commit.** It now also writes an inert `freeze/SANDBOX_FREEZE_NONCE.txt`, which exists only in
  sandboxes. Otherwise, once the dev manifest was committed in HEAD, the sandbox freeze commit changed no frozen path.
* **Stage-flow stub runner.** It passes its payload through a side file instead of argv (E2BIG).
* **F20 pass condition.** The setup plants the TEST marker, and the flow now checks that `execute` changed no ref,
  rather than that the marker is absent.
* **S12 fixture.** The manufactured rung record now carries every ladder key.
* **`p309_postexec.checks`.** A refusal from `run_seal_only` now makes P5 false instead of crashing the checker.
* **New flow S14.** It checks the frozen budget mechanics (delta review D2).

The development runs used a scratch evidence directory and wrote their ledger lines to `ledger/ZERO_TARGET_LEDGER.jsonl`
as usual. Two scratch runs of the stage flows alone, made through `runpy`, wrote no ledger line; they used stubs only.

## FE-9: the `cells.json` endpoint representation was misread (found while fixing R4 B1; never executed)

**The representation.** In the pinned cover `cells.json`, each endpoint is a list of two exact-rational strings whose
**sum** is the value. The canonical loader, `k5_minimality.rat`, reads it as `F(p[0]) + F(p[1])`.

**The misreading.** Three places read an endpoint as `F(p[0], p[1])`, that is, as numerator and denominator:
* `decoy_stage1b` (QC09);
* the proposal tool;
* the first draft of the B1 fix.

With string arguments that raises TypeError, so nothing was ever computed on a misread interval:
* `decoy_stage1b` had never run (no ledger line);
* the proposal tool had never run;
* the B1 draft was corrected before any run.

**The fix.** All three now use the driver's `cover_rat` / `cover_interval`. A ledgered structural check found them equal
to the canonical `rat` on all 326 CUSUM cover cells. Only the boolean result, and the raw entries of cover cells 0
and 1, were displayed (exposure ledger).

**Direction:** none. Without the fix, QC09 would have failed, and every execute would have been refused before the
marker.

## FE-10: QC03's research test depended on unpinned, unmirrored inputs (found by the pre-freeze dry run of the QC runner)

**Finding.** The coordinator dry-ran the QC runner's items before the freeze, into scratch output. That run is
development, not the qualification. In it, QC03 failed at import:
* `tests/test_srk_fsm_truth.py` (research) imports `d309_core` and `d309_rso`, from the overnight cell-309 stream
  `p5y_k5_tail_overnight_research/streams/D_309/code/`;
* through them it imports `ov_fixtures` and `ov_quarantine`, from `p5y_k5_tail_overnight_research/code/`.

None of the four was in the qualification's `git archive` mirror or in the freeze manifest's pins.

**Fix.**
* The four files are added to the mirror paths (`code/p309_qualify.py`) and to the manifest's pinned code
  (`code/make_freeze_manifest.py`). Qualification therefore runs them on frozen bytes.
* Re-checked in development: QC03 passes (12 declared seeds, mutants caught).
* No other file changed.
* These are cell-309 overnight-stream code files. They are not part of any cell-308 campaign.

**Why the dry run.** A27 allows no retry, so a plumbing defect found during the frozen qualification would have ended
the attempt.

**Direction:** none.
