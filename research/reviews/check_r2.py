#!/usr/bin/env python3
"""Independent real-map/null-space and deterministic complex-disk checks."""
from pathlib import Path
import csv
import hashlib
import itertools
import json
import math
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).with_name('R2-independent-checks.json')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pair(z):
    return np.array([z[0].real, z[0].imag, z[1].real, z[1].imag])


def real_matrix(z):
    a = np.zeros((4,4))
    for j in range(2):
        for k in range(2):
            a[2*j:2*j+2,2*k:2*k+2] = [[z[j,k].real,-z[j,k].imag],[z[j,k].imag,z[j,k].real]]
    return a


def currents(z, e):
    """Explicit complex determinant, never producer solver."""
    det = z[0,0]*z[1,1]-z[0,1]*z[1,0]
    return np.array([(z[1,1]*e[0]-z[0,1]*e[1])/det, (-z[1,0]*e[0]+z[0,0]*e[1])/det])


def main():
    c = json.loads((ROOT/'docs/contracts/R2.json').read_text())
    p = c['parameters']
    inherited = json.loads((ROOT/'docs/contracts/R1.json').read_text())['parameters']
    omega = 1/math.sqrt(inherited['L1_H']*inherited['C1_F'])
    mutual = inherited['M_H']
    z = np.array([[inherited['R1_ohm']+1j*(omega*inherited['L1_H']-1/(omega*inherited['C1_F'])), 1j*omega*mutual],[1j*omega*mutual,inherited['R2_ohm']+inherited['nominal_load_ohm']+1j*(omega*inherited['L2_H']-1/(omega*inherited['C2_F']))]])
    e = np.array([complex(*p['source1_complex_V']), p['injected_receiver_amplitude_V']*np.exp(1j*p['injected_receiver_phase_rad'])])
    i = currents(z,e)
    zr = real_matrix(z)
    # Independent real observation generator H, obtained from scalar determinant.
    h = np.column_stack([pair(currents(z,np.array(v,dtype=complex))) for v in [[1,0],[1j,0],[0,1],[0,1j]]])
    gradient_receiver_squared = np.array([[0,0,2*i[1].real,2*i[1].imag]])
    gradient_both_squared = np.array([[2*i[0].real,2*i[0].imag,0,0],[0,0,2*i[1].real,2*i[1].imag]])
    jacobians = [gradient_receiver_squared@h, gradient_both_squared@h, h[2:,:], h]
    ranks = [int(np.linalg.matrix_rank(a)) for a in jacobians]
    nullities = [4-r for r in ranks]
    # Construct kernels geometrically in current coordinates, then map to drive coordinates.
    kernels = [np.column_stack([pair(z@np.array(v)) for v in [[1,0],[1j,0],[0,1j*i[1]]]]),np.column_stack([pair(z@np.array(v)) for v in [[1j*i[0],0],[0,1j*i[1]]]]),np.column_stack([pair(z@np.array(v)) for v in [[1,0],[1j,0]]]),np.zeros((4,0))]
    kernel_residuals = [float(np.max(abs(a@k))) if k.size else 0.0 for a,k in zip(jacobians,kernels)]
    checks = {'real_map_inverse':bool(np.max(abs(zr@h-np.eye(4)))<1e-12),'expected_local_ranks':ranks==[1,2,2,4],'expected_local_nullities':nullities==[3,2,2,0],'explicit_kernel_bases':all(np.linalg.matrix_rank(k)==n and err<1e-10 for k,n,err in zip(kernels,nullities,kernel_residuals) if n),'zero_squared_amplitude_boundary_rank0':np.linalg.matrix_rank(np.zeros((2,4))@h)==0,'coherent_source_reconstruction':bool(np.max(abs(z@i-e))<1e-12)}
    # A finite source change invisible to the complete complex receiver channel.
    delta = 0.037+0.011j
    alternate_i = i+np.array([delta,0])
    alternate_e = z@alternate_i
    recovered = currents(z,alternate_e)
    checks['finite_complex_receiver_rival'] = bool(abs(recovered[1]-i[1])<1e-12 and np.linalg.norm(alternate_e-e)>.1)
    phase_i = i*np.array([1,np.exp(1j*p['finite_rival_receiver_phase_rotation_rad'])])
    phase_e = z@phase_i
    phase_back = currents(z,phase_e)
    checks['finite_two_amplitude_rival'] = bool(np.max(abs(abs(phase_back)**2-abs(i)**2))<1e-12 and np.linalg.norm(phase_e-e)>.1)
    eps = p['current_error_bounds_A']
    dm = p['mutual_inductance_error_bound_H']
    def bound(observed):
        return omega*abs(mutual)*eps[0]+abs(z[1,1])*eps[1]+omega*dm*(abs(observed[0])+eps[0])
    nominal_radius = bound(i)
    checks['nominal_disk_excludes_zero'] = bool(abs(e[1])>nominal_radius)
    boundary_rows = []
    phases = 2*np.pi*np.arange(p['error_phase_points'])/p['error_phase_points']
    for sign, ph1, ph2 in itertools.product([-1,1],phases,phases):
        actual_z=z.copy()
        actual_z[0,1]=actual_z[1,0]=1j*omega*(mutual+sign*dm)
        actual_i=currents(actual_z,e)
        noisy_i=actual_i+np.array(eps)*np.exp(1j*np.array([ph1,ph2]))
        estimate=z@noisy_i
        radius=bound(noisy_i)
        error=abs(estimate[1]-e[1])
        boundary_rows.append((error,radius))
    boundary=np.array(boundary_rows)
    checks['all_128_boundary_disks_contain_truth'] = bool(len(boundary)==128 and np.max(boundary[:,0]-boundary[:,1])<=1e-12)
    # This is an algebraic triangle-inequality bound for all disk phases; the128
    # sampled phase endpoints are checks, not a probabilistic coverage assertion.
    zero_i=currents(z,np.array([e[0],0]))
    artifact=[]
    for phase in p['phase_error_grid_rad']:
        measured=zero_i*np.array([1,np.exp(1j*phase)])
        inferred=(z@measured)[1]
        exact=z[1,1]*zero_i[1]*(np.exp(1j*phase)-1)
        artifact.append(dict(phase_rad=phase,inferred_amplitude_V=float(abs(inferred)),exact_amplitude_V=float(abs(exact)),error_V=float(abs(inferred-exact))))
    checks['phase_skew_exact_artifact'] = max(a['error_V'] for a in artifact)<1e-12
    checks['zero_phase_zero_residual_nonzero_phase_false_residual'] = artifact[0]['inferred_amplitude_V']<1e-12 and all(a['inferred_amplitude_V']>0 for a in artifact[1:])
    saved_maps=json.loads((ROOT/'research/R2/observation-maps.json').read_text())
    saved_jacobian_error=0.0
    saved_kernel_error=0.0
    for row,independent_jacobian,expected_nullity in zip(saved_maps,jacobians,nullities):
        jac=np.array(row['jacobian'])
        ker=np.array(row['kernel_columns'])
        saved_jacobian_error=max(saved_jacobian_error,float(np.max(abs(jac-independent_jacobian))))
        if ker.size:
            saved_kernel_error=max(saved_kernel_error,float(np.max(abs(independent_jacobian@ker))))
            assert np.linalg.matrix_rank(ker)==expected_nullity
    checks['saved_jacobians_and_kernel_bases_verified'] = len(saved_maps)==4 and saved_jacobian_error<1e-12 and saved_kernel_error<1e-10
    saved_boundary_count=0
    saved_boundary_error=0.0
    with (ROOT/'research/R2/uncertainty-boundary-fixtures.csv').open(newline='') as stream:
        for row in csv.DictReader(stream):
            row={key:float(value) for key,value in row.items()}
            ztrue=z.copy(); ztrue[0,1]=ztrue[1,0]=1j*omega*row['true_mutual_H']
            truth=currents(ztrue,e)
            readout=truth+np.array(eps)*np.exp(1j*np.array([row['i1_error_phase_rad'],row['i2_error_phase_rad']]))
            estimate=z@readout
            reconstructed_i=np.array([complex(row['measured_i1_real_A'],row['measured_i1_imag_A']),complex(row['measured_i2_real_A'],row['measured_i2_imag_A'])])
            reconstructed_e2=complex(row['reconstructed_e2_real_V'],row['reconstructed_e2_imag_V'])
            saved_boundary_error=max(saved_boundary_error,float(np.max(abs(readout-reconstructed_i))),float(abs(estimate[1]-reconstructed_e2)),float(abs(bound(readout)-row['disk_radius_V'])),float(abs(abs(estimate[1]-e[1])-row['absolute_error_V'])))
            assert row['absolute_error_V']<=row['disk_radius_V']
            saved_boundary_count+=1
    checks['all128_saved_fixtures_independently_reconstructed'] = saved_boundary_count==128 and saved_boundary_error<1e-12
    rivals=json.loads((ROOT/'research/R2/exact-rivals.json').read_text())
    saved_rival_error=0.0
    for row in rivals:
        source=np.array([complex(*v) for v in row['source_V']])
        saved_current=np.array([complex(*v) for v in row['current_A']])
        saved_rival_error=max(saved_rival_error,float(np.max(abs(currents(z,source)-saved_current))))
    checks['all_saved_rival_drive_vectors_verified'] = len(rivals)==3 and saved_rival_error<1e-12
    producer=json.loads((ROOT/'research/R2/result.json').read_text())
    checks['producer_nominal_disk_and_ranks_verified'] = abs(producer['metrics']['nominal_receiver_disk_radius_V']-nominal_radius)<1e-12 and producer['metrics']['observation_local_ranks']==ranks and producer['metrics']['observation_local_nullities']==nullities
    checks['unknown_calibration_result_withheld'] = producer['metrics']['unknown_calibration_receiver_interval'] is None
    manifest=json.loads((ROOT/'research/R2/manifest.json').read_text())
    checks['all_manifest_bindings']=all(sha(ROOT/a['path'])==a['sha256'] for a in [manifest['contract'],*manifest['dependencies'],*manifest['files']])
    checks={key:bool(value) for key,value in checks.items()}
    result=dict(round='R2',method='Explicit complex determinant; real observation derivatives; geometrically constructed null bases and exact finite phase/source rivals; triangle-inequality disk and 128 error-boundary checks',checks=checks,ranks=ranks,nullities=nullities,kernel_residuals=kernel_residuals,nominal_current_real_coordinates_A=pair(i).tolist(),nominal_reconstruction_disk_radius_V=nominal_radius,nominal_exclusion_margin_V=float(abs(e[1])-nominal_radius),independent_boundary_fixtures=dict(count=len(boundary),max_error_V=float(boundary[:,0].max()),max_error_minus_radius_V=float((boundary[:,0]-boundary[:,1]).max())),saved_output_comparison=dict(boundary_count=saved_boundary_count,max_boundary_reconstruction_error=saved_boundary_error,max_saved_rival_current_error_A=saved_rival_error,max_jacobian_error=saved_jacobian_error,max_saved_kernel_error=saved_kernel_error),phase_artifacts=artifact,limitations=['Finite covariance-free supplied bounds, not observed detector sensitivity or confidence intervals.','All four real drive coordinates are identifiable only with calibrated Z and a shared phase reference.','An effective electrical residual has no particle or gravity identity in this model.'])
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps(dict(round='R2',checks=len(checks),passed=all(checks.values()),ranks=ranks,nominal_radius_V=nominal_radius,phase_artifacts=artifact),indent=2))
    if not all(checks.values()):
        raise SystemExit('Failed checks: '+str([k for k,v in checks.items() if not v]))


if __name__=='__main__':
    main()
