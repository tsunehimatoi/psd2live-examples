import numpy as np,os,json
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
M=np.asarray(Image.open('legs/master_hr.png').convert('RGB'))
L=lambda n:np.load(f'legs/{n}.npy'); H,W=3072,2048
cl=L('cut_leg'); cl=np.where(np.isnan(cl),1020,cl)
meta={}
for s,box in [('R',(700,1220,1060,1960)),('L',(980,1220,1340,1960))]:
    v=L(f'vis_leg_{s}'); sil=v|L(f'hid_leg_{s}')
    ys=np.arange(1520,1700); outer=[]
    for y in ys:
        q=np.where(sil[y])[0]; outer.append(q.min() if s=='R' else q.max())
    k,b=np.polyfit(ys,outer,1)
    yt=1250; ox=k*yt+b; ox=ox-25 if s=='R' else ox+25
    ix=cl[1460]
    # polygon: outer top -> along outer line down to 1960, inner along cut, crotch
    pts=[(ox,yt)]+[(k*y+b+(-6 if s=='R' else 6),y) for y in range(1300,1700,20)]
    pts+= [(outer[-1],1700)]
    reg=Image.new('L',(W,H),0); d=ImageDraw.Draw(reg)
    inner=[(cl[y]+(0 if s=='R' else 0),y) for y in range(1700,1380,-20)]
    d.polygon(pts+[(cl[1700],1700)]+inner+[(ix,1300)],fill=255)
    reg=np.asarray(reg)>0
    xx=np.arange(W)[None]; yy=np.arange(H)[:,None]
    band=(yy>=1250)&(yy<1720)&((xx>=980)&(xx<1022) if s=='R' else (xx>=1004)&(xx<1060))
    reg|=band
    reg|=sil&(np.arange(H)[:,None]<1960)
    reg=ndi.binary_closing(reg,iterations=5)
    hid=reg&~v; hid[1960:]=False
    x0,y0,x1,y1=box
    im=np.zeros((y1-y0,x1-x0,3),np.uint8); im[:]=(0,255,0)
    vv=v[y0:y1,x0:x1]; hh=hid[y0:y1,x0:x1]
    im[vv]=M[y0:y1,x0:x1][vv]; im[hh]=(255,0,255)
    dd=f'legs/jobs3/thigh_{s}'; os.makedirs(dd,exist_ok=True)
    Image.fromarray(im).save(f'{dd}/input.png'); Image.fromarray((hh*255).astype(np.uint8)).save(f'{dd}/mask.png')
    np.save(f'legs/hid3_thigh_{s}.npy',hid)
    side='right leg (left side of image)' if s=='R' else 'left leg (right side of image)'
    open(f'{dd}/prompt.txt','w').write(f"""Files here: input.png ({x1-x0}x{y1-y0}) and mask.png (white = area to paint). input.png is a crop of an anime character illustration: the character's {side}, front view, in a black semi-sheer thigh-high stocking with pale skin above it; the skirt and garters were removed. The MAGENTA area is where the upper thigh was hidden. Using your built-in image generation/editing, paint a complete, natural upper thigh inside the magenta area: smooth skin continuing all the way up to the thigh root / hip crease at the top of the magenta region, rounded natural contour, same cel-shaded anime style, lighting and skin tone as the visible skin, continuing the black stocking top band where it was covered. No clothing, no straps, no cut edges, no hard horizontal lines, no fading. Wherever the magenta extends beyond the natural leg silhouette (outside the leg), fill with flat pure #00FF00 green. Do not change non-magenta pixels; same canvas size and framing. Save as output.png in this directory (resize to exactly {x1-x0}x{y1-y0}). Then stop.""")
    meta[f'thigh_{s}']=dict(layer=f'leg_{s}',box=list(box),hid=int(hh.sum()))
json.dump(meta,open('legs/jobs3/meta.json','w'),indent=1); print(meta)
