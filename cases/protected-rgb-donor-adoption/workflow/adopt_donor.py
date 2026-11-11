#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Copy explicitly allowed donor RGB at known coordinates, preserving source alpha."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import zlib

from PIL import Image

CONVENTION = "white-edit-black-protect"
COLOR_CHUNKS = {b"iCCP", b"sRGB", b"gAMA", b"cHRM", b"cICP", b"mDCV", b"cLLI"}
UNSUPPORTED_CHUNKS = COLOR_CHUNKS | {b"tRNS", b"eXIf", b"acTL", b"fcTL", b"fdAT"}
MAX_PIXELS = 40_000_000


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load_png(path, label, mask=False):
    """Check encoded depth/type before Pillow decoding; retain the exact input hash."""
    data = Path(path).read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{label}: expected PNG signature")
    position, chunks, header, seen_idat = 8, 0, None, False
    while position < len(data):
        if position + 12 > len(data):
            raise ValueError(f"{label}: truncated PNG chunk")
        length = struct.unpack(">I", data[position:position + 4])[0]
        kind = data[position + 4:position + 8]
        end = position + 12 + length
        if end > len(data):
            raise ValueError(f"{label}: truncated PNG payload")
        payload = data[position + 8:position + 8 + length]
        crc = struct.unpack(">I", data[position + 8 + length:end])[0]
        if zlib.crc32(kind + payload) & 0xFFFFFFFF != crc:
            raise ValueError(f"{label}: PNG CRC mismatch")
        if chunks == 0 and (kind != b"IHDR" or length != 13):
            raise ValueError(f"{label}: missing first IHDR")
        if kind == b"IHDR":
            if header is not None or length != 13:
                raise ValueError(f"{label}: invalid duplicate IHDR")
            header = struct.unpack(">IIBBBBB", payload)
            width, height, depth, color, compression, filtering, interlace = header
            if depth != 8 or color not in ({0} if mask else {2, 6}):
                expected = "8-bit grayscale L" if mask else "8-bit RGB or RGBA"
                raise ValueError(f"{label}: requires {expected} PNG (encoded header)")
            if not width or not height or width * height > MAX_PIXELS:
                raise ValueError(f"{label}: dimensions exceed supported 1..{MAX_PIXELS} pixels")
            if compression != 0 or filtering != 0 or interlace != 0:
                raise ValueError(f"{label}: requires standard noninterlaced PNG")
        elif kind in UNSUPPORTED_CHUNKS:
            raise ValueError(f"{label}: unsupported PNG metadata/chunk {kind.decode('ascii')}")
        elif kind == b"IDAT":
            seen_idat = True
        elif kind == b"IEND":
            if length or end != len(data) or not seen_idat:
                raise ValueError(f"{label}: invalid IEND or trailing data")
            position = end
            break
        elif not kind[0] & 32:
            raise ValueError(f"{label}: unsupported critical PNG chunk")
        position = end
        chunks += 1
    else:
        raise ValueError(f"{label}: missing IEND")
    with Image.open(io.BytesIO(data)) as opened:
        opened.load()
        if opened.mode not in ({"L"} if mask else {"RGB", "RGBA"}):
            raise ValueError(f"{label}: unexpected decoded mode")
        image = opened.copy() if mask else opened.convert("RGBA")
    return image, {"name": Path(path).name, "sha256": sha(data),
                   "dimensions": list(image.size), "encoded_bit_depth": header[2],
                   "encoded_color_type": header[3]}


def checked_box(values, size, label):
    left, top, right, bottom = values
    if not (0 <= left < right <= size[0] and 0 <= top < bottom <= size[1]):
        raise ValueError(f"{label}: rectangle is empty, reversed, or out of bounds")
    return tuple(values)


def adopt(args):
    output = Path(args.out_dir)
    if os.path.lexists(output):
        raise ValueError("output directory must not already exist; inputs are never overwritten")
    if not output.parent.is_dir():
        raise ValueError("output parent directory must already exist")
    source, source_info = load_png(args.source, "source")
    donor, donor_info = load_png(args.donor, "donor")
    mask, mask_info = load_png(args.mask, "mask", mask=True)
    if mask.size != source.size:
        raise ValueError("mask dimensions must equal source dimensions")
    if set(mask.get_flattened_data()) - {0, 255}:
        raise ValueError("mask must be binary L: only 0 and 255")
    crop = checked_box(args.donor_crop, donor.size, "donor crop")
    place = checked_box(args.place, source.size, "placement")
    patch = donor.crop(crop)
    if patch.size != (place[2] - place[0], place[3] - place[1]):
        raise ValueError("donor crop and placement dimensions must match exactly; no resizing")
    effective = Image.new("L", source.size, 0)
    local_mask = mask.crop(place)
    effective.paste(local_mask, place[:2])
    adoption_pixels = local_mask.histogram()[255]
    if adoption_pixels == 0:
        raise ValueError("no adoptable pixels in placement intersect mask")
    for allowed, rgba in zip(local_mask.get_flattened_data(), patch.get_flattened_data()):
        if allowed and rgba[3] != 255:
            raise ValueError("donor must be opaque at every adoptable pixel")
    before_patch = source.crop(place)
    rejected = sum(1 for a, b, selected in zip(before_patch.get_flattened_data(), patch.get_flattened_data(), local_mask.get_flattened_data())
                   if not selected and a[:3] != b[:3])
    # Binary paste modifies RGB only. Copy the original alpha, including zero-alpha RGB.
    rgb = source.convert("RGB")
    rgb.paste(patch.convert("RGB"), place[:2], local_mask)
    result = rgb.convert("RGBA")
    result.putalpha(source.getchannel("A"))
    changed_rgb = protected_changes = alpha_changes = 0
    for old, new, allowed in zip(source.get_flattened_data(), result.get_flattened_data(), effective.get_flattened_data()):
        changed_rgb += old[:3] != new[:3]
        protected_changes += not allowed and old != new
        alpha_changes += old[3] != new[3]
    if protected_changes or alpha_changes:
        raise ValueError("internal invariant failed: protected pixels or alpha changed")
    checker = Image.new("RGBA", source.size)
    checker.putdata([(210, 216, 225, 255) if (x // 8 + y // 8) % 2 else (245, 247, 250, 255)
                     for y in range(source.height) for x in range(source.width)])
    preview = Image.alpha_composite(checker, result)
    highlight = Image.new("RGBA", source.size, (0, 190, 235, 0))
    highlight.putalpha(effective.point(lambda value: 80 if value else 0))
    preview = Image.alpha_composite(preview, highlight).convert("RGB")
    record = {"schema_version": 1, "operation": "exact RGB crop and translation",
              "inputs": {"source": source_info, "donor": donor_info, "mask": mask_info},
              "mask_convention": CONVENTION, "coordinate_convention": "integer xyxy, left/top inclusive, right/bottom exclusive",
              "donor_crop": list(crop), "placement": list(place),
              "source_dimensions": list(source.size), "output_mode": "RGBA",
              "mask_white_pixels_total": mask.histogram()[255], "allowed_pixels": adoption_pixels,
              "actual_rgb_changed_pixels": changed_rgb, "protected_rgba_changed_pixels": protected_changes,
              "alpha_changed_pixels": alpha_changes,
              "rejected_donor_rgb_differences_in_placement_protected": rejected,
              "rejected_comparison_scope": "Only donor crop mapped 1:1 to placement, where mask is black; no mapping claimed outside placement or for donor padding",
              "color_policy": "numeric RGB preserved; no color-space conversion; color-management metadata rejected",
              "alpha_policy": "all source alpha preserved; RGB may change under zero source alpha inside the effective mask",
              "metadata_policy": "output PNGs carry no input metadata",
              "outputs": {}}
    # Stage the whole set and publish only after validation and all writes succeed.
    with tempfile.TemporaryDirectory(prefix=".adopt-", dir=output.parent) as staging:
        stage = Path(staging) / "complete"
        stage.mkdir()
        for name, image in [("adopted.png", result), ("adoption-preview.png", preview)]:
            image.save(stage / name)
            data = (stage / name).read_bytes()
            record["outputs"][name] = {"sha256": sha(data), "dimensions": list(image.size)}
        (stage / "adoption.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        if os.path.lexists(output):
            raise ValueError("output appeared during execution; refusing overwrite")
        stage.rename(output)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ["source", "donor", "mask", "out-dir"]:
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--mask-convention", choices=[CONVENTION], required=True)
    parser.add_argument("--donor-crop", nargs=4, type=int, metavar=("L", "T", "R", "B"), required=True)
    parser.add_argument("--place", nargs=4, type=int, metavar=("L", "T", "R", "B"), required=True)
    args = parser.parse_args()
    try:
        record = adopt(args)
    except (ValueError, OSError, Image.DecompressionBombError) as error:
        parser.exit(2, f"adopt_donor: {error}\n")
    print(json.dumps({"status": "OK", "allowed_pixels": record["allowed_pixels"],
                      "actual_rgb_changed_pixels": record["actual_rgb_changed_pixels"]}))


if __name__ == "__main__":
    main()
