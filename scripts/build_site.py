"""Assemble authored static files and record the exact source revision."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'dist'


def main():
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir()
    for name in ['index.html', 'styles.css', 'app.js', 'README.md', 'LICENSE', 'requirements.txt', 'package.json', 'package-lock.json']:
        shutil.copy2(ROOT / name, DEST / name)
    for name in ['assets', 'data', 'docs', 'research', 'scripts', 'tests']:
        if (ROOT / name).exists():
            shutil.copytree(ROOT / name, DEST / name,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    (DEST / '.nojekyll').write_text('')
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    revision = head.stdout.strip() if head.returncode == 0 else 'uncommitted'
    dirty = bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip())
    files = {str(p.relative_to(DEST)): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(DEST.rglob('*')) if p.is_file()}
    manifest = {'sourceCommit': revision, 'dirtyWorktree': dirty, 'filesSHA256': files,
                'scope': 'Authored static artifacts; no physical validation or live API dependencies.'}
    (DEST / 'build-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'status': 'built', 'sourceCommit': revision, 'dirtyWorktree': dirty, 'files': len(files)}))


if __name__ == '__main__':
    main()
