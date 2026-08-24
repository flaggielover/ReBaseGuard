#!/usr/bin/env python3
"""Persist two rounds of backward/forward citation evidence from OpenAlex."""

from __future__ import annotations

import concurrent.futures
import json
import re
import subprocess
import urllib.parse
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
INSPECTION = BASE / "results/inspection_evidence.json"
MANIFEST = BASE / "results/search_manifest.json"
OUTPUT = BASE / "results/snowball_evidence.json"
UA = "ReBaseGuard-novelty-audit/1.0"

ROUNDS = {
    "ROUND-1": ["W01", "W03", "W05", "W06", "W07", "W08", "W10", "W11", "W14", "W25", "W33"],
    "ROUND-2": ["W09", "W13", "W16", "W19", "W21", "W26"],
}

TERMS = ["cusum", "shiryaev", "sequential", "stopping", "adaptive", "reference", "baseline",
         "changepoint", "change-point", "drift", "forgetting", "reset", "control chart"]


def fetch(url: str) -> tuple[dict | None, str | None]:
    completed = subprocess.run(
        ["curl", "-fLsS", "--retry", "2", "--retry-all-errors", "--max-time", "40", "-A", UA, url],
        capture_output=True, text=True, timeout=100,
    )
    if completed.returncode:
        return None, completed.stderr.strip() or f"curl exit {completed.returncode}"
    try:
        return json.loads(completed.stdout), None
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON: {exc}"


def compact(work: dict) -> dict:
    inv = work.get("abstract_inverted_index") or {}
    abstract = " ".join(word for _, word in sorted((p, word) for word, ps in inv.items() for p in ps)) or None
    title = work.get("display_name")
    text = f"{title or ''} {abstract or ''}".lower()
    return {
        "openalex_id": work.get("id"), "title": title,
        "authors": [a.get("author", {}).get("display_name") for a in work.get("authorships", [])],
        "year": work.get("publication_year"), "doi": work.get("doi"),
        "venue": (work.get("primary_location") or {}).get("source", {}).get("display_name") if (work.get("primary_location") or {}).get("source") else None,
        "stable_url": (work.get("primary_location") or {}).get("landing_page_url") or work.get("doi") or work.get("id"),
        "abstract": abstract, "cited_by_count": work.get("cited_by_count"),
        "matched_terms": [term for term in TERMS if term in text],
    }


def fetch_seed(job: tuple[str, str, dict]) -> dict:
    round_id, work_id, work = job
    openalex_id = work["openalex"]["id"].rsplit("/", 1)[-1]
    refs = [item.rsplit("/", 1)[-1] for item in work["openalex"].get("referenced_works", [])]
    backward = []
    errors = []
    for start in range(0, len(refs), 100):
        ids = "|".join(refs[start:start + 100])
        url = "https://api.openalex.org/works?filter=openalex_id:" + urllib.parse.quote(ids, safe="|") + "&per-page=100"
        payload, error = fetch(url)
        if payload:
            backward.extend(compact(item) for item in payload.get("results", []))
        elif error:
            errors.append({"direction": "BACKWARD", "url": url, "error": error})
    forward_url = f"https://api.openalex.org/works?filter=cites:{openalex_id}&sort=cited_by_count:desc&per-page=100"
    payload, error = fetch(forward_url)
    forward = [compact(item) for item in payload.get("results", [])] if payload else []
    if error:
        errors.append({"direction": "FORWARD", "url": forward_url, "error": error})
    return {
        "round": round_id, "seed_work_id": work_id, "seed_openalex_id": openalex_id,
        "backward_status": "COMPLETED" if not any(e["direction"] == "BACKWARD" for e in errors) else "ACCESS-UNAVAILABLE",
        "forward_status": "COMPLETED" if not any(e["direction"] == "FORWARD" for e in errors) else "ACCESS-UNAVAILABLE",
        "backward": backward, "forward": forward, "errors": errors,
    }


def main() -> None:
    inspection = json.loads(INSPECTION.read_text())
    by_id = {work["work_id"]: work for work in inspection["works"]}
    jobs = [(round_id, work_id, by_id[work_id]) for round_id, ids in ROUNDS.items() for work_id in ids]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        seeds = list(executor.map(fetch_seed, jobs))
    seeds.sort(key=lambda row: (row["round"], row["seed_work_id"]))

    selected_oa_ids = {work["openalex"]["id"] for work in inspection["works"]}
    unique = {}
    for seed in seeds:
        for direction in ("backward", "forward"):
            for work in seed[direction]:
                if work["openalex_id"] not in selected_oa_ids:
                    unique.setdefault(work["openalex_id"], work)
    candidates = sorted(unique.values(), key=lambda row: (-len(row["matched_terms"]), -(row["cited_by_count"] or 0), row["title"] or ""))
    OUTPUT.write_text(json.dumps({
        "schema": "rebaseguard.novelty-snowball-evidence.v1",
        "round_definitions": ROUNDS,
        "seeds": seeds,
        "unique_nonseed_candidates": candidates,
        "manual_round_assessments": {
            "ROUND-1": {"new_direct": None, "new_high_partial": None, "status": "PENDING-MANUAL-SCREEN"},
            "ROUND-2": {"new_direct": None, "new_high_partial": None, "status": "PENDING-MANUAL-SCREEN"}
        }
    }, indent=2, sort_keys=True, ensure_ascii=False) + "\n")

    manifest = json.loads(MANIFEST.read_text())
    manifest["snowball_runs"] = [
        {"mode": "SNOWBALL", "round": seed["round"], "seed_work_id": seed["seed_work_id"],
         "directions": {"BACKWARD": seed["backward_status"], "FORWARD": seed["forward_status"]},
         "backward_records": len(seed["backward"]), "forward_records": len(seed["forward"]),
         "errors": seed["errors"]}
        for seed in seeds
    ]
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
