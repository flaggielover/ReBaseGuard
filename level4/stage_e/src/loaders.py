"""Stage E dataset loaders. Pure numpy: no pandas, no sklearn, no network at
evaluation time. Every loader is deterministic and returns data in strict
chronological order.

Raw files live in level4/stage_e/data/_cache/ (gitignored -- the datasets are
not redistributed here). Only checksums and manifests are committed.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np

CACHE = Path(__file__).resolve().parents[1] / "data" / "_cache"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass(frozen=True, slots=True)
class Stream:
    """A chronologically ordered supervised stream."""
    name: str
    X: np.ndarray            # (n, p) features, chronological
    y: np.ndarray            # (n,)   target
    feature_names: tuple[str, ...]
    target_name: str
    source_file: str
    source_sha256: str

    def __post_init__(self):
        if self.X.shape[0] != self.y.shape[0]:
            raise ValueError("X and y length mismatch")


# ----------------------------------------------------------------- Task A
def load_electricity() -> Stream:
    """Elec2 (OpenML id 151, 'electricity-normalized').

    Canonical concept-drift benchmark: half-hourly NSW electricity market,
    7 May 1996 - 5 Dec 1998, already in chronological order in the ARFF.
    Target: class UP/DOWN (price moved up relative to a moving average).
    """
    p = CACHE / "electricity-normalized.arff"
    names, rows, in_data = [], [], False
    for line in p.read_text().splitlines():
        s = line.strip()
        if not s:
            continue
        low = s.lower()
        if low.startswith("@attribute"):
            names.append(s.split()[1])
        elif low.startswith("@data"):
            in_data = True
        elif in_data:
            rows.append(s.split(","))
    arr = np.array(rows, dtype=object)
    cls = np.array([1.0 if v.strip().upper() == "UP" else 0.0
                    for v in arr[:, -1]])
    num = arr[:, :-1].astype(np.float64)
    # `date` is a normalised timestamp and is the ordering key, not a feature;
    # `day` is categorical and enters as cyclical sin/cos, not as a magnitude.
    day = num[:, 1]
    feats = np.column_stack([
        num[:, 2],                      # period (time of day, normalised)
        np.sin(2 * np.pi * day / 7.0),
        np.cos(2 * np.pi * day / 7.0),
        num[:, 3], num[:, 4], num[:, 5], num[:, 6], num[:, 7],
    ])
    fn = ("period", "day_sin", "day_cos", "nswprice", "nswdemand",
          "vicprice", "vicdemand", "transfer")
    # ORDERING. The `date` column of this ARFF is NOT globally monotone: it has
    # five backward jumps, every one of them at a day boundary where `period`
    # wraps 1.0 -> 0.0 (see notes/DATA_PROVENANCE.md). The authoritative order
    # is the FILE ROW ORDER -- Elec2 is a sequential half-hourly recording.
    # Sorting by `date` would scramble it. The integrity check below is on the
    # half-hourly period cycle, which is clean.
    per48 = np.rint(num[:, 2] * 47).astype(int)
    d = np.diff(per48)
    if not np.all((d == 1) | ((per48[:-1] == 47) & (per48[1:] == 0))):
        raise ValueError("electricity: period does not cycle 0..47 in row order")
    return Stream("electricity", feats, cls, fn, "class_UP",
                  p.name, sha256(p))


# ----------------------------------------------------------------- Task B
def load_air_quality() -> Stream:
    """UCI Air Quality (id 360): hourly metal-oxide sensor array, an Italian
    city, Mar 2004 - Apr 2005. Semicolon-separated, comma decimal separator,
    -200 codes missing. Documented sensor drift over the recording year.

    Target: true benzene concentration C6H6(GT) from a reference analyser.
    Features: the five PT08 metal-oxide sensor responses plus T/RH.
    """
    p = CACHE / "AirQualityUCI.csv"
    lines = [l for l in p.read_text(encoding="latin-1").splitlines() if l.strip()]
    head = [h.strip() for h in lines[0].split(";")]
    cols = {h: i for i, h in enumerate(head) if h}
    use = ("PT08.S1(CO)", "PT08.S2(NMHC)", "PT08.S3(NOx)", "PT08.S4(NO2)",
           "PT08.S5(O3)", "T", "RH")
    tgt = "C6H6(GT)"

    def num(tok: str) -> float:
        tok = tok.strip().replace(",", ".")
        return float(tok) if tok else np.nan

    X, y = [], []
    for line in lines[1:]:
        f = line.split(";")
        if len(f) < len(head):
            continue
        try:
            row = [num(f[cols[c]]) for c in use]
            t = num(f[cols[tgt]])
        except (ValueError, KeyError):
            continue
        # -200 is the dataset's missing code; drop incomplete hours. This rule
        # is fixed in the protocol and does not depend on any outcome.
        if any(np.isnan(v) or v <= -200 for v in row) or np.isnan(t) or t <= -200:
            continue
        X.append(row)
        y.append(t)
    return Stream("air_quality", np.array(X), np.array(y), use, tgt,
                  p.name, sha256(p))


# ----------------------------------------------------------------- Task C
def load_bike_sharing() -> Stream:
    """UCI Bike Sharing (id 275), hourly, 2011-2012, chronological.

    Production-style ML monitoring: a frozen demand model, monitored on its
    residuals. Target log1p(cnt); `casual`/`registered` are EXCLUDED because
    they sum to `cnt` and would leak the target.
    """
    p = CACHE / "hour.csv"
    lines = p.read_text().splitlines()
    head = lines[0].split(",")
    idx = {h: i for i, h in enumerate(head)}
    use = ("season", "yr", "mnth", "hr", "holiday", "weekday", "workingday",
           "weathersit", "temp", "atemp", "hum", "windspeed")
    X, y, inst = [], [], []
    for line in lines[1:]:
        f = line.split(",")
        if len(f) != len(head):
            continue
        X.append([float(f[idx[c]]) for c in use])
        y.append(np.log1p(float(f[idx["cnt"]])))
        inst.append(int(f[idx["instant"]]))
    X = np.array(X)
    inst = np.array(inst)
    if not np.all(np.diff(inst) > 0):
        raise ValueError("bike sharing rows are not chronological")
    hr = X[:, use.index("hr")]
    mn = X[:, use.index("mnth")]
    # hour and month are cyclical; encode as such rather than as magnitudes
    feats = np.column_stack([
        X[:, [use.index(c) for c in
              ("season", "yr", "holiday", "workingday", "weathersit",
               "temp", "atemp", "hum", "windspeed")]],
        np.sin(2 * np.pi * hr / 24), np.cos(2 * np.pi * hr / 24),
        np.sin(2 * np.pi * mn / 12), np.cos(2 * np.pi * mn / 12),
    ])
    fn = ("season", "yr", "holiday", "workingday", "weathersit", "temp",
          "atemp", "hum", "windspeed", "hr_sin", "hr_cos", "mnth_sin",
          "mnth_cos")
    return Stream("bike_sharing", feats, np.array(y), fn, "log1p_cnt",
                  p.name, sha256(p))


LOADERS = {"electricity": load_electricity,
           "air_quality": load_air_quality,
           "bike_sharing": load_bike_sharing}
