"""Command-line entry point for the P1 experiment."""

from __future__ import annotations

import argparse
from pathlib import Path

from .experiment import ExperimentConfig, run_experiment
from .sources import FakeGasConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the PlasMacintosh P1 fading-memory calibration experiment."
    )
    parser.add_argument("--samples", type=int, default=6000, help="number of input steps")
    parser.add_argument("--nodes", type=int, default=64, help="FAKE GAS node count")
    parser.add_argument("--max-delay", type=int, default=30, help="largest tested delay")
    parser.add_argument("--washout", type=int, default=200, help="discarded settling steps")
    parser.add_argument("--seed", type=int, default=20260916, help="input sequence seed")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/p1_memory"),
        help="metrics and plot directory",
    )
    parser.add_argument(
        "--data-directory",
        type=Path,
        default=Path("data/generated/p1_memory"),
        help="generated standardized datasets",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = ExperimentConfig(
        sample_count=args.samples,
        sequence_seed=args.seed,
        max_delay=args.max_delay,
        washout=args.washout,
        fake_gas=FakeGasConfig(node_count=args.nodes),
    )
    summary = run_experiment(
        config,
        output_directory=args.output,
        data_directory=args.data_directory,
    )
    print("PlasMacintosh P1 complete")
    print(f"  plot: {args.output / 'memory_curve.png'}")
    print(f"  metrics: {args.output / 'memory_curve.csv'}")
    for source, values in summary["sources"].items():
        print(
            f"  {source:8s} memory score={values['total_memory_score']:.3f} "
            f"delay-1 R^2={values['delay_1_correlation_squared']:.3f}"
        )


if __name__ == "__main__":
    main()
