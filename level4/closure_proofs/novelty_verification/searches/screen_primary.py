#!/usr/bin/env python3
"""Deduplicate and mechanically triage the persisted primary-search records."""

from __future__ import annotations

import html
import json
import re
from collections import defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
MANIFEST = BASE / "results/search_manifest.json"
OUTPUT = BASE / "results/candidate_pool.json"

TERMS = {
    "cusum": 7, "shiryaev": 7, "roberts": 4, "control chart": 6,
    "change point": 5, "changepoint": 5, "change detection": 5,
    "sequential detection": 5, "sequential estimation": 6,
    "optional stopping": 7, "stopping rule": 5, "stopping time": 5,
    "post-selection": 7, "self-start": 7, "reference estimation": 7,
    "baseline": 4, "forgetting factor": 6, "adaptive filter": 4,
    "event-trigger": 5, "threshold reset": 7, "reset system": 5,
    "concept drift": 6, "drift detection": 6, "adaptive window": 7,
    "recursive estimation": 6, "parameter estimation": 4,
}


def clean_markup(value: str | None) -> str:
    if not value:
        return ""
    return html.unescape(re.sub(r"<[^>]+>", " ", value)).replace("\n", " ")


def normalize_doi(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip().lower()
    value = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", value)
    return value.rstrip(". ") or None


def normalize_title(value: str | None) -> str:
    value = clean_markup(value).lower()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def candidate_key(record: dict) -> str:
    doi = normalize_doi(record.get("doi"))
    if doi:
        return f"doi:{doi}"
    return f"title:{normalize_title(record.get('title'))}|{record.get('year')}"


def relevance_score(title: str, abstract: str) -> tuple[int, list[str]]:
    title_low, text = title.lower(), f"{title} {abstract}".lower()
    matches = []
    score = 0
    for term, weight in TERMS.items():
        if term in text:
            matches.append(term)
            score += weight * (3 if term in title_low else 1)
    return score, matches


def main() -> None:
    manifest = json.loads(MANIFEST.read_text())
    merged: dict[str, dict] = {}
    hits: dict[str, list[dict]] = defaultdict(list)
    raw_records = 0
    for run in manifest["runs"]:
        if run["status"] != "COMPLETED":
            continue
        run["screening_status"] = "SCREENED-TITLE-ABSTRACT-METADATA"
        for rank, record in enumerate(run["records"], 1):
            raw_records += 1
            key = candidate_key(record)
            hits[key].append({
                "family": run["family"], "query_id": run["query_id"],
                "query": run["query"], "source": run["source"], "rank": rank,
            })
            if key not in merged:
                merged[key] = record.copy()
            else:
                current = merged[key]
                for field in ("title", "authors", "year", "venue", "doi", "stable_url", "abstract"):
                    if not current.get(field) and record.get(field):
                        current[field] = record[field]
                if (record.get("cited_by_count") or 0) > (current.get("cited_by_count") or 0):
                    current["cited_by_count"] = record["cited_by_count"]

    candidates = []
    for key, record in merged.items():
        title = clean_markup(record.get("title"))
        abstract = clean_markup(record.get("abstract"))
        score, matches = relevance_score(title, abstract)
        source_hits = hits[key]
        families = sorted({hit["family"] for hit in source_hits})
        sources = sorted({hit["source"] for hit in source_hits})
        candidates.append({
            "candidate_key": key,
            "title": title or None,
            "authors": record.get("authors") or [],
            "year": record.get("year"),
            "venue": record.get("venue"),
            "doi": normalize_doi(record.get("doi")),
            "stable_url": record.get("stable_url") or record.get("source_id"),
            "abstract": abstract or None,
            "families": families,
            "sources": sources,
            "query_hits": source_hits,
            "mechanical_relevance_score": score,
            "matched_terms": matches,
            "triage": "MANUAL-REVIEW" if score >= 10 else "SCREENED-LOW-SCORE",
        })
    candidates.sort(key=lambda row: (-row["mechanical_relevance_score"], -(len(row["families"])), row["title"] or ""))
    for rank, candidate in enumerate(candidates, 1):
        candidate["mechanical_rank"] = rank

    pool = {
        "schema": "rebaseguard.novelty-candidate-pool.v1",
        "source_manifest": "results/search_manifest.json",
        "raw_records_screened": raw_records,
        "unique_candidates_screened": len(candidates),
        "manual_review_queue": sum(c["triage"] == "MANUAL-REVIEW" for c in candidates),
        "screening_basis": "title, abstract when returned, and bibliographic metadata; no DIRECT classification is made here",
        "candidates": candidates,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    OUTPUT.write_text(json.dumps(pool, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
