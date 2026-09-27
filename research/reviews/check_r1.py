#!/usr/bin/env python3
"""Independent R1 algebra and exact matrix-exponential transient.

Does not import the producer or its shared helpers. Only the frozen contract,
saved producer tables/results and declared manifest are read.
"""
from pathlib import Path
import csv
import hashlib
import json
import math
import numpy as np
from scipy.integrate import simpson
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).with_name('R1-independent-checks.json')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def response(p, omega, load, coupling=None, source=None, resistance_multiplier=1):
    """Explicit two-by-two determinant, independent of a matrix solver."""
    m = p['M_H'] if coupling is None else coupling
    v = p['source_peak_V'] if source is None else source
    z1 = resistance_multiplier*p['R1_ohm'] + 1j*(omega*p['L1_H']-1/(omega*p['C1_F']))
    z2 = resistance_multiplier*p['R2_ohm'] + load + 1j*(omega*p['L2_H']-1/(omega*p['C2_F']))
    cross = 1j*omega*m
    det = z1*z2-cross*cross
    i1, i2 = v*z2/det, -v*cross/det
    ps = (v*np.conjugate(i1)).real/2
    pl = load*abs(i2)**2/2
    loss = resistance_multiplier*(p['R1_ohm']*abs(i1)**2+p['R2_ohm']*abs(i2)**2)/2
    return i1, i2, ps, pl, loss


def exact_transient(p, count):
    """Solve the constant linear forced system by a particular phasor and exp(A t).

    Capacitor voltages are state variables here; producer charges need not share
    this state representation or its time-stepping algorithm.
    """
    omega = 1/math.sqrt(p['L1_H']*p['C1_F'])
    rload = p['nominal_load_ohm']
    l = np.array([[p['L1_H'], p['M_H']], [p['M_H'], p['L2_H']]])
    c = np.diag([p['C1_F'], p['C2_F']])
    resistance = np.diag([p['R1_ohm'], p['R2_ohm']+rload])
    linv = np.linalg.inv(l)
    generator = np.block([[np.zeros((2, 2)), np.diag(1/np.diag(c))], [-linv, -linv@resistance]])
    i1, i2, *_ = response(p, omega, rload)
    ihat = np.array([i1, i2])
    vhat = ihat/(1j*omega*np.diag(c))
    xhat = np.concatenate([vhat, ihat])
    times = np.linspace(0, p['transient_end_s'], count)
    particular = np.imag(np.exp(1j*omega*times[:, None])*xhat)
    homogeneous = np.einsum('tij,j->ti', expm(times[:, None, None]*generator), -np.imag(xhat))
    state = particular + homogeneous
    currents = state[:, 2:]
    capv = state[:, :2]
    source = p['source_peak_V']*np.sin(omega*times)*currents[:, 0]
    load = rload*currents[:, 1]**2
    loss = p['R1_ohm']*currents[:, 0]**2+p['R2_ohm']*currents[:, 1]**2
    energy = (np.einsum('ti,ij,tj->t', currents, l, currents)+np.einsum('ti,ij,tj->t', capv, c, capv))/2
    works = [float(simpson(a, x=times)) for a in [source, load, loss]]
    residual = works[0]-works[1]-works[2]-float(energy[-1]-energy[0])
    return times, state, dict(source_work_J=works[0], load_work_J=works[1], winding_heat_J=works[2], stored_delta_J=float(energy[-1]-energy[0]), residual_J=residual, relative_residual=abs(residual)/max(abs(works[0]), 1e-30))


def main():
    contract_path = ROOT/'docs/contracts/R1.json'
    manifest_path = ROOT/'research/R1/manifest.json'
    c = json.loads(contract_path.read_text())
    p = c['parameters']
    m = json.loads(manifest_path.read_text())
    checks = {}
    bindings = [m['contract'], *m['dependencies'], *m['files']]
    checks['all_manifest_bindings'] = all(sha(ROOT/a['path']) == a['sha256'] for a in bindings)
    w0 = 1/math.sqrt(p['L1_H']*p['C1_F'])
    rl = p['nominal_load_ohm']
    i1, i2, ps, pl, loss = response(p, w0, rl)
    x = w0*p['M_H']
    denominator = p['R1_ohm']*(p['R2_ohm']+rl)+x*x
    closed = np.array([p['source_peak_V']*(p['R2_ohm']+rl)/denominator, -1j*x*p['source_peak_V']/denominator])
    checks['resonant_reflected_resistance_formula'] = bool(np.max(np.abs(np.array([i1, i2])-closed)) < 1e-12)
    checks['gain_above_one_below_unit_efficiency'] = bool(rl*abs(i2)/p['source_peak_V'] > 1 and 0 < pl/ps < 1)
    checks['nominal_real_power_identity'] = bool(abs(ps-pl-loss) < 1e-14)
    checks['zero_coupling_zero_receiver'] = response(p, w0, rl, coupling=0)[1] == 0
    checks['zero_source_zero_everything'] = all(v == 0 for v in response(p, w0, rl, source=0))
    reversed_response = response(p, w0, rl, coupling=-p['M_H'])
    checks['coupling_reversal_phase_and_power'] = bool(abs(reversed_response[0]-i1) < 1e-14 and abs(reversed_response[1]+i2) < 1e-14 and max(abs(a-b) for a,b in zip(reversed_response[2:], [ps, pl, loss])) < 1e-14)
    _, _, ps2, pl2, _ = response(p, w0, rl, resistance_multiplier=2)
    checks['doubled_winding_resistance_lowers_efficiency'] = bool(pl2/ps2 < pl/ps)
    grid_residual = 0.0
    efficiencies = []
    for load in p['loads_ohm']:
        for ratio in np.linspace(*p['frequency_ratio_domain'], p['frequency_points']):
            _, _, a,b,d = response(p, w0*ratio, load)
            grid_residual = max(grid_residual, abs(a-b-d)/max(a, 1e-30))
            efficiencies.append(b/a)
    checks['entire_frozen_frequency_grid_passive'] = bool(min(efficiencies) >= 0 and max(efficiencies) <= 1 and grid_residual < 1e-10)
    saved_rows = 0
    saved_current_error = 0.0
    saved_power_error = 0.0
    saved_gain_error = 0.0
    for name in ['frequency-sweep.csv', 'load-sweep.csv']:
        with (ROOT/'research/R1'/name).open(newline='') as stream:
            for row in csv.DictReader(stream):
                row = {key: float(value) for key, value in row.items()}
                a,b,power,pload,heat = response(p, row['omega_rad_s'], row['load_ohm'])
                saved_current_error = max(saved_current_error, abs(a-complex(row['i1_real_A'], row['i1_imag_A'])), abs(b-complex(row['i2_real_A'], row['i2_imag_A'])))
                saved_power_error = max(saved_power_error, abs(power-row['source_power_W']), abs(pload-row['load_power_W']), abs(heat-row['winding_loss_W']))
                saved_gain_error = max(saved_gain_error, abs(row['load_ohm']*abs(b)/p['source_peak_V']-row['voltage_gain']))
                saved_rows += 1
    checks['all_saved_phasor_rows_match_independent_formula'] = saved_rows == len(p['loads_ohm'])*p['frequency_points']+p['load_points'] and max(saved_current_error, saved_power_error, saved_gain_error) < 1e-12
    inductance = np.array([[p['L1_H'], p['M_H']], [p['M_H'], p['L2_H']]])
    checks['positive_definite_storage'] = bool(np.linalg.eigvalsh(inductance).min() > 0)
    checks['critical_coupling_is_excluded_singular_boundary'] = bool(abs(p['M_H']) < math.sqrt(p['L1_H']*p['L2_H']) and math.isclose(p['L1_H']*p['L2_H']-math.sqrt(p['L1_H']*p['L2_H'])**2, 0, abs_tol=1e-18))
    ts = []
    saved_transient_current_error = 0.0
    saved_transient_charge_error = 0.0
    saved_transient_files = 0
    for count in p['transient_samples']:
        time, state, budget = exact_transient(p, count)
        ts.append(dict(samples=count, **budget))
        for path in sorted((ROOT/'research/R1').glob(f'transient-n{count}-*.csv')):
            rows = np.genfromtxt(path, delimiter=',', names=True)
            assert len(rows) == count and np.max(abs(rows['time_s']-time)) < 1e-14
            saved_transient_current_error = max(saved_transient_current_error, float(np.max(abs(rows['i1_A']-state[:, 2]))), float(np.max(abs(rows['i2_A']-state[:, 3]))))
            saved_transient_charge_error = max(saved_transient_charge_error, float(np.max(abs(rows['q1_C']-state[:, 0]*p['C1_F']))), float(np.max(abs(rows['q2_C']-state[:, 1]*p['C2_F']))))
            saved_transient_files += 1
    checks['all_three_saved_transients_match_matrix_exponential'] = saved_transient_files == 3 and saved_transient_current_error < 1e-8 and saved_transient_charge_error < 1e-11
    checks['independent_exact_transient_budget'] = all(t['relative_residual'] < c['acceptance']['transient_relative_energy_residual'] for t in ts)
    grid_difference = max(abs(ts[0][key]-ts[1][key])/max(abs(ts[1]['source_work_J']), 1e-30) for key in ['source_work_J', 'load_work_J', 'winding_heat_J', 'stored_delta_J'])
    checks['independent_transient_grid_convergence'] = grid_difference < c['acceptance']['transient_grid_energy_difference_relative']
    producer = json.loads((ROOT/'research/R1/result.json').read_text())
    checks['producer_nominal_claims_match_independent_result'] = bool(abs(producer['metrics']['nominal']['efficiency']-pl/ps) < 1e-12 and abs(producer['metrics']['nominal']['voltage_gain']-rl*abs(i2)/p['source_peak_V']) < 1e-12)
    result = dict(round='R1', method='Explicit complex determinant and reflected impedance; capacitor-voltage-state matrix exponential with independent external Simpson quadrature', checks=checks, nominal=dict(omega_rad_s=w0, source_current_peak_A=[i1.real, i1.imag], receiver_current_peak_A=[i2.real, i2.imag], gain=rl*abs(i2)/p['source_peak_V'], source_W=ps, load_W=pl, winding_W=loss, efficiency=pl/ps), independent_grid=dict(max_relative_power_residual=grid_residual, efficiency_range=[min(efficiencies), max(efficiencies)]), saved_output_comparison=dict(phasor_rows=saved_rows, max_current_error_A=saved_current_error, max_power_error_W=saved_power_error, max_voltage_gain_error=saved_gain_error, transient_files=saved_transient_files, max_transient_current_error_A=saved_transient_current_error, max_transient_charge_error_C=saved_transient_charge_error), transients=ts, grid_relative_difference=grid_difference)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n')
    if not all(checks.values()):
        raise SystemExit('Failed checks: '+str([k for k,v in checks.items() if not v]))
    print(json.dumps(dict(round='R1', checks=len(checks), passed=all(checks.values()), nominal=result['nominal'], transient=result['transients'][-1]), indent=2))


if __name__ == '__main__':
    main()
