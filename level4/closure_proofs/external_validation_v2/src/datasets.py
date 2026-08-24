"""Deterministic, leak-safe preprocessing for the frozen primary tasks."""
from __future__ import annotations

import csv
import gzip
import io
import warnings
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta

import numpy as np

from acquire import archive_path


@dataclass(frozen=True)
class TaskData:
    task: str
    timestamps: np.ndarray
    X: np.ndarray
    y: np.ndarray
    audit: dict


def _calendar(ts: list[datetime]) -> np.ndarray:
    hour = np.array([t.hour + t.minute / 60 for t in ts], float)
    weekday = np.array([t.weekday() for t in ts], float)
    year_day = np.array([t.timetuple().tm_yday - 1 + hour[i] / 24 for i, t in enumerate(ts)])
    return np.column_stack([
        np.sin(2 * np.pi * hour / 24), np.cos(2 * np.pi * hour / 24),
        np.sin(2 * np.pi * weekday / 7), np.cos(2 * np.pi * weekday / 7),
        np.sin(2 * np.pi * year_day / 365.2425),
        np.cos(2 * np.pi * year_day / 365.2425),
    ])


def _lagged(log_target: np.ndarray, timestamps: list[datetime], lags: tuple[int, ...],
            extra: np.ndarray | None = None, valid: np.ndarray | None = None) -> TaskData:
    ok = np.isfinite(log_target) if valid is None else valid.copy()
    lag_eligible = np.isfinite(log_target) if valid is None else valid
    for lag in lags:
        ok[:lag] = False
        ok[lag:] &= lag_eligible[:-lag]
    idx = np.flatnonzero(ok)
    lag_features = np.column_stack([log_target[idx - lag] for lag in lags])
    cal = _calendar([timestamps[i] for i in idx])
    pieces = [lag_features, cal]
    if extra is not None:
        pieces.insert(1, extra[idx])
    return idx, np.column_stack(pieces), log_target[idx]


def load_household() -> TaskData:
    path = archive_path("household")
    with zipfile.ZipFile(path) as archive, archive.open("household_power_consumption.txt") as raw:
        rows = csv.reader(io.TextIOWrapper(raw, encoding="utf-8"), delimiter=";")
        next(rows)
        means, times, counts = [], [], []
        total = count = 0.0
        start = None
        n_raw = missing = 0
        for row in rows:
            if start is None:
                start = datetime.strptime(row[0] + " " + row[1], "%d/%m/%Y %H:%M:%S")
            value = row[2].strip()
            if value not in {"", "?"}:
                total += float(value)
                count += 1
            else:
                missing += 1
            n_raw += 1
            if n_raw % 15 == 0:
                means.append(total / count if count >= 12 else np.nan)
                counts.append(int(count))
                times.append(start + timedelta(minutes=n_raw - 15))
                total = count = 0.0
        if n_raw % 15:
            means.append(total / count if count >= 12 else np.nan)
            counts.append(int(count))
            times.append(start + timedelta(minutes=n_raw - n_raw % 15))
    target = np.log1p(np.asarray(means, float))
    idx, X, y = _lagged(target, times, (1, 4, 96, 672))
    return TaskData("household", np.array(times, dtype="datetime64[m]")[idx], X, y, {
        "raw_rows": n_raw, "missing_target_rows": missing,
        "bins": len(means), "eligible_bins": int(idx.size),
        "minimum_real_measurements_per_bin": 12,
    })


def load_metro() -> TaskData:
    path = archive_path("metro")
    by = defaultdict(list)
    with zipfile.ZipFile(path) as archive, archive.open("Metro_Interstate_Traffic_Volume.csv.gz") as packed:
        with gzip.GzipFile(fileobj=packed) as raw:
            rows = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8"))
            for row in rows:
                by[row["date_time"]].append(row)
    times = [datetime.fromisoformat(value) for value in sorted(by)]
    target, weather = [], []
    disagreements = 0
    for key in sorted(by):
        rows = by[key]
        values = np.array([float(row["traffic_volume"]) for row in rows])
        disagreements += int(np.ptp(values) > 0)
        target.append(float(values.mean()))
        weather.append([
            np.mean([float(row["temp"]) for row in rows]),
            np.mean([float(row["rain_1h"]) for row in rows]),
            np.mean([float(row["snow_1h"]) for row in rows]),
            np.mean([float(row["clouds_all"]) for row in rows]),
            float(any(row["holiday"] != "None" for row in rows)),
        ])
    if disagreements:
        raise ValueError("duplicate metro timestamps disagree on target")
    y = np.log1p(np.asarray(target, float))
    X = np.column_stack([np.asarray(weather, float), _calendar(times)])
    return TaskData("metro", np.array(times, dtype="datetime64[h]"), X, y, {
        "raw_rows": int(sum(map(len, by.values()))),
        "unique_timestamps": len(times), "duplicate_target_disagreements": disagreements,
    })


def _number(value: str) -> float:
    value = value.strip()
    return float(value) if value not in {"", "NA", "?"} else np.nan


def load_beijing() -> TaskData:
    path = archive_path("beijing")
    variables = ("PM2.5", "TEMP", "PRES", "DEWP", "RAIN", "WSPM")
    with zipfile.ZipFile(path) as outer:
        nested = zipfile.ZipFile(io.BytesIO(outer.read("PRSA2017_Data_20130301-20170228.zip")))
        files = sorted(name for name in nested.namelist() if name.endswith(".csv"))
        sites, common_times = [], None
        for name in files:
            rows = csv.DictReader(io.TextIOWrapper(nested.open(name), encoding="utf-8-sig"))
            times, values = [], []
            for row in rows:
                times.append(datetime(int(row["year"]), int(row["month"]),
                                      int(row["day"]), int(row["hour"])))
                values.append([_number(row[key]) for key in variables])
            if common_times is None:
                common_times = times
            elif times != common_times:
                raise ValueError("Beijing station timestamps are not synchronized")
            sites.append(np.asarray(values, float))
    panel = np.stack(sites)
    observed = np.isfinite(panel[:, :, 0]).sum(axis=0)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="All-NaN slice encountered")
        city = np.nanmedian(panel, axis=0)
    target = np.log1p(city[:, 0])
    extra = city[:, 1:]
    valid = (observed >= 8) & np.isfinite(target) & np.all(np.isfinite(extra), axis=1)
    idx, X, y = _lagged(target, common_times, (1, 24, 168), extra=extra, valid=valid)
    return TaskData("beijing", np.array(common_times, dtype="datetime64[h]")[idx], X, y, {
        "stations": len(files), "rows_per_station": len(common_times),
        "missing_pm25_cells": int(np.size(panel[:, :, 0]) - np.isfinite(panel[:, :, 0]).sum()),
        "hours_at_least_eight_sites": int((observed >= 8).sum()),
        "eligible_hours": int(idx.size),
    })


LOADERS = {"household": load_household, "metro": load_metro, "beijing": load_beijing}
