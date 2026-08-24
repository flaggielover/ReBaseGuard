# Limitations

- Google Scholar returned no inspectable payload and Semantic Scholar's public API returned HTTP 429; both are persisted as `ACCESS-UNAVAILABLE`. OpenAlex and Crossref supplied complete frozen-query coverage.
- Search engines, metadata, and citation graphs are imperfect. The search can support only a scoped position, not global novelty or priority.
- Several papers were abstract-only; W07, W15, and W18 were metadata-only and therefore were not classified DIRECT or HIGH-PARTIAL.
- The historical `Touboul` name remains `UNRESOLVED HISTORICAL REFERENCE`. W21 is a plausible independently identified analogue, not a recovered historical citation.
- 2445 combined unique candidates were screened by title/abstract/metadata; 33 were included and individually classified. Screening is broad but not exhaustive full-text review.
- Production implementations may be proprietary or poorly documented. Practical mechanism overlap is separated from theoretical overlap.
- No new science or external validation was performed.
