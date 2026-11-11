#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Generate original geometric fixtures (CC0), independently of the adoption tool."""
import argparse
import json
from pathlib import Path

from PIL import Image

SIZE = (96, 80)
PLACE = (23, 19, 71, 59)
CROP = (5, 7, 53, 47)


def editable(x, y):
    return ((31 <= x < 55 and 27 <= y < 47 and not (45 <= x < 48 or 35 <= y < 37))
            or (55 <= x < 63 and 39 <= y < 45))


def target_rgb(x, y):
    if 45 <= x < 48 or 35 <= y < 37:
        return (22, 36, 65)  # A protected cross runs through the repair rectangle.
    if (x - 49) ** 2 // 3 + (y - 39) ** 2 < 420:
        return (40 + x % 9 * 5, 130 + y % 8 * 8, 100 + (x + 2 * y) % 7 * 7)
    return (210 + x % 5 * 7, 160 + y % 7 * 8, 65 + (x + y) % 6 * 12)


def source_alpha(x, y):
    if x < 9 or y < 8 or x >= 88 or y >= 73 or (35 <= x < 38 and 41 <= y < 44):
        return 0
    return 96 if (3 * x + y) % 9 == 0 else (190 if (x + y) % 7 == 0 else 255)


def generate(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    expected, source, mask = [], [], []
    for y in range(SIZE[1]):
        for x in range(SIZE[0]):
            good = (*target_rgb(x, y), source_alpha(x, y))
            expected.append(good)
            source.append((230, 35, 150, good[3]) if editable(x, y) else good)
            # White outside the placement deliberately tests the intersection rule.
            mask.append(255 if editable(x, y) or (x, y) == (2, 3) else 0)
    for name, pixels in [("source.png", source), ("expected.png", expected)]:
        image = Image.new("RGBA", SIZE)
        image.putdata(pixels)
        image.save(out / name)
    image = Image.new("L", SIZE)
    image.putdata(mask)
    image.save(out / "mask.png")
    donor = Image.new("RGB", (60, 54), (245, 20, 210))
    for y in range(40):
        for x in range(48):
            sx, sy = x + PLACE[0], y + PLACE[1]
            color = target_rgb(sx, sy) if editable(sx, sy) else (185, 55, 235)
            donor.putpixel((x + CROP[0], y + CROP[1]), color)
    donor.save(out / "donor-padded.png")
    # Literal expectations derived from the fixture's rectangular geometry:
    # 24*20 - 3*20 - 2*24 + 3*2 + 8*6 = 426; crop 48*40 - 426 = 1494.
    spec = {"fixture_kind": "original synthetic geometry, no character assets",
            "source_size": list(SIZE), "donor_size": [60, 54],
            "crop": list(CROP), "placement": list(PLACE),
            "expected_allowed_pixels": 426, "expected_mask_white_pixels": 427,
            "expected_rgb_changes": 426, "expected_naive_protected_contamination": 1494,
            "expected_protected_changes": 0, "expected_alpha_changes": 0,
            "known_points": {"repaired": [32, 28], "protected_cross": [46, 30],
                             "asymmetric_wing": [61, 42], "white_outside_placement": [2, 3],
                             "transparent_repair": [36, 42], "transparent_protected": [1, 1]},
            "expected_image_oracle": "target_rgb and source_alpha evaluated directly over the whole canvas, without importing or calling adopt_donor",
            "alpha_zero_note": "RGB changes under alpha=0 do not create visible content"}
    (out / "expected.json").write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
    return spec


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", required=True)
    print(json.dumps(generate(parser.parse_args().out_dir), indent=2))
