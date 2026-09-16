"""Standardized observable dataset used by simulated and physical reservoirs."""

from __future__ import annotations

from dataclasses import dataclass, field
import csv
import json
from pathlib import Path
from typing import Any

import numpy as np


DATASET_SCHEMA = "plasmacintosh.dataset.v0.1"


@dataclass
class ExperimentDataset:
    """One synchronized input/observable recording.

    Rows are temporal samples. Observables are the state exposed to the readout;
    they may be simulated nodes, photodiodes, current, voltage, or any future
    synchronized measurement channel.
    """

    sample_index: np.ndarray
    time_s: np.ndarray
    input_value: np.ndarray
    observables: np.ndarray
    observable_names: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        self.sample_index = np.asarray(self.sample_index, dtype=np.int64)
        self.time_s = np.asarray(self.time_s, dtype=np.float64)
        self.input_value = np.asarray(self.input_value, dtype=np.float64)
        self.observables = np.asarray(self.observables, dtype=np.float64)

        if self.observables.ndim != 2:
            raise ValueError("observables must be a two-dimensional array")
        row_count = len(self.sample_index)
        if row_count == 0:
            raise ValueError("dataset must contain at least one sample")
        if len(self.time_s) != row_count or len(self.input_value) != row_count:
            raise ValueError("sample_index, time_s, and input_value lengths differ")
        if self.observables.shape[0] != row_count:
            raise ValueError("observable row count does not match sample count")
        if self.observables.shape[1] != len(self.observable_names):
            raise ValueError("observable_names does not match observable columns")
        if len(set(self.observable_names)) != len(self.observable_names):
            raise ValueError("observable names must be unique")
        if not np.array_equal(self.sample_index, np.arange(row_count)):
            raise ValueError("sample_index must be contiguous and start at zero")
        if np.any(np.diff(self.time_s) <= 0):
            raise ValueError("time_s must be strictly increasing")
        if not np.all(np.isfinite(self.input_value)):
            raise ValueError("input_value contains non-finite values")
        if not np.all(np.isfinite(self.observables)):
            raise ValueError("observables contain non-finite values")

    def save(self, directory: str | Path) -> Path:
        """Write a human-readable samples CSV and metadata JSON."""

        self.validate()
        destination = Path(directory)
        destination.mkdir(parents=True, exist_ok=True)

        samples_path = destination / "samples.csv"
        header = ["sample_index", "time_s", "input_value", *self.observable_names]
        with samples_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(header)
            for index in range(len(self.sample_index)):
                writer.writerow(
                    [
                        int(self.sample_index[index]),
                        f"{self.time_s[index]:.12g}",
                        f"{self.input_value[index]:.12g}",
                        *(f"{value:.12g}" for value in self.observables[index]),
                    ]
                )

        metadata = dict(self.metadata)
        metadata.update(
            {
                "schema": DATASET_SCHEMA,
                "sample_count": len(self.sample_index),
                "observable_count": len(self.observable_names),
                "observable_names": self.observable_names,
                "files": {"samples": "samples.csv"},
            }
        )
        (destination / "metadata.json").write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return destination

    @classmethod
    def load(cls, directory: str | Path) -> "ExperimentDataset":
        source = Path(directory)
        metadata = json.loads((source / "metadata.json").read_text(encoding="utf-8"))
        if metadata.get("schema") != DATASET_SCHEMA:
            raise ValueError(f"unsupported dataset schema: {metadata.get('schema')!r}")

        with (source / metadata["files"]["samples"]).open(
            newline="", encoding="utf-8"
        ) as handle:
            reader = csv.reader(handle)
            header = next(reader)
            rows = list(reader)

        expected_header = [
            "sample_index",
            "time_s",
            "input_value",
            *metadata["observable_names"],
        ]
        if header != expected_header:
            raise ValueError("samples.csv header disagrees with metadata")

        values = np.asarray(rows, dtype=np.float64)
        dataset = cls(
            sample_index=values[:, 0].astype(np.int64),
            time_s=values[:, 1],
            input_value=values[:, 2],
            observables=values[:, 3:],
            observable_names=list(metadata["observable_names"]),
            metadata={
                key: value
                for key, value in metadata.items()
                if key
                not in {"schema", "sample_count", "observable_count", "observable_names", "files"}
            },
        )
        dataset.validate()
        return dataset
