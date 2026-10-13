"""Render a case preview from an exported .model3.json through the PSD2Live Cubism preview bridge.

Plays the model's own motions with physics on a white background and encodes a 320x480, 15 fps animated WebP.
Needs Pillow, ffmpeg with libwebp, and the native bridge built from the main project (native/live2d_renderer).
"""

import argparse
import ctypes
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageChops


WIDTH, HEIGHT, FPS, STEP = 320, 480, 15, 2


def bridge(directory):
    name = "live2d_renderer.dll" if sys.platform == "win32" else "liblive2d_renderer.so"
    if sys.platform == "win32":
        os.add_dll_directory(str(directory))
    lib = ctypes.CDLL(str(Path(directory) / name))
    lib.Live2D_GetLastError.restype = ctypes.c_char_p
    lib.Live2D_CreateModel.restype = ctypes.c_void_p
    lib.Live2D_CreateModel.argtypes = [ctypes.c_char_p]
    lib.Live2D_Update.argtypes = [ctypes.c_void_p, ctypes.c_float]
    lib.Live2D_StartMotion.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
    lib.Live2D_RenderToRgba.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_float,
                                        ctypes.c_float, ctypes.c_float, ctypes.c_void_p]
    return lib


def check(lib, ok):
    if not ok:
        raise RuntimeError(lib.Live2D_GetLastError().decode(errors="replace"))


def plan(model, names, limit):
    motions = json.loads(model.read_text(encoding="utf-8"))["FileReferences"].get("Motions", {})
    names = [name for name in names or ["Nod", "Shake", "Idle"] if name in motions] or list(motions)
    steps, total = [], 0.0
    for name in names:
        duration = json.loads((model.parent / motions[name][0]["File"]).read_text(encoding="utf-8"))["Meta"]["Duration"]
        duration = min(duration, limit - total)
        if duration <= 0:
            break
        steps.append((name, duration))
        total += duration
    return steps


def render(lib, model, steps, frames):
    width, height = WIDTH * 2, HEIGHT * 2
    check(lib, lib.Live2D_InitOffscreen())
    handle = lib.Live2D_CreateModel(str(model.resolve()).encode())
    check(lib, handle)
    buffer = (ctypes.c_uint8 * (width * height * 4))()
    images = []
    for name, duration in steps:
        check(lib, lib.Live2D_StartMotion(handle, name.encode(), 0, 3))
        for index in range(int(duration * FPS * STEP)):
            lib.Live2D_Update(handle, 1.0 / (FPS * STEP))
            if index % STEP:
                continue
            check(lib, lib.Live2D_RenderToRgba(handle, width, height, 1.0, 0.0, 0.0, buffer))
            r, g, b, a = Image.frombuffer("RGBA", (width, height), buffer, "raw", "RGBA", 0, 1).copy().split()
            white = ImageChops.invert(a)
            # The bridge reads back premultiplied pixels, so laying them over white adds the uncovered part.
            images.append(Image.merge("RGB", [ImageChops.add(channel, white) for channel in (r, g, b)]))
    lib.Live2D_Shutdown()
    box = None
    for image in images:
        b = image.convert("L").point(lambda v: 255 if v < 250 else 0).getbbox()
        if b:
            box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
    x0, y0, x1, y1 = box
    # A 2:3 window round everything the motions touch, with a little margin.
    span_y = max(y1 - y0, (x1 - x0) * HEIGHT / WIDTH) * 1.06
    span_x = span_y * WIDTH / HEIGHT
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    crop = tuple(round(v) for v in (cx - span_x / 2, cy - span_y / 2, cx + span_x / 2, cy + span_y / 2))
    for index, image in enumerate(images):
        image.crop(crop).resize((WIDTH, HEIGHT), Image.LANCZOS).save(frames / f"{index:04d}.png")
    return len(images)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("model", type=Path, help="exported .model3.json")
    parser.add_argument("output", type=Path, help="preview .webp to write")
    parser.add_argument("--renderer", type=Path, required=True,
                        help="directory holding the built bridge and its FrameworkShaders/")
    parser.add_argument("--motions", help="comma separated motion groups (default: Nod,Shake,Idle)")
    parser.add_argument("--seconds", type=float, default=10.0, help="longest preview length")
    arguments = parser.parse_args()
    if not shutil.which("ffmpeg"):
        parser.error("ffmpeg is required")
    steps = plan(arguments.model, arguments.motions and arguments.motions.split(","), arguments.seconds)
    with tempfile.TemporaryDirectory() as directory:
        count = render(bridge(arguments.renderer), arguments.model, steps, Path(directory))
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i", f"{directory}/%04d.png",
                        "-c:v", "libwebp_anim", "-lossless", "0", "-quality", "85", "-compression_level", "6",
                        "-loop", "0", str(arguments.output)], check=True)
    print(f"{arguments.output}: {count} frames, {' -> '.join(name for name, _ in steps)}, "
          f"{arguments.output.stat().st_size} bytes")


if __name__ == "__main__":
    main()
