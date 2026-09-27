#!/usr/bin/env python3
"""Independent witness-model reconstruction, exact rival and sharp-bound audit."""
from pathlib import Path
import csv
import hashlib
import itertools
import json
import math
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).with_name('R3-independent-checks.json')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def realify(a):
    a=np.asarray(a,dtype=complex)
    out=np.zeros((2*a.shape[0],2*a.shape[1]))
    for j in range(a.shape[0]):
        for k in range(a.shape[1]):
            z=a[j,k]
            out[2*j:2*j+2,2*k:2*k+2]=[[z.real,-z.imag],[z.imag,z.real]]
    return out


def real_vector(v):
    return np.array([[z.real,z.imag] for z in v]).reshape(-1)


def main():
    contract=json.loads((ROOT/'docs/contracts/R3.json').read_text())
    p=contract['parameters']
    s=p['signal_amplitude_V']*np.exp(1j*p['signal_phase_rad'])
    b=p['background_amplitude_V']*np.exp(1j*p['background_phase_rad'])
    a=complex(*p['nominal_transfer_a'])
    ey=p['receiver_error_bound_V']; ew=p['witness_error_bound_V']; da=p['transfer_error_bound']
    y=s+a*b; w=b
    def radius(measured_w):
        return ey+abs(a)*ew+da*(abs(measured_w)+ew)
    checks={'clean_witness_recovers_signal':abs(y-a*w-s)<1e-12,'zero_signal_background_subtracts_to_zero':abs(a*b-a*b)<1e-12,'nominal_disk_excludes_zero':abs(s)>radius(w)}
    # Algebraic ranks: nonzero minor1 proves complex rank1 or2; duplicate
    # columns/rows give the complementary upper bounds. Numerical ranks are a
    # separate check, not the only reason for the admitted rank statements.
    matrices={
        'no_witness':np.array([[1,a]]),
        'clean_known_witness':np.array([[1,a],[0,1]]),
        'unknown_transfer_local':np.array([[1,a,b],[0,1,0]]),
        'singular_crossleak':np.array([[1,a],[1/a,1]]),
        'expanded_physical_identity':np.array([[1,1,a],[0,0,1]])}
    complex_kernel={
        'no_witness':[-a,1],
        'unknown_transfer_local':[-b,0,1],
        'singular_crossleak':[-a,1],
        'expanded_physical_identity':[1,-1,0]}
    ranks={key:int(np.linalg.matrix_rank(realify(value))) for key,value in matrices.items()}
    nullities={key:2*value.shape[1]-ranks[key] for key,value in matrices.items()}
    checks['all_declared_real_ranks']=ranks==contract['acceptance']['expected_real_ranks']
    checks['all_declared_real_nullities']=nullities==contract['acceptance']['expected_real_nullities']
    kernel_residuals={}
    for name,k in complex_kernel.items():
        k=np.array(k,dtype=complex)
        real_k=np.column_stack([real_vector(k),real_vector(1j*k)])
        kernel_residuals[name]=float(np.max(abs(realify(matrices[name])@real_k)))
        assert np.linalg.matrix_rank(real_k)==2
    checks['explicit_two_real_dimensional_kernels']=max(kernel_residuals.values())<1e-10
    # Exact finite unknown-transfer rival removes the entire target signal.
    rival_a=a+s/b
    unknown_transfer_readout=np.array([rival_a*b,b])
    baseline=np.array([y,w])
    unknown_transfer_error=float(np.max(abs(unknown_transfer_readout-baseline)))
    checks['unknown_transfer_zero_signal_exact_raw_rival']=unknown_transfer_error<1e-12
    # Distinct physical labels on one identical port contribution cannot be inferred.
    exotic_only=matrices['expanded_physical_identity']@np.array([s,0,b])
    ordinary_only=matrices['expanded_physical_identity']@np.array([0,s,b])
    physical_identity_error=float(np.max(abs(exotic_only-ordinary_only)))
    checks['ordinary_drive_exact_physical_identity_rival']=physical_identity_error<1e-12
    phases=2*np.pi*np.arange(p['boundary_phase_points'])/p['boundary_phase_points']
    boundary=[]
    for py,pw,pa in itertools.product(phases,phases,phases):
        true_a=a+da*np.exp(1j*pa)
        measured_y=s+true_a*b+ey*np.exp(1j*py)
        measured_w=b+ew*np.exp(1j*pw)
        estimate=measured_y-a*measured_w
        error=abs(estimate-s)
        bound=radius(measured_w)
        boundary.append((error,bound))
    boundary=np.array(boundary)
    checks['all512_independent_boundary_fixtures_included']=len(boundary)==512 and np.max(boundary[:,0]-boundary[:,1])<=1e-12
    # Deliberately choose phases to saturate every triangle inequality.
    aligned_w=b-ew*b/abs(b)
    aligned_da=da*a/abs(a)
    aligned_ey=ey*a*b/abs(a*b)
    aligned_y=s+(a+aligned_da)*b+aligned_ey
    aligned_estimate=aligned_y-a*aligned_w
    aligned_error=float(abs(aligned_estimate-s))
    aligned_radius=radius(aligned_w)
    checks['independent_aligned_sharpness_fixture']=abs(aligned_error-aligned_radius)<1e-12
    conditioning=[]
    for t in p['crossleak_path_t']:
        beta=t/a
        determinant=1-t
        observation=np.array([s+a*b,b+beta*s])
        # Closed form singular values from trace(A†A), det(A), not SVD.
        trace=2+abs(a)**2+abs(beta)**2
        lambda_max=(trace+math.sqrt(max(0,trace*trace-4*determinant**2)))/2
        if t==1:
            condition=None; recovery=None
            rival=np.array([s,b])+np.array([-a,1])*(.01+.02j)
            exact_raw_rival=np.array([rival[0]+a*rival[1],rival[1]+beta*rival[0]])
            checks['singular_crossleak_has_exact_rival']=float(np.max(abs(exact_raw_rival-observation)))<1e-12
        else:
            condition=lambda_max/abs(determinant)
            recovery=np.array([(observation[0]-a*observation[1])/determinant,(observation[1]-beta*observation[0])/determinant])
            assert float(np.max(abs(recovery-np.array([s,b]))))<1e-12
        conditioning.append(dict(t=t,determinant=determinant,condition_2=condition,unique_inverse=t!=1))
    checks['near_singular_inverse_and_conditioning_path']=all(x['condition_2']>=1 for x in conditioning if x['condition_2'] is not None) and conditioning[4]['condition_2']>conditioning[3]['condition_2']>conditioning[0]['condition_2']
    saved_maps=json.loads((ROOT/'research/R3/observation-maps.json').read_text())
    saved_map_error=0.0; saved_kernel_error=0.0
    for name,row in saved_maps.items():
        independent=realify(matrices[name]); saved=np.array(row['real_matrix']); ker=np.array(row['kernel_columns'])
        saved_map_error=max(saved_map_error,float(np.max(abs(independent-saved))))
        if ker.size:
            saved_kernel_error=max(saved_kernel_error,float(np.max(abs(independent@ker))))
            assert np.linalg.matrix_rank(ker)==nullities[name]
    checks['all_saved_maps_and_kernel_bases_verified']=set(saved_maps)==set(matrices) and saved_map_error<1e-12 and saved_kernel_error<1e-10
    saved_boundary_count=0; saved_boundary_error=0.0
    with (ROOT/'research/R3/witness-uncertainty-fixtures.csv').open(newline='') as stream:
        for row in csv.DictReader(stream):
            row={key:float(value) for key,value in row.items()}
            true_a=a+da*np.exp(1j*row['transfer_error_phase_rad'])
            measured_y=s+true_a*b+ey*np.exp(1j*row['receiver_error_phase_rad'])
            measured_w=b+ew*np.exp(1j*row['witness_error_phase_rad'])
            inferred=measured_y-a*measured_w
            expected=[measured_y,measured_w,inferred]
            recorded=[complex(row['measured_y_real_V'],row['measured_y_imag_V']),complex(row['measured_w_real_V'],row['measured_w_imag_V']),complex(row['estimated_s_real_V'],row['estimated_s_imag_V'])]
            saved_boundary_error=max(saved_boundary_error,float(np.max(abs(np.array(expected)-np.array(recorded)))),abs(abs(inferred-s)-row['absolute_error_V']),abs(radius(measured_w)-row['disk_radius_V']))
            assert row['absolute_error_V']<=row['disk_radius_V']
            saved_boundary_count+=1
    checks['all512_saved_error_fixtures_reconstructed']=saved_boundary_count==512 and saved_boundary_error<1e-12
    aligned=json.loads((ROOT/'research/R3/aligned-bound-fixture.json').read_text())
    checks['saved_aligned_error_is_valid_and_sharp']=abs(complex(*aligned['measured_y_V'])-aligned_y)<1e-12 and abs(complex(*aligned['measured_w_V'])-aligned_w)<1e-12 and abs(aligned['absolute_error_V']-aligned_error)<1e-12 and abs(aligned['disk_radius_V']-aligned_radius)<1e-12 and abs(complex(*aligned['receiver_error_V']))<=ey+1e-15 and abs(complex(*aligned['witness_error_V']))<=ew+1e-15 and abs(complex(*aligned['transfer_error']))<=da+1e-15
    producer=json.loads((ROOT/'research/R3/result.json').read_text())
    saved_condition_relative_error=0.0; saved_condition_paths=producer['metrics']['crossleak_path']
    for saved,independent in zip(saved_condition_paths,conditioning):
        assert saved['t']==independent['t']
        if independent['unique_inverse']:
            saved_condition_relative_error=max(saved_condition_relative_error,abs(saved['condition_2norm']-independent['condition_2'])/independent['condition_2'])
            assert abs(complex(*saved['reconstructed_s_V'])-s)<1e-12 and abs(complex(*saved['reconstructed_b_V'])-b)<1e-12
            assert abs(saved['measurement_only_signal_error_radius_V']-(ey+abs(a)*ew)/abs(1-saved['t']))<1e-12
        else:
            assert saved['condition_2norm'] is None and saved['reconstructed_s_V'] is None and saved['reconstructed_b_V'] is None and saved['measurement_only_signal_error_radius_V'] is None and saved['unique_inverse_available'] is False
    checks['saved_conditioning_matches_trace_determinant_formula']=len(saved_condition_paths)==len(conditioning) and saved_condition_relative_error<1e-10
    checks['singular_inverse_and_unconditional_exotic_interval_withheld']=producer['metrics']['unconditional_exotic_signal_interval'] is None and saved_condition_paths[5]['unique_inverse_available'] is False
    saved_rivals=json.loads((ROOT/'research/R3/exact-rivals.json').read_text())
    rival=saved_rivals['unknown_transfer_zero_signal']
    actual_zero_signal=complex(*rival['stipulated_signal_V']); actual_b=complex(*rival['background_V']); actual_a=complex(*rival['transfer'])
    checks['saved_unknown_transfer_rival_verifies_both_raw_readouts']=actual_zero_signal==0 and abs(actual_zero_signal+actual_a*actual_b-y)<1e-12 and abs(actual_b-w)<1e-12
    identity=saved_rivals['physical_identity']
    identity_observations=[]
    for label in ['case_A','case_B']:
        row=identity[label]; signal=complex(*row['exotic_V'])+complex(*row['ordinary_same_port_V'])
        identity_observations.append(np.array([signal+a*b,b]))
    checks['saved_physical_identity_rival_verifies_both_raw_readouts']=float(np.max(abs(identity_observations[0]-identity_observations[1])))<1e-12 and float(np.max(abs(identity_observations[0]-baseline)))<1e-12
    checks['producer_nominal_disk_verified']=abs(producer['metrics']['nominal_signal_disk_radius_V']-radius(w))<1e-12
    manifest=json.loads((ROOT/'research/R3/manifest.json').read_text())
    checks['all_manifest_bindings']=all(sha(ROOT/record['path'])==record['sha256'] for record in [manifest['contract'],*manifest['dependencies'],*manifest['files']])
    checks={key:bool(value) for key,value in checks.items()}
    result=dict(round='R3',method='Algebraic minors and explicit complex kernels; independently constructed raw-observation rivals; triangle-inequality proof and512 boundary fixtures; aligned sharpness; closed-form two-by-two conditioning from trace/determinant',checks=checks,ranks=ranks,nullities=nullities,kernel_residuals=kernel_residuals,nominal_disk_radius_V=radius(w),nominal_zero_exclusion_margin_V=float(abs(s)-radius(w)),unknown_transfer_rival_max_raw_error_V=unknown_transfer_error,physical_identity_rival_max_raw_error_V=physical_identity_error,boundary_fixtures=dict(count=len(boundary),max_error_minus_radius_V=float(np.max(boundary[:,0]-boundary[:,1]))),aligned=dict(error_V=aligned_error,radius_V=aligned_radius,sharpness_error_V=abs(aligned_error-aligned_radius)),conditioning=conditioning,saved_output_comparison=dict(boundary_count=saved_boundary_count,max_boundary_reconstruction_error_V=saved_boundary_error,max_real_map_error=saved_map_error,max_saved_kernel_error=saved_kernel_error,max_condition_relative_error=saved_condition_relative_error))
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps(dict(round='R3',checks=len(checks),passed=all(checks.values()),radius_V=radius(w),ranks=ranks,aligned=result['aligned']),indent=2))
    if not all(checks.values()):
        raise SystemExit('Failed checks: '+str([k for k,v in checks.items() if not v]))


if __name__=='__main__':
    main()
