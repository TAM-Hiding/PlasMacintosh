# PlasMacintosh

PlasMacintosh asks whether the nonlinear, history-dependent dynamics of a
low-pressure glow-discharge plasma can act as a useful physical reservoir for
temporal information processing.

The first software milestone is deliberately hardware-free. It runs the same
P1 fading-memory experiment against:

- **NO GAS** — the instantaneous input with no memory.
- **FAKE GAS** — a deterministic echo-state reservoir with known fading memory.
- **SHUFFLED** — FAKE GAS observations shuffled within the train and test
  partitions to expose timing leakage.

See [Overview.md](Overview.md) for the project definition and
[Work_Session_Handoff.md](Work_Session_Handoff.md) for current status.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
python3 -m plasmacintosh
```

The command writes generated datasets beneath `data/generated/` and the memory
curve, metrics, plot, and run summary beneath `results/p1_memory/`. These
generated artifacts are intentionally excluded from Git.

Useful options:

```bash
python3 -m plasmacintosh --samples 8000 --nodes 96 --max-delay 40 --seed 20260916
python3 -m plasmacintosh --help
```

Run the tests with:

```bash
python3 -m unittest discover -s tests -v
```

## Dataset contract v0.1

Every reservoir run is a directory containing:

- `samples.csv` — `sample_index`, `time_s`, `input_value`, then one or more
  named observable channels.
- `metadata.json` — schema version, source identity, channel names, timing,
  input encoding, sequence identity, and source parameters.

The analysis code does not need to know whether the observables came from a
simulation or physical acquisition hardware. Future GAS hardware only needs to
produce the same contract.
