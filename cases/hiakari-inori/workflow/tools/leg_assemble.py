import numpy as np,json,os,cv2
from PIL import Image
from scipy import ndimage as ndi
M=np.asarray(Image.open('legs/master_hr.png').convert('RGB'))
L=lambda n:np.load(f'legs/{n}.npy'); H,W=3072,2048
meta=json.load(open('legs/jobs/meta.json'))
fill={k:np.zeros((H,W,3),np.uint8) for k in ['leg_R','leg_L','boot_R','boot_L']}
have={k:np.zeros((H,W),bool) for k in fill}
for j,m in meta.items():
    x0,y0,x1,y1=m['box']; o=np.asarray(Image.open(f'legs/jobs/{j}/output.png').convert('RGB').resize((x1-x0,y1-y0),Image.LANCZOS))
    h=L('hid_'+m['layer'])[y0:y1,x0:x1]
    sub=fill[m['layer']][y0:y1,x0:x1]; hv=have[m['layer']][y0:y1,x0:x1]
    sub[h&~hv]=o[h&~hv]; hv|=h
os.makedirs('legs/layers',exist_ok=True); stats={}
def mk(vis,hidm,fillimg):
    rgb=np.zeros((H,W,3),np.uint8); rgb[vis]=M[vis]; rgb[hidm]=fillimg[hidm]
    a=(vis|hidm).astype(np.float32); a=cv2.GaussianBlur(a,(0,0),0.6); a[ndi.binary_erosion(vis|hidm)]=1
    # don't fade inner seams against other layers: only feather outer edges
    return np.dstack([rgb,(a*255+.5).astype(np.uint8)])
yy=np.arange(H)[:,None]
out={}
for s in 'RL':
    v=L(f'vis_leg_{s}'); h=L(f'hid_leg_{s}')&have[f'leg_{s}']
    f=fill[f'leg_{s}'].astype(int); green=(f[...,1]>150)&(f[...,1]-np.maximum(f[...,0],f[...,2])>60); h&=~green
    if s=='L':
        cl=np.where(np.isnan(L('cut_leg')),1020,L('cut_leg'))[:,None]; xx=np.arange(W)[None]
        h&=~((xx<cl)&~(L('vis_leg_R')|L('hid_leg_R')))
    stats[f'leg_{s}_uncovered_hidden']=int((L(f'hid_leg_{s}')&~have[f'leg_{s}']).sum())
    full=mk(v,h,fill[f'leg_{s}'])
    th=full.copy(); fade=np.clip((2060-yy)/40,0,1); th[...,3]=(th[...,3]*fade).astype(np.uint8)
    sh=full.copy(); sh[:1980,:,3]=0
    out[f'thigh_{s}']=th; out[f'shin_{s}']=sh
    vb=L(f'vis_boot_{s}'); hb=L(f'hid_boot_{s}')&have[f'boot_{s}']
    f=fill[f'boot_{s}'].astype(int); hb&=~((f[...,1]>150)&(f[...,1]-np.maximum(f[...,0],f[...,2])>60))
    if s=='L':
        cb=np.where(np.isnan(L('cut_boot')),1011,L('cut_boot'))[:,None]; xx=np.arange(W)[None]
        hb&=~((xx<cb)&~L('vis_boot_R'))
    out[f'boot_{s}']=mk(vb,hb,fill[f'boot_{s}'])
    g=L(f'gar_{s}'); out[f'garter_{s}']=mk(g,np.zeros_like(g),fill['leg_R'])
for k,a in out.items(): Image.fromarray(a,'RGBA').save(f'legs/layers/{k}.png')
# skirt without garters
sk=np.asarray(Image.open('final/skirt.png').convert('RGBA')).copy()
g=ndi.binary_dilation(L('gar_R')|L('gar_L'),iterations=2); sk[g,3]=0
Image.fromarray(sk,'RGBA').save('legs/layers/skirt_nogarter.png')
json.dump(stats,open('legs/assemble_stats.json','w')); print(stats)
