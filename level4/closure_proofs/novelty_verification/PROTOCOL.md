# Frozen protocol — prior-art / novelty verification

**Campaign:** isolated closure of `L4R-16`  
**Freeze date:** 2026-08-24 (Asia/Tokyo)  
**Pre-freeze external search outcomes:** none inspected in this campaign  
**Historical inputs:** repository artifacts only, inventoried in
`HISTORICAL_PROVENANCE_AUDIT.md`

This protocol and `SEARCH_STRATEGY.md` are immutable after their combined
SHA-256 is recorded in `results/protocol_hash.json`. Primary query strings,
criteria, labels, and stopping rules may not change after search results are
interpreted. Later searches must be recorded as `FOLLOW-UP` or `SNOWBALL`.

## 1. Scope

The unit under review is stopping-selected recursive reference reuse and its
theorem/certificate/interpretation components C1–C11. The campaign asks what
literature establishes, not whether an attractive novelty outcome can be
manufactured. Negative or threatening evidence is retained.

Out of scope: new simulation, new theorem work, external validation, detector
design, modification of Stage F or any later closure, and a global Level-4
re-audit.

## 2. Sources

The frozen primary scholarly indexes are OpenAlex, Crossref, Semantic Scholar,
and Google Scholar. The first three are queried through their public APIs or
public search endpoints; Google Scholar is attempted through its public web
interface. Publisher, DOI, arXiv, ACM, IEEE, Springer, Wiley, JSTOR, zbMATH,
and author/preprint pages are inspection and metadata-validation sources when
available. Ordinary web search is discovery-only.

Every access failure is recorded as `ACCESS-UNAVAILABLE`; it is never treated
as a completed search. Closure NV2 requires usable results from at least two
independent scholarly indexes.

## 3. Inclusion and exclusion

Include a work if it is scholarly or a stable primary technical specification,
was public by the search date, has recoverable authorship/title/year metadata,
and materially bears on C1–C11 or on one mandatory search family's stated
distinction. Production-system material may be included only to establish
practical mechanism overlap and is never promoted to theoretical overlap.

Exclude unsourced blogs, AI summaries, marketing pages, duplicate records,
works with no material bearing on the components, and sources whose identity
cannot be verified. Query hits screened out remain countable in the manifest
but are not bibliography entries. Non-English works are included when an
English title and abstract/full text are inspectable; otherwise access is
marked insufficient.

## 4. Duplicate and metadata rules

Normalize DOIs by lower-casing and removing `https://doi.org/`, `http://doi.org/`,
`doi:`, surrounding whitespace, and a terminal period. A normalized DOI is the
primary deduplication key. Without a DOI, use normalized title plus year. Merge
source observations without overwriting conflicts; unresolved conflicts are
explicit. Never infer a DOI or arXiv identifier.

Required included-work fields are title, authors, year, venue, DOI or explicit
null, arXiv identifier or explicit null, stable URL, discovering family and
query, relevance, exactly one overlap label, classification reason, evidence
basis, and access level (`FULL-TEXT`, `ABSTRACT`, `METADATA-ONLY`, or
`ACCESS-UNAVAILABLE`).

## 5. Classification

Each included work has exactly one primary label:

- `DIRECT`: substantially the same stopping-selected recursive reference-reuse
  mechanism and overlap with a load-bearing theoretical contribution.
- `HIGH-PARTIAL`: a major mechanism or theorem component, but not the complete
  recursive problem.
- `MODERATE-PARTIAL`: neighboring theory with a materially different mechanism
  or objective.
- `ANALOGUE`: similar mathematics without the same monitoring semantics.
- `BACKGROUND`: context, not novelty-threatening.
- `NOT-RELEVANT`: screened evidence retained to explain a false lead.

Matrix cells are exactly `YES`, `PARTIAL`, `NO`, or `UNCLEAR`. Threat level is
`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, or `NONE` and cannot replace the overlap
label.

No work is classified `DIRECT` from a title, snippet, or metadata alone.
`DIRECT` and `HIGH-PARTIAL` require an individual 13-question audit based on an
abstract at minimum; limitations from abstract-only access are explicit.

## 6. Search execution and stopping

All 36 primary queries in `SEARCH_STRATEGY.md` are executed in every usable
frozen primary index. At least the first 20 results, or all returned results if
fewer, are screened per index/query. Deduplication occurs only after raw query
provenance is saved.

Every `DIRECT` or `HIGH-PARTIAL` work receives backward citation searching and,
where feasible, forward citation searching. Snowball rounds stop only after two
consecutive completed rounds yield no new `DIRECT` or `HIGH-PARTIAL` work.
Additional terminology or named-reference searches are separately labeled
`FOLLOW-UP`; they do not rewrite the primary protocol.

## 7. Historical-name rule

`Touboul`, `forgetting`, and `post-selection` receive explicit follow-up
searches. If repository clues and external evidence cannot identify the exact
Touboul work referenced by the historical AI review, the record must say
`UNRESOLVED HISTORICAL REFERENCE`; a plausible paper may be discussed only as
a separately discovered analogue.

## 8. Claim taxonomy

Candidate claims receive one of `SAFE`, `SAFE-WITH-QUALIFIER`, `UNSUPPORTED`,
or `FORBIDDEN`. The priority words `first`, `first-ever`, and `unprecedented`
are `FORBIDDEN` absent extraordinary evidence. Search closure is not proof of
global novelty. The allowed scoped novelty positions are N1–N4 exactly as
defined in the campaign brief.

## 9. Closure derivation

`NOVELTY-VERIFICATION-CLOSED` is mechanically available only when NV1–NV12 all
pass. A systematic negative result or direct overlap does not itself fail the
audit if threatening evidence is preserved and claims are narrowed. Missing
search-family coverage, insufficient independent sources, unaudited high-risk
works, or fabricated metadata prevents closure. A material integrity or
dishonesty failure yields `NOVELTY-VERIFICATION-FAILED`; otherwise incomplete
coverage yields `NOVELTY-VERIFICATION-PARTIAL`.

The current global Level-4 verdict is not recomputed here. If this scoped
requirement closes, the only remaining fail/open blocker is expected to be
`SEMI-REAL EXTERNAL VALIDATION`; that statement is a requirement update, not a
new global audit.

