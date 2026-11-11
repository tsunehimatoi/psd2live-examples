#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Render a labelled synthetic comparison; requires the CLI's results/demo output."""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

CASE = Path(__file__).resolve().parents[1]


def load(name):
    with Image.open(CASE / name) as image:
        return image.copy()


def checker(image):
    bg = Image.new("RGBA", image.size)
    bg.putdata([(205, 214, 225, 255) if (x // 8 + y // 8) % 2 else (246, 248, 251, 255)
                for y in range(image.height) for x in range(image.width)])
    return Image.alpha_composite(bg, image.convert("RGBA")).convert("RGB")


def main():
    source = load("fixtures/source.png")
    donor = load("fixtures/donor-padded.png")
    mask = load("fixtures/mask.png")
    expected = load("fixtures/expected.png")
    adopted = load("results/demo/adopted.png")
    naive = source.convert("RGB")
    naive.paste(donor.crop((5, 7, 53, 47)), (23, 19))
    naive = naive.convert("RGBA")
    naive.putalpha(source.getchannel("A"))
    naive.save(CASE / "results/naive-whole-crop.png")
    record = json.loads((CASE / "results/demo/adoption.json").read_text(encoding="utf-8"))
    pollution = sum(a != b and not m for a, b, m in zip(source.get_flattened_data(), naive.get_flattened_data(), mask.get_flattened_data()))
    assert pollution == 1494 and adopted.tobytes() == expected.tobytes()
    board = Image.new("RGB", (1408, 650), "#111d30")
    draw = ImageDraw.Draw(board)
    font = ImageFont.load_default(size=18)
    small = ImageFont.load_default(size=15)
    title = ImageFont.load_default(size=25)
    draw.text((24, 18), "PROTECTED RGB DONOR ADOPTION", font=title, fill="#f1f5fb")
    draw.text((24, 54), "Original synthetic fixture | Exact crop + translation | Nearest-neighbor display; no character assets", font=small, fill="#a9bad1")
    panels = [(source, "01  SOURCE", "426 wrong-color pixels"),
              (naive, "02  WHOLE-CROP CONTROL", "1,494 protected pixels polluted"),
              (adopted, "03  PROTECTED ADOPTION", "0 protected / 0 alpha changes"),
              (expected, "04  INDEPENDENT TARGET", "Full decoded RGBA matches result")]
    for index, (image, heading, caption) in enumerate(panels):
        x = 24 + index * 346
        draw.text((x, 96), heading, font=font, fill="#f2f7ff")
        board.paste(checker(image).resize((288, 240), Image.Resampling.NEAREST), (x, 130))
        draw.text((x, 383), caption, font=small, fill="#6fe0d1" if index > 1 else "#ffb2a8")
    draw.line((24, 424, 1384, 424), fill="#344660", width=1)
    draw.text((24, 445), "BINARY MASK", font=font, fill="#f2f7ff")
    board.paste(mask.convert("RGB").resize((192, 160), Image.Resampling.NEAREST), (24, 477))
    draw.text((240, 445), "PADDED DONOR", font=font, fill="#f2f7ff")
    board.paste(donor.resize((180, 162), Image.Resampling.NEAREST), (240, 477))
    draw.text((452, 449), "White mask intersect placement = 426 pixels", font=font, fill="#c9d6e8")
    draw.text((452, 484), "Crop [5,7,53,47] -> Place [23,19,71,59]", font=font, fill="#c9d6e8")
    draw.text((452, 519), "Dark cross stays protected; asymmetric green wing tests alignment.", font=small, fill="#a9bad1")
    draw.text((452, 550), "427 white mask pixels: the one outside placement is ignored.", font=small, fill="#a9bad1")
    draw.text((452, 581), "Zero source alpha stays invisible. RGB-only cannot fill an alpha hole.", font=small, fill="#a9bad1")
    draw.text((452, 612), "Counts are fixture measurements, not character or motion acceptance.", font=small, fill="#a9bad1")
    board.save(CASE / "preview.png")
    summary = {"fixture_only": True, "adopted_rgb_pixels": record["actual_rgb_changed_pixels"],
               "protected_changes": record["protected_rgba_changed_pixels"], "alpha_changes": record["alpha_changed_pixels"],
               "naive_protected_contamination": pollution, "full_rgba_matches_independent_target": True}
    (CASE / "results/comparison.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
