const CATEGORIES = { electricity: 'Electricity', gravity: 'Gravity', magnetism: 'Magnetism', history: 'History' };
const state = { hypotheses: [], sources: [], category: 'all', query: '', sourceQuery: '' };
const asArray = value => Array.isArray(value) ? value : [];
const words = value => value == null ? '' : typeof value === 'string' ? value : Array.isArray(value) ? value.map(words).join('; ') : Object.entries(value).map(([k, v]) => `${k.replaceAll('_', ' ')}: ${words(v)}`).join('; ');
const human = value => words(value).replaceAll('_', ' ');
const format = (value, digits = 3) => Number.isFinite(value) ? value.toLocaleString('en-US', { maximumFractionDigits: digits, minimumFractionDigits: digits }) : '—';

function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value == null) continue;
    if (key === 'className') node.className = value;
    else if (key === 'text') node.textContent = value;
    else node.setAttribute(key, String(value));
  }
  for (const child of Array.isArray(children) ? children : [children]) if (child != null) node.append(typeof child === 'string' ? document.createTextNode(child) : child);
  return node;
}
function replace(id, children) { const target = document.getElementById(id); if (target) target.replaceChildren(...(Array.isArray(children) ? children : [children])); }
function safeHref(value) {
  if (typeof value !== 'string' || !value.trim() || /^(javascript|data|vbscript):/i.test(value) || value.startsWith('//')) return null;
  if (/^[a-z]+:/i.test(value) && !/^https?:/i.test(value)) return null;
  return value;
}
function anchor(label, path) {
  const href = safeHref(path);
  if (!href) return el('span', { text: label });
  return el('a', { href, ...(/^https?:/.test(href) ? { target: '_blank', rel: 'noopener noreferrer' } : {}) }, label);
}
function badge(status) {
  const text = human(status || 'proposed');
  const type = /accepted|verified|reviewed/.test(status) && !/unverified|not_verified/.test(status) ? 'accepted' : /fail|reject|withheld/.test(status) ? 'failed' : 'proposed';
  return el('span', { className: `tag ${type}`, text });
}
function block(label, value) {
  const text = words(value);
  return el('div', { className: 'detail-block' }, [el('h4', { text: label }), el('p', { text: text || 'Not specified in this record.' })]);
}
function loadError(id, label, path) { replace(id, el('div', { className: 'loading-error' }, [el('p', { text: `${label} could not be loaded. No completion or result has been inferred.` }), anchor('Open the data file directly', path)])); }

function renderHypotheses() {
  const items = state.hypotheses.filter(item => (state.category === 'all' || item.category === state.category) && words(item).toLowerCase().includes(state.query));
  replace('hypothesis-count', el('span', { text: `${items.length} ${items.length === 1 ? 'proposal' : 'proposals'}${state.category !== 'all' ? ` · ${CATEGORIES[state.category] || state.category}` : ' across all areas'}` }));
  if (!items.length) return replace('hypothesis-list', el('p', { className: 'empty-note', text: 'No proposals match these filters. Try another term or choose All areas.' }));
  replace('hypothesis-list', items.map((item, i) => {
    const details = el('details', {}, [el('summary', { text: 'Observable, controls & limits' }), el('div', { className: 'details-grid' }, [block('Predicted observation', item.prediction), block('Ordinary rival', item.rival), block('What to measure', item.observable), block('Controls', item.controls), block('Materials / prerequisites', item.materials), block('What would count against it', item.falsifier)])]);
    const links = el('div', { className: 'reference-links' }, asArray(item.sourceIds).map(id => anchor(id, `#source-${id}`)));
    details.append(links);
    if (item.limits || item.limitations) details.append(block('Limits', item.limits || item.limitations));
    return el('article', { className: 'hypothesis-row', id: `hypothesis-${item.id}` }, [el('span', { className: 'row-number', text: String(i + 1).padStart(2, '0') }), el('div', {}, [el('div', { className: 'row-topline' }, [el('h3', { text: item.title }), badge(item.status)]), el('p', { className: 'hypothesis-summary', text: item.prediction || item.observable || 'See the predeclared observation and controls below.' }), details])]);
  }));
}
function renderSources() {
  const records = state.sources.filter(item => words(item).toLowerCase().includes(state.sourceQuery));
  replace('source-count', el('span', { text: `${records.length} source ${records.length === 1 ? 'record' : 'records'} · reading depth and claim limits are shown separately` }));
  if (!records.length) return replace('source-list', el('p', { className: 'empty-note', text: 'No source records match your search.' }));
  replace('source-list', records.map(item => {
    const details = el('details', { className: 'source-record', id: `source-${item.id}` }, [el('summary', {}, [el('h3', { text: item.title }), el('span', { className: 'source-id', text: item.id })])]);
    const metadata = `${CATEGORIES[item.category] || human(item.category)} · ${words(item.date) || 'Date not recorded'} · ${human(item.status) || 'Status not recorded'}${item.provenance ? ` · ${words(item.provenance)}` : ''}`;
    details.append(el('div', { className: 'source-body' }, [
      block('What it supports', item.claim), block('What it does not establish', item.limits),
      block('Reading depth', item.readDepth), block('Sections inspected', item.sections),
      el('div', {}, [anchor('Read the original source ↗', item.url)]),
      el('p', { className: 'source-metadata', text: metadata }),
    ]));
    return details;
  }));
}
function setCategory(category) {
  state.category = Object.hasOwn(CATEGORIES, category) ? category : 'all';
  for (const button of document.querySelectorAll('[data-category]')) button.setAttribute('aria-pressed', String(button.dataset.category === state.category));
  renderHypotheses();
}

function setupImage(asset, title) {
  const image = el('img', { src: asset.path, alt: `${title}: ${asset.label || human(asset.kind)}. Scientific geometry, not a photograph.`, loading: 'lazy' });
  image.addEventListener('error', () => image.replaceWith(el('p', { className: 'empty-note', text: 'This drawing is unavailable. Consult its setup record below.' })), { once: true });
  return image;
}
function renderSetups(data) {
  const items = asArray(data.items);
  const first = items.find(item => asArray(item.assets).some(asset => /plan|orthographic|svg/i.test(`${asset.kind} ${asset.path}`)));
  if (first) {
    const asset = first.assets.find(asset => /plan|orthographic|svg/i.test(`${asset.kind} ${asset.path}`));
    const image = setupImage(asset, first.title); image.removeAttribute('loading');
    replace('hero-setup', image);
    replace('hero-caption', el('span', { text: `${first.title}. ${first.status ? human(first.status) + '. ' : ''}Dimensioned geometry; not a built apparatus.` }));
  } else replace('hero-setup', el('p', { className: 'empty-note', text: 'No published apparatus drawing is present in this record.' }));
  if (!items.length) return replace('setup-list', el('p', { className: 'empty-note', text: 'No setup geometry has been published yet.' }));
  replace('setup-list', items.map(item => {
    const assets = asArray(item.assets).filter(asset => safeHref(asset.path));
    const figure = el('div', { className: 'setup-visual', role: 'tabpanel', id: `view-${item.id}`, 'aria-labelledby': `tab-${item.id}-0` });
    if (assets.length) figure.append(setupImage(assets[0], item.title));
    const caption = el('p', { className: 'setup-caption', text: assets[0]?.label || 'No drawing published.' });
    const tabs = el('div', { className: 'view-tabs', role: 'tablist', 'aria-label': `${item.title} views` });
    assets.forEach((asset, index) => {
      const button = el('button', { type: 'button', role: 'tab', id: `tab-${item.id}-${index}`, 'aria-controls': `view-${item.id}`, tabindex: index === 0 ? 0 : -1, 'aria-selected': String(index === 0), text: asset.label || human(asset.kind) });
      button.addEventListener('click', () => { for (const tab of tabs.children) { tab.setAttribute('aria-selected', String(tab === button)); tab.setAttribute('tabindex', tab === button ? '0' : '-1'); } figure.setAttribute('aria-labelledby', button.id); figure.replaceChildren(setupImage(asset, item.title)); caption.textContent = asset.label || human(asset.kind); });
      button.addEventListener('keydown', event => { if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') { event.preventDefault(); const next = tabs.children[(index + (event.key === 'ArrowRight' ? 1 : assets.length - 1)) % assets.length]; next.focus(); next.click(); } });
      tabs.append(button);
    });
    const details = el('details', {}, [el('summary', { text: 'Model boundary & measurement plan' }), block('Model boundary', item.modelBoundary), block('Measurements', item.measurements), block('Components', item.components), block('Connections', item.wiring), block('Parameter provenance', item.parameterSource), block('Limitations', item.limitations), el('div', { className: 'reference-links' }, [...assets.map(asset => anchor(`Open ${asset.label || human(asset.kind)}`, asset.path)), ...asArray(item.contractPaths).map(path => anchor(`Contract ${path.split('/').at(-1).replace('.json', '')}`, path))])]);
    return el('article', { className: 'setup-sheet', id: `setup-${item.id}` }, [el('h3', { text: item.title }), badge(item.status || 'proposed geometry'), el('p', { className: 'setup-summary', text: item.summary }), figure, tabs, caption, details]);
  }));
}

export function ledgerCounts(data) {
  const rounds = asArray(data.rounds);
  const loops = rounds.flatMap(round => asArray(round.loops));
  const completed = loops.filter(loop => /^(completed_producer|accepted_narrow|completed|accepted|repaired_accepted)$/.test(loop.status));
  return { completedLoops: completed.length, acceptedRounds: rounds.filter(round => /^(accepted_narrow|accepted)$/.test(round.verdict)).length, requestedRounds: data.program?.rounds || 3, requestedLoops: (data.program?.rounds || 3) * (data.program?.loops_per_round || 2) };
}
function renderLedger(data) {
  const counts = ledgerCounts(data);
  replace('program-count', el('span', { text: `${counts.acceptedRounds}/${counts.requestedRounds} rounds admitted · ${counts.completedLoops}/${counts.requestedLoops} loops recorded` }));
  const rounds = asArray(data.rounds);
  const rows = [];
  for (let index = 0; index < counts.requestedRounds; index++) {
    const round = rounds.find(r => r.id === `R${index + 1}`) || rounds[index];
    if (!round) {
      rows.push(el('article', { className: 'ledger-round' }, [el('div', {}, [el('p', { className: 'round-label', text: `ROUND ${String(index + 1).padStart(2, '0')}` }), badge('not recorded')]), el('div', {}, [el('h3', { text: 'Awaiting the next recorded decision' }), el('p', { text: 'The advisor selects the next question after reviewing the preceding result. This slot is part of the requested sequence, not a completed experiment.' })])]));
      continue;
    }
    const links = el('div', { className: 'model-links' }, [[round.contract, 'Contract'], [round.producer, 'Results'], [round.review, 'Independent review']].filter(([p]) => p).map(([p, title]) => anchor(title, p)));
    const loops = el('div', { className: 'loop-list' }, asArray(round.loops).map(loop => el('div', { className: 'loop-entry' }, [el('h4', { text: `${loop.id} · ${human(loop.status)}` }), el('p', { text: loop.summary || (loop.id.endsWith('A') ? 'Executed model and producer artifacts.' : 'Independent check and bounded interpretation.') }), ...asArray(loop.artifacts).slice(0, 2).map(artifact => anchor((artifact.path || '').split('/').at(-1) || 'Artifact', artifact.path))])));
    rows.push(el('article', { className: 'ledger-round', id: `round-${round.id}` }, [el('div', {}, [el('p', { className: 'round-label', text: `ROUND ${String(index + 1).padStart(2, '0')}` }), badge(round.verdict || 'pending review')]), el('div', {}, [el('h3', { text: round.title }), ...asArray(round.summary).map(text => el('p', { text })), loops, links, el('details', {}, [el('summary', { text: 'Limits & next decision' }), block('Limits', round.limits), block('Next decision', round.nextDecision)])])]));
  }
  replace('research-ledger', rows);
}

const cmul = ([a, b], [c, d]) => [a * c - b * d, a * d + b * c];
const cadd = ([a, b], [c, d]) => [a + c, b + d];
const csub = ([a, b], [c, d]) => [a - c, b - d];
const cdiv = ([a, b], [c, d]) => { const denominator = c * c + d * d; return [(a * c + b * d) / denominator, (b * c - a * d) / denominator]; };
const norm2 = ([a, b]) => a * a + b * b;
export function coupledCircuit(parameters, frequencyRatio = 1, loadOhm = 20, sourcePeak = 1) {
  const p = parameters;
  if (![frequencyRatio, loadOhm, sourcePeak, p.L1_H, p.L2_H, p.C1_F, p.C2_F, p.M_H, p.R1_ohm, p.R2_ohm].every(Number.isFinite)) throw new Error('All model inputs must be finite numbers.');
  if (frequencyRatio <= 0 || loadOhm < 0 || sourcePeak < 0 || Math.min(p.L1_H, p.L2_H, p.C1_F, p.C2_F) <= 0 || Math.min(p.R1_ohm, p.R2_ohm) <= 0 || p.M_H ** 2 >= p.L1_H * p.L2_H) throw new Error('Use positive passive components, nonnegative load and a positive-definite inductance matrix.');
  const omega0 = 1 / Math.sqrt(p.L1_H * p.C1_F), omega = omega0 * frequencyRatio;
  const z1 = [p.R1_ohm, omega * p.L1_H - 1 / (omega * p.C1_F)], z2 = [p.R2_ohm + loadOhm, omega * p.L2_H - 1 / (omega * p.C2_F)];
  const det = cmul(z1, z2); det[0] += (omega * p.M_H) ** 2;
  const i1 = cdiv([sourcePeak * z2[0], sourcePeak * z2[1]], det), i2 = cdiv([0, -sourcePeak * omega * p.M_H], det);
  const sourcePower = .5 * sourcePeak * i1[0], loadPower = .5 * loadOhm * norm2(i2), windingLoss = .5 * (p.R1_ohm * norm2(i1) + p.R2_ohm * norm2(i2));
  const magneticCross = i1[0] * i2[0] + i1[1] * i2[1];
  const averageStoredEnergy = .25 * (p.L1_H * norm2(i1) + p.L2_H * norm2(i2) + 2 * p.M_H * magneticCross + norm2(i1) / (omega ** 2 * p.C1_F) + norm2(i2) / (omega ** 2 * p.C2_F));
  return { omega, frequencyHz: omega / (2 * Math.PI), i1, i2, sourcePower, loadPower, windingLoss, averageStoredEnergy, efficiency: sourcePower > 0 ? loadPower / sourcePower : null, voltageGain: sourcePeak > 0 ? loadOhm * Math.sqrt(norm2(i2)) / sourcePeak : null, residual: sourcePower - loadPower - windingLoss };
}

function inputRow(id, label, value, min, max, step) { return el('div', { className: 'input-row' }, [el('label', { for: id, text: label }), el('input', { id, type: 'number', value, min, max, step, inputmode: 'decimal', required: '' })]); }
function output(label, value) { return el('div', { className: 'output-cell' }, [el('small', { text: label }), el('strong', { text: value })]); }
function svgNode(tag, attrs, text) { const node = document.createElementNS('http://www.w3.org/2000/svg', tag); Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, value)); if (text) node.textContent = text; return node; }
function circuitChart(parameters, ratio, load) {
  const width = 640, height = 190, left = 48, right = 15, top = 15, bottom = 38;
  const svg = svgNode('svg', { viewBox: `0 0 ${width} ${height}`, class: 'calc-chart', role: 'img', 'aria-label': 'Analytical receiver voltage gain as frequency changes, at the selected load.' });
  const rows = Array.from({ length: 141 }, (_, i) => { const x = .3 + i * .01; return [x, coupledCircuit(parameters, x, load).voltageGain]; });
  const maximum = Math.max(1, ...rows.map(row => row[1])) * 1.1;
  const x = value => left + (value - .3) / 1.4 * (width - left - right), y = value => height - bottom - value / maximum * (height - top - bottom);
  for (const fraction of [0, .5, 1]) { const value = fraction * maximum; svg.append(svgNode('line', { x1: left, x2: width - right, y1: y(value), y2: y(value), stroke: '#d3d8cc' }), svgNode('text', { x: left - 8, y: y(value) + 4, 'text-anchor': 'end' }, format(value, 1))); }
  svg.append(svgNode('path', { d: rows.map((row, i) => `${i ? 'L' : 'M'}${x(row[0]).toFixed(3)},${y(row[1]).toFixed(3)}`).join(' '), fill: 'none', stroke: '#254d40', 'stroke-width': 2 }));
  const selected = coupledCircuit(parameters, ratio, load).voltageGain;
  svg.append(svgNode('line', { x1: x(ratio), x2: x(ratio), y1: top, y2: height - bottom, stroke: '#86532e', 'stroke-dasharray': '3 4' }), svgNode('circle', { cx: x(ratio), cy: y(selected), r: 4, fill: '#86532e' }));
  [.3, 1, 1.7].forEach(value => svg.append(svgNode('text', { x: x(value), y: height - 19, 'text-anchor': 'middle' }, value.toFixed(1))));
  svg.append(svgNode('text', { x: (width + left) / 2, y: height - 2, 'text-anchor': 'middle' }, 'Drive frequency / uncoupled resonance'));
  return svg;
}
function circuitCalculator(contract) {
  const p = contract.parameters;
  const form = el('form', { className: 'input-panel', 'aria-label': 'Coupled resonator inputs' }, [inputRow('circuit-ratio', 'Frequency ratio ω / ω₀', 1, .3, 1.7, .01), inputRow('circuit-load', 'Receiver load (Ω)', p.nominal_load_ohm, 1, 1000, 1), el('p', { className: 'input-hint', text: `Fixed contract: L₁ = ${p.L1_H * 1000} mH, L₂ = ${p.L2_H * 1000} mH, M = ${p.M_H * 1000} mH. Source peak ${p.source_peak_V} V. Coil resistances ${p.R1_ohm} Ω and ${p.R2_ohm} Ω. Linear steady state; no measured device.` }), el('button', { type: 'reset', className: 'text-link', text: 'Reset to the frozen example' })]);
  const result = el('div', { id: 'circuit-results', 'aria-live': 'polite' });
  const update = () => {
    const ratioInput = form.querySelector('#circuit-ratio'), loadInput = form.querySelector('#circuit-load');
    const ratio = Number(ratioInput.value), load = Number(loadInput.value);
    if (!ratioInput.value.trim() || !loadInput.value.trim() || !Number.isFinite(ratio) || !Number.isFinite(load) || ratio < .3 || ratio > 1.7 || load < 1 || load > 1000) { result.replaceChildren(el('p', { className: 'calc-error', role: 'alert', text: 'Enter a frequency ratio from 0.3 to 1.7 and a load from 1 to 1,000 Ω. The previous result is withheld.' })); return; }
    const r = coupledCircuit(p, ratio, load, p.source_peak_V);
    result.replaceChildren(el('div', { className: 'calc-output' }, [output('Receiver voltage / source', `${format(r.voltageGain)} ×`), output('Real power delivered to load', `${format(100 * r.efficiency, 1)} %`), output('Mean stored field energy', `${format(r.averageStoredEnergy * 1000)} mJ`), output('Source real power', `${format(r.sourcePower * 1000)} mW`), output('Load real power', `${format(r.loadPower * 1000)} mW`), output('Winding dissipation', `${format(r.windingLoss * 1000)} mW`)]), circuitChart(p, ratio, load), el('p', { className: 'calc-note', text: `Drive ${format(r.frequencyHz, 2)} Hz. Source power = load power + winding dissipation; numerical residual ${r.residual.toExponential(2)} W. Voltage amplification is compatible with a passive energy budget. Mean stored energy is not continuous output power.` }));
  };
  form.addEventListener('input', update); form.addEventListener('submit', event => event.preventDefault()); form.addEventListener('reset', () => setTimeout(update, 0));
  queueMicrotask(update);
  return el('article', { className: 'calculator', id: 'coupled-calculator' }, [el('div', { className: 'calculator-header' }, [el('div', {}, [el('h3', { text: 'Coupled resonators & the source budget' }), el('p', { text: 'Receiver voltage can exceed source voltage. The coupled circuit also changes the source current. Follow the real power on both sides.' })]), badge('analytical model')]), el('div', { className: 'calculator-grid' }, [form, result]), el('p', { className: 'calc-equation', text: 'Z I = (V, 0) · Z₁₂ = jωM · Psource = ½ Re(V I₁*) · Pload = ½ RL |I₂|²' }), el('div', { className: 'model-links' }, [anchor('Frozen R1 contract', 'docs/contracts/R1.json'), anchor('Executed results', 'research/R1/result.json'), anchor('Complete derivation', 'research/R1/report.md'), anchor('Transient energy check', 'research/R1/transient-budget.svg')])]);
}

export function sourceReadout(parameters, { receiverAmplitude = .005, receiverPhase = Math.PI / 3, phaseError = 0, currentError = 1e-5, mutualError = 3e-6, calibrationKnown = true } = {}) {
  if (![receiverAmplitude, receiverPhase, phaseError, currentError, mutualError].every(Number.isFinite) || Math.min(receiverAmplitude, currentError, mutualError) < 0) throw new Error('Finite nonnegative amplitudes and error bounds are required.');
  coupledCircuit(parameters, 1, parameters.nominal_load_ohm || 20, 1);
  const p = parameters, omega = 1 / Math.sqrt(p.L1_H * p.C1_F), load = p.nominal_load_ohm || 20;
  const z1 = [p.R1_ohm, omega * p.L1_H - 1 / (omega * p.C1_F)], z2 = [p.R2_ohm + load, omega * p.L2_H - 1 / (omega * p.C2_F)], zm = [0, omega * p.M_H];
  const determinant = csub(cmul(z1, z2), cmul(zm, zm));
  const e1 = [1, 0], e2 = [receiverAmplitude * Math.cos(receiverPhase), receiverAmplitude * Math.sin(receiverPhase)];
  const i1 = cdiv(csub(cmul(z2, e1), cmul(zm, e2)), determinant), i2 = cdiv(csub(cmul(z1, e2), cmul(zm, e1)), determinant);
  const observedI2 = cmul(i2, [Math.cos(phaseError), Math.sin(phaseError)]);
  const receiverEstimate = cadd(cmul(zm, i1), cmul(z2, observedI2));
  const errorRadius = omega * Math.abs(p.M_H) * currentError + Math.sqrt(norm2(z2)) * currentError + omega * mutualError * (Math.sqrt(norm2(i1)) + currentError);
  const imposedCurrentError = Math.sqrt(norm2(csub(observedI2, i2)));
  const calibrationWithinBudget = imposedCurrentError <= currentError + 1e-15;
  const magnitude = Math.sqrt(norm2(receiverEstimate));
  return { i1, i2, observedI2, receiverEstimate, magnitude, errorRadius, imposedCurrentError, calibrationWithinBudget, excludesZero: calibrationKnown && calibrationWithinBudget ? magnitude > errorRadius : null, calibrationKnown, trueReceiver: e2 };
}
function readoutCalculator(r1, r2) {
  const p = r1.parameters, q = r2.parameters;
  const form = el('form', { className: 'input-panel', 'aria-label': 'Source readout inputs' }, [inputRow('readout-drive', 'Injected receiver drive (mV)', q.injected_receiver_amplitude_V * 1000, 0, 10, .5), inputRow('readout-phase', 'Receiver phase error (mrad)', 0, 0, 10, .1), inputRow('readout-current-error', 'Current error bound (µA)', q.current_error_bounds_A[0] * 1e6, 0, 100, 1), inputRow('readout-mutual-error', 'Mutual-L error bound (µH)', q.mutual_inductance_error_bound_H * 1e6, 0, 30, .5)]);
  const known = el('input', { id: 'readout-known', type: 'checkbox', checked: '' });
  form.append(el('label', { className: 'checkbox-row', for: 'readout-known' }, [known, 'Apply the supplied calibration bounds']), el('p', { className: 'input-hint', text: 'Synthetic two-channel, phase-coherent currents. The receiver drive and error budgets are specified inputs, not measured instrument performance. Both source-port voltages are reconstructed from currents.' }), el('button', { type: 'reset', className: 'text-link', text: 'Reset to the frozen example' }));
  const results = el('div', { id: 'readout-results', 'aria-live': 'polite' });
  const update = () => {
    const nodes = ['readout-drive', 'readout-phase', 'readout-current-error', 'readout-mutual-error'].map(id => form.querySelector(`#${id}`));
    const values = nodes.map(input => Number(input.value));
    if (nodes.some((input, i) => !input.value.trim() || !Number.isFinite(values[i]) || values[i] < Number(input.min) || values[i] > Number(input.max))) { results.replaceChildren(el('p', { className: 'calc-error', role: 'alert', text: 'Enter values inside each declared range. Incomplete or invalid inputs withhold the reconstruction.' })); return; }
    const r = sourceReadout(p, { receiverAmplitude: values[0] / 1000, receiverPhase: q.injected_receiver_phase_rad, phaseError: values[1] / 1000, currentError: values[2] / 1e6, mutualError: values[3] / 1e6, calibrationKnown: known.checked });
    let conclusion;
    if (!r.calibrationKnown) conclusion = 'Calibration unknown: a bound-based signal conclusion is withheld.';
    else if (!r.calibrationWithinBudget) conclusion = 'The imposed phase error exceeds the supplied current-error budget. This disk cannot justify a signal conclusion for this fixture.';
    else conclusion = r.excludesZero ? 'Zero lies outside this conditional effective-voltage disk. This identifies a model residual; it does not identify its physical cause.' : 'Zero lies inside this conditional disk. This readout does not separate a receiver residual from zero under the supplied bounds.';
    const rankRows = [['Receiver amplitude²', '1 / 3'], ['Both amplitudes²', '2 / 2'], ['Receiver complex current', '2 / 2'], ['Both coherent complex currents', '4 / 0']];
    const rankTable = el('table', { className: 'rank-table' }, [
      el('caption', { text: 'Local observation rank at the nonzero fixture · four real source parameters' }),
      el('thead', {}, [el('tr', {}, [el('th', { scope: 'col', text: 'Observation' }), el('th', { scope: 'col', text: 'Rank / nullity' })])]),
      el('tbody', {}, rankRows.map(([name, rank]) => el('tr', {}, [el('th', { scope: 'row', text: name }), el('td', { text: rank })]))),
    ]);
    results.replaceChildren(
      el('div', { className: 'calc-output' }, [output('Reconstructed receiver drive', `${format(r.magnitude * 1000)} mV`), output('Conditional error-disk radius', `${format(r.errorRadius * 1000)} mV`), output('Imposed current mismatch', `${format(r.imposedCurrentError * 1e6)} µA`)]),
      el('p', { className: !r.calibrationKnown || !r.calibrationWithinBudget ? 'calc-error' : 'calc-note', text: conclusion }),
      el('p', { className: 'calc-equation', text: `ê₂ = ${format(r.receiverEstimate[0] * 1000)} + j ${format(r.receiverEstimate[1] * 1000)} mV` }),
      rankTable,
      el('p', { className: 'calc-note', text: 'Amplitude-map ranks describe local Jacobians at the recorded nonzero fixture. Exact finite phase rivals are a separate result. At zero current, the squared-amplitude Jacobians have rank zero. Full rank requires the declared calibrated model.' }),
    );
  };
  form.addEventListener('input', update); form.addEventListener('change', update); form.addEventListener('submit', event => event.preventDefault()); form.addEventListener('reset', () => setTimeout(update, 0)); queueMicrotask(update);
  return el('article', { className: 'calculator', id: 'readout-calculator' }, [el('div', { className: 'calculator-header' }, [el('div', {}, [el('h3', { text: 'Source location & the calibration boundary' }), el('p', { text: 'A phase error can create an apparent receiver drive. Change the injected signal or the readout error and inspect what the stated bounds allow.' })]), badge('conditional reconstruction')]), el('div', { className: 'calculator-grid' }, [form, results]), el('p', { className: 'calc-equation', text: 'ê = Ẑ Î · |ê₂ − e₂| ≤ ω |M̂| ε₁ + |Ẑ₂₂| ε₂ + ω ΔM (|Î₁| + ε₁)' }), el('div', { className: 'model-links' }, [anchor('Frozen R2 contract', 'docs/contracts/R2.json'), anchor('Executed inverse checks', 'research/R2/result.json'), anchor('Rivals and derivation', 'research/R2/report.md')])]);
}

async function getJSON(path, fetcher) { const response = await fetcher(path, { cache: 'no-store' }); if (!response.ok) throw new Error(`Could not load ${path}`); return response.json(); }
export async function boot(fetcher = fetch) {
  document.querySelectorAll('[data-category]').forEach(button => button.addEventListener('click', () => setCategory(button.dataset.category)));
  document.querySelectorAll('[data-scope]').forEach(link => link.addEventListener('click', () => setCategory(link.dataset.scope)));
  document.getElementById('hypothesis-search')?.addEventListener('input', event => { state.query = event.target.value.trim().toLowerCase(); renderHypotheses(); });
  document.getElementById('source-search')?.addEventListener('input', event => { state.sourceQuery = event.target.value.trim().toLowerCase(); renderSources(); });
  document.addEventListener('click', event => { const link = event.target.closest('a[href^="#source-"]'); if (link) { const record = document.getElementById(link.getAttribute('href').slice(1)); if (record) record.open = true; } });
  const jobs = [
    getJSON('data/hypotheses.json', fetcher).then(data => { state.hypotheses = asArray(data.hypotheses); renderHypotheses(); }).catch(() => loadError('hypothesis-list', 'The proposal catalogue', 'data/hypotheses.json')),
    getJSON('data/sources.json', fetcher).then(data => { state.sources = asArray(data.sources); renderSources(); }).catch(() => loadError('source-list', 'The source notebook', 'data/sources.json')),
    getJSON('data/setups.json', fetcher).then(renderSetups).catch(() => { loadError('setup-list', 'The geometry catalogue', 'data/setups.json'); replace('hero-setup', el('p', { className: 'empty-note', text: 'The setup drawing could not be loaded. Geometry records are linked below.' })); }),
    getJSON('research/decisions.json', fetcher).then(renderLedger).catch(() => { loadError('research-ledger', 'The research record', 'research/decisions.json'); replace('program-count', el('span', { text: 'Research status unavailable' })); }),
    Promise.allSettled([getJSON('docs/contracts/R1.json', fetcher), getJSON('docs/contracts/R2.json', fetcher)]).then(([r1, r2]) => { if (r1.status !== 'fulfilled') throw new Error('R1 unavailable'); const calculators = [circuitCalculator(r1.value)]; if (r2.status === 'fulfilled') calculators.push(readoutCalculator(r1.value, r2.value)); replace('calculator-root', calculators); }).catch(() => loadError('calculator-root', 'The frozen calculator model', 'docs/contracts/R1.json')),
  ];
  await Promise.allSettled(jobs);
}
if (typeof document !== 'undefined') boot();
