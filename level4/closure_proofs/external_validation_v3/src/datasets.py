"""Deterministic, outcome-blind preprocessing for the two frozen V3 tasks."""
from __future__ import annotations

import csv
import io
import math
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from xml.etree.ElementTree import iterparse

import numpy as np

from acquire import archive_path


@dataclass(frozen=True)
class TaskData:
    task: str
    timestamps: np.ndarray
    X: np.ndarray
    y: np.ndarray
    audit: dict


def _calendar(times: list[datetime]) -> np.ndarray:
    hour = np.asarray([value.hour + value.minute / 60 for value in times], float)
    weekday = np.asarray([value.weekday() + hour[i] / 24 for i, value in enumerate(times)], float)
    return np.column_stack([
        np.sin(2 * np.pi * hour / 24), np.cos(2 * np.pi * hour / 24),
        np.sin(2 * np.pi * weekday / 7), np.cos(2 * np.pi * weekday / 7),
    ])


def _lagged(task: str, target: np.ndarray, times: list[datetime],
            lags: tuple[int, ...], extra: np.ndarray | None = None) -> TaskData:
    maximum = max(lags)
    index = np.arange(maximum, target.size)
    pieces = [np.column_stack([target[index - lag] for lag in lags])]
    if extra is not None:
        pieces.append(extra[index])
    pieces.append(_calendar([times[i] for i in index]))
    return TaskData(task, np.asarray(times, dtype="datetime64[m]")[index],
                    np.column_stack(pieces), target[index], {})


def load_metropt() -> TaskData:
    names = (
        "TP2", "TP3", "H1", "DV_pressure", "Reservoirs", "Oil_temperature",
        "Motor_current", "COMP", "DV_eletric", "Towers", "MPG", "LPS",
        "Pressure_switch", "Oil_level", "Caudal_impulses",
    )
    sums: dict[datetime, np.ndarray] = {}
    counts: defaultdict[datetime, int] = defaultdict(int)
    raw_rows = malformed = 0
    with zipfile.ZipFile(archive_path("metropt")) as archive:
        with archive.open("MetroPT3(AirCompressor).csv") as packed:
            rows = csv.DictReader(io.TextIOWrapper(packed, encoding="utf-8"))
            for row in rows:
                raw_rows += 1
                try:
                    observed = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
                    stamp = observed.replace(minute=(observed.minute // 15) * 15,
                                             second=0, microsecond=0)
                    values = np.asarray([float(row[name]) for name in names])
                except (KeyError, TypeError, ValueError):
                    malformed += 1
                    continue
                if stamp not in sums:
                    sums[stamp] = np.zeros(len(names))
                sums[stamp] += values
                counts[stamp] += 1
    times = sorted(stamp for stamp in sums if counts[stamp] >= 72)
    values = np.asarray([sums[stamp] / counts[stamp] for stamp in times])
    gap = np.zeros(len(times))
    gap[1:] = [float(right - left != timedelta(minutes=15))
               for left, right in zip(times, times[1:])]
    target_index = names.index("Oil_temperature")
    target = values[:, target_index]
    extra = np.column_stack([values[:, [i for i in range(len(names)) if i != target_index]], gap])
    data = _lagged("metropt", target, times, (1, 2, 4, 8, 24, 96), extra)
    return TaskData(data.task, data.timestamps, data.X, data.y, {
        "raw_rows": raw_rows,
        "malformed_selected_rows": malformed,
        "eligible_15min_bins_before_lags": len(times),
        "eligible_after_lags": int(data.y.size),
        "minimum_raw_readings_per_bin": 72,
        "observation_time_gaps": int(gap.sum()),
        "coverage_start": times[0].isoformat(),
        "coverage_end": times[-1].isoformat(),
    })


def _cell_values(row, namespace: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for cell in row.findall(namespace + "c"):
        reference = cell.attrib.get("r", "")
        column = "".join(character for character in reference if character.isalpha())
        value = cell.find(namespace + "v")
        if value is not None and value.text is not None:
            values[column] = value.text
    return values


def load_retail() -> TaskData:
    namespace = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    hourly: defaultdict[int, float] = defaultdict(float)
    raw_rows = positive_rows = return_or_zero_rows = malformed = 0
    with zipfile.ZipFile(archive_path("retail")) as outer:
        workbook = zipfile.ZipFile(io.BytesIO(outer.read("online_retail_II.xlsx")))
        for sheet in ("xl/worksheets/sheet1.xml", "xl/worksheets/sheet2.xml"):
            with workbook.open(sheet) as source:
                for _, row in iterparse(source, events=("end",)):
                    if row.tag != namespace + "row":
                        continue
                    if row.attrib.get("r") == "1":
                        row.clear()
                        continue
                    raw_rows += 1
                    values = _cell_values(row, namespace)
                    try:
                        quantity = float(values["D"])
                        serial = float(values["E"])
                        price = float(values["F"])
                    except (KeyError, TypeError, ValueError):
                        malformed += 1
                        row.clear()
                        continue
                    if quantity > 0 and price >= 0:
                        hourly[int(math.floor(serial * 24))] += quantity
                        positive_rows += 1
                    else:
                        return_or_zero_rows += 1
                    row.clear()
    start, stop = min(hourly), max(hourly)
    hours = np.arange(start, stop + 1)
    demand = np.asarray([hourly.get(int(hour), 0.0) for hour in hours])
    epoch = datetime(1899, 12, 30)
    times = [epoch + timedelta(hours=int(hour)) for hour in hours]
    target = np.log1p(demand)
    data = _lagged("retail", target, times, (1, 2, 24, 168))
    return TaskData(data.task, data.timestamps.astype("datetime64[h]"), data.X, data.y, {
        "raw_rows": raw_rows,
        "positive_rows": positive_rows,
        "return_or_zero_rows": return_or_zero_rows,
        "malformed_selected_rows": malformed,
        "clock_hour_bins_before_lags": int(hours.size),
        "zero_demand_hours": int(np.sum(demand == 0)),
        "eligible_after_lags": int(data.y.size),
        "coverage_start": times[0].isoformat(),
        "coverage_end": times[-1].isoformat(),
    })


LOADERS = {"metropt": load_metropt, "retail": load_retail}
