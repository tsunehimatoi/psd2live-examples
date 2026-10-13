import sys, os, subprocess, json, numpy as np
from PIL import Image
names=sys.argv[1:]
meta={}
if os.path.exists('up4/meta.json'): meta=json.load(open('up4/meta.json'))
for n in names:
    im=Image.open(f'keyed/{n}.png').convert('RGBA'); a=np.asarray(im)[...,3]
    ys,xs=np.where(a>8); pad=12
    x0=max(0,xs.min()-pad); y0=max(0,ys.min()-pad); x1=min(im.width,xs.max()+1+pad); y1=min(im.height,ys.max()+1+pad)
    im.crop((x0,y0,x1,y1)).save(f'up4/{n}_crop.png')
    r=subprocess.run(['python3','/workspace/tools/upscale.py',f'up4/{n}_crop.png',f'up4/{n}_x4.png','--scale','4'],capture_output=True,text=True)
    print(n,(x1-x0,y1-y0),r.stdout.strip()[-80:],r.stderr.strip()[-200:])
    meta[n]=dict(x0=int(x0),y0=int(y0))
    json.dump(meta,open('up4/meta.json','w'))
