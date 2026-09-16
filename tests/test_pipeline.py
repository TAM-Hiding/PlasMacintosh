from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from plasmacintosh.dataset import ExperimentDataset
from plasmacintosh.experiment import ExperimentConfig, run_experiment
from plasmacintosh.readout import memory_curve
from plasmacintosh.sources import (
    FakeGasConfig,
    generate_binary_input,
    make_fake_gas,
    make_no_gas,
)


class SourceTests(unittest.TestCase):
    def test_binary_input_is_reproducible(self) -> None:
        first = generate_binary_input(100, seed=42)
        second = generate_binary_input(100, seed=42)
        different = generate_binary_input(100, seed=43)
        np.testing.assert_array_equal(first, second)
        self.assertFalse(np.array_equal(first, different))
        self.assertEqual(set(first), {0.0, 1.0})

    def test_no_gas_exposes_only_present_input(self) -> None:
        inputs = generate_binary_input(100, seed=1)
        dataset = make_no_gas(inputs, sequence_seed=1)
        np.testing.assert_array_equal(dataset.observables[:, 0], inputs)
        self.assertEqual(dataset.observable_names, ["direct_input"])

    def test_fake_gas_is_deterministic(self) -> None:
        inputs = generate_binary_input(100, seed=2)
        config = FakeGasConfig(node_count=12, reservoir_seed=3)
        first = make_fake_gas(inputs, config=config, sequence_seed=2)
        second = make_fake_gas(inputs, config=config, sequence_seed=2)
        np.testing.assert_allclose(first.observables, second.observables)
        self.assertEqual(first.observables.shape, (100, 12))


class DatasetTests(unittest.TestCase):
    def test_csv_json_round_trip(self) -> None:
        inputs = generate_binary_input(80, seed=11)
        original = make_fake_gas(
            inputs,
            config=FakeGasConfig(node_count=8),
            sequence_seed=11,
        )
        with tempfile.TemporaryDirectory() as temporary:
            original.save(temporary)
            loaded = ExperimentDataset.load(temporary)
        np.testing.assert_array_equal(original.sample_index, loaded.sample_index)
        np.testing.assert_allclose(original.time_s, loaded.time_s)
        np.testing.assert_allclose(original.input_value, loaded.input_value)
        np.testing.assert_allclose(original.observables, loaded.observables, atol=1e-11)
        self.assertEqual(original.observable_names, loaded.observable_names)


class AnalysisTests(unittest.TestCase):
    def test_controls_and_fake_gas_have_expected_memory(self) -> None:
        inputs = generate_binary_input(3500, seed=2026)
        no_gas = make_no_gas(inputs, sequence_seed=2026)
        fake_gas = make_fake_gas(
            inputs,
            config=FakeGasConfig(node_count=48, reservoir_seed=7),
            sequence_seed=2026,
        )
        options = dict(
            max_delay=12,
            washout=150,
            train_fraction=0.6,
            ridge_alpha=1e-4,
        )
        no_gas_curve = memory_curve(no_gas.observables, inputs, **options)
        fake_curve = memory_curve(fake_gas.observables, inputs, **options)
        shuffled_curve = memory_curve(
            fake_gas.observables,
            inputs,
            shuffle_seed=99,
            **options,
        )

        self.assertGreater(no_gas_curve[0].correlation_squared, 0.99)
        self.assertLess(max(score.correlation_squared for score in no_gas_curve[1:]), 0.03)
        self.assertGreater(fake_curve[1].correlation_squared, 0.75)
        self.assertGreater(
            sum(score.correlation_squared for score in fake_curve[1:6]),
            2.0,
        )
        self.assertLess(
            max(score.correlation_squared for score in shuffled_curve),
            0.05,
        )

    def test_end_to_end_writes_expected_artifacts(self) -> None:
        config = ExperimentConfig(
            sample_count=700,
            max_delay=8,
            washout=50,
            fake_gas=FakeGasConfig(node_count=16),
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            summary = run_experiment(
                config,
                output_directory=root / "results",
                data_directory=root / "data",
            )
            self.assertTrue((root / "results/memory_curve.csv").is_file())
            self.assertTrue((root / "results/memory_curve.png").is_file())
            self.assertTrue((root / "results/summary.json").is_file())
            self.assertTrue((root / "data/no_gas/samples.csv").is_file())
            self.assertTrue((root / "data/fake_gas/metadata.json").is_file())
            self.assertIn("FAKE_GAS", summary["sources"])


if __name__ == "__main__":
    unittest.main()
