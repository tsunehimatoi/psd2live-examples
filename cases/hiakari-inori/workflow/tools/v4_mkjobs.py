import numpy as np,os,json,sys
from PIL import Image
os.chdir('/workspace/art/inori')
M=np.asarray(Image.open('v4/legs/master_hr.png').convert('RGB'))
meta=json.load(open('v4/legs/jobs_meta.json'))
VAR={'shorts':"fitted plain black safety shorts (spats) made of matte opaque fabric, matching the outfit, covering the hip and the top of the thigh; below the shorts hem, pale skin down to the stocking",
     'briefs':"plain opaque solid black fabric briefs-style bottoms (non-revealing, fully opaque, simple full-coverage cut, like part of a costume) covering the hip area at the very top; below them, pale smooth skin of the thigh down to the stocking"}
jobs=[]
for s in 'RL':
    x0,y0,x1,y1=meta[s]['box']; vis=np.load(f'v4/legs/vis_{s}.npy')[y0:y1,x0:x1]; hid=np.load(f'v4/legs/hid_{s}.npy')[y0:y1,x0:x1]
    im=np.zeros((y1-y0,x1-x0,3),np.uint8); im[:]=(0,255,0); im[vis]=M[y0:y1,x0:x1][vis]; im[hid]=(255,0,255)
    side="the character's right leg (left side of the image)" if s=='R' else "the character's left leg (right side of the image)"
    for v,desc in VAR.items():
        for k in (1,2,3):
            d=f'v4/legs/jobs/{s}_{v}_c{k}'; os.makedirs(d,exist_ok=True)
            Image.fromarray(im).save(f'{d}/input.png'); Image.fromarray((hid*255).astype(np.uint8)).save(f'{d}/mask.png')
            W,H=x1-x0,y1-y0
            open(f'{d}/prompt.txt','w').write(f"""Files here: input.png ({W}x{H}) and mask.png (white = area to paint). input.png is a crop of a costume design sheet for an anime character (Live2D layer work): ONE leg only, {side}, front view, standing, in a black semi-sheer over-the-knee stocking and (lower part) a platform boot that has been removed; the skirt, garter straps and the other leg were removed and replaced by flat green. The MAGENTA area is the part of this leg that was hidden. Using your built-in image generation/editing, paint inside the magenta area: at the top, {desc}; the stocking top band continuing cleanly where straps covered it; at the bottom, the stocking-covered lower shin, ankle and foot as it would look inside the boot (no boot). Complete, rounded, natural leg silhouette running all the way to the top of the magenta region, same cel-shaded anime style, lighting and colors as the visible pixels. No straps, no garters, no charms, no cut edges, no hard horizontal lines, no fading, no fragments, no vertical ridge. Wherever the magenta extends beyond the natural leg/shorts silhouette, fill with flat pure #00FF00 green. Do not change non-magenta pixels; same canvas size and framing. The magenta pixels must come from your image generation output (resize to canvas, copy only magenta-position pixels). Save as output.png in this directory (exactly {W}x{H}). Then stop.""")
            jobs.append(d)
print(' '.join(jobs))
