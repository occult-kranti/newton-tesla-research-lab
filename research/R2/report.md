# R2 — A residual is not a source identity

All inputs and results are synthetic. The R1 nominal circuit is retained, with both actual port-source phasors unknown to the inverse problem. A source control setting is not substituted for a calibrated port-voltage measurement. The injected receiver source is 5 mV at π/3 radians.

## What observations identify

The source domain has four real dimensions. The four declared observation maps have local real ranks **[1, 2, 2, 4]** and nullities **[3, 2, 2, 0]** at the stipulated nonzero-current fixture. Full coherent complex currents give e = ZI; restricted channels have exact finite rivals stored in `exact-rivals.json`. Rotating a receiver current's phase preserves both current magnitudes while changing the required source vector. Adding a source-current increment of (0.01+0.02j) A preserves the receiver's full complex current while changing the source vector.

The amplitude-squared maps are nonlinear: their Jacobian kernels are local tangent statements. The exact rival families provide the separate finite ambiguity proof. At zero currents those squared-amplitude Jacobians have rank zero, which does not make the nonlinear maps globally constant.

## Conditional calibration disk

Writing measured current as Î and model mutual inductance as M̂, the receiver-drive error obeys

|ê₂−e₂| ≤ ω|M̂|ε₁ + |Z₂₂|ε₂ + ωΔM(|Î₁|+ε₁).

This follows by subtracting ZI from ẐÎ and applying the triangle inequality; all other components are exact in this model. The nominal radius is **0.00193222044655 V**, below the injected 0.005 V amplitude by **0.00306777955345 V**. Every one of 128 bounded endpoint fixtures lies inside its corresponding disk. These are deterministic supplied bounds, not confidence intervals and not instrument specifications established by measurement. Unknown calibration withholds any unconditional exclusion of zero.

## False residual control

With true receiver source zero, rotate only measured I₂ by φ. The apparent source becomes Z₂₂I₂(exp(iφ)−1). At φ=0.01 rad the false amplitude is **0.0160438418675 V**. It can exceed the injected signal despite there being no real receiver source in this control. Physical source identity, gravity change, new particles and free energy remain unestablished.

12/12 producer checks pass. Inspect raw phasor observations, exact rival voltages, all boundary fixtures and phase artifacts in the CSV/JSON files. Run `python3 research/R2/run.py --output DIR` for a separate reconstruction.
