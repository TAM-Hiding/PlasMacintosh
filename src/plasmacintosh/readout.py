"""Simple linear readout and fading-memory metrics."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class DelayScore:
    delay: int
    correlation_squared: float
    accuracy: float
    normalized_rmse: float
    train_samples: int
    test_samples: int


def _ridge_predict(
    train_features: np.ndarray,
    train_targets: np.ndarray,
    test_features: np.ndarray,
    ridge_alpha: float,
) -> np.ndarray:
    mean = train_features.mean(axis=0)
    scale = train_features.std(axis=0)
    scale[scale < 1e-12] = 1.0
    train_scaled = (train_features - mean) / scale
    test_scaled = (test_features - mean) / scale

    target_mean = float(train_targets.mean())
    centered_targets = train_targets - target_mean
    gram = train_scaled.T @ train_scaled
    regularized = gram + ridge_alpha * np.eye(gram.shape[0])
    try:
        weights = np.linalg.solve(regularized, train_scaled.T @ centered_targets)
    except np.linalg.LinAlgError:
        weights = np.linalg.lstsq(regularized, train_scaled.T @ centered_targets, rcond=None)[0]
    return test_scaled @ weights + target_mean


def _score(targets: np.ndarray, predictions: np.ndarray) -> tuple[float, float, float]:
    target_std = float(np.std(targets))
    prediction_std = float(np.std(predictions))
    if target_std < 1e-12 or prediction_std < 1e-12:
        correlation_squared = 0.0
    else:
        correlation = float(np.corrcoef(targets, predictions)[0, 1])
        correlation_squared = correlation * correlation
    accuracy = float(np.mean((predictions >= 0.5) == (targets >= 0.5)))
    rmse = float(np.sqrt(np.mean((predictions - targets) ** 2)))
    normalized_rmse = rmse / target_std if target_std >= 1e-12 else float("inf")
    return correlation_squared, accuracy, normalized_rmse


def memory_curve(
    observables: np.ndarray,
    input_values: np.ndarray,
    *,
    max_delay: int,
    washout: int,
    train_fraction: float,
    ridge_alpha: float,
    shuffle_seed: int | None = None,
) -> list[DelayScore]:
    """Measure how well current observables reconstruct past input values.

    All delays use exactly the same current-time rows. When ``shuffle_seed`` is
    supplied, observable rows are shuffled independently inside the training and
    testing partitions, preserving the chronological boundary while destroying
    input/state alignment.
    """

    observables = np.asarray(observables, dtype=np.float64)
    input_values = np.asarray(input_values, dtype=np.float64)
    if observables.ndim != 2 or observables.shape[0] != len(input_values):
        raise ValueError("observables and input_values have incompatible shapes")
    if max_delay < 0 or washout < 0:
        raise ValueError("max_delay and washout must be non-negative")
    if not 0 < train_fraction < 1:
        raise ValueError("train_fraction must be in (0, 1)")

    current_times = np.arange(washout + max_delay, len(input_values))
    if len(current_times) < 20:
        raise ValueError("not enough samples after washout and delay allowance")
    split = int(len(current_times) * train_fraction)
    if split < 10 or len(current_times) - split < 10:
        raise ValueError("training and test partitions must each contain ten samples")

    features = observables[current_times].copy()
    if shuffle_seed is not None:
        rng = np.random.default_rng(shuffle_seed)
        features[:split] = features[rng.permutation(split)]
        test_permutation = rng.permutation(len(features) - split) + split
        features[split:] = features[test_permutation]

    train_features = features[:split]
    test_features = features[split:]
    scores: list[DelayScore] = []
    for delay in range(max_delay + 1):
        targets = input_values[current_times - delay]
        train_targets = targets[:split]
        test_targets = targets[split:]
        predictions = _ridge_predict(
            train_features,
            train_targets,
            test_features,
            ridge_alpha,
        )
        correlation_squared, accuracy, normalized_rmse = _score(test_targets, predictions)
        scores.append(
            DelayScore(
                delay=delay,
                correlation_squared=correlation_squared,
                accuracy=accuracy,
                normalized_rmse=normalized_rmse,
                train_samples=split,
                test_samples=len(current_times) - split,
            )
        )
    return scores
