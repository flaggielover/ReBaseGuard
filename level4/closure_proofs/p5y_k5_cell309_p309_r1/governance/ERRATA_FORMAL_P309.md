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
