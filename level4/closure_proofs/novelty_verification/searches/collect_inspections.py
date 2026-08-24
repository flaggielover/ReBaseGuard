#!/usr/bin/env python3
"""Persist exact-title/DOI follow-ups for the manually selected audit set."""

from __future__ import annotations

import concurrent.futures
import json
import subprocess
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
MANIFEST = BASE / "results/search_manifest.json"
OUTPUT = BASE / "results/inspection_evidence.json"
UA = "ReBaseGuard-novelty-audit/1.0"

SPECS = [
    ("W01", "10.2307/2348827", "Self-Starting Cusum Charts for Location and Scale", ["7A"]),
    ("W02", "10.1080/00224065.2006.11918623", "Effects of Parameter Estimation on Control Chart Properties: A Literature Review", ["7A", "7H"]),
    ("W03", "10.1080/07408170801961412", "Adaptive CUSUM procedures with EWMA-based shift estimators", ["7A", "7E"]),
    ("W04", "10.1198/004017003000000023", "An adaptive exponentially weighted moving average control chart", ["7A", "7F"]),
    ("W05", "10.1007/s11222-016-9684-8", "Continuous monitoring for changepoints in data streams using adaptive estimation", ["7A", "7F", "7I"]),
    ("W06", "10.1080/07474949908836432", "Quasi-stationary biases of change point and change magnitude estimation after sequential cusum test", ["7D", "7E"]),
    ("W07", "10.1016/j.jspi.2004.09.005", "On the biases of change point and change magnitude estimation after CUSUM test", ["7D", "7E"]),
    ("W08", "10.5539/ijsp.v5n5p43", "Estimation of Change-point and Post-change Parameters after Adaptive Sequential CUSUM Test in an Exponential Family", ["7A", "7D", "7E"]),
    ("W09", "10.1080/07474940902816767", "Distributional Properties of CUSUM Stopping Times and Stopped Processes", ["7B", "7D"]),
    ("W10", "10.1214/009053605000000183", "Nonanticipating estimation applied to sequential analysis and changepoint detection", ["7C", "7D", "7E"]),
    ("W11", "10.1214/aos/1176347990", "Sequential Detection of a Change in a Normal Mean when the Initial Value is Unknown", ["7A", "7C", "7H"]),
    ("W12", "10.1214/09-AOS775", "On optimality of the Shiryaev–Roberts procedure for detecting a change in distribution", ["7B", "7C"]),
    ("W13", "10.1002/asmb.2026", "Efficient performance evaluation of the generalized Shiryaev–Roberts detection procedure in a multi-cyclic setup", ["7B", "7C"]),
    ("W14", "10.1080/03610918.2014.906611", "An Adaptive Shiryaev–Roberts Procedure for Signalling Varying Location Shifts", ["7C"]),
    ("W15", "10.1016/j.cie.2011.07.006", "An adaptive Shiryaev-Roberts procedure for monitoring dispersion", ["7C"]),
    ("W16", "10.1017/S0305004100076386", "Large-sample theory of sequential estimation", ["7D"]),
    ("W17", "10.1214/20-AOS1991", "Time-uniform, nonparametric, nonasymptotic confidence sequences", ["7D"]),
    ("W18", "10.1016/0005-1098(81)90070-4", "Implementation of self-tuning regulators with variable forgetting factors", ["7F"]),
    ("W19", "10.1080/00207179308923034", "On a general concept of forgetting", ["7F"]),
    ("W20", "10.1109/LSP.2008.2001559", "A Robust Variable Forgetting Factor Recursive Least-Squares Algorithm for System Identification", ["7F"]),
    ("W21", "10.1007/s00422-008-0267-4", "Dynamics and bifurcations of the adaptive exponential integrate-and-fire model", ["7G"]),
    ("W22", "10.1051/cocv:2008008", "Generalized solutions to hybrid dynamical systems", ["7G"]),
    ("W23", "10.1198/004017001750386279", "The performance of exponentially weighted moving average charts with estimated parameters", ["7H"]),
    ("W24", "10.1080/00207540701325462", "Conditional and marginal performance of the Poisson CUSUM control chart with parameter estimation", ["7H"]),
    ("W25", "10.1137/1.9781611972771.42", "Learning from Time-Changing Data with Adaptive Windowing", ["7H", "7I"]),
    ("W26", "10.1145/2523813", "A survey on concept drift adaptation", ["7H", "7I"]),
    ("W27", "10.1145/2939672.2939836", "Fast Unsupervised Online Drift Detection Using Incremental Kolmogorov-Smirnov Test", ["7I"]),
    ("W28", "10.1109/TKDE.2018.2876857", "Learning under Concept Drift: A Review", ["7I"]),
    ("W29", "10.1007/978-3-540-28645-5_29", "Learning with Drift Detection", ["7I"]),
    ("W30", None, "The Changepoint Model for Statistical Process Control", ["7A", "7E", "7H"]),
    ("W31", "10.1080/07474940008836437", "Nonparametric adaptive change point estimation and on line detection", ["7E", "7H"]),
    ("W32", "10.1080/07474941003741284", "Sequential Detection and Estimation of Change-Points", ["7E"]),
    ("W33", "10.1002/qre.1511", "A Self-Starting CUSUM Chart Combined with a Maximum Likelihood Estimator for the Time of a Detected Shift in the Process Mean", ["7A", "7E"]),
]


def fetch(url: str) -> tuple[dict | None, str | None]:
    completed = subprocess.run(
        ["curl", "-fLsS", "--retry", "2", "--retry-all-errors", "--max-time", "35", "-A", UA, url],
        capture_output=True, text=True, timeout=90,
    )
    if completed.returncode:
        return None, completed.stderr.strip() or f"curl exit {completed.returncode}"
    try:
        return json.loads(completed.stdout), None
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON: {exc}"


def inspect(spec: tuple) -> dict:
    work_id, doi, title, families = spec
    if doi:
        oa_url = "https://api.openalex.org/works/https://doi.org/" + urllib.parse.quote(doi, safe="")
        cr_url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    else:
        encoded = urllib.parse.quote(title)
        oa_url = f"https://api.openalex.org/works?search={encoded}&per-page=5"
        cr_url = f"https://api.crossref.org/works?query.title={encoded}&rows=5"
    oa, oa_error = fetch(oa_url)
    cr, cr_error = fetch(cr_url)
    if oa and "results" in oa:
        exact = [item for item in oa["results"] if item.get("display_name", "").casefold() == title.casefold()]
        oa = exact[0] if exact else (oa["results"][0] if oa["results"] else None)
    if cr and "message" in cr and isinstance(cr["message"], dict) and "items" in cr["message"]:
        exact = [item for item in cr["message"]["items"] if (item.get("title") or [""])[0].casefold() == title.casefold()]
        cr = exact[0] if exact else (cr["message"]["items"][0] if cr["message"]["items"] else None)
    elif cr and "message" in cr:
        cr = cr["message"]
    return {
        "work_id": work_id, "requested_doi": doi, "requested_title": title, "families": families,
        "mode": "FOLLOW-UP", "query": doi or title,
        "openalex_url": oa_url, "openalex": oa, "openalex_error": oa_error,
        "crossref_url": cr_url, "crossref": cr, "crossref_error": cr_error,
    }


def main() -> None:
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        records = list(executor.map(inspect, SPECS))
    records.sort(key=lambda row: row["work_id"])
    OUTPUT.write_text(json.dumps({
        "schema": "rebaseguard.novelty-inspection-evidence.v1",
        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
        "works": records,
    }, indent=2, sort_keys=True, ensure_ascii=False) + "\n")

    manifest = json.loads(MANIFEST.read_text())
    manifest["follow_up_runs"] = [
        {
            "mode": "FOLLOW-UP", "work_id": row["work_id"], "families": row["families"],
            "query": row["query"], "source": source,
            "status": "COMPLETED" if row[source.lower()] else "ACCESS-UNAVAILABLE",
            "request_url": row[f"{source.lower()}_url"],
            "error": row[f"{source.lower()}_error"],
        }
        for row in records for source in ("OpenAlex", "Crossref")
    ]
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
