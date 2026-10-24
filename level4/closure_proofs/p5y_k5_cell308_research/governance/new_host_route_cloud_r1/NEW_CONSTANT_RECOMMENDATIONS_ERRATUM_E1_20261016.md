# Erratum E1 to the new-constant recommendations (Cell-308 Cloud route r1) — after external B3 (Y1, Y2)

**Status: PROPOSED CORRECTION · RECOMMENDATIONS UNCHANGED IN VALUE · NOT ADOPTED.** This erratum corrects the
provenance statements of `NEW_CONSTANT_RECOMMENDATIONS_20261016.md` (sha256 `fcac5f09…10fc`), which is preserved
unchanged. Where the two differ, this erratum governs. Its source is external B3
(`reviews/external/REVIEW_EXTERNAL_B3_PROVENANCE.md`, `16188ffd…e96a`): rows N1 and N2 (lines 80–85) and findings Y1 and
Y2 (lines 181–187).

**The values are unchanged:** N1 = 24 hours and N2 = 21 days, both still recommendations. No number, definition or
rule is changed to manufacture a derivation. `new_target_evaluations = 0` · `cell309_activity = none`.

## E1.1 — N1 (response time): the choices are stated, not hidden (Y1)

The recommendations file §2 says N1's free-choice content is "none beyond reading 'about 3 days' as 72 h". **That
statement is withdrawn.** N1 rests on these choices, none of which the accepted text requires:

| # | choice | why it is a choice |
|---|---|---|
| C1 | read "up to about 3 days" (ratification row 19) as a **fixed 72-hour budget** | the accepted text is an approximate weekend allowance in a deadline's rationale, not a budget |
| C2 | treat that budget as **shared** across the resumes | row 19 does not say whether the allowance is per event or in total |
| C3 | divide it **equally** over three responses | row 18 bounds the resumes at 3; it does not require equal allocation, or any individual maximum |
| C4 | make 24 hours an **individual obligation**, triggered by an interruption **or by a step's readiness** | the readiness trigger, and the extension to anchor checks and `recover`, are additions |
| C5 | add an **EVAL_CAP ceiling** (4 × EVAL_CAP + 72 h ≤ 168 h, so EVAL_CAP ≤ 24 h under MBS-8 (ii)) | a new rule, not an output of the historical §3.2 rule |
| C6 | add the consequence **stop before the freeze** when a derived EVAL_CAP exceeds that ceiling | a new rule |

What the arithmetic establishes, and what it does not:
* It is valid under C1–C3: 72 / 3 = 24, and 4 × 8 + 3 × 24 = 104 h, inside 168 h.
* It is a **three-resume planning envelope**. It does not show that every anchor, `recover` or readiness event is one
  of exactly three non-overlapping delays. It does not show that all other elapsed time is zero.
* It establishes **no response capacity**. Whether the owner or the named checker can respond within 24 hours is
  operational evidence. It can exist only once the checker is named (matrix R4 B1 and OPS-10), and in practice only
  after the marker.
* The inherited **7-day deadline governs** in every case and is never extended.

## E1.2 — N2 (interpreter build to marker): discretionary, with the source limit stated (Y2)

N2 = 21 days is a **discretionary recommendation**. It is not a derivation. The choices:

| # | choice |
|---|---|
| D1 | treat the accepted principle "about one Rapid-Security-Response cadence" (ratification row 19) as applying to the whole window from the interpreter build (amendment E1.4 moved the window's start) |
| D2 | choose Ubuntu's **regular 4-week** cycle, not its **2-week urgent CVE** cycle, as "one cadence" |
| D3 | treat that cadence as a **tolerable update-deferral interval** |
| D4 | reserve the 7-day deadline inside it: 28 − 7 = 21 |

Limits that stay attached:
* A public release cadence does **not** establish an update-free interval on a host. It does not show that deferring
  an urgent fix is safe. It does not control the phase within a cycle, urgent respins, or provider actions.
* It does not show that the pre-marker governance steps fit in 21 days.
* **The urgent-update terminal rule is preserved.** Any update inside the window stops the route on that platform,
  including an urgent fix the owner decides must be applied (amendment E2.7; ratification row 19, "A platform change is
  terminal anyway"). An update is never applied and then continued.

## E1.3 — The external source: what was and was not verified (Y2)

* **B3's request failed.** B3's single authorized fetch of the Ubuntu SRU page failed at its proxy with 403, so B3 did
  not verify the quotation (report line 34).
* **The coordinator side retrieved the page.** On 2026-10-16 at 12:48:13Z it fetched
  `https://ubuntu.com/kernel/docs/explanation/stable-release-updates/` (HTTP/2 200; `last-modified: Tue, 13 Oct 2026
  01:05:45 GMT`). The raw bytes are recorded in `evidence/ubuntu_sru_20261016/`:

  | file | content | sha256 |
  |---|---|---|
  | `page.html.txt` | 32,737 bytes, unmodified | `9f89bcfd…2282` |
  | `headers_redacted.txt` | the response headers, with the `set-cookie` values redacted | `39071101…f47d` |
  | `retrieved_utc.txt` | the retrieval time | `510b3021…8d5f` |

  The sentence quoted in the recommendations §1 occurs verbatim in that page. Its `article:modified_time` is
  2026-10-13T01:04:50+00:00.
* **This is a recorded retrieval by the author's side, not an independent verification.** The coordinator side wrote
  N2 and chose the source. A reviewer can re-hash the committed bytes, but cannot confirm that the live page held those
  bytes at that time. The limit B3 stated therefore stands, narrowed to that.
* The page itself says "SRU cycle dates are tentative. As such, they cannot be guaranteed and may be subject to
  change."

## E1.4 — "A stop before the marker consumes nothing": scope corrected (B3 line 85)

Recommendations §3 says a stop before the marker "consumes nothing of cell 308". That is confined to **target
consumption**: no evaluation of cell 308 happens before the target marker. A pre-marker stop does **not**:
* restore a consumed L-DET attempt (there is no repeat);
* erase the host-attempt record, or any permanent adverse attestation outcome for the machine (procedure r3 errata E1
  and E2);
* avoid the owner process that any further attempt needs (a new owner ruling, a fresh S12 rating and a formal review,
  amendment E2.7).

## E1.5 — Adoption

N1 and N2 remain owner numbers, fixed before the Phase-1 inventory (matrix R4 A17). Adopting them now needs:
* B3's single confirmation of this erratum;
* the owner's own decision, made with C1–C6 and D1–D4 in view.

Neither number is evidence that the response or the window will hold. That evidence is operational (OPS-5, OPS-10).
