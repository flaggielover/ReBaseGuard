"""Frozen chronological ridge residual construction."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


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
    a = int(round(0.30 * n))
    b = a + int(round(0.20 * n))
    return slice(0, a), slice(a, b), slice(b, n)


def build(task_data, ridge_lambda: float = 1.0) -> ResidualStream:
    train, calibration, evaluation = split(task_data.y.size)
    Xtr, ytr = task_data.X[train], task_data.y[train]
    mean = Xtr.mean(axis=0)
    sd = Xtr.std(axis=0)
    sd = np.where(sd < 1e-12, 1.0, sd)
    Ztr = np.column_stack([np.ones(Xtr.shape[0]), (Xtr - mean) / sd])
    penalty = np.eye(Ztr.shape[1]) * ridge_lambda
    penalty[0, 0] = 0.0
    beta = np.linalg.solve(Ztr.T @ Ztr + penalty, Ztr.T @ ytr)
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
         "n_features": int(task_data.X.shape[1])},
        task_data.audit,
    )
