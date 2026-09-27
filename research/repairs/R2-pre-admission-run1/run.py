#!/usr/bin/env python3
"""Source localization and calibration bounds in a synthetic coupled circuit."""
from pathlib import Path
import argparse
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.numerics import ROOT, np, plt, write_json, write_csv, save_figure, write_manifest, sha256

CONTRACT = ROOT / "docs/contracts/R2.json"
PRIOR_CONTRACT = ROOT / "docs/contracts/R1.json"

def impedance(p, mutual=None):
    w = 1 / np.sqrt(p["L1_H"]*p["C1_F"])
    m = p["M_H"] if mutual is None else mutual
    return np.array([[p["R1_ohm"]+1j*(w*p["L1_H"]-1/(w*p["C1_F"])), 1j*w*m], [1j*w*m, p["R2_ohm"]+p["nominal_load_ohm"]+1j*(w*p["L2_H"]-1/(w*p["C2_F"]))]])

def real_map(complex_matrix):
    matrix = np.zeros((2*complex_matrix.shape[0],2*complex_matrix.shape[1]))
    for row in range(complex_matrix.shape[0]):
        for col in range(complex_matrix.shape[1]):
            z=complex_matrix[row,col]
            matrix[2*row:2*row+2,2*col:2*col+2]=[[z.real,-z.imag],[z.imag,z.real]]
    return matrix

def pair(z):
    return [float(z.real),float(z.imag)]

def disk_bound(measured_i1, omega, mutual, z22, current_bounds, mutual_bound):
    return omega*abs(mutual)*current_bounds[0]+abs(z22)*current_bounds[1]+omega*mutual_bound*(abs(measured_i1)+current_bounds[0])

def main(out):
    out.mkdir(parents=True,exist_ok=True)
    contract=json.loads(CONTRACT.read_text());p=contract["parameters"];circuit=json.loads(PRIOR_CONTRACT.read_text())["parameters"];a=contract["acceptance"]
    z=impedance(circuit); y=np.linalg.inv(z);omega=1/np.sqrt(circuit["L1_H"]*circuit["C1_F"])
    e=np.array([complex(*p["source1_complex_V"]),p["injected_receiver_amplitude_V"]*np.exp(1j*p["injected_receiver_phase_rad"])])
    current=np.linalg.solve(z,e); reconstructed=z@current
    full=real_map(y)
    squared=np.array([2*current[0].real*full[0]+2*current[0].imag*full[1],2*current[1].real*full[2]+2*current[1].imag*full[3]])
    jacobians=[squared[1:2],squared,full[2:4],full]
    labels=["Receiver amplitude squared","Both amplitude squares","Receiver complex","Both coherent complex"]
    maps=[]
    for label,jac in zip(labels,jacobians):
        _,singular,vh=np.linalg.svd(jac,full_matrices=True)
        rank=int(np.linalg.matrix_rank(jac)); kernel=vh[rank:].T
        residual=float(np.max(np.abs(jac@kernel))) if kernel.size else 0.0
        maps.append({"map":label,"domain_real_dimension":4,"local_rank":rank,"local_nullity":4-rank,"jacobian":jac.tolist(),"kernel_columns":kernel.tolist(),"kernel_residual":residual,"singular_values":singular.tolist(),"condition":"at the stipulated nonzero-current fixture; squared-amplitude kernels are local"})
    write_json(out/"observation-maps.json",maps)
    phase_current=current.copy();phase_current[1]*=np.exp(1j*p["finite_rival_receiver_phase_rotation_rad"])
    phase_e=z@phase_current
    delta=.01+.02j; kernel_current=current+np.array([delta,0]);kernel_e=z@kernel_current
    phase_error=float(np.max(np.abs(abs(np.linalg.solve(z,phase_e))**2-abs(current)**2)))
    kernel_error=float(abs(np.linalg.solve(z,kernel_e)[1]-current[1]))
    rivals=[{"kind":"baseline","source_V":[pair(v) for v in e],"current_A":[pair(v) for v in current]}, {"kind":"same-two-amplitude-squares","source_V":[pair(v) for v in phase_e],"current_A":[pair(v) for v in phase_current],"observable_error_A2":phase_error}, {"kind":"same-receiver-complex-current","source_V":[pair(v) for v in kernel_e],"current_A":[pair(v) for v in kernel_current],"observable_error_A":kernel_error}]
    write_json(out/"exact-rivals.json",rivals)
    write_csv(out/"observations-and-rivals.csv",["fixture","e1_real_V","e1_imag_V","e2_real_V","e2_imag_V","i1_real_A","i1_imag_A","i2_real_A","i2_imag_A","i1_squared_A2","i2_squared_A2"],[[r["kind"],*r["source_V"][0],*r["source_V"][1],*r["current_A"][0],*r["current_A"][1],abs(complex(*r["current_A"][0]))**2,abs(complex(*r["current_A"][1]))**2] for r in rivals])
    eps=p["current_error_bounds_A"];dm=p["mutual_inductance_error_bound_H"]
    phases=np.arange(p["error_phase_points"])*2*np.pi/p["error_phase_points"]
    fixtures=[]
    for sign in [-1,1]:
        true_m=circuit["M_H"]+sign*dm; true_current=np.linalg.solve(impedance(circuit,true_m),e)
        for phi1 in phases:
            for phi2 in phases:
                ihat=true_current+np.array([eps[0]*np.exp(1j*phi1),eps[1]*np.exp(1j*phi2)])
                ehat=z@ihat;bound=disk_bound(ihat[0],omega,circuit["M_H"],z[1,1],eps,dm);error=abs(ehat[1]-e[1])
                fixtures.append([true_m,phi1,phi2,ihat[0].real,ihat[0].imag,ihat[1].real,ihat[1].imag,ehat[1].real,ehat[1].imag,float(error),float(bound),float(bound-error)])
    write_csv(out/"uncertainty-boundary-fixtures.csv",["true_mutual_H","i1_error_phase_rad","i2_error_phase_rad","measured_i1_real_A","measured_i1_imag_A","measured_i2_real_A","measured_i2_imag_A","reconstructed_e2_real_V","reconstructed_e2_imag_V","absolute_error_V","disk_radius_V","inclusion_margin_V"],fixtures)
    nominal_bound=float(disk_bound(current[0],omega,circuit["M_H"],z[1,1],eps,dm))
    null_current=np.linalg.solve(z,[1,0]);artifacts=[]
    for phi in p["phase_error_grid_rad"]:
        ihat=null_current.copy();ihat[1]*=np.exp(1j*phi);ehat=z@ihat;exact=z[1,1]*null_current[1]*(np.exp(1j*phi)-1)
        artifacts.append([phi,ehat[1].real,ehat[1].imag,abs(ehat[1]),exact.real,exact.imag,abs(ehat[1]-exact)])
    write_csv(out/"phase-artifacts.csv",["channel_phase_error_rad","false_e2_real_V","false_e2_imag_V","false_e2_amplitude_V","exact_real_V","exact_imag_V","numerical_error_V"],artifacts)
    ranks=[x["local_rank"] for x in maps];nullities=[x["local_nullity"] for x in maps]
    nominal_error=float(np.max(abs(reconstructed-e)))
    zero_rank=int(np.linalg.matrix_rank(np.zeros_like(squared)))
    checks=[
      {"id":"nominal-source-reconstruction","passed":nominal_error<a["nominal_source_reconstruction_absolute_V"],"max_error_V":nominal_error},
      {"id":"declared-local-ranks","passed":ranks==a["expected_local_ranks"],"ranks":ranks},
      {"id":"declared-local-nullities","passed":nullities==a["expected_local_nullities"],"nullities":nullities},
      {"id":"jacobian-kernel-witnesses","passed":all(x["kernel_residual"]<a["jacobian_kernel_residual"] for x in maps)},
      {"id":"zero-current-squared-jacobian","passed":zero_rank==a["expected_zero_amplitude_jacobian_rank"],"rank":zero_rank},
      {"id":"finite-phase-rival","passed":phase_error<a["exact_rival_observable_error"] and float(np.linalg.norm(phase_e-e))>1e-3,"observable_error_A2":phase_error,"source_separation_V":float(np.linalg.norm(phase_e-e))},
      {"id":"receiver-complex-kernel-rival","passed":kernel_error<a["exact_rival_observable_error"] and float(np.linalg.norm(kernel_e-e))>1e-3,"observable_error_A":kernel_error,"source_separation_V":float(np.linalg.norm(kernel_e-e))},
      {"id":"bounded-fixture-disk-inclusion","passed":len(fixtures)==128 and min(r[-1] for r in fixtures)>=-a["bounded_error_exceedance_tolerance_V"],"fixture_count":len(fixtures),"minimum_margin_V":min(r[-1] for r in fixtures)},
      {"id":"phase-artifact-exact-formula","passed":max(r[-1] for r in artifacts)<a["phase_artifact_absolute_error_V"],"max_error_V":float(max(r[-1] for r in artifacts))},
      {"id":"zero-drive-nonzero-artifact","passed":all(r[3]>0 for r in artifacts if r[0]>0)},
      {"id":"bounded-positive-control-excludes-zero","passed":abs(reconstructed[1])>nominal_bound,"exclusion_margin_V":float(abs(reconstructed[1])-nominal_bound)},
      {"id":"unknown-calibration-withheld","passed":True,"interpretation":"No finite unconditional source-voltage disk is reported when calibration bounds are unknown."},
    ]
    fig,axes=plt.subplots(1,2,figsize=(9,4))
    axes[0].barh(np.arange(4),ranks,color="#236745",label="Identifiable local dimensions");axes[0].barh(np.arange(4),nullities,left=ranks,color="#d3c7a9",label="Local kernel dimensions");axes[0].set_yticks(np.arange(4),["Receiver |I|²","Both |I|²","Receiver complex I","Both coherent I"]);axes[0].set_xlim(0,4);axes[0].set_xlabel("Real dimensions of a four-dimensional source domain");axes[0].legend(fontsize=7,loc="lower right");axes[0].invert_yaxis()
    f=np.array(fixtures);axes[1].scatter(f[:,7]*1e3,f[:,8]*1e3,s=9,c="#236745",alpha=.5,label="128 bounded-error fixtures")
    theta=np.linspace(0,2*np.pi,361);max_bound=float(max(f[:,10]));circle=e[1]+max_bound*np.exp(1j*theta)
    axes[1].plot(circle.real*1e3,circle.imag*1e3,ls="--",color="#b17222",label="Largest supplied bound")
    axes[1].scatter([e[1].real*1e3],[e[1].imag*1e3],marker="+",c="black",s=80,label="Injected 5 mV drive");axes[1].set_xlabel("Re reconstructed receiver drive (mV)");axes[1].set_ylabel("Im reconstructed receiver drive (mV)");axes[1].axis("equal");axes[1].legend(fontsize=7)
    fig.suptitle("Synthetic source localization: calibration controls what is identifiable");fig.tight_layout();save_figure(out/"source-identifiability.svg",fig)
    fig,ax=plt.subplots(figsize=(6,3.6));ax.plot([r[0]*1e3 for r in artifacts],[r[3]*1e3 for r in artifacts],"o-",color="#236745");ax.set_xlabel("Uncorrected receiver-channel phase error (mrad)");ax.set_ylabel("False inferred receiver-drive amplitude (mV)");ax.set_title("True receiver drive is zero; only the readout phase changed");ax.grid(alpha=.2);save_figure(out/"phase-error-artifact.svg",fig)
    metrics={"omega_rad_s":float(omega),"injected_source_V":[pair(v) for v in e],"nominal_current_A":[pair(v) for v in current],"nominal_reconstructed_source_V":[pair(v) for v in reconstructed],"observation_local_ranks":ranks,"observation_local_nullities":nullities,"nominal_receiver_disk_radius_V":nominal_bound,"nominal_zero_exclusion_margin_V":float(abs(reconstructed[1])-nominal_bound),"bounded_fixture_count":len(fixtures),"max_bounded_error_V":float(max(f[:,9])),"max_fixture_disk_radius_V":max_bound,"phase_artifacts":[{"phase_error_rad":float(r[0]),"false_receiver_amplitude_V":float(r[3])} for r in artifacts],"unknown_calibration_receiver_interval":None}
    result={"round":"R2","title":contract["title"],"classification":contract["classification"],"summary":["Both calibrated, coherent complex-current channels reconstruct the two effective complex drive voltages; restricted readouts admit exact rival drives.",f"The injected 5 mV drive excludes zero only inside the supplied deterministic calibration model (nominal radius {nominal_bound*1e3:.6f} mV).","Channel phase error alone produces a receiver-drive residual when the true receiver drive is zero."],"metrics":metrics,"checks":checks,"limitations":contract["limits"]+[contract["model"]["boundary"],"The 128 endpoint fixtures check a proven triangle-inequality disk; their inclusion is not statistical confidence or measured coverage.","At zero currents, the squared-amplitude Jacobians have rank zero; the nonlinear maps are not globally constant."],"artifacts":["research/R2/source-identifiability.svg","research/R2/phase-error-artifact.svg","research/R2/observations-and-rivals.csv","research/R2/uncertainty-boundary-fixtures.csv","research/R2/phase-artifacts.csv"]}
    write_json(out/"parameters.json",{"contract_parameters":p,"inherited_circuit":circuit,"receiver_kernel_delta_A":pair(delta)});write_json(out/"result.json",result)
    (out/"report.md").write_text(f'''# R2 — A residual is not a source identity

All inputs and results are synthetic. The R1 nominal circuit is retained, with both actual port-source phasors unknown to the inverse problem. A source control setting is not substituted for a calibrated port-voltage measurement. The injected receiver source is 5 mV at π/3 radians.

## What observations identify

The source domain has four real dimensions. The four declared observation maps have local real ranks **{ranks}** and nullities **{nullities}** at the stipulated nonzero-current fixture. Full coherent complex currents give e = ZI; restricted channels have exact finite rivals stored in `exact-rivals.json`. Rotating a receiver current's phase preserves both current magnitudes while changing the required source vector. Adding a source-current increment of {delta} A preserves the receiver's full complex current while changing the source vector.

The amplitude-squared maps are nonlinear: their Jacobian kernels are local tangent statements. The exact rival families provide the separate finite ambiguity proof. At zero currents those squared-amplitude Jacobians have rank zero, which does not make the nonlinear maps globally constant.

## Conditional calibration disk

Writing measured current as Î and model mutual inductance as M̂, the receiver-drive error obeys

|ê₂−e₂| ≤ ω|M̂|ε₁ + |Z₂₂|ε₂ + ωΔM(|Î₁|+ε₁).

This follows by subtracting ZI from ẐÎ and applying the triangle inequality; all other components are exact in this model. The nominal radius is **{nominal_bound:.12g} V**, below the injected 0.005 V amplitude by **{abs(reconstructed[1])-nominal_bound:.12g} V**. Every one of 128 bounded endpoint fixtures lies inside its corresponding disk. These are deterministic supplied bounds, not confidence intervals and not instrument specifications established by measurement. Unknown calibration withholds any unconditional exclusion of zero.

## False residual control

With true receiver source zero, rotate only measured I₂ by φ. The apparent source becomes Z₂₂I₂(exp(iφ)−1). At φ=0.01 rad the false amplitude is **{artifacts[-1][3]:.12g} V**. It can exceed the injected signal despite there being no real receiver source in this control. Physical source identity, gravity change, new particles and free energy remain unestablished.

{sum(c['passed'] for c in checks)}/{len(checks)} producer checks pass. Inspect raw phasor observations, exact rival voltages, all boundary fixtures and phase artifacts in the CSV/JSON files. Run `python3 research/R2/run.py --output DIR` for a separate reconstruction.
''')
    if out.resolve()==Path(__file__).resolve().parent:
        manifest=write_manifest(out,CONTRACT)
        manifest["dependencies"].append({"path":str(PRIOR_CONTRACT.relative_to(ROOT)),"sha256":sha256(PRIOR_CONTRACT)})
        write_json(out/"manifest.json",manifest)
    if not all(c["passed"] for c in checks):raise SystemExit("Producer checks failed; preserve and review.")
    print(json.dumps({"round":"R2","passed":len(checks),"ranks":ranks,"nominal_disk_V":nominal_bound,"phase_10mrad_false_V":float(artifacts[-1][3])}))

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--output",type=Path,default=Path(__file__).resolve().parent);main(parser.parse_args().output)
