# Proposed apparatus and coordinate drawings

These drawings describe proposed, unbuilt arrangements. The electrical simulations use a stipulated lumped circuit; the physical winding-pack geometry does not predict its inductances or coupling. No instrument display, field map or experimental trace has been invented.

The [catalog](../data/setups.json) connects each arrangement to its illustrations. The [coordinate file](../assets/setups/geometry.json) and [Python generator](../scripts/render_setups.py) reconstruct the geometry. SVG plan and elevation are dimensioned projections; the PNG is a perspective rendering of actual three-dimensional coordinate surfaces and wires. A separate generated artistic reconstruction, if present, is an illustration and has no dimensional authority.

## Coupled resonators: build boundary

The [plan](../assets/setups/coupled-coils-plan.svg), [elevation](../assets/setups/coupled-coils-elevation.svg) and [3D view](../assets/setups/coupled-coils-3d.png) use a 1.20 × 0.72 m bench. Coordinates refer to the tabletop, with z upwards. Both coil axes run along x.

| Proposed dimension | Value |
|---|---:|
| Primary coil centre (x, y, z) | (0.420, 0.420, 0.105) m |
| Receiver coil centre (x, y, z) | (0.500, 0.420, 0.105) m |
| Centre spacing / clear axial gap | 0.080 m / 0.030 m |
| Each pack outer / inner diameter | 0.056 m / 0.032 m |
| Each pack axial length | 0.050 m |
| Adjustable nonconductive rail footprint | 0.260 × 0.080 m |

The pack is a volume envelope, not a specified winding. Turn count, wire gauge, material, core and parasitic parameters remain unspecified. These dimensions are deliberately separate from the R1 contract values: L₁ = 10 mH, L₂ = 40 mH, M = +3 mH, C₁ = 10 µF, C₂ = 2.5 µF, R₁ = 2 Ω, R₂ = 3 Ω and nominal Rᴸ = 20 Ω. The parameter matrix is positive definite and has k = 0.15, but no geometry-to-inductance calculation or empirical calibration establishes that this bench achieves those values.

The [circuit](../assets/setups/coupled-coils-circuit.svg) is the authority for the ideal topology and sign convention. Each reference current enters its winding dot, giving the off-diagonal impedance +iωM and stored mutual energy +M i₁(t)i₂(t). The red primary and teal receiver are separate closed conductive loops. The primary return defines 0 V locally; the receiver has no galvanic connection to that return or earth. The source is nominally 1 V peak in the numerical model. A physical source's actual port waveform and impedance must be characterized.

For R1, the model boundary includes both loops, winding losses, receiver load and mutual magnetic energy:

\[
E(t)=\tfrac12 L_1 i_1(t)^2+Mi_1(t)i_2(t)+\tfrac12L_2i_2(t)^2+\tfrac12 C_1v_{C1}(t)^2+\tfrac12C_2v_{C2}(t)^2,
\qquad W_{in}=\Delta E+Q_{R1}+Q_{R2}+Q_{RL}.
\]

Here i₁(t), i₂(t) and capacitor voltages are real instantaneous values. Complex peak phasors I₁, I₂ and V instead use average power Re(VI*)/2; they must not be inserted directly into the instantaneous quadratic. Any deliberately added receiver drive supplies work that must be added to the boundary. A large capacitor voltage or receiver voltage is not an energy balance.

## Measurement and controls

The [coherent-readout schematic](../assets/setups/coherent-readout.svg) makes R2's observation requirements explicit. Simultaneously record source voltage, both currents and load voltage using a shared timebase. Use characterized isolated/differential channels that preserve the floating receiver. The current symbols in the plan denote measurement locations; they do not select a zero-burden physical sensor. A shunt adds resistance, an inductive sensor has its own response, and channel delay can corrupt relative phase. Include the selected sensor's impedance and complex transfer function in the physical model.

Before a quantitative pilot:

1. Characterize L₁, L₂, signed M and losses at the operating frequency and at each gap. Preserve the measured polarity and uncertainty. Treat the numerical values as targets only if an actual measurement justifies that comparison.
2. Characterize source impedance, channel gain, phase, isolation and burden with the actual wiring. A common clock alone does not calibrate relative channel delay.
3. Record source-off background, known drive, receiver-load changes and gap changes. Preserve all runs and the actual component temperature and geometry.
4. For transient energy, record initial and final currents and both capacitor voltages; retain signed source work. Account for sensor/source dissipation and any additional injection port.
5. Apply the calibrated full complex observation model. R2's supplied uncertainty bounds are assumptions, not achieved hardware performance. Unknown calibration requires withholding an unconditional residual-drive claim.

R2 reconstructs an effective port-voltage vector, ê = ẐÎ. Receiver amplitude alone, both amplitudes, or one complex channel can retain exact rival source configurations. Two coherent current channels can identify the two complex port quantities only within the declared calibrated circuit. A residual receiver-port voltage is not identification of dark matter, gravity, free energy or any other physical cause.

## Environmental witness: additional calibration obligation

The [witness plan](../assets/setups/environmental-witness-plan.svg) and [coordinate 3D view](../assets/setups/environmental-witness-3d.png) add an independently read pickup W, centred at (0.840, 0.500, 0.105) m with the same proposed pack envelope. Its two blue leads end at an isolated differential readout. The pack position and orientation are proposed test variables, not an optimized or validated response. There is no assertion that this pickup ignores the intended signal.

The [R3 observation diagram](../assets/setups/environmental-witness-map.svg) separates raw pickup voltage from the model's witness-equivalent complex voltage w. It also separates the R2 reconstructed receiver-port voltage y from any direct sensor voltage. Independent complex calibration must justify both transformations. In the clean-witness fixture, y = s + ab and w = b, hence ŝ = ŷ − âŵ. Here a is dimensionless and complex; the contract supplies uncertainty bounds that a physical experiment must establish separately.

First record source-off data, then deliberate background-only and known receiver-port injections. Measure both channels synchronously. Check transfer stability across position, orientation, drive amplitude and time. A physical pickup can load or couple to the receiver, so adding it may require extending the R1 two-loop impedance model as well as calibrating the witness map.

Explicitly test signal leakage, w = b + βs. Known leakage is invertible only when 1 − aβ ≠ 0; near its singular boundary, the inverse amplifies errors. Unknown a admits an exact zero-signal rival even when both readouts are available. Perfect subtraction still cannot distinguish an exotic contribution from an unmonitored ordinary drive at the same port. This is a proposed calibration platform, not a dark-matter detector or a calculation of search sensitivity.

## Newton-style prism illustration

The [ray drawing](../assets/setups/newton-prism-rays.svg) is a modern source-supported reconstruction of first-prism separation. Newton's 1672 letter describes an aperture, prism, variations of aperture and incidence, and subsequent second-prism discrimination. The selected passage was read in the [Newton Project normalized primary text](https://www.newtonproject.ox.ac.uk/view/texts/normalized/NATP00006), printed pp. 3076–3078, source ID `NT-NEWTON-LIGHT1672`.

Our 120 mm equilateral prism and screen at x = 450 mm are modern teaching geometry. Incoming rays make 20° with the horizontal. The three refractive indices, 1.51, 1.52 and 1.53, are stipulated at 650, 550 and 450 nm; they are not a measured glass dispersion curve. Vector Snell refraction and polygon intersections calculate each path. The generator checks both interfaces; its residual is a numerical consistency check rather than observational agreement.

The drawing does not reproduce Newton's historical dimensions, his complete two-prism experiment, a finite solar disk, intensity or diffraction. A physical study would require measured geometry and dispersion, finite-aperture uncertainty and the second-prism controls before making the broader inference.

## Reproduce and inspect

From the repository root:

```sh
python scripts/render_setups.py
```

Python requires NumPy and Matplotlib. The renderer writes dimensioned SVGs, the coordinate 3D PNG, `geometry.json` and a SHA-256 manifest. The manifest checks the proposed coil gap, algebraic coupling factor, positive-definite inductance matrix and Snell consistency. It does not certify a built coil, calibration or field solution. Exact raster bytes also depend on the recorded software/font environment; this release used Python 3.12.14, NumPy 2.3.5 and Matplotlib 3.10.8.
