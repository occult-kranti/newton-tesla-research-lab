# R3 — What a witness can and cannot remove

This synthetic single-frequency observation model uses y=s+ab and a clean calibrated witness w=b. Voltages are complex peak amplitudes. The stipulated signal is 5 mV, environmental equivalent voltage is 20 mV and transfer is a=0.6+0.2i. A witness-equivalent voltage is not automatically the raw voltage of a physical coil.

## Conditional recovery and a sharp bound

Known exact transfer gives s=y−aw. For measured ŷ,ŵ and supplied uncertainty radii, the estimation error is δa·b + ηᵧ − aηw. Triangle inequality, followed by |b|≤|ŵ|+εw, gives

|ŝ−s| ≤ εᵧ + |a|εw + Δa(|ŵ|+εw).

The nominal radius is **0.00272622776602 V** and the nominal zero-exclusion margin is **0.00227377223398 V**. Every one of the 512 boundary fixtures lies in its own disk. An extra aligned fixture attains its radius **0.00271622776602 V** with discrepancy 1.301e-18 V. Its witness error opposes b; its receiver and transfer errors align with ab, so both triangle inequalities attain equality.

The 2 mV receiver radius is a new stipulated effective-voltage bound, slightly above R2's nominal 1.932 mV value. It is not derived over all R3 physical circuit conditions. It, the 0.5 mV witness bound, and the 0.02 transfer bound must be calibrated before application to hardware. The fixture count is not a confidence level.

## Exact counterexamples

With unknown transfer, a′=a+s/b=(0.816506350946)+(0.325)i and s′=0 give exactly the same y,w. The local map has domain dimension six, rank four and nullity two. This is a finite rival as well as a local kernel statement.

If the witness also sees signal, w=b+βs, the known transfer matrix has determinant 1−aβ. The saved path β=t/a includes both sides of the singular boundary. At t=1 the real rank falls from four to two and the producer explicitly returns no unique inverse. The nearby noise radii assume known a and β; they are not the clean-witness uncertain-transfer bound.

Finally, writing s=s_exotic+d yields the same observations whether all 5 mV is assigned to an exotic source or to ordinary unmonitored same-port drive d. A perfect environmental witness cannot settle this physical identity. A mechanism-specific modulation/control is still necessary.

14/14 producer checks pass. All raw uncertainty cases, transfer-path records, analytic real maps, kernel columns and exact rivals are saved. No hardware, dark matter, gravity change or free-energy extraction has been demonstrated. This is the final producer round of the authorized three-round program; subsequent physical work is in the roadmap.
