"""Reference reservoir sources for P1 pipeline validation."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from .dataset import ExperimentDataset


def generate_binary_input(sample_count: int, seed: int) -> np.ndarray:
    """Return a reproducible independent binary sequence."""

    if sample_count < 2:
        raise ValueError("sample_count must be at least two")
    rng = np.random.default_rng(seed)
    return rng.integers(0, 2, size=sample_count, dtype=np.int8).astype(np.float64)


def _base_dataset(
    input_values: np.ndarray,
    observables: np.ndarray,
    observable_names: list[str],
    source_id: str,
    sample_period_s: float,
    sequence_seed: int,
    source_parameters: dict[str, object],
) -> ExperimentDataset:
    input_values = np.asarray(input_values, dtype=np.float64)
    if sample_period_s <= 0:
        raise ValueError("sample_period_s must be positive")
    dataset = ExperimentDataset(
        sample_index=np.arange(len(input_values), dtype=np.int64),
        time_s=np.arange(len(input_values), dtype=np.float64) * sample_period_s,
        input_value=input_values,
        observables=observables,
        observable_names=observable_names,
        metadata={
            "source_id": source_id,
            "sample_period_s": sample_period_s,
            "sequence_id": f"binary-pcg64-seed-{sequence_seed}",
            "input_encoding": {"low": 0.0, "high": 1.0},
            "source_parameters": source_parameters,
        },
    )
    dataset.validate()
    return dataset


def make_no_gas(
    input_values: np.ndarray,
    *,
    sample_period_s: float = 1.0,
    sequence_seed: int = 0,
) -> ExperimentDataset:
    """Direct-input control with no state and therefore no temporal memory."""

    input_values = np.asarray(input_values, dtype=np.float64)
    return _base_dataset(
        input_values=input_values,
        observables=input_values[:, None],
        observable_names=["direct_input"],
        source_id="NO_GAS",
        sample_period_s=sample_period_s,
        sequence_seed=sequence_seed,
        source_parameters={},
    )


@dataclass(frozen=True)
class FakeGasConfig:
    node_count: int = 64
    spectral_radius: float = 0.92
    input_scale: float = 0.8
    bias_scale: float = 0.15
    leak_rate: float = 0.35
    connection_density: float = 0.15
    reservoir_seed: int = 1701

    def validate(self) -> None:
        if self.node_count < 2:
            raise ValueError("node_count must be at least two")
        if not 0 < self.spectral_radius < 1.5:
            raise ValueError("spectral_radius must be between zero and 1.5")
        if not 0 < self.leak_rate <= 1:
            raise ValueError("leak_rate must be in (0, 1]")
        if not 0 < self.connection_density <= 1:
            raise ValueError("connection_density must be in (0, 1]")


def make_fake_gas(
    input_values: np.ndarray,
    *,
    config: FakeGasConfig | None = None,
    sample_period_s: float = 1.0,
    sequence_seed: int = 0,
) -> ExperimentDataset:
    """Create a deterministic echo-state reservoir with fading memory.

    This is a pipeline calibration source, not a plasma-physics simulation.
    """

    config = config or FakeGasConfig()
    config.validate()
    input_values = np.asarray(input_values, dtype=np.float64)
    rng = np.random.default_rng(config.reservoir_seed)

    input_weights = rng.uniform(-1.0, 1.0, size=config.node_count) * config.input_scale
    bias = rng.uniform(-1.0, 1.0, size=config.node_count) * config.bias_scale
    recurrent = rng.normal(0.0, 1.0, size=(config.node_count, config.node_count))
    mask = rng.random(recurrent.shape) < config.connection_density
    # Sparse random graphs can occasionally contain no recurrent cycle,
    # especially in small test reservoirs. Self-connections guarantee that the
    # calibration source actually has state while retaining sparse coupling.
    np.fill_diagonal(mask, True)
    recurrent *= mask

    eigenvalues = np.linalg.eigvals(recurrent)
    observed_radius = float(np.max(np.abs(eigenvalues)))
    if observed_radius == 0:
        raise RuntimeError("generated reservoir has zero spectral radius")
    recurrent *= config.spectral_radius / observed_radius

    states = np.empty((len(input_values), config.node_count), dtype=np.float64)
    state = np.zeros(config.node_count, dtype=np.float64)
    signed_input = input_values * 2.0 - 1.0
    for index, value in enumerate(signed_input):
        candidate = np.tanh(input_weights * value + recurrent @ state + bias)
        state = (1.0 - config.leak_rate) * state + config.leak_rate * candidate
        states[index] = state

    return _base_dataset(
        input_values=input_values,
        observables=states,
        observable_names=[f"fake_node_{index:03d}" for index in range(config.node_count)],
        source_id="FAKE_GAS",
        sample_period_s=sample_period_s,
        sequence_seed=sequence_seed,
        source_parameters=asdict(config),
    )
