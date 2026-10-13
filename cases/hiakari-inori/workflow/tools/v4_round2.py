import numpy as np,os,json,sys
from PIL import Image
from scipy import ndimage as ndi
os.chdir('/workspace/art/inori')
M=np.asarray(Image.open('v4/legs/master_hr.png').convert('RGB')).astype(int)
meta=json.load(open('v4/legs/jobs_meta.json'))
base={'R':'R_shorts_c3','L':'L_shorts_c2'}; g=dict(np.load('v4/legs/masks.npz'))
isg=lambda o:(o[...,1]>150)&(o[...,1]-np.maximum(o[...,0],o[...,2])>60)
for s in 'RL':
    x0,y0,x1,y1=meta[s]['box']; W,H=x1-x0,y1-y0
    o=np.asarray(Image.open(f'v4/legs/jobs/{base[s]}/output.png').convert('RGB').resize((W,H),Image.LANCZOS)).astype(int)
    vis=np.load(f'v4/legs/vis_{s}.npy')[y0:y1,x0:x1]; hid=np.load(f'v4/legs/hid_{s}.npy')[y0:y1,x0:x1]; sil=np.load(f'v4/legs/sil_{s}.npy')[y0:y1,x0:x1]
    im=np.zeros((H,W,3),int); im[:]=(0,255,0); im[vis]=M[y0:y1,x0:x1][vis]; h=hid&~isg(o); im[h]=o[h]
    yy=np.arange(H)[:,None]+y0
    # band rows: shorts hem .. below sock band; find garter extent in this side
    gar=g['gar'][y0:y1,x0:x1]&sil
    gy=np.where(gar.any(1))[0]+y0; gyl=gy.max()
    mag=sil&(yy>=1475)&(yy<=1715)
    gb=ndi.binary_dilation(gar&(yy>1715),iterations=10); mag|=gb&sil
    mag|=ndi.binary_dilation(sil&isg(im.astype(np.uint8))&(yy<2440),iterations=3)&sil
    im[mag]=(255,0,255)
    np.save(f'v4/legs/hid2_{s}.npy',mag)
    for k in (1,2,3):
        d=f'v4/legs/jobs/{s}_r2_c{k}'; os.makedirs(d,exist_ok=True)
        Image.fromarray(im.astype(np.uint8)).save(f'{d}/input.png'); Image.fromarray((mag*255).astype(np.uint8)).save(f'{d}/mask.png')
        open(f'{d}/prompt.txt','w').write(f"""Files here: input.png ({W}x{H}) and mask.png (white = area to paint). input.png is a crop of a costume design sheet for an anime character (Live2D layer work): ONE leg only, front view, wearing fitted plain black safety shorts at the top and a black semi-sheer over-the-knee stocking below, on flat green. The MAGENTA band is where garter straps and a charm were removed. Using your built-in image generation/editing, inpaint ONLY the magenta pixels: continue the pale smooth thigh skin evenly between the shorts hem and the stocking (uniform soft cel shading, no pale patches, no blotches), then the stocking's plain black top band as one continuous clean band, then the black semi-sheer stocking below it, matching the visible stocking exactly. No straps, no garters, no charms, no tassels, no ghosts, no fragments, no green holes, no cut edges. Keep the leg outline smooth and the same width as above and below. Where magenta lies outside the leg silhouette fill flat #00FF00. Do not change non-magenta pixels; same canvas size and framing. The magenta pixels must come from your image generation output (resize to canvas, copy only magenta-position pixels). Save as output.png here (exactly {W}x{H}). Then stop.""")
        print(d)
