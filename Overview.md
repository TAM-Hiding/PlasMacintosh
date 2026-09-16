# PLASMACINTOSH

### Plasma Reservoir Computing Demonstrator

**Project Definition & Experimental Roadmap — v0.1**
**16 September 2026**

**Working description:** Field-configured gaseous computing apparatus.

**Technical description:** Experimental investigation of low-pressure glow-discharge plasma as a physical reservoir for temporal information processing.

**Current computational substrate:** Mostly Neon

---

## 1. The Question

Can the nonlinear, history-dependent dynamics of a low-pressure glow-discharge plasma act as a useful physical reservoir?

More specifically:

Given a controlled time-varying electrical input, does the instantaneous observable state of the plasma contain enough information about previous inputs and nonlinear interactions that a simple external readout can perform temporal information-processing tasks better than appropriate non-plasma controls?

The objective is not initially to make a useful computer.

The objective is to determine whether the plasma does anything computationally interesting at all.

A negative result is acceptable.

---

## 2. Basic Model

Treat the plasma as a physical black box.

**INPUT → PLASMA DYNAMICS → OBSERVABLE STATE → SIMPLE READOUT**

The input is a controlled electrical waveform.

The plasma evolves according to its own physics. Previous excitation may influence its current state through effects including residual charge, excited/metastable species, surface charge, thermal state, ionization/recombination dynamics, and other discharge phenomena.

The plasma state is sampled through multiple observables:

* Optical intensity
* Spatial optical intensity
* Discharge current
* Discharge voltage
* Eventually, wavelength-specific optical emission and other diagnostics

Only the external readout is trained.

The plasma is not optimized to produce a desired answer during the initial experiments.

---

## 3. What Counts as Success?

The weakest interesting result is evidence of reproducible **fading memory**.

For example:

The optical/electrical state produced by

**LOW now, HIGH previously**

is measurably distinguishable from

**LOW now, LOW previously.**

A stronger result is that a simple trained readout can reconstruct previous inputs from the current plasma state.

Stronger still is successful performance on tasks requiring both memory and nonlinear transformation, such as delayed parity.

Ultimately, computational capacity can be characterized over different physical operating regimes.

---

## 4. What Does NOT Count?

PlasMacintosh has not demonstrated meaningful reservoir computation merely because:

* Plasma brightness follows the input voltage.
* Plasma current follows the input voltage.
* A complicated decoder can infer the driving waveform.
* The surrounding analog electronics themselves provide sufficient memory/nonlinearity.
* Training performance is high but unseen test performance is poor.
* Results disappear between runs.
* Results depend upon accidental timing leakage in the acquisition software.

Controls therefore matter as much as the glowing bit.

At minimum, compare:

**Input → decoder**

**Input → equivalent acquisition/electronics → decoder**

**Input → plasma → decoder**

Additional controls should include timestamp/data shuffling and strict separation of training and test datasets.

Scientific objective:

**Attempt to prove that the gas computer is actually just a fancy resistor.**

Proceed only when it refuses to cooperate.

---

# 5. P0 — Make Plasma and Measure It

### Purpose

Build the minimum apparatus required to create a repeatable glow discharge, perturb it in a controlled manner, and record synchronized optical and electrical measurements.

### Initial physical reservoir

Prefer:

* Sealed low-pressure noble-gas discharge tube
* Neon as likely first gas
* Known or reasonably characterized geometry
* Controllable/current-limited excitation
* Black optical enclosure

Do not initially require:

* Vacuum system
* Interchangeable gases
* Adjustable pressure
* Movable electrodes
* UV spectroscopy
* Elaborate automated sensor positioning

### Initial observables

Approximately 4–8 identical silicon photodiodes positioned along the active plasma column.

Also record:

* Discharge current
* Discharge voltage
* Exact commanded input waveform
* Timestamp/sample index

### P0 question

**Can we reproducibly measure interesting time-dependent plasma dynamics?**

No machine learning heroics required.

---

# 6. P1 — Does It Remember?

Feed the reservoir a known pseudorandom temporal sequence.

Example:

**HIGH / LOW / HIGH / HIGH / LOW / ...**

Train a simple linear readout to reconstruct the input from:

* 1 step previously
* 2 steps previously
* 3 steps previously
* etc.

Plot reconstruction performance against delay.

Expected useful behavior:

Good reconstruction for recent history, followed by gradual degradation.

That curve is the reservoir's experimentally measured fading memory.

Compare against all appropriate controls.

### P1 question

**Does the present plasma state contain useful information about its past?**

---

# 7. P2 — Does It Transform Information?

Introduce tasks that cannot be solved merely by delaying the input.

Candidate benchmark:

**Delayed parity / XOR-type temporal tasks**

These require both:

* Memory of previous inputs
* Nonlinear transformation

If a simple readout succeeds using plasma observables where the corresponding control does not, the plasma is performing a useful physical transformation before the readout sees the data.

### P2 question

**Does the plasma provide useful nonlinear processing in addition to memory?**

---

# 8. P3 — Map the Dynamical Regime

Do not assume that maximum visible chaos equals maximum computational usefulness.

Sweep controllable operating parameters such as:

* Discharge voltage/current
* Input amplitude
* Input frequency/time scale
* Ballast resistance
* Relevant capacitance
* Electrode separation, if available

Characterize observed behavior:

**stable → oscillatory → complex → chaotic**

At each condition, run the same computational benchmarks.

This allows comparison of computational performance with physical dynamical regime.

### P3 question

**Where does this particular gas computer work best?**

A particularly interesting possibility is that useful performance peaks near transitions between highly stable and strongly chaotic behavior.

This is a hypothesis to test, not an assumption.

---

# 9. P4 — Gas Is Now a Parameter

Once the basic apparatus and benchmark pipeline are proven, compare different gases under as closely controlled conditions as practical.

Candidates include:

* Neon
* Argon
* Helium
* Nitrogen
* Selected mixtures

Gas composition changes much more than atomic mass. It changes ionization behavior, excitation states, collision processes, metastable populations, emission spectra, recombination pathways, and—when molecular gases are introduced—additional rotational/vibrational and chemical processes.

### P4 question

**Do different gaseous computational substrates produce measurably different reservoir characteristics?**

---

# 10. P5 — See More of the Plasma

Increase the dimensionality of the observed state.

### Spatial observation

Measure optical emission at multiple positions along the plasma column.

Determine whether spatially separated sensors provide distinct information or merely redundant copies of the same global brightness signal.

Later possibilities:

* More axial channels
* Radial/angular channels
* Time-resolved propagation measurements

### Spectral observation

Split optical measurements into wavelength regions.

Possible future channels:

* UV
* Multiple visible bands
* Near-IR

Different spectral bands may reveal different excited states, species, or plasma processes.

A possible future sensor arrangement might therefore contain:

**position × wavelength × time**

rather than simply total brightness.

### P5 question

**How much of the hidden plasma state can we actually observe?**

---

# 11. P6 — Cascaded Plasma Reservoirs

Construct two independently characterized reservoirs.

Example:

**INPUT → RESERVOIR A → coupling → RESERVOIR B → READOUT**

Reservoir A and B may eventually differ in:

* Gas
* Pressure
* Geometry
* Operating regime
* Time constant

The first implementation should use explicit electrical coupling:

Measure A → condition signal → use signal to modulate B.

Later experiments may investigate optical, electromagnetic, or direct physical coupling.

Compare:

**Input → A → readout**

**Input → B → readout**

**Input → A → B → readout**

### P6 question

**Does cascading physically different reservoirs produce useful transformations unavailable from either reservoir alone?**

---

# 12. Eventual R1 Experimental Chamber

The eventual apparatus may replace sealed commercial tubes with a demountable, controllable plasma chamber.

**Current speculative geometry only:**

Approximately:

* 15–30 mm internal diameter
* 250–500 mm useful length
* Borosilicate/quartz transparent chamber
* Machined removable end assemblies
* Replaceable electrodes
* One fixed electrode
* One movable electrode
* Approximately 50–100 mm useful electrode-spacing adjustment
* Vacuum port
* Gas inlet
* Pressure measurement
* Current-limited high-voltage excitation

Final dimensions will be selected from P0–P3 observations rather than intuition alone.

---

# 13. Self-Normalizing Optical Sensor Array

A future chamber with adjustable electrode spacing creates a measurement problem:

Changing the active plasma-column length changes the relative positions of fixed photodiodes.

Proposed solution:

Mount each photodiode carriage on a common linear guide.

Connect the carriages with an equal-spacing lazy-tong/scissor linkage.

The guide constrains:

* Straightness
* Rotation
* Sensor orientation

The linkage controls only relative spacing.

Moving the endpoint expands or contracts all sensor positions proportionally.

If active electrode spacing is **L**, sensor positions can therefore remain approximately:

**0.1L, 0.2L, 0.3L ...**

regardless of the absolute electrode separation.

This permits two useful experimental coordinate systems:

### NORMALIZED

Sensors maintain constant fractional position along the active column.

Useful for comparing overall plasma structure as electrode spacing changes.

### ABSOLUTE

Sensors remain at fixed physical coordinates.

Useful for measuring propagation distance, velocity, and spatial behavior independent of normalized chamber length.

**Important:** This mechanism is not required for P0.

Do not build a CNC machine for the photodiodes before establishing that the plasma does anything useful.

---

# 14. Data Architecture

Design the analysis pipeline so that the physical reservoir can eventually be replaced transparently by another data source.

Conceptually:

**BENCHMARK GENERATOR**

↓

**RESERVOIR**

↓

**STANDARDIZED OBSERVABLE DATA**

↓

**ANALYSIS / READOUT**

Possible reservoir sources:

* Simulated nonlinear reservoir
* Direct-input control
* Electronics-only control
* PlasMacintosh

The same benchmark and analysis code should operate on all of them.

Suggested UI labels:

**RESERVOIR: FAKE GAS / GAS**

This is scientifically important.

It is also non-negotiably funny.

---

# 15. Design Philosophy

### Change one stupid thing at a time.

Every added degree of freedom increases the number of explanations available for an observed result.

Early experiments should therefore deliberately be boring.

One gas.

One geometry.

One excitation architecture.

Known inputs.

Simple observables.

Simple readout.

Strong controls.

Only after the basic effect survives should the apparatus gain adjustable pressure, gases, geometry, spectral sensing, magnetic fields, multiple reservoirs, or other complexity.

---

# 16. Immediate Work That Costs Approximately $0

Before purchasing hardware:

1. Define the standardized experiment/data format.
2. Define the P1 short-term-memory benchmark.
3. Define the P2 nonlinear benchmark.
4. Implement a simulated reservoir.
5. Implement the direct-input control.
6. Implement training/test separation.
7. Implement plots and performance metrics.
8. Sketch P0 electrical/acquisition architecture.
9. Determine required sampling rates and sensor bandwidth.
10. Investigate practical controllable high-voltage driver architectures.
11. Select an inexpensive sacrificial first discharge tube.
12. Establish the P0 bill of materials.

The objective is to have the software and experimental protocol waiting for the plasma rather than inventing the experiment after the plasma starts glowing.

---

# 17. Current Status

**Project:** Active exploratory design

**Hardware:** None dedicated yet

**Theory:** Plausible enough to test

**Prior art:** Related glow-discharge computation, nonlinear plasma dynamics, plasma memory effects, and physical reservoir computing exist. Exact prior demonstration of the proposed glow-discharge reservoir architecture has not yet been established and requires a more rigorous literature search before any novelty claim.

**Primary technical unknown:** Practical, controllable, safe, inexpensive high-voltage excitation architecture.

**Primary scientific unknown:** Whether measurable plasma dynamics provide useful reservoir memory/nonlinearity beyond controls.

**Primary financial condition:** Broke.

---

# 18. Governing Principle

PlasMacintosh does not need to prove that plasma is a good computer.

It needs to ask a sufficiently precise question that **physical reality gets to answer.**

If the answer is no, determine why.

If the answer is yes, determine under what conditions.

If the answer is:

**"What the fuck is THAT?"**

repeat the experiment.

