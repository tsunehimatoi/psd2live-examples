#!/usr/bin/env python3
"""CPU anime upscaler: Real-ESRGAN x4plus anime 6B (torch CPU via spandrel).
usage: python3 upscale.py in.png out.png --scale 4 [--tile 192] [--model RealESRGAN_x4plus_anime_6B|realesr-animevideov3]
- RGB goes through the model; alpha (if RGBA) is Lanczos-upscaled separately + light edge treatment.
- scale 2/3/4 supported (model is native x4; other scales are resized from the x4 result with Lanczos/area).
Auto re-execs under /workspace/tools/venv-sr/bin/python (has torch-cpu, spandrel, scipy, cv2) if torch is missing.
"""
import sys, os, time, argparse
try:
    import torch, spandrel
except ImportError:
    vp = '/workspace/tools/venv-sr/bin/python'
    if os.path.exists(vp) and os.path.realpath(sys.executable) != vp and not os.environ.get('_UPS_REEXEC'):
        os.environ['_UPS_REEXEC'] = '1'
        os.execv(vp, [vp] + sys.argv)
    raise
import numpy as np, cv2
from PIL import Image
from scipy import ndimage as ndi

W = '/workspace/tools/weights/'
def load(name):
    from spandrel import ModelLoader
    m = ModelLoader().load_from_file(W + name + '.pth'); m.eval(); return m

def sr4(rgb, m, tile=192, pad=16, log=True):
    H, Wd, _ = rgb.shape; s = m.scale
    out = np.zeros((H*s, Wd*s, 3), np.float32)
    x = torch.from_numpy(rgb.transpose(2, 0, 1).copy())[None]
    n = ((H + tile - 1)//tile) * ((Wd + tile - 1)//tile); k = 0; t0 = time.time()
    for y0 in range(0, H, tile):
        for x0 in range(0, Wd, tile):
            y1, x1 = min(y0+tile, H), min(x0+tile, Wd)
            a, b, c, d = max(y0-pad, 0), max(x0-pad, 0), min(y1+pad, H), min(x1+pad, Wd)
            with torch.inference_mode():
                o = m(x[:, :, a:c, b:d])[0].float().numpy().transpose(1, 2, 0)
            oy, ox = (y0-a)*s, (x0-b)*s
            out[y0*s:y1*s, x0*s:x1*s] = o[oy:oy+(y1-y0)*s, ox:ox+(x1-x0)*s]
            k += 1
            if log and (k % 10 == 0 or k == n):
                print(f'  tile {k}/{n}  {time.time()-t0:.0f}s', flush=True)
    return np.clip(out, 0, 1)

def resize(img, size, down=False):
    interp = cv2.INTER_AREA if down else cv2.INTER_LANCZOS4
    return cv2.resize(img, size, interpolation=interp)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('inp'); ap.add_argument('out')
    ap.add_argument('--scale', type=float, default=4)
    ap.add_argument('--tile', type=int, default=192)
    ap.add_argument('--model', default='RealESRGAN_x4plus_anime_6B')
    ap.add_argument('--threads', type=int, default=8)
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    t0 = time.time()
    im = Image.open(a.inp)
    has_a = im.mode in ('RGBA', 'LA') or 'transparency' in im.info
    im = im.convert('RGBA' if has_a else 'RGB')
    arr = np.array(im).astype(np.float32) / 255
    H, Wd = arr.shape[:2]
    rgb = arr[..., :3]
    m = load(a.model)
    tw, th = int(round(Wd*a.scale)), int(round(H*a.scale))
    if has_a:
        al = arr[..., 3]
        solid = al >= 0.5
        if solid.any():
            idx = ndi.distance_transform_edt(~solid, return_distances=False, return_indices=True)
            ext = rgb[idx[0], idx[1]]
            w = np.clip(al*2, 0, 1)[..., None]
            rgb = rgb*w + ext*(1-w)   # no halo/black fringe from transparent pixels
    up = sr4(rgb, m, a.tile)
    s = m.scale
    if (tw, th) != (Wd*s, H*s):
        up = resize(up, (tw, th), down=a.scale < s)
    up = np.clip(up, 0, 1)
    if has_a:
        au = cv2.resize(al, (tw, th), interpolation=cv2.INTER_LANCZOS4).clip(0, 1)
        # light edge treatment: 0.7px blur, then gentle contrast on the edge ramp to keep it crisp, kill far-field noise
        au = cv2.GaussianBlur(au, (0, 0), 0.7)
        au = np.clip((au - 0.5)*1.25 + 0.5, 0, 1)
        far = cv2.dilate((cv2.resize(al, (tw, th), interpolation=cv2.INTER_LINEAR) > 0.002).astype(np.uint8), np.ones((5, 5), np.uint8)) == 0
        au[far] = 0
        out = np.dstack([up, au])
    else:
        out = up
    Image.fromarray(np.round(out*255).astype(np.uint8)).save(a.out)
    print(f'done {Wd}x{H} -> {tw}x{th} in {time.time()-t0:.1f}s -> {a.out}')
if __name__ == '__main__':
    main()
