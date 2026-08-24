#!/usr/bin/env python3
"""Collect the frozen primary searches. This is a live evidence step, not reproduction."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import subprocess
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
STRATEGY = BASE / "SEARCH_STRATEGY.md"
OUTPUT = BASE / "results/search_manifest.json"
USER_AGENT = "ReBaseGuard-novelty-audit/1.0 (mailto:repository-audit@example.invalid)"


def queries() -> list[dict[str, str]]:
    family = None
    rows: list[dict[str, str]] = []
    for line in STRATEGY.read_text().splitlines():
        match = re.match(r"## 7([A-I]) — (.+)", line)
        if match:
            family = f"7{match.group(1)}"
            continue
        match = re.match(r"([1-4])\. `(.+)`$", line)
        if match and family:
            rows.append({"family": family, "query_id": f"{family}-Q{match.group(1)}", "query": match.group(2)})
    if len(rows) != 36:
        raise RuntimeError(f"expected 36 frozen queries, found {len(rows)}")
    return rows


def get_json(url: str, attempts: int = 2) -> tuple[dict | None, str | None, int | None]:
    command = [
        "curl", "-fLsS", "--retry", str(attempts), "--retry-all-errors",
        "--connect-timeout", "10", "--max-time", "30",
        "-A", USER_AGENT, "-H", "Accept: application/json", url,
    ]
    completed = subprocess.run(command, capture_output=True, text=True, timeout=75)
    if completed.returncode:
        error = completed.stderr.strip() or f"curl exit {completed.returncode}"
        return None, error, None
    try:
        return json.loads(completed.stdout), None, 200
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON: {exc}", 200


def abstract_from_inverted(index: dict | None) -> str | None:
    if not index:
        return None
    positions = [(position, word) for word, values in index.items() for position in values]
    return " ".join(word for _, word in sorted(positions))


def openalex_record(item: dict) -> dict:
    primary = item.get("primary_location") or {}
    source = primary.get("source") or {}
    return {
        "source_id": item.get("id"),
        "title": item.get("display_name"),
        "authors": [a.get("author", {}).get("display_name") for a in item.get("authorships", [])],
        "year": item.get("publication_year"),
        "venue": source.get("display_name"),
        "doi": item.get("doi"),
        "stable_url": primary.get("landing_page_url") or item.get("doi") or item.get("id"),
        "cited_by_count": item.get("cited_by_count"),
        "type": item.get("type"),
        "is_retracted": item.get("is_retracted"),
        "open_access": item.get("open_access"),
        "abstract": abstract_from_inverted(item.get("abstract_inverted_index")),
    }


def crossref_record(item: dict) -> dict:
    title = (item.get("title") or [None])[0]
    container = (item.get("container-title") or [None])[0]
    year_parts = (item.get("published") or item.get("issued") or {}).get("date-parts", [[None]])
    authors = []
    for author in item.get("author", []):
        name = " ".join(x for x in [author.get("given"), author.get("family")] if x)
        authors.append(name or author.get("name"))
    return {
        "source_id": item.get("URL") or item.get("DOI"),
        "title": title,
        "authors": authors,
        "year": year_parts[0][0] if year_parts and year_parts[0] else None,
        "venue": container,
        "doi": item.get("DOI"),
        "stable_url": item.get("URL"),
        "type": item.get("type"),
        "is_retracted": None,
        "abstract": item.get("abstract"),
        "score": item.get("score"),
    }


def run_source(source: str, row: dict[str, str]) -> dict:
    encoded = urllib.parse.quote(row["query"])
    if source == "OpenAlex":
        url = f"https://api.openalex.org/works?search={encoded}&per-page=20"
    elif source == "Crossref":
        url = f"https://api.crossref.org/works?query={encoded}&rows=20&select=DOI,title,author,published,issued,container-title,URL,type,abstract,score"
    else:
        raise ValueError(source)
    payload, error, status = get_json(url)
    if payload is None:
        return {**row, "source": source, "mode": "PRIMARY", "status": "ACCESS-UNAVAILABLE", "request_url": url,
                "http_status": status, "error": error, "returned": 0, "screening_status": "NOT-RUN", "records": []}
    raw = payload.get("results", []) if source == "OpenAlex" else payload.get("message", {}).get("items", [])
    converter = openalex_record if source == "OpenAlex" else crossref_record
    return {**row, "source": source, "mode": "PRIMARY", "status": "COMPLETED", "request_url": url,
            "http_status": status, "error": None, "returned": len(raw), "screening_status": "PENDING",
            "records": [converter(item) for item in raw]}


def unavailable_run(source: str, row: dict[str, str], evidence: str) -> dict:
    return {**row, "source": source, "mode": "PRIMARY", "status": "ACCESS-UNAVAILABLE",
            "request_url": None, "http_status": None, "error": evidence, "returned": 0,
            "screening_status": "NOT-RUN", "records": []}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if OUTPUT.exists() and not args.overwrite:
        raise SystemExit(f"refusing to overwrite {OUTPUT}; pass --overwrite only before interpretation")

    started = datetime.now(timezone.utc).isoformat()
    frozen_queries = queries()
    primary_jobs = [(source, row) for row in frozen_queries for source in ("OpenAlex", "Crossref")]
    runs = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(run_source, source, row) for source, row in primary_jobs]
        for future in concurrent.futures.as_completed(futures):
            runs.append(future.result())
    runs.sort(key=lambda row: (row["query_id"], row["source"]))
    for row in frozen_queries:
        runs.append(unavailable_run(
            "Semantic Scholar", row,
            "Public Graph API returned HTTP 429 during the pre-run access probe on 2026-08-24; no query result was represented as completed.",
        ))
        runs.append(unavailable_run(
            "Google Scholar", row,
            "Public Scholar page attempts returned no inspectable result payload in the browsing environment on 2026-08-24.",
        ))

    manifest = {
        "schema": "rebaseguard.novelty-search-manifest.v1",
        "protocol_combined_sha256": "deb800951b0353f3771ad6d9c1f795cf2f351c4da564ef5d0d5e3fe5b9cbd712",
        "search_date": "2026-08-24",
        "started_at_utc": started,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "primary_queries": 36,
        "top_n_requested": 20,
        "source_access": {
            "OpenAlex": "COMPLETED",
            "Crossref": "COMPLETED",
            "Semantic Scholar": "ACCESS-UNAVAILABLE",
            "Google Scholar": "ACCESS-UNAVAILABLE",
        },
        "runs": runs,
        "follow_up_runs": [],
        "snowball_runs": [],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
