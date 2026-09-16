# PlasMacintosh — Work Session Handoff

## Start Here

Read `Overview.md` first. It contains the project definition, experimental philosophy, roadmap, controls, and longer-term apparatus concepts.

This project is an experimental investigation of low-pressure glow-discharge plasma as a physical reservoir for reservoir computing.

The immediate objective is **not** to design the eventual elaborate plasma chamber.

The immediate objective is to design and implement **P0/P1**. The first
software calibration slice is now complete:

1. Generate standardized temporal input data.
2. Build a simulated reservoir so the analysis pipeline can be developed without hardware.
3. Define a standardized experimental dataset format.
4. Implement a direct-input baseline/control.
5. Implement strict train/test separation.
6. Implement a simple linear readout.
7. Implement the first fading-memory benchmark.
8. Produce plots showing reconstruction performance versus temporal delay.
9. Begin defining the physical P0 acquisition architecture.

## Current Repository

GitHub repository:

`https://github.com/TAM-Hiding/PlasMacintosh`

Current project-definition files:

`Overview.md` — project definition and roadmap

`Work_Session_Handoff.md` — current handoff/status

Current implemented structure:

`README.md` — setup, commands, and dataset contract

`src/plasmacintosh/` — sources, dataset interface, readout, experiment, and CLI

`tests/` — deterministic unit and end-to-end tests

`data/generated/` — generated datasets; excluded from Git

`results/` — generated metrics and plots; excluded from Git

Planned expansion areas:

`docs/` — apparatus notes, literature notes, experimental protocols

`src/` — analysis/acquisition software

`sim/` — simulated reservoirs

`data/` — experimental datasets; do not casually commit large raw datasets to Git

`experiments/` — individual experiment definitions/results

`hardware/` — schematics, CAD notes, BOMs

## Engineering Philosophy

Keep early experiments deliberately simple.

Change one variable at a time.

Define expected measurements, controls, success criteria, and falsification criteria before interpreting results.

Do not interpret visually interesting plasma behavior as computation without benchmark evidence.

Do not claim novelty until a dedicated literature/prior-art search supports that claim.

Maintain the ability to run the same analysis against:

**FAKE GAS** — simulated reservoir

**NO GAS** — direct/electronics control

**GAS** — physical plasma reservoir

## Completed Software Calibration — v0.1

The first **data format and simulated P1 memory experiment** is implemented.

The pipeline now performs:

Generate a repeatable pseudorandom binary input sequence → pass it through a simple simulated nonlinear dynamical reservoir → train a linear readout → test on unseen data → attempt reconstruction at multiple delays → graph memory performance versus delay.

The standardized dataset interface is frozen as
`plasmacintosh.dataset.v0.1`: a human-readable `samples.csv` plus
`metadata.json`. Each row contains sample index, elapsed time, commanded input,
and named observable channels.

Implemented sources and controls:

**NO GAS** — direct current input only; no state

**FAKE GAS** — deterministic echo-state reservoir; calibration source, not a
plasma-physics simulation

**SHUFFLED** — FAKE GAS observations shuffled independently within the train
and test partitions

Default calibration run (`6000` samples, `64` nodes, delays `0–30`) produced:

* NO GAS: delay-1 squared correlation `0.000`; total score `1.011`
* FAKE GAS: delay-1 squared correlation `0.947`; total score `7.884`
* SHUFFLED: delay-1 squared correlation `0.002`; total score `0.015`

All six deterministic, dataset, control, and end-to-end tests pass.

These are software calibration results only. They make no claim about plasma.

The hardware should later plug into the existing experiment rather than requiring the experiment to be rewritten around the hardware.

## Next Work

1. Define the physical P0 electrical and acquisition block diagram.
2. Set realistic sample-rate and analog-bandwidth requirements.
3. Select a sacrificial sealed discharge tube.
4. Evaluate controllable, current-limited high-voltage driver architectures.
5. Add an electronics-only model/control once the likely P0 front end is known.
6. Add the first nonlinear temporal benchmark after the P1 interface is stable.

## Rule

If an unexpected result appears:

**Do not immediately explain it. Reproduce it.**
