# Historical novelty/provenance audit

## Finding

The expected baseline is confirmed: no standalone, paper-level novelty or
prior-art review was persisted at Stage F. Historical artifacts are preserved
unchanged; this file records, rather than reinterprets, their claims.

## Repository chronology

1. `rebaseguard_phase15.md` §8 records three targeted searches and says they
   returned neighboring facts but no direct hit. It names no papers, authors,
   identifiers, query logs, or inspected text and explicitly says “No citations
   are asserted” and that the search is suggestive, not exhaustive. It is a
   historical search summary, not reproducible literature evidence.
2. `level_4_theory_numerics/rebaseguard_level4_design.md`, “Blocking caveat on
   prior art,” says its requested reconnaissance could not run because the
   scholarly connector required an unavailable OpenAlex key. It declined to
   substitute recalled citations and left novelty risk unquantified.
3. The Stage-D blueprint inherited D-1/D-2/D-3 prior-art risk labels and D-4
   discussion from an external brief. At
   `ReBaseGuard_Level4_StageD_TheoryBlueprint_and_Pilot_2026-08-22/
   rebaseguard_staged_blueprint.md` line 486, the author states that D-1 through
   D-4 were not independently verified. They are planning/risk codes, not
   verified literature conclusions.
4. `level4/stage_f/notes/FAILURE_DIAGNOSES.md` SF3 and
   `level4/reports/LEVEL_4_FINAL_REPORT.md` §20 preserve two separate facts:
   (a) the repository lacked a standalone review; (b) project history supplied
   externally claimed a later adaptive/SR kill-search found no direct overlap.
   The underlying references and review artifact were not persisted.
5. `level4/stage_f/results/final_decision.json` therefore retained novelty as
   `OPEN`. The derived post-closure table preserved it as mandatory L4R-16,
   `OPEN / provenance gap`, blocker type `DOCUMENTATION_PROVENANCE`.

## Historical claims found

- A conditional-go memo described no direct hit across three targeted searches
  and required formal clearance before novelty claims.
- Neighboring areas were described as estimated-parameter run-length effects,
  self-starting/conditional-ARL work, and multi-cyclic quickest detection.
- The externally supplied project-history statement listed self-starting and
  adaptive CUSUM, optional stopping/post-selection, Touboul–Brette adaptation
  maps, variable-forgetting RLS, multi-cyclic and adaptive SR, and robust
  sequential detection, with an alleged `SR-NOVELTY-DEFENSIBLE` outcome.
- Stage F authorized only: a later external search reportedly found no direct
  overlap to the extent searched, but its artifact was absent and exhaustive
  novelty was not established. It forbade `novel`, `first`, `first-ever`, and
  `unprecedented`.

## Named-reference resolution before external search

Repository-wide searches for `Touboul` find only the Stage-F description of an
unpersisted external review. No title, year, DOI, or bibliographic clue exists.
Thus the historical name is initially classified
`UNRESOLVED HISTORICAL REFERENCE`. Plausible external works will not be treated
as the historical source without independent evidence.

`forgetting` and `post-selection` likewise occur as topic labels, not recovered
bibliographic records. Claude/ChatGPT mentions in the repository concern
scientific computation or project history rather than persisted novelty
evidence. No Perplexity result with underlying references was found.

## Audit conclusion

Prior AI summaries are not literature evidence for this campaign. The new
search starts from a documented provenance gap. The historical Stage-F verdict
remains `LEVEL-4-PARTIAL`, the current post-closure verdict remains
`LEVEL-4-PARTIAL`, and no historical wording is changed.

