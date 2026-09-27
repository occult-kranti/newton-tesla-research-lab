#!/usr/bin/env python3
"""Check frozen hashes and optionally rerun producers without rewriting evidence.

This is a reproducibility gate, not the independent scientific review. The latter
uses separate numerical methods and lives in research/reviews/.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--regenerate", action="store_true")
    parser.add_argument("--round", choices=["R1","R2","R3"], action="append", dest="rounds")
    args = parser.parse_args()
    summary=[]
    for round_id in args.rounds or ["R1","R2","R3"]:
        folder=ROOT/"research"/round_id
        manifest=json.loads((folder/"manifest.json").read_text())
        assert manifest["round"] == round_id
        entries=manifest["files"]+[manifest["contract"]]+manifest["dependencies"]
        for entry in entries:
            assert digest(ROOT/entry["path"]) == entry["sha256"], f"Changed frozen artifact: {entry['path']}"
        result=json.loads((folder/"result.json").read_text())
        assert result["checks"] and all(c["passed"] is True for c in result["checks"]), f"Failed producer check: {round_id}"
        generated_count=0
        if args.regenerate:
            with tempfile.TemporaryDirectory(prefix=f"newton-tesla-{round_id}-") as temp:
                subprocess.run([sys.executable,str(folder/"run.py"),"--output",temp],check=True,cwd=ROOT,stdout=subprocess.PIPE,text=True)
                regenerated={str(p.relative_to(Path(temp))):p for p in Path(temp).rglob("*") if p.is_file()}
                expected={str((ROOT/e["path"]).relative_to(folder)):e for e in manifest["files"] if (ROOT/e["path"]).suffix != ".py"}
                assert set(regenerated)==set(expected), f"Output file set changed: {round_id}"
                for name,path in regenerated.items():
                    assert digest(path)==expected[name]["sha256"], f"Reproduction mismatch: {round_id}/{name}"
                generated_count=len(regenerated)
        summary.append({"round":round_id,"frozen_bindings_checked":len(entries),"producer_checks":len(result["checks"]),"regenerated_artifacts":generated_count})
    print(json.dumps({"status":"passed","mode":"regenerated" if args.regenerate else "hashes","rounds":summary},indent=2))

if __name__ == "__main__":
    main()
