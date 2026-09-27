# R1 — Coupled resonators and reflected loading

All results are synthetic solutions of the frozen, linear, lumped passive circuit. This is a modern reconstruction inspired by coupled tuning, not Tesla's historical hardware.

## Fixed witness

At ω₀ = 3162.277660168 rad/s (503.292121 Hz), a 1 V peak source and 20 Ω receiver load give voltage gain **1.395122497** and load/source real-power fraction **0.575447570**. Source power is 0.0845588235294 W; load power is 0.0486591695502 W; winding loss is 0.0358996539792 W.

At resonance the receiver reflects (ωM)²/(R₂+Rᴸ) = 3.91304347826 Ω into the source. This changes the source current. Omitting this term creates a false account of available source power.

## Finite-time accounting

Starting from zero charge/current, the sinusoidal drive runs for 0.25 s. DOP853 evolves only the four circuit states; external Simpson quadrature of sampled instantaneous powers calculates work, independently of any integrated work state. Coarse/fine grids and a tighter ODE tolerance are all retained in CSV. The tight run has source work 0.0210589534867 J, load heat 0.0118882472264 J, winding heat 0.00891632984916 J, final storage 0.000254376368877 J and residual 4.225e-11 J.

## Controls and limits

13/13 producer controls pass. They include zero source, zero coupling, reversed mutual sign, closed-form resonance currents, increased winding loss, passive sampled efficiencies and transient refinement. The frequency/load domain is a finite fixture, not a global optimization proof. No hardware was measured. Source impedance beyond R₁, radiation, nonlinear materials and environmental coupling are outside this model. There is no gravity degree of freedom and no claim of source-free energy.

Run `python3 research/R1/run.py`. `--output DIR` writes recomputed outputs separately; the canonical manifest binds the producer, contract and dependencies.
