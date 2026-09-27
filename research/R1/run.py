#!/usr/bin/env python3
"""Frozen-contract, passive coupled-resonator experiment; all values synthetic."""
from pathlib import Path
import argparse
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.numerics import ROOT, np, plt, write_json, write_csv, save_figure, write_manifest
from scipy.integrate import solve_ivp, simpson

CONTRACT = ROOT / "docs/contracts/R1.json"

def phasor(omega, load, p, mutual=None, voltage=None, winding_scale=1):
    M = p["M_H"] if mutual is None else mutual
    V = p["source_peak_V"] if voltage is None else voltage
    R1, R2 = p["R1_ohm"] * winding_scale, p["R2_ohm"] * winding_scale
    z = np.array([[R1 + 1j * (omega * p["L1_H"] - 1 / (omega * p["C1_F"])), 1j * omega * M],
                  [1j * omega * M, R2 + load + 1j * (omega * p["L2_H"] - 1 / (omega * p["C2_F"]))]])
    current = np.linalg.solve(z, np.array([V, 0]))
    source = float(np.real(V * np.conjugate(current[0])) / 2)
    load_power = float(load * abs(current[1]) ** 2 / 2)
    loss = float((R1 * abs(current[0]) ** 2 + R2 * abs(current[1]) ** 2) / 2)
    return {"omega_rad_s": float(omega), "load_ohm": float(load), "i1_real_A": float(current[0].real), "i1_imag_A": float(current[0].imag), "i2_real_A": float(current[1].real), "i2_imag_A": float(current[1].imag), "source_power_W": source, "load_power_W": load_power, "winding_loss_W": loss, "voltage_gain": float(load * abs(current[1]) / abs(V)) if V else 0.0, "efficiency": load_power / source if source else 0.0, "power_residual_W": source - load_power - loss}

def transient(p, samples, rtol):
    L = np.array([[p["L1_H"], p["M_H"]], [p["M_H"], p["L2_H"]]])
    R = np.array([p["R1_ohm"], p["R2_ohm"] + p["nominal_load_ohm"]])
    C = np.array([p["C1_F"], p["C2_F"]])
    omega = 1 / np.sqrt(p["L1_H"] * p["C1_F"])
    def rhs(t, y):
        return np.r_[y[2:], np.linalg.solve(L, np.array([p["source_peak_V"] * np.sin(omega*t), 0]) - R*y[2:] - y[:2]/C)]
    times = np.linspace(0, p["transient_end_s"], samples)
    solution = solve_ivp(rhs, (0, times[-1]), np.zeros(4), t_eval=times, method="DOP853", rtol=rtol, atol=rtol*1e-5)
    if not solution.success:
        raise RuntimeError(solution.message)
    charge, current = solution.y[:2], solution.y[2:]
    source = p["source_peak_V"] * np.sin(omega*times) * current[0]
    load = p["nominal_load_ohm"] * current[1]**2
    winding = p["R1_ohm"] * current[0]**2 + p["R2_ohm"] * current[1]**2
    energy = .5 * (np.einsum("it,ij,jt->t", current, L, current) + np.sum(charge**2 / C[:,None], axis=0))
    source_work, load_heat, winding_heat = [float(simpson(v, x=times)) for v in (source, load, winding)]
    residual = source_work - load_heat - winding_heat - float(energy[-1] - energy[0])
    metrics = {"samples": samples, "rtol": rtol, "source_work_J": source_work, "load_heat_J": load_heat, "winding_heat_J": winding_heat, "stored_energy_change_J": float(energy[-1]-energy[0]), "residual_J": residual, "relative_residual": abs(residual)/max(abs(source_work),1e-30)}
    rows = np.column_stack([times, charge.T, current.T, source, load, winding, energy])
    return metrics, rows

def main(out):
    out.mkdir(parents=True, exist_ok=True)
    contract = json.loads(CONTRACT.read_text()); p = contract["parameters"]; a = contract["acceptance"]
    omega0 = 1 / np.sqrt(p["L1_H"] * p["C1_F"])
    ratios = np.linspace(*p["frequency_ratio_domain"], p["frequency_points"])
    sweep = [phasor(omega0*x, load, p) for load in p["loads_ohm"] for x in ratios]
    columns = list(sweep[0]); write_csv(out/"frequency-sweep.csv", columns, ([row[k] for k in columns] for row in sweep))
    loads = np.geomspace(*p["load_log_domain_ohm"], p["load_points"])
    load_sweep = [phasor(omega0, load, p) for load in loads]
    write_csv(out/"load-sweep.csv", columns, ([row[k] for k in columns] for row in load_sweep))
    nominal = phasor(omega0,p["nominal_load_ohm"],p)
    rt = p["R2_ohm"] + p["nominal_load_ohm"]
    reflected = (omega0*p["M_H"])**2/rt
    i1_closed = p["source_peak_V"]/(p["R1_ohm"]+reflected)
    i2_closed = -1j*omega0*p["M_H"]*i1_closed/rt
    closed_error = max(abs(complex(nominal["i1_real_A"],nominal["i1_imag_A"])-i1_closed)/abs(i1_closed), abs(complex(nominal["i2_real_A"],nominal["i2_imag_A"])-i2_closed)/abs(i2_closed))
    no_coupling = phasor(omega0,p["nominal_load_ohm"],p,mutual=0)
    no_source = phasor(omega0,p["nominal_load_ohm"],p,voltage=0)
    reverse = phasor(omega0,p["nominal_load_ohm"],p,mutual=-p["M_H"])
    more_loss = phasor(omega0,p["nominal_load_ohm"],p,winding_scale=2)
    transients=[]
    for n, tol in [(p["transient_samples"][0],1e-10),(p["transient_samples"][1],1e-10),(p["transient_samples"][1],1e-12)]:
        data, rows = transient(p,n,tol); transients.append(data)
        write_csv(out/f"transient-n{n}-rtol{tol:.0e}.csv",["time_s","q1_C","q2_C","i1_A","i2_A","source_power_W","load_power_W","winding_power_W","stored_energy_J"],rows)
    sampled=sweep+load_sweep
    power_error=max(abs(r["power_residual_W"])/r["source_power_W"] for r in sampled)
    winding_phase_error=abs(complex(reverse["i2_real_A"],reverse["i2_imag_A"])+complex(nominal["i2_real_A"],nominal["i2_imag_A"]))
    reverse_power_error=max(abs(reverse[k]-nominal[k]) for k in ["source_power_W","load_power_W","winding_loss_W"])
    grid_difference=abs(transients[1]["source_work_J"]-transients[0]["source_work_J"])/abs(transients[1]["source_work_J"])
    tight_difference=abs(transients[2]["source_work_J"]-transients[1]["source_work_J"])/abs(transients[2]["source_work_J"])
    checks=[
      {"id":"positive-inductance", "passed":bool(np.min(np.linalg.eigvalsh([[p["L1_H"],p["M_H"]],[p["M_H"],p["L2_H"]]]))>0)},
      {"id":"phasor-power-closure", "passed":power_error<a["phasor_relative_power_balance"], "max_relative_residual":power_error},
      {"id":"closed-form-at-resonance", "passed":closed_error<a["resonance_closed_form_relative_error"],"max_relative_error":closed_error},
      {"id":"zero-coupling", "passed":abs(no_coupling["i2_real_A"])+abs(no_coupling["i2_imag_A"])<a["control_absolute_tolerance"]},
      {"id":"zero-source", "passed":all(abs(no_source[k])<a["control_absolute_tolerance"] for k in ["i1_real_A","i1_imag_A","i2_real_A","i2_imag_A"])},
      {"id":"mutual-sign-phase", "passed":winding_phase_error<a["control_absolute_tolerance"],"absolute_error_A":winding_phase_error},
      {"id":"mutual-sign-powers", "passed":reverse_power_error<a["control_absolute_tolerance"],"absolute_error_W":reverse_power_error},
      {"id":"doubled-winding-loss", "passed":more_loss["efficiency"]<nominal["efficiency"]},
      {"id":"transient-quadrature-closure", "passed":all(x["relative_residual"]<a["transient_relative_energy_residual"] for x in transients)},
      {"id":"transient-grid-refinement", "passed":grid_difference<a["transient_grid_energy_difference_relative"],"relative_difference":grid_difference},
      {"id":"transient-solver-refinement", "passed":tight_difference<a["transient_grid_energy_difference_relative"],"relative_difference":tight_difference},
      {"id":"passive-sampled-efficiency", "passed":all(-a["all_sampled_efficiencies_in_0_1_with_tolerance"]<=r["efficiency"]<=1+a["all_sampled_efficiencies_in_0_1_with_tolerance"] for r in sampled)},
      {"id":"gain-above-one-witness", "passed":nominal["voltage_gain"]>1 and nominal["efficiency"]<=1},
    ]
    fig,axes=plt.subplots(2,1,figsize=(8,6),sharex=True)
    for load in p["loads_ohm"]:
        rs=[r for r in sweep if r["load_ohm"]==load]
        axes[0].plot(ratios,[r["voltage_gain"] for r in rs],label=f"Load {load:g} Ω")
        axes[1].plot(ratios,[r["efficiency"] for r in rs])
    axes[0].axhline(1,color="#777",lw=.8,ls="--");axes[0].set_ylabel("Load voltage / source voltage")
    axes[0].legend();axes[0].set_title("Synthetic passive coupled resonators: gain does not create energy")
    axes[1].set_ylabel("Load power / source real power");axes[1].set_xlabel("Angular frequency / uncoupled resonance frequency")
    for ax in axes: ax.grid(alpha=.2)
    save_figure(out/"coupled-resonators.svg",fig)
    fig,ax=plt.subplots(figsize=(7,3.8)); x=np.arange(4)
    energies=[transients[-1][k] for k in ["source_work_J","load_heat_J","winding_heat_J","stored_energy_change_J"]]
    ax.bar(x,np.array(energies)*1000,color=["#17684a","#68945e","#ad8e55","#777"])
    ax.set_xticks(x,["Source work","Load heat","Winding heat","Final storage"]);ax.set_ylabel("Energy (mJ)");ax.set_title("External Simpson quadrature, synthetic 0.25 s transient")
    save_figure(out/"transient-budget.svg",fig)
    result={"round":"R1","title":contract["title"],"classification":contract["classification"],"summary":[f"At the fixed nominal load, receiver voltage gain is {nominal['voltage_gain']:.6f}, with load/source power fraction {nominal['efficiency']:.6f}.","The passive receiver is supplied by the source; reflected resistance changes the source current.","Finite-time source work equals load heat, winding heat and stored-energy change within external-quadrature tolerance."],"metrics":{"omega0_rad_s":float(omega0),"resonance_frequency_Hz":float(omega0/(2*np.pi)),"nominal":nominal,"reflected_resistance_ohm":float(reflected),"doubled_winding_efficiency":more_loss["efficiency"],"transients":transients,"sampled_rows":len(sampled),"max_voltage_gain_sampled":max(r["voltage_gain"] for r in sampled),"max_efficiency_sampled":max(r["efficiency"] for r in sampled)},"checks":checks,"limitations":contract["limits"]+[contract["model"]["boundary"],"Voltage gain and apparent power do not measure energy production; all reported powers are real powers with peak-phasor factor 1/2."],"artifacts":["research/R1/coupled-resonators.svg","research/R1/transient-budget.svg","research/R1/frequency-sweep.csv","research/R1/load-sweep.csv"]}
    write_json(out/"parameters.json",p);write_json(out/"result.json",result)
    report=f'''# R1 — Coupled resonators and reflected loading

All results are synthetic solutions of the frozen, linear, lumped passive circuit. This is a modern reconstruction inspired by coupled tuning, not Tesla's historical hardware.

## Fixed witness

At ω₀ = {omega0:.9f} rad/s ({omega0/(2*np.pi):.6f} Hz), a 1 V peak source and 20 Ω receiver load give voltage gain **{nominal['voltage_gain']:.9f}** and load/source real-power fraction **{nominal['efficiency']:.9f}**. Source power is {nominal['source_power_W']:.12g} W; load power is {nominal['load_power_W']:.12g} W; winding loss is {nominal['winding_loss_W']:.12g} W.

At resonance the receiver reflects (ωM)²/(R₂+Rᴸ) = {reflected:.12g} Ω into the source. This changes the source current. Omitting this term creates a false account of available source power.

## Finite-time accounting

Starting from zero charge/current, the sinusoidal drive runs for 0.25 s. DOP853 evolves only the four circuit states; external Simpson quadrature of sampled instantaneous powers calculates work, independently of any integrated work state. Coarse/fine grids and a tighter ODE tolerance are all retained in CSV. The tight run has source work {transients[-1]['source_work_J']:.12g} J, load heat {transients[-1]['load_heat_J']:.12g} J, winding heat {transients[-1]['winding_heat_J']:.12g} J, final storage {transients[-1]['stored_energy_change_J']:.12g} J and residual {transients[-1]['residual_J']:.4g} J.

## Controls and limits

{sum(c['passed'] for c in checks)}/{len(checks)} producer controls pass. They include zero source, zero coupling, reversed mutual sign, closed-form resonance currents, increased winding loss, passive sampled efficiencies and transient refinement. The frequency/load domain is a finite fixture, not a global optimization proof. No hardware was measured. Source impedance beyond R₁, radiation, nonlinear materials and environmental coupling are outside this model. There is no gravity degree of freedom and no claim of source-free energy.

Run `python3 research/R1/run.py`. `--output DIR` writes recomputed outputs separately; the canonical manifest binds the producer, contract and dependencies.
'''
    (out/"report.md").write_text(report)
    if out.resolve()==Path(__file__).resolve().parent:
        write_manifest(out,CONTRACT)
    if not all(c["passed"] for c in checks): raise SystemExit("Producer checks failed; retain outputs and review.")
    print(json.dumps({"round":"R1","passed":len(checks),"nominal_gain":nominal["voltage_gain"],"efficiency":nominal["efficiency"],"energy_residual_J":transients[-1]["residual_J"]}))

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--output",type=Path,default=Path(__file__).resolve().parent)
    main(parser.parse_args().output)
