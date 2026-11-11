#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Execute the real CLI against an independently specified geometric fixture."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

from PIL import Image

CASE = Path(__file__).resolve().parents[1]
FIXTURES = CASE / "fixtures"
RESULTS = []


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def insert_chunk(data, kind, payload):
    chunk = struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    return data[:33] + chunk + data[33:]


def png16(path):
    # Real encoded 16-bit RGB, which Pillow may expose as decoded RGB8.
    header = struct.pack(">IIBBBBB", 2, 2, 16, 2, 0, 0, 0)
    def chunk(kind, payload):
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    raw = b"\0" + struct.pack(">HHH", 1000, 2000, 3000) * 2
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(raw * 2)) + chunk(b"IEND", b""))


def command(output, **changes):
    values = {"source": FIXTURES / "source.png", "donor": FIXTURES / "donor-padded.png",
              "mask": FIXTURES / "mask.png", "mask-convention": "white-edit-black-protect",
              "donor-crop": [5, 7, 53, 47], "place": [23, 19, 71, 59], "out-dir": output}
    values.update(changes)
    args = [sys.executable, str(CASE / "workflow/adopt_donor.py")]
    for key, value in values.items():
        args.append("--" + key)
        args.extend(map(str, value if isinstance(value, list) else [value]))
    return args


class AdoptionContract(unittest.TestCase):
    def test_rgb_source_and_rgba_donor(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            source, donor = root / "source-rgb.png", root / "donor-rgba.png"
            with Image.open(FIXTURES / "source.png") as image:
                image.convert("RGB").save(source)
            with Image.open(FIXTURES / "donor-padded.png") as image:
                image.convert("RGBA").save(donor)
            out = root / "result"
            proc = subprocess.run(command(out, source=source, donor=donor), text=True, capture_output=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            with Image.open(out / "adopted.png") as actual, Image.open(FIXTURES / "expected.png") as expected:
                self.assertEqual(actual.tobytes(), expected.convert("RGB").convert("RGBA").tobytes())
            RESULTS.append({"test": "rgb_source_rgba_donor", "status": "PASS", "output_alpha": 255})

    def test_normal_and_replay(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            before_hashes = {p.name: sha(p) for p in FIXTURES.iterdir() if p.is_file()}
            outputs = []
            for run in ["first", "clean-replay"]:
                out = root / run
                proc = subprocess.run(command(out), text=True, capture_output=True)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                with Image.open(out / "adopted.png") as actual, Image.open(FIXTURES / "expected.png") as expected:
                    self.assertEqual(actual.mode, "RGBA")
                    self.assertEqual(actual.size, (96, 80))
                    self.assertEqual(actual.tobytes(), expected.tobytes())
                    outputs.append(actual.tobytes())
                record = json.loads((out / "adoption.json").read_text(encoding="utf-8"))
                for key, value in {"allowed_pixels": 426, "mask_white_pixels_total": 427,
                                   "actual_rgb_changed_pixels": 426, "protected_rgba_changed_pixels": 0,
                                   "alpha_changed_pixels": 0,
                                   "rejected_donor_rgb_differences_in_placement_protected": 1494}.items():
                    self.assertEqual(record[key], value, key)
                for file, info in record["outputs"].items():
                    self.assertEqual(sha(out / file), info["sha256"])
            self.assertEqual(outputs[0], outputs[1])
            self.assertEqual(before_hashes, {p.name: sha(p) for p in FIXTURES.iterdir() if p.is_file()})
            RESULTS.append({"test": "normal_and_clean_replay", "status": "PASS", "full_rgba_equals_independent_expected": True,
                            "changed_rgb": 426, "protected_rgba_changes": 0, "alpha_changes": 0,
                            "ignored_protected_donor_changes_in_placement": 1494})

    def test_naive_control(self):
        with Image.open(FIXTURES / "source.png") as image:
            source = image.copy()
        with Image.open(FIXTURES / "donor-padded.png") as image:
            patch = image.crop((5, 7, 53, 47))
        with Image.open(FIXTURES / "mask.png") as image:
            mask = image.copy()
        naive = source.convert("RGB")
        naive.paste(patch, (23, 19))
        naive = naive.convert("RGBA")
        naive.putalpha(source.getchannel("A"))
        polluted = sum(a != b and not m for a, b, m in zip(source.get_flattened_data(), naive.get_flattened_data(), mask.get_flattened_data()))
        self.assertEqual(polluted, 1494)
        RESULTS.append({"test": "whole_crop_paste_control", "status": "PASS", "protected_pixels_polluted": polluted,
                        "source_alpha_preserved_for_fair_comparison": True})

    def test_rejections(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            bad_mask = root / "nonbinary.png"
            with Image.open(FIXTURES / "mask.png") as im:
                im.putpixel((32, 28), 128)
                im.save(bad_mask)
            wrong_mask = root / "wrong-mask.png"
            Image.new("L", (95, 80), 255).save(wrong_mask)
            zero_mask = root / "zero.png"
            Image.new("L", (96, 80), 0).save(zero_mask)
            alpha_donor = root / "translucent.png"
            with Image.open(FIXTURES / "donor-padded.png") as im:
                im = im.convert("RGBA")
                im.putpixel((14, 16), (1, 2, 3, 254))  # source32,28: selected.
                im.save(alpha_donor)
            deep = root / "rgb16.png"
            png16(deep)
            with Image.open(deep) as image:
                self.assertEqual(image.mode, "RGB", "exercise the decoded-mode trap")
            color = root / "gamma.png"
            color.write_bytes(insert_chunk((FIXTURES / "source.png").read_bytes(), b"gAMA", struct.pack(">I", 45455)))
            indexed = root / "palette.png"
            Image.new("P", (96, 80)).save(indexed)
            corrupt = root / "corrupt.png"
            corrupt.write_bytes((FIXTURES / "source.png").read_bytes()[:-9])
            cases = [
                ("size_mismatch", {"place": [23, 19, 70, 59]}, "dimensions must match"),
                ("crop_out_of_bounds", {"donor-crop": [5, 7, 61, 47]}, "out of bounds"),
                ("place_out_of_bounds", {"place": [-1, 19, 47, 59]}, "out of bounds"),
                ("reversed_crop", {"donor-crop": [53, 7, 5, 47]}, "reversed"),
                ("nonbinary_mask", {"mask": bad_mask}, "binary"),
                ("wrong_mask_size", {"mask": wrong_mask}, "mask dimensions"),
                ("mask_rgb_mode", {"mask": FIXTURES / "source.png"}, "grayscale L"),
                ("donor_not_opaque", {"donor": alpha_donor}, "opaque"),
                ("zero_adoption", {"mask": zero_mask}, "no adoptable"),
                ("encoded_rgb16", {"donor": deep}, "encoded header"),
                ("gamma_metadata", {"source": color}, "gAMA"),
                ("palette_input", {"source": indexed}, "encoded header"),
                ("truncated_png", {"source": corrupt}, "truncated"),
                ("wrong_mask_convention", {"mask-convention": "black-edit"}, "invalid choice"),
            ]
            for label, changes, error in cases:
                with self.subTest(label=label):
                    out = root / ("rejected-" + label)
                    proc = subprocess.run(command(out, **changes), text=True, capture_output=True)
                    self.assertNotEqual(proc.returncode, 0)
                    self.assertIn(error, proc.stderr)
                    self.assertFalse(out.exists())
                    self.assertFalse(list(root.glob(".adopt-*")))
                    RESULTS.append({"test": label, "status": "REJECTED_AS_EXPECTED", "exit_code": proc.returncode,
                                    "error": proc.stderr.strip().splitlines()[-1], "success_outputs_exist": False})
            out = root / "existing"
            out.mkdir()
            (out / "sentinel").write_text("unchanged", encoding="utf-8")
            proc = subprocess.run(command(out), text=True, capture_output=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertEqual([p.name for p in out.iterdir()], ["sentinel"])
            self.assertEqual((out / "sentinel").read_text(), "unchanged")
            RESULTS.append({"test": "existing_output", "status": "REJECTED_AS_EXPECTED", "sentinel_preserved": True})
            input_file = root / "source.png"
            input_file.write_bytes((FIXTURES / "source.png").read_bytes())
            old_hash = sha(input_file)
            proc = subprocess.run(command(input_file, source=input_file), text=True, capture_output=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertEqual(sha(input_file), old_hash)
            RESULTS.append({"test": "output_is_input", "status": "REJECTED_AS_EXPECTED", "input_bytes_preserved": True})

    def test_nonopaque_donor_protected_pixel_is_ignored(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            donor = root / "donor.png"
            with Image.open(FIXTURES / "donor-padded.png") as im:
                im = im.convert("RGBA")
                im.putpixel((5, 7), (1, 2, 3, 0))  # protected pixel in the mapped crop.
                im.save(donor)
            out = root / "accepted"
            proc = subprocess.run(command(out, donor=donor), text=True, capture_output=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            with Image.open(out / "adopted.png") as actual, Image.open(FIXTURES / "expected.png") as expected:
                self.assertEqual(actual.tobytes(), expected.tobytes())
            RESULTS.append({"test": "protected_transparent_donor_pixel", "status": "PASS"})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(AdoptionContract)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {"status": "PASS" if result.wasSuccessful() else "FAIL", "unittest_methods": result.testsRun,
              "failures": len(result.failures), "errors": len(result.errors), "cases": RESULTS}
    Path(args.report).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    sys.exit(0 if result.wasSuccessful() else 1)
