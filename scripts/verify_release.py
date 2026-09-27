"""Verify six admitted loops and their immutable evidence before publication.

Numerical reproduction and independent scientific reviews remain distinct gates.
This standard-library check runs in Pages CI without a numerical environment.
"""
from datetime import datetime
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def artifact(relative):
    path = (ROOT / relative).resolve()
    require(path.is_relative_to(ROOT), f'Path outside repository: {relative}')
    require(path.is_file(), f'Missing artifact: {relative}')
    return path


def digest(relative):
    return hashlib.sha256(artifact(relative).read_bytes()).hexdigest()


def read(relative):
    return json.loads(artifact(relative).read_text())


def main():
    ledger = read('research/decisions.json')
    require(ledger['program']['rounds'] == 3 and ledger['program']['loops_per_round'] == 2,
            'Program must contain three two-loop rounds')
    require(ledger['loop_count'] == 6, 'Six completed loops required')
    require([r['id'] for r in ledger['rounds']] == ['R1', 'R2', 'R3'], 'Ordered R1-R3 required')
    sources = read('data/sources.json')['sources']
    ids = set()
    for source in sources:
        require(source['id'] not in ids, 'Duplicate source identifier')
        ids.add(source['id'])
        for alias in source.get('aliases', []):
            require(alias not in ids, 'Duplicate source alias')
            ids.add(alias)
        require(source.get('readDepth') and source.get('limits') and source.get('url'),
                'Source must state reading depth, limits and URL')
    bound = set()
    previous = None
    previous_time = None
    for index, record in enumerate(ledger['rounds'], start=1):
        rid = f'R{index}'
        require(record['verdict'] == 'accepted_narrow', f'{rid} not admitted')
        require(record.get('summary') and record.get('limits') and record.get('nextDecision'),
                f'{rid} lacks findings, limits or next decision')
        require([x['id'] for x in record['loops']] == [rid + 'A', rid + 'B'], 'Loop order mismatch')
        require([x['status'] for x in record['loops']] == ['completed_producer', 'accepted_narrow'],
                'Incomplete loop status')
        for loop in record['loops']:
            require(loop.get('artifacts'), 'Loop evidence missing')
            for item in loop['artifacts']:
                require(digest(item['path']) == item['sha256'], f'Stale loop artifact: {item["path"]}')
                bound.add(item['path'])
        contract = read(record['contract'])
        result = read(record['producer'])
        review = read(record['review'])
        manifest = read(f'research/{rid}/manifest.json')
        require(contract['round'] == result['round'] == review['round'] == rid, 'Round identity mismatch')
        require(review['verdict'] == 'accepted_narrow', 'Review file differs from ledger')
        for document in [result, review]:
            require(document.get('checks') and all(c['passed'] is True for c in document['checks']),
                    f'{rid} contains missing or failed checks')
        for key, relative in review['paths'].items():
            require(digest(relative) == review['bindings'][key + '_sha256'],
                    f'Stale reviewer binding: {relative}')
            bound.add(relative)
        for item in manifest['files'] + [manifest['contract']] + manifest['dependencies']:
            require(digest(item['path']) == item['sha256'], f'Stale producer binding: {item["path"]}')
            bound.add(item['path'])
        frozen = datetime.fromisoformat(contract['frozen_at'])
        reviewed = datetime.fromisoformat(review['reviewed_at'])
        require(frozen < reviewed, 'Contract must precede review')
        if previous:
            incoming = contract['incoming_evidence']
            require(incoming['previous_review'] == previous, 'Wrong predecessor review')
            require(incoming['previous_review_sha256'] == digest(previous), 'Predecessor bytes changed')
            require(frozen > previous_time, 'Adaptive contract predates preceding verdict')
        previous, previous_time = record['review'], reviewed
        for source in contract.get('source_records', []):
            require(source['id'] in ids, f'Unresolved contract source: {source["id"]}')
    for name in ['index.html', 'styles.css', 'app.js', 'README.md', 'LICENSE',
                 'docs/SCOPE.md', 'docs/roadmap.md', 'docs/panel-log.md',
                 'docs/derivations.md', 'docs/source-review.md', 'docs/historical-corpus.md',
                 'docs/tool-audit.md', 'docs/apparatus.md', 'data/hypotheses.json',
                 'data/setups.json', 'scripts/render_setups.py', 'scripts/verify_reproduction.py']:
        artifact(name)
    for path in (ROOT / 'assets' / 'setups').glob('*.svg'):
        ET.parse(path)
    geometry = read('assets/setups/manifest.json')
    require(digest(geometry['generatorPath']) == geometry['generatorSHA256'], 'Drawing generator changed')
    for name, expected in geometry['files'].items():
        require(digest('assets/setups/' + name) == expected, f'Drawing changed: {name}')
    hypotheses = read('data/hypotheses.json')['hypotheses']
    require(len({h['id'] for h in hypotheses}) == len(hypotheses), 'Duplicate hypothesis ID')
    for hypothesis in hypotheses:
        require(hypothesis.get('status') and hypothesis.get('rival') and hypothesis.get('falsifier'),
                'Hypothesis needs status, rival and falsifier')
        require(all(s in ids for s in hypothesis['sourceIds']), 'Unresolved hypothesis source')
    require(ledger.get('final_bindings'), 'Final source and advisor records are not bound')
    for item in ledger['final_bindings']:
        require(digest(item['path']) == item['sha256'], f'Stale final record: {item["path"]}')
        bound.add(item['path'])
    print(json.dumps({'status': 'passed', 'rounds': 3, 'loops': 6,
                      'boundArtifacts': len(bound), 'sourceRecords': len(sources),
                      'scope': 'Completion, provenance and exact bytes; no physical validation.'}, indent=2))


if __name__ == '__main__':
    main()
