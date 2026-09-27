# From mechanism to an identifiable observable

These are modern derivations for frozen synthetic fixtures. They are not transcriptions of Newton or Tesla, new laws, measurements or external peer review. The source ledger keeps the historical motivation separate from what the code tests.

## R1: two coupled circuits

Let `q=(q1,q2)` be capacitor charges in coulombs and `i=qdot` currents in amperes. The inductance matrix is

\[
\mathbf L=\begin{pmatrix}L_1&M\\M&L_2\end{pmatrix},\quad M=k\sqrt{L_1L_2},\quad |k|<1.
\]

Positive individual inductances and `|k|<1` make magnetic energy positive. With `R=diag(R1,R2+RL)` and `C^{-1}=diag(1/C1,1/C2)`, the forward model is

\[
\mathbf L\dot{\mathbf i}+\mathbf R\mathbf i+\mathbf C^{-1}\mathbf q=\mathbf v.
\]

Multiplying by the current gives the complete instantaneous identity

\[
E=\tfrac12\mathbf i^T\mathbf L\mathbf i+\tfrac12\mathbf q^T\mathbf C^{-1}\mathbf q,
\qquad \dot E=\mathbf v^T\mathbf i-\mathbf i^T\mathbf R\mathbf i.
\]

This includes the mutual term `M i1 i2`; dropping it would corrupt a transient energy budget. Fixed geometry and time-independent linear inductances are essential. A moving or pumped element adds a mechanical or parametric source port.

For peak phasors and angular frequency `ω`,

\[
\mathbf Z=\begin{pmatrix}
R_1+j(\omega L_1-1/(\omega C_1))&j\omega M\\
j\omega M&R_2+R_L+j(\omega L_2-1/(\omega C_2))
\end{pmatrix},\qquad \mathbf Z\mathbf I=(V,0)^T.
\]

With positive resistances the Hermitian real part of `Z` is positive definite. If `Z I=0`, taking the real part of `I† Z I` forces `I=0`; therefore the forward inverse exists at every real positive frequency in this model.

At common uncoupled resonance `ω0=1/sqrt(L1 C1)=1/sqrt(L2 C2)`, write `x=ω0 M` and `Rs=R2+RL`. Then

\[
I_1=\frac{V}{R_1+x^2/R_s},\qquad I_2=-\frac{jx}{R_s}I_1.
\]

The receiver reflects the positive resistance `x²/Rs` to the source. A large receiver voltage does not remove that backaction. Average real power is

\[
P_\text{source}=\tfrac12\Re(VI_1^*),\quad
P_\text{load}=\tfrac12R_L|I_2|^2,\quad
P_\text{loss}=\tfrac12(R_1|I_1|^2+R_2|I_2|^2).
\]

The factor one half belongs to the declared peak-phasor convention; an RMS convention would have different amplitude definitions. In steady state `Psource=Pload+Ploss`. Over a finite start/stop window the stored-energy change must also be included. Reversing the signed mutual inductance reverses the receiver phase but leaves powers unchanged.

**Scope.** These identities apply to a passive, lumped, linear, time-invariant two-loop circuit. They do not establish the value of any component, immunity to readout loading, a globally optimal design, a gravity mechanism or an axion coupling. The fixture's two-coil phase map is a useful test bed for later source-localization questions only after independent review.

## R2: the source-space observation map

The unknown effective source vector is `e=(e1,e2)∈C²`, a four-real-dimensional domain, and `I=H e`, `H=Z^{-1}`. A prescribed waveform-generator knob setting is not substituted for a measured source port voltage. All phases use a shared reference.

At a nonzero current fixture, the real differential of a squared magnitude is

\[
\delta |I_j|^2=2\Re(I_j^*\,\delta I_j),\qquad \delta\mathbf I=\mathbf H\delta\mathbf e.
\]

Because `H` is invertible, the receiver-only squared magnitude has local rank one, both squared magnitudes rank two, receiver complex current rank two, and both coherent complex currents rank four. Their local nullities in the four-real-dimensional source domain are three, two, two and zero. At the zero-current point the derivatives of the squared-magnitude maps have rank zero. These local statements are not a claim that a nonlinear map has one global linear kernel.

There are also exact, finite ambiguities:

- Keeping `I2` fixed while changing `I1` leaves the entire complex receiver readout unchanged. The source change is `δe=Z(δ,0)`, so the receiver-complex map has an explicit one-complex-dimensional linear kernel.
- Replacing `I2` with `exp(jφ) I2` preserves both current magnitudes while usually changing both inferred sources. The source rival is `e'=Z(I1,exp(jφ)I2)`. An amplitude measurement cannot choose between these finite source vectors.
- With both calibrated coherent currents, `e=Z I` reconstructs the two effective port drives uniquely within this model. This is source localization, not a theory of the source's physical origin.

For the receiver port, `e2=jωM I1+Z22 I2`. Let measured values be `Ihat`, nominal mutual inductance `Mhat`, complex current-error bounds `ε1,ε2` and mutual-inductance bound `ΔM`; all other parameters are exact in this frozen bounded model. Then

\[
|\widehat e_2-e_2|\leq\omega|\widehat M|\epsilon_1+|\widehat Z_{22}|\epsilon_2+\omega\Delta M\,(|\widehat I_1|+\epsilon_1).
\]

This follows by adding and subtracting the nominal products and using `|I1|≤|Ihat1|+ε1`. It is a conservative deterministic error disk conditional on supplied bounds, not an instrument calibration, confidence interval or detection significance.

A relative phase error is a concrete rival. For true `e2=0`, rotate only the receiver readout by `φ`. The reconstructed false drive is exactly

\[
\widehat e_2=Z_{22}I_2(e^{j\phi}-1).
\]

Thus a small uncalibrated channel delay can leave conspicuous source-location residuals even though the actual receiver port has no independent drive. Real calibration must bound phase, gain, offsets, transfer functions and component uncertainty over the actual bandwidth; the finite synthetic fixtures do not establish those bounds.

## R3: conditional witness subtraction

Let `s` be the stipulated receiver signal and `b` the environmental nuisance, both complex effective voltages in volts. The calibrated observation model is

\[
y=s+ab,\qquad w=b,
\]

where `a` is a complex dimensionless transfer. The nuisance-equivalent `w` requires a calibration from a physical witness sensor; it is not automatically its raw voltage.

Without a witness, the map from `(s,b)∈C²` to `y∈C` has real rank two and nullity two, with exact kernel `(-a t,t)`. With known `a` and a clean witness, the triangular map to `(y,w)` has determinant one and `s=y-a w` is unique.

Let `a_true=ahat+δa`, `|δa|≤Δa`; measured values satisfy `yhat=y+ηy`, `what=b+ηw`, with bounds `εy,εw`. The estimated signal obeys

\[
\widehat s-s=\delta a\,b+\eta_y-\widehat a\eta_w,
\]

and hence

\[
|\widehat s-s|\leq\epsilon_y+|\widehat a|\epsilon_w+\Delta a\,(|\widehat w|+\epsilon_w).
\]

The final term charges the difference between measured witness magnitude and true nuisance magnitude. A useful exact sharpness construction chooses the witness error opposite `b`, so `|what|+εw=|b|`, and aligns the receiver and transfer errors with `ahat b`. It is a deterministic triangle-inequality bound, not a statistical coverage statement. The fixture's 2 mV receiver allowance is stipulated anew and needs real calibration.

If `a` is unknown, `(s,a)→(s-δa b,a+δa)` leaves **both** readouts unchanged. For nonzero `b`, choosing `δa=s/b` makes an exact zero-signal rival. The local map from `(s,b,a)∈C³` to `(y,w)∈C²` has real rank four and nullity two, with tangent witness `(-b t,0,t)` for dimensionless `t`.

A witness can also respond to the signal. With known leakage `β`,

\[
\begin{pmatrix}y\\w\end{pmatrix}
=\begin{pmatrix}1&a\\\beta&1\end{pmatrix}
\begin{pmatrix}s\\b\end{pmatrix},
\qquad s=\frac{y-aw}{1-a\beta}.
\]

This requires `1-aβ≠0`. At `β=1/a`, the map has complex rank one, real rank two, and kernel `(-a t,t)`. Close to that boundary, readout errors are amplified. Simply adding a sensor does not ensure an independent observation.

Finally, a clean witness cannot assign physical identity to a residual. If `s=s_exotic+d` includes an unmonitored ordinary same-port drive, the raw map from `(s_exotic,d,b)∈C³` has real rank four and nullity two with exact kernel `(t,-t,0)`. Reassigning all 5 mV from the putative exotic term to the ordinary drive leaves both readouts unchanged. Rejecting that rival requires a further physical discriminator, not another fit of the same data.
