"""Frozen chronological ridge residual construction."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from config import PROTOCOL


@dataclass(frozen=True)
class ResidualStream:
    task: str
    timestamps: np.ndarray
    residual: np.ndarray
    train: slice
    calibration: slice
    evaluation: slice
    scale: float
    model: dict
    dataset_audit: dict


def split(n: int) -> tuple[slice, slice, slice]:
    fractions = PROTOCOL["splits"]
    first = int(round(fractions["train"] * n))
    second = first + int(round(fractions["calibration"] * n))
    return slice(0, first), slice(first, second), slice(second, n)


def build(task_data, ridge_lambda: float = 1.0) -> ResidualStream:
    train, calibration, evaluation = split(task_data.y.size)
    X_train, y_train = task_data.X[train], task_data.y[train]
    mean = X_train.mean(axis=0)
    sd = X_train.std(axis=0)
    sd = np.where(sd < 1e-12, 1.0, sd)
    Z_train = np.column_stack([np.ones(X_train.shape[0]), (X_train - mean) / sd])
    penalty = np.eye(Z_train.shape[1]) * ridge_lambda
    penalty[0, 0] = 0.0
    beta = np.linalg.solve(Z_train.T @ Z_train + penalty, Z_train.T @ y_train)
    Z = np.column_stack([np.ones(task_data.X.shape[0]), (task_data.X - mean) / sd])
    residual = task_data.y - Z @ beta
    scale = float(residual[train].std())
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError(f"{task_data.task}: degenerate train residual scale")
    return ResidualStream(
        task_data.task, task_data.timestamps, residual, train, calibration,
        evaluation, scale,
        {"kind": "ridge", "lambda": ridge_lambda, "feature_mean": mean.tolist(),
         "feature_sd": sd.tolist(), "beta": beta.tolist(),
         "n_features": int(task_data.X.shape[1]), "fit_source": "train only"},
        task_data.audit,
    )
