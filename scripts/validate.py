"""Validate catalog metadata and keep large binaries out of Git."""

import json
from pathlib import Path
import re
import subprocess

from fetch import validate_fixture


ROOT = Path(__file__).resolve().parents[1]


def validate_source(source):
    if source.get("kind") == "local-import":
        if not source.get("name") or not re.fullmatch(r"[0-9a-f]{64}", source.get("inventory_sha256", "")):
            raise ValueError("Local imports must identify their source inventory")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", source.get("imported_on", "")):
            raise ValueError("Local imports must record the import date")
    elif not re.fullmatch(r"[0-9a-f]{40}", source.get("commit", "")):
        raise ValueError("Git case sources must pin a full commit SHA")


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
        validate_source(manifest["source"])
        validate_fixture(manifest)
        fixtures.append({key: manifest[key] for key in ["id", "version", "archive", "files"]})
    for case_dir in (root / "cases").iterdir():
        if case_dir.is_dir():
            if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", case_dir.name):
                raise ValueError(f"Invalid case directory name: {case_dir.name}")
            if not (case_dir / "README.md").is_file():
                raise ValueError(f"Missing case README: {case_dir.name}")
            if (case_dir / "manifest.json").is_file() and case_dir.name not in ids:
                raise ValueError(f"Case manifest is not in the catalog: {case_dir.name}")
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
