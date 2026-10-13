"""Package tracked case assets, then update the manifest and download lock."""

import argparse
import json
from pathlib import Path
import subprocess
import zipfile

from fetch import digest, relative_path, validate_fixture


ROOT = Path(__file__).resolve().parents[1]


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case")
    parser.add_argument("--source-repository", type=Path, required=True)
    parser.add_argument("--source-directory", default="examples")
    parser.add_argument("--release-tag", required=True)
    arguments = parser.parse_args()
    manifest_path = ROOT / "cases" / arguments.case / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    case_id = manifest["id"]
    relative_path(f"{case_id}/input.psd", case_id)
    source = arguments.source_repository.resolve()
    prefix = f"{arguments.source_directory}/{case_id}/"
    subprocess.run(["git", "diff", "--exit-code", "HEAD", "--", prefix], cwd=source, check=True)
    tracked = subprocess.check_output(["git", "ls-files", "-z", "--", prefix], cwd=source).decode().split("\0")
    # Markdown is maintained in the case directory; only explicitly tracked assets are bundled.
    paths = sorted(path for path in tracked if path and not path.lower().endswith(".md"))
    if not paths:
        parser.error("No tracked assets found for this case")
    output = ROOT / "build" / "assets"
    output.mkdir(parents=True, exist_ok=True)
    name = f"{case_id}-{manifest['version']}.zip"
    archive = output / name
    records = []
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in paths:
            local = source / path
            name_in_bundle = path[len(arguments.source_directory) + 1:]
            relative_path(name_in_bundle, case_id)
            record = {"path": name_in_bundle, "size_bytes": local.stat().st_size, "sha256": digest(local)}
            info = zipfile.ZipInfo(name_in_bundle, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, local.read_bytes())
            records.append(record)
    manifest["source"]["commit"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source).decode().strip()
    manifest["archive"] = {
        "url": f"https://github.com/tsunehimatoi/psd2live-examples/releases/download/{arguments.release_tag}/{name}",
        "size_bytes": archive.stat().st_size, "sha256": digest(archive),
    }
    manifest["files"] = records
    validate_fixture(manifest)
    write_json(manifest_path, manifest)
    catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    fixtures = []
    for case in catalog["cases"]:
        entry = json.loads((ROOT / case["manifest"]).read_text(encoding="utf-8"))
        if entry.get("archive"):
            fixtures.append({key: entry[key] for key in ["id", "version", "archive", "files"]})
    write_json(ROOT / "scripts" / "fixtures.lock.json", {"schema_version": 1, "fixtures": fixtures})
    print(f"Packaged {case_id}: {len(records)} files, {archive.stat().st_size} bytes")


if __name__ == "__main__":
    main()
