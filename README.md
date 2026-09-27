# Newton–Tesla Research Lab

A source-led experiment notebook for coupled electrical mechanisms, magnetic and gravity claims, dark-matter inference, and historical alchemy and prophecy.

**[Open the research lab](https://occult-kranti.github.io/newton-tesla-research-lab/)** · [Stepwise roadmap](docs/roadmap.md) · [Six-loop record](research/decisions.json) · [Scope and evidence](docs/SCOPE.md)

The program contains three adaptive rounds, each with a producer loop and an independent model-agent skeptical review. Later questions follow the actual preceding verdict. Historical figures supply documented methods; they are not participants or endorsements, and this is not human peer review.

## What to inspect

| Area | Deliverable |
|---|---|
| Coupled resonators | Source loading, receiver voltage gain, signed power and finite-time stored-energy calculations |
| Hidden source reconstruction | Four observation maps, exact rival drives and phase/calibration error controls |
| Environmental witness | Conditional pickup subtraction, transfer uncertainty, witness leakage and remaining source-identity ambiguity |
| Proposed experiments | Fifteen grouped candidates, each with an observable, rival, falsifier, source and material burden |
| Historical and current sources | Twenty-five selected records with passages and reading depth; patents and government files retain their evidential status |
| Scientific apparatus | Dimensioned plans, circuit/readout diagrams, coordinate-defined 3D rendering and Newton prism rays |
| Interactive tools | Coupled-circuit and coherent-readout calculators; searchable hypotheses, sources and actual review records |

These are reproducible model results and proposed physical setups. There are no new hardware measurements, measured free-energy gains, antigravity effects or dark-matter detections. The project contribution is the linked implementation, counterexamples, independent calculations and prospective measurement design; established circuit and inverse-problem mathematics is not claimed as a new law.

## Reproduce

Python 3.12 was used. Exact numerical dependency versions are in [requirements.txt](requirements.txt).

```bash
python3 -m pip install -r requirements.txt
python3 scripts/verify_reproduction.py --regenerate
python3 scripts/verify_release.py
npm ci
npm test
python3 scripts/build_site.py
python3 -m http.server --directory dist 8000
```

The numerical verifier regenerates outputs in temporary directories and compares exact hashes without rewriting admitted evidence. Reviewer scripts in `research/reviews/` use separate formulations; hash matching is not a substitute for those reviews. The release gate checks six ordered loops, exact scientific artifacts, frozen predecessors, resolved source records and drawing identities. UI tests check mathematical examples, behavior and claim withholding; rendered browser inspection is recorded separately.

`build-manifest.json` in the assembled site records its source commit and per-file hashes. The Pages workflow verifies the evidence and interface before deploying. Numerical regeneration requires the pinned numerical environment; the default CI gate checks admitted bytes without silently regenerating scientific results.

## Find the record

- [Panel exchanges](docs/panel-log.md), [derivations](docs/derivations.md), [advisor review](docs/advisor-review.md) and [skeptical review](docs/skeptic-review.md).
- [Historical corpus](docs/historical-corpus.md), [source review](docs/source-review.md), [source ledger](data/sources.json) and [hypothesis catalogue](data/hypotheses.json).
- [Apparatus instructions and limits](docs/apparatus.md), [geometry](assets/setups/geometry.json), [drawing generator](scripts/render_setups.py) and [setup catalogue](data/setups.json).
- [Existing tool audit](docs/tool-audit.md), including the requested confluence and astrology workbench pages. These external tools are linked and audited; their cultural interpretations are not imported as physical predictions.
- [Team and tools](docs/TEAM.md) and [release validation](docs/RELEASE.md).

One generated realistic image introduced unsupported mechanical and wiring details. Its [rejection record](docs/concept-render-review.json) is retained. Dimensioned diagrams and executable geometry govern the setup; the rejected image is not used as a scientific plate.

## Earlier checkpoints

The separate [Resonance Research Atlas](https://occult-kranti.github.io/resonance-research-atlas/sound-lab/field-notes.html) and [Resonant Vessels](https://occult-kranti.github.io/resonant-vessels/research-continuation.html) contain the preceding five-round continuation. Its two sound rounds and three electrical/magnetic rounds remain separately identified. This repository is the new, three-round extension requested afterward.

New code and drawings use the [MIT license](LICENSE). Linked historical editions, research papers, third-party tools and other sources retain their respective rights and licenses. The reading corpus is selected and expandable; it is not exhaustive coverage of every book, patent, theory or available open-source tool.
