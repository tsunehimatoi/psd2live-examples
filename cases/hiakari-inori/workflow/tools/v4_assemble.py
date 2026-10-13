import numpy as np,json,cv2,os
from PIL import Image
from scipy import ndimage as ndi
os.chdir('/workspace/art/inori')
H,W=3072,2048; yy,xx=np.mgrid[:H,:W]
M=np.asarray(Image.open('v4/legs/master_hr.png').convert('RGB')).astype(np.float32)
g=dict(np.load('v4/legs/masks.npz')); occ,fg,cut,boot,gar=g['occ'],g['fg'],g['cut'],g['boot'],g['gar']
rf=json.load(open('v4/wleg/refine.json'))
def sc2(Mx): Mx=np.array(Mx,np.float64).copy(); Mx[:,2]*=2; return Mx
def warp(rgba,Mx):
    a=rgba[...,3:].astype(np.float32)/255; pm=np.dstack([rgba[...,:3]*a,a*255]).astype(np.float32)
    w=cv2.warpAffine(pm,Mx,(W,H),flags=cv2.INTER_LANCZOS4); al=np.clip(w[...,3],0,255)
    rgb=np.where(al[...,None]>0,w[...,:3]/np.maximum(al[...,None],1e-3)*255,0); return np.clip(rgb,0,255),al
OUT={}; ST={}
for d,s in [('R_w4','R'),('L_w8','L')]:
    G=np.asarray(Image.open(f'v4/wleg/{d}/hr.png')).astype(np.float32)
    gr,ga=warp(G,sc2(rf[f'{d}_thigh']['M']))
    side=(xx<cut[:,None]) if s=='R' else (xx>=cut[:,None])
    sock=np.load(f'v4/legs/sock_{s}.npy'); bt=boot&side; gs=gar&side
    gsil=ga>128
    lab,n=ndi.label(gsil); 
    if n>1: sz=ndi.sum(gsil,lab,range(1,n+1)); gsil=lab==(1+np.argmax(sz))
    # visible leg from master: fg on this side inside generated silhouette (dilated) or sock; not occluded
    vis=fg&side&~occ&~bt&(ndi.binary_dilation(gsil,iterations=6)|sock)
    vis=ndi.binary_opening(vis,iterations=1)
    hid=gsil&~vis&(yy<2100)&~ndi.binary_dilation(vis,iterations=0 if False else 1)&(occ|~fg)
    hid&=(yy>=1200)
    # color match generated to master on ring near boundary
    ring=ndi.binary_dilation(hid,iterations=8)&vis
    off=(M[ring]-gr[ring]).mean(0) if ring.sum()>200 else np.zeros(3)
    ST[s]=dict(vis=int(vis.sum()),hid=int(hid.sum()),ring=int(ring.sum()),coloff=off.round(1).tolist())
    rgb=np.zeros((H,W,3),np.float32); rgb[vis]=M[vis]; rgb[hid]=np.clip(gr[hid]+off*0.7,0,255)
    full=vis|hid
    a=cv2.GaussianBlur(full.astype(np.float32),(0,0),0.6); a[ndi.binary_erosion(full)]=1
    A=(a*255+.5).astype(np.uint8)
    th=np.dstack([rgb,A]).astype(np.uint8); th[yy[:, :1].ravel()>=2040,:,3]=0
    sh_m=(sock|ndi.binary_dilation(bt,iterations=0)&False)&(yy>=1960)
    shb=sh_m|(bt&(yy<2520)&ndi.binary_dilation(sock,iterations=30))
    shc=np.zeros((H,W,3),np.float32); shc[shb]=M[shb]; a2=cv2.GaussianBlur(shb.astype(np.float32),(0,0),0.6); a2[ndi.binary_erosion(shb)]=1
    sh=np.dstack([shc,a2*255]).astype(np.uint8)
    def lay(m):
        c=np.zeros((H,W,3),np.float32); c[m]=M[m]; aa=cv2.GaussianBlur(m.astype(np.float32),(0,0),0.6); aa[ndi.binary_erosion(m)]=1
        return np.dstack([c,aa*255]).astype(np.uint8)
    OUT[f'thigh_{s}']=th; OUT[f'shin_{s}']=sh; OUT[f'boot_{s}']=lay(bt); OUT[f'garter_{s}']=lay(gs&~occ)
for k,v in OUT.items(): Image.fromarray(v,'RGBA').save(f'v4/legs/layers/{k}.png')
json.dump(ST,open('v4/legs/assemble_stats.json','w')); print(ST)
