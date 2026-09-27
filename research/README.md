# Reproduce the numerical panel

These calculations are synthetic fixtures, not apparatus measurements. Inputs use SI units; circuit phasors use **peak amplitudes**, so cycle-average real power includes a factor of ½. A passing computation establishes the stated model result and implementation checks. It does not establish the model's adequacy for an unbuilt experiment.

Use Python 3.11 or later and install the open-source numerical runtime:

```sh
python3 -m pip install -r requirements.txt
```

The producer uses NumPy for linear algebra, SciPy for integration and Matplotlib for deterministic SVG charts. Exact versions used are pinned in `requirements.txt`; each round manifest records the runtime, contract, dependencies and artifact hashes.

Every round starts with the advisor's frozen contract in `docs/contracts/`. The producer saves SI parameters, raw CSV, a result JSON, explanatory report and SVG charts under its own `research/R*/` directory. Independent review is stored separately under `research/reviews/` and uses separately derived numerical methods. Producer files are frozen after admission; failed or superseded evidence must remain distinguishable.

| Round | Computation | Main limit |
|---|---|---|
| [R1](R1/report.md) | Coupled passive resonators, reflected source loading, 3,205 phasor rows and three externally quadratured transients | Voltage gain is supplied by source work; no source-free energy |
| [R2](R2/report.md) | Four observation maps, exact drive rivals, coherent reconstruction, 128 bounded calibration fixtures and phase-error artifacts | Effective source location depends on measured phase and calibrated parameters; it does not identify a physical cause |
| [R3](R3/report.md) | Environmental witness subtraction, 512 bounded fixtures, an attained sharp bound, crossleak singularity and exact remaining rivals | An ordinary same-port source reproduces the ideal observations, even after perfect witness subtraction |

The three producers contain 39 model/implementation checks. Their outputs comprise 32 reproducible generated artifacts, excluding producer code and manifest files. The independent reviewer check counts and final admission statuses are recorded separately; producer passes alone are not admission.

Verify all admitted producer bindings without numerical dependencies:

```sh
python3 scripts/verify_reproduction.py
```

Recompute outputs in temporary directories and compare their bytes without rewriting the evidence:

```sh
python3 scripts/verify_reproduction.py --regenerate
```

For one round, append `--round R1`, `--round R2` or `--round R3`. Byte equality is expected with the recorded runtime. It is a reproducibility check, separate from the scientific review. Different library or platform versions can change numerical last digits or SVG bytes and require numerical comparison rather than silently replacing the recorded files.

Individual producer scripts accept `--output DIR`, for example:

```sh
python3 research/R1/run.py --output /tmp/resonator-reproduction
```

Running a producer without `--output` rewrites its canonical outputs. Use the temporary-output option when inspecting already admitted work. Do not interpret a numerical residual, voltage gain, force reading or inverse-model fit as free energy, reduced gravity or a unique hidden cause without the experiment's separate controls and calibration.

Two pre-admission programming repairs are retained under `research/repairs/`: R2 converted NumPy boolean comparison results to JSON-compatible builtin booleans; R3 repaired a missing list bracket before any computation could execute. Their original source snapshots and failure descriptions are preserved. Neither changed a scientific contract, parameter, threshold or admitted result, and neither counts as a panel loop.
