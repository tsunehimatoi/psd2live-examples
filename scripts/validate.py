"""Validate catalog metadata and keep large binaries out of Git."""

import json
from pathlib import Path
import re
import subprocess

from fetch import validate_fixture


ROOT = Path(__file__).resolve().parents[1]


def validate(root=ROOT):
    catalog = json.loads((root / "catalog.json").read_text(encoding="utf-8"))
    if catalog["schema_version"] != 1:
        raise ValueError("Unsupported catalog version")
    ids = set()
    fixtures = []
    for case in catalog["cases"]:
        case_id = case["id"]
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", case_id) or case_id in ids:
            raise ValueError("Invalid or duplicate case ID")
        ids.add(case_id)
        if case["manifest"] != f"cases/{case_id}/manifest.json":
            raise ValueError("Unexpected case manifest path")
        manifest = json.loads((root / case["manifest"]).read_text(encoding="utf-8"))
        if manifest["schema_version"] != 1 or manifest["id"] != case_id:
            raise ValueError("Manifest identity differs from catalog")
        for key in ["title", "description", "version", "author", "tags", "source", "compatibility"]:
            if not manifest.get(key):
                raise ValueError(f"Missing case metadata: {case_id}.{key}")
        if not re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"]):
            raise ValueError("Case version must use major.minor.patch")
        if not re.fullmatch(r"[0-9a-f]{40}", manifest["source"]["commit"]):
            raise ValueError("Case source must pin a full commit SHA")
        if not (root / "cases" / case_id / "README.md").is_file():
            raise ValueError("Missing case README")
        validate_fixture(manifest)
        fixtures.append({key: manifest[key] for key in ["id", "version", "archive", "files"]})
    lock = json.loads((root / "scripts" / "fixtures.lock.json").read_text(encoding="utf-8"))
    if lock != {"schema_version": 1, "fixtures": fixtures}:
        raise ValueError("Download lock differs from case manifests")
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=root).decode().split("\0")
    for name in filter(None, tracked):
        path = root / name
        if path.stat().st_size > 5 * 1024 * 1024:
            raise ValueError(f"Put large files in a Release asset: {name}")
        if path.suffix.lower() in {".psd", ".psb", ".psd2live", ".cmo3", ".can3", ".moc3", ".zip", ".dll", ".so", ".dylib"}:
            raise ValueError(f"Put binary assets outside Git: {name}")
    print(f"Validated {len(ids)} cases and their pinned assets")


if __name__ == "__main__":
    validate()
