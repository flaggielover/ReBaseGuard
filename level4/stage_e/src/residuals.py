"""Frozen predictive models and the scalar monitoring streams they produce.

Chronological discipline (Stage E protocol S13):

    [ reference / train 30% ] -> [ calibration 20% ] -> [ evaluation 50% ]

The model and every scaling constant are fitted on the REFERENCE block only.
The detector threshold is fitted on the CALIBRATION block only. Nothing is ever
fitted on the evaluation stream, and no model is refitted after any monitoring
outcome is seen.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

TRAIN_FRAC = 0.30
CALIB_FRAC = 0.20


@dataclass(frozen=True, slots=True)
class Split:
    train: slice
    calib: slice
    eval: slice
    n: int


def chronological_split(n: int, train_frac: float = TRAIN_FRAC,
                        calib_frac: float = CALIB_FRAC) -> Split:
    a = int(round(n * train_frac))
    b = a + int(round(n * calib_frac))
    return Split(slice(0, a), slice(a, b), slice(b, n), n)


def _standardise(Xtr: np.ndarray):
    mu = Xtr.mean(axis=0)
    sd = Xtr.std(axis=0)
    sd = np.where(sd < 1e-12, 1.0, sd)          # constant columns pass through
    return mu, sd


def fit_ridge(X: np.ndarray, y: np.ndarray, lam: float = 1.0):
    """Closed-form ridge on standardised features; the intercept is unpenalised."""
    mu, sd = _standardise(X)
    Z = (X - mu) / sd
    Z1 = np.column_stack([np.ones(Z.shape[0]), Z])
    P = np.eye(Z1.shape[1]) * lam
    P[0, 0] = 0.0
    beta = np.linalg.solve(Z1.T @ Z1 + P, Z1.T @ y)
    return {"kind": "ridge", "mu": mu, "sd": sd, "beta": beta, "lam": lam}


def fit_logistic(X: np.ndarray, y: np.ndarray, lam: float = 1.0,
                 n_iter: int = 50, tol: float = 1e-10):
    """L2-penalised logistic regression by IRLS. Deterministic; no RNG."""
    mu, sd = _standardise(X)
    Z = np.column_stack([np.ones(X.shape[0]), (X - mu) / sd])
    beta = np.zeros(Z.shape[1])
    P = np.eye(Z.shape[1]) * lam
    P[0, 0] = 0.0
    for _ in range(n_iter):
        eta = Z @ beta
        p = 1.0 / (1.0 + np.exp(-np.clip(eta, -35, 35)))
        w = np.maximum(p * (1 - p), 1e-8)
        g = Z.T @ (y - p) - P @ beta
        H = Z.T @ (Z * w[:, None]) + P
        step = np.linalg.solve(H, g)
        beta = beta + step
        if np.max(np.abs(step)) < tol:
            break
    return {"kind": "logistic", "mu": mu, "sd": sd, "beta": beta, "lam": lam}


def predict(model, X: np.ndarray) -> np.ndarray:
    Z = np.column_stack([np.ones(X.shape[0]), (X - model["mu"]) / model["sd"]])
    eta = Z @ model["beta"]
    if model["kind"] == "logistic":
        return 1.0 / (1.0 + np.exp(-np.clip(eta, -35, 35)))
    return eta


@dataclass(frozen=True, slots=True)
class MonitorStream:
    """The scalar stream the detector sees, plus its frozen constants."""
    task: str
    residual: np.ndarray      # full-length residual, chronological
    split: Split
    scale: float              # residual SD from the REFERENCE block only
    model_kind: str
    n_features: int

    @property
    def calib(self) -> np.ndarray:
        return self.residual[self.split.calib]

    @property
    def evaluation(self) -> np.ndarray:
        return self.residual[self.split.eval]


MODEL_SPEC = {
    "electricity": ("logistic", 1.0),
    "air_quality": ("ridge", 1.0),
    "bike_sharing": ("ridge", 1.0),
}


def build_stream(stream) -> MonitorStream:
    """Fit the frozen model on the reference block; residualise everything."""
    sp = chronological_split(stream.X.shape[0])
    kind, lam = MODEL_SPEC[stream.name]
    Xtr, ytr = stream.X[sp.train], stream.y[sp.train]
    model = (fit_logistic(Xtr, ytr, lam) if kind == "logistic"
             else fit_ridge(Xtr, ytr, lam))
    resid = stream.y - predict(model, stream.X)
    scale = float(resid[sp.train].std())        # reference block ONLY
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError(f"{stream.name}: degenerate residual scale")
    return MonitorStream(stream.name, resid, sp, scale, kind,
                         stream.X.shape[1])


# ------------------------------------------------------------- diagnostics
def acf(x: np.ndarray, lags: int = 10) -> np.ndarray:
    x = x - x.mean()
    d = float(x @ x)
    return np.array([1.0 if k == 0 else float(x[:-k] @ x[k:]) / d
                     for k in range(lags + 1)])


def describe(x: np.ndarray) -> dict:
    x = np.asarray(x, dtype=float)
    n = x.size
    m, s = float(x.mean()), float(x.std())
    z = (x - m) / s
    a = acf(x, 10)
    # variance stability: ratio of second-half to first-half variance
    h = n // 2
    return {
        "n": int(n), "mean": m, "sd": s,
        "skew": float((z ** 3).mean()), "excess_kurtosis": float((z ** 4).mean() - 3.0),
        "q01": float(np.quantile(x, 0.01)), "q99": float(np.quantile(x, 0.99)),
        "frac_beyond_3sd": float(np.mean(np.abs(z) > 3)),
        "acf1": float(a[1]), "acf2": float(a[2]), "acf5": float(a[5]),
        "acf10": float(a[10]),
        "acf_sum_1_10": float(a[1:11].sum()),
        "variance_ratio_2nd_half_over_1st": float(x[h:].var() / x[:h].var()),
    }
