# Tool audit and reuse decision

Audit date: **27 September 2026**. This audit checks the particular pinned source below; it does not certify every page, calculation or dependency of the astrology project.

## Requested pages and pinned source

- Requested [atlas confluence page](https://occult-kranti.github.io/resonance-research-atlas/projects/astrology-sim-ant/pages/confluence.html).
- Requested [astrology workbench](https://occult-kranti.github.io/astrology-sim-ant/pages/workbench.html).
- Inspected repository: [occult-kranti/astrology-sim-ant](https://github.com/occult-kranti/astrology-sim-ant/tree/3a3ce9953e47a078e659723a52187648f1f08486), commit **`3a3ce9953e47a078e659723a52187648f1f08486`**.

Both requested page fetches failed with the web retriever's `InternalError`. This is a retrieval limitation, not evidence that the deployed pages are absent or broken. The local checkout was inspected at the exact commit above. No claim of visual/runtime inspection of those two deployed pages is made by the source lane.

| File examined | Observed behavior | Boundary |
| --- | --- | --- |
| `assets/js/core/astro.js` | Calls Astronomy Engine's `GeoVector`, transforms equatorial J2000 vectors to ecliptic-of-date coordinates, normalizes longitude; computes speed by a centered ±0.25-day difference. | The coordinate frame, time interpretation, apparent/geometric option and differencing interval matter. This is code inspection, not an independent ephemeris benchmark. |
| `assets/js/core/astro.js` | Implements a mean-node polynomial in TT centuries and several house systems. Placidus at absolute latitude above 66 degrees falls back to Regiomontanus. | A reused UI must disclose this fallback; the named system and returned algorithm can otherwise differ. |
| `assets/js/core/confluence.js` | Implements geometry/query operations and a piecewise-linear, era-warped historical timeline with declared scale bands. | Timeline distance is a display mapping, not a physical clock or a measure of cultural causation. |
| `assets/js/core/data/confluence.js` | Sample bibliography and cultural-influence records were inspected. | The complete historical catalogue and every relationship were not independently verified. |
| `scripts/engine-test.mjs` | Existing suite checks broad astronomical sanity and repository feature/rule consistency. | Equinox/solstice checks are comparatively loose (under one degree); rule-output consistency is not a test of predictive validity for human outcomes. |

The code comments refer to approximately one-arcminute accuracy and reference vectors in `data/ENGINE_VALIDATION.md`. **That validation file is absent from the inspected pinned tree.** The comment is therefore not an accuracy result reproduced by this review.

The existing suite was executed using `node scripts/engine-test.mjs`; its output ended **`[engine-test] all passed`**. The source checkout remained unchanged. This establishes that suite's success in the local environment, not an external-ephemeris accuracy bound, astrological predictive power or deployed-page functionality.

## Provenance hashes

SHA-256 at the pinned commit:

| File | SHA-256 |
| --- | --- |
| `assets/js/lib/astronomy.js` | `068f1445ed0c636c94818fe6d20d7d125120e605e0bab9fc4675c3d531be5ad7` |
| `assets/js/core/astro.js` | `9c767c41add9346a8310d6c1448b045dbeb8d0a7178e686af6a0de23b9e164f8` |
| `assets/js/core/confluence.js` | `152a1d3f18f9b804c41c4c565d45af34552b7300b37f52e4e798fa6c7d14318e` |
| `scripts/engine-test.mjs` | `cbc2c563fb0011cfefa8ae17c5087e274c368bca46b3c0919008c66f2493029c` |

## License and reuse boundary

The README describes the project as educational/non-commercial and attributes astronomy calculations to Don Cross's MIT-licensed Astronomy Engine. No standard top-level license file was found in the inspected tree. A vendored dependency's license does not license the whole site's code, prose, data or artwork. The Astronomy Engine file has its own MIT notice; selected other vendored material has separate notices.

The implementation decision is therefore to **link the existing workbench/confluence pages and rebuild narrowly scoped scientific calculators from explicit equations**, rather than import the whole site. A later reuse of any original code/data needs its applicable permission or clear license. No whole-site import has been made by this source lane.

Useful standalone scientific calculators include a two-coil phasor/energy model, a phase-error sensitivity plot, a complete-system force budget, a prism ray trace and an orbital-scaling demonstration. Each can declare assumptions and limits directly. There is no reason to attach astrological interpretation to these calculations.

## External open-source candidates

| Tool and primary documentation checked | Version/license evidence | Useful role | Status here |
| --- | --- | --- | --- |
| [ngspice maintainer news](https://ngspice.sourceforge.io/news.html) and [development/licensing information](https://ngspice.sourceforge.io/devel.html) | Maintainer news lists version **47**, 11 August 2026. Base license is modified BSD; component exceptions must be retained. | Independent circuit solution and loss/phase checks after mapping the exact model and component conventions. | Documentation inspected earlier in this session; not installed or run in the source audit. |
| [Magpylib 5.2.3 documentation](https://magpylib.readthedocs.io/en/5.2.3/) and [installation guide](https://magpylib.readthedocs.io/en/5.2.3/_pages/user_guide/guide_start_01_install.html) | Version-pinned docs and BSD-2-Clause notice inspected. | A later finite-magnet field model, with units and material assumptions checked against the intended force calculation. | Documentation only; not executed, and no computed field is attributed to it here. |
| Vendored Astronomy Engine in the pinned repository | Exact file hash above and MIT notice, not an inferred package version. | Astronomical coordinate calculation after a separately supplied reference-vector validation. | Selected wrapper/source inspection and existing repo tests; no new high-precision certification. |

External tools are independent checks only when their implementation, conventions and data path are sufficiently independent of the producer model. Running a package on the same mistaken equations is not experimental confirmation. Tool availability and a public repository also do not establish validity of every claim expressed through them.
