"""End-to-end P1 fading-memory experiment."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .readout import DelayScore, memory_curve
from .sources import FakeGasConfig, generate_binary_input, make_fake_gas, make_no_gas


@dataclass(frozen=True)
class ExperimentConfig:
    sample_count: int = 6000
    sample_period_s: float = 1.0
    sequence_seed: int = 20260916
    max_delay: int = 30
    washout: int = 200
    train_fraction: float = 0.60
    ridge_alpha: float = 1e-4
    fake_gas: FakeGasConfig = FakeGasConfig()

    def validate(self) -> None:
        minimum = self.washout + self.max_delay + 20
        if self.sample_count < minimum:
            raise ValueError(f"sample_count must be at least {minimum}")
        if self.sample_period_s <= 0:
            raise ValueError("sample_period_s must be positive")
        self.fake_gas.validate()


def _write_curve_csv(path: Path, curves: dict[str, list[DelayScore]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "source",
                "delay_steps",
                "correlation_squared",
                "accuracy",
                "normalized_rmse",
                "train_samples",
                "test_samples",
            ]
        )
        for source, scores in curves.items():
            for score in scores:
                writer.writerow(
                    [
                        source,
                        score.delay,
                        f"{score.correlation_squared:.12g}",
                        f"{score.accuracy:.12g}",
                        f"{score.normalized_rmse:.12g}",
                        score.train_samples,
                        score.test_samples,
                    ]
                )


def _plot_curves(path: Path, curves: dict[str, list[DelayScore]]) -> None:
    colors = {"NO_GAS": "#777777", "FAKE_GAS": "#e4572e", "SHUFFLED": "#4c78a8"}
    figure, axes = plt.subplots(2, 1, figsize=(9, 8), sharex=True)
    for source, scores in curves.items():
        delays = [score.delay for score in scores]
        axes[0].plot(
            delays,
            [score.correlation_squared for score in scores],
            marker="o",
            markersize=3,
            linewidth=1.7,
            label=source.replace("_", " "),
            color=colors[source],
        )
        axes[1].plot(
            delays,
            [score.accuracy for score in scores],
            marker="o",
            markersize=3,
            linewidth=1.7,
            label=source.replace("_", " "),
            color=colors[source],
        )

    axes[0].set_ylabel("Squared correlation")
    axes[0].set_ylim(-0.02, 1.02)
    axes[0].grid(alpha=0.25)
    axes[0].legend()
    axes[0].set_title("PlasMacintosh P1 — delayed input reconstruction")
    axes[1].axhline(0.5, color="black", linestyle="--", linewidth=1, label="chance")
    axes[1].set_xlabel("Delay (input steps ago)")
    axes[1].set_ylabel("Binary accuracy")
    axes[1].set_ylim(0.4, 1.02)
    axes[1].grid(alpha=0.25)
    axes[1].legend()
    figure.tight_layout()
    figure.savefig(path, dpi=180)
    plt.close(figure)


def run_experiment(
    config: ExperimentConfig,
    *,
    output_directory: str | Path,
    data_directory: str | Path,
) -> dict[str, object]:
    """Run and persist the complete NO GAS / FAKE GAS P1 experiment."""

    config.validate()
    output_path = Path(output_directory)
    data_path = Path(data_directory)
    output_path.mkdir(parents=True, exist_ok=True)
    data_path.mkdir(parents=True, exist_ok=True)

    inputs = generate_binary_input(config.sample_count, config.sequence_seed)
    no_gas = make_no_gas(
        inputs,
        sample_period_s=config.sample_period_s,
        sequence_seed=config.sequence_seed,
    )
    fake_gas = make_fake_gas(
        inputs,
        config=config.fake_gas,
        sample_period_s=config.sample_period_s,
        sequence_seed=config.sequence_seed,
    )
    no_gas.save(data_path / "no_gas")
    fake_gas.save(data_path / "fake_gas")

    analysis_options = {
        "max_delay": config.max_delay,
        "washout": config.washout,
        "train_fraction": config.train_fraction,
        "ridge_alpha": config.ridge_alpha,
    }
    curves = {
        "NO_GAS": memory_curve(no_gas.observables, inputs, **analysis_options),
        "FAKE_GAS": memory_curve(fake_gas.observables, inputs, **analysis_options),
        "SHUFFLED": memory_curve(
            fake_gas.observables,
            inputs,
            shuffle_seed=config.sequence_seed + 1,
            **analysis_options,
        ),
    }

    _write_curve_csv(output_path / "memory_curve.csv", curves)
    _plot_curves(output_path / "memory_curve.png", curves)

    summary: dict[str, object] = {
        "experiment": "P1_fading_memory",
        "config": {
            **asdict(config),
            "fake_gas": asdict(config.fake_gas),
        },
        "sources": {},
    }
    for source, scores in curves.items():
        summary["sources"][source] = {
            "delay_0_correlation_squared": scores[0].correlation_squared,
            "delay_1_correlation_squared": scores[1].correlation_squared,
            "total_memory_score": float(
                np.sum([score.correlation_squared for score in scores])
            ),
            "last_delay_above_half_correlation": max(
                (score.delay for score in scores if score.correlation_squared >= 0.5),
                default=None,
            ),
        }
    (output_path / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary
