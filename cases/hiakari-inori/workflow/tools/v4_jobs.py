import numpy as np,os,json
from PIL import Image
from scipy import ndimage as ndi
os.chdir('/workspace/art/inori')
M=np.asarray(Image.open('v4/legs/master_hr.png').convert('RGB')).astype(int)
d=dict(np.load('v4/legs/masks.npz')); H,W=3072,2048; yy,xx=np.mgrid[:H,:W]
occ,fg,cut,boot,gar=d['occ'],d['fg'],d['cut'],d['boot'],d['gar']
C=cut[:,None]
dark=(M.max(2)<120)&fg
garD=ndi.binary_dilation(gar,iterations=4)
skin=fg&(M[...,0]>150)&(M[...,0]-M[...,2]>22)&~garD&~occ
Y0,YS,YB=1250,1680,2440   # hip top, sock fully below garter band, boot top approx
out={}
for s in 'RL':
    side=(xx<C) if s=='R' else (xx>=C)
    sk=dark&side&(yy>=YS)&(yy<2700)&~boot
    lab,n=ndi.label(sk); sz=ndi.sum(sk,lab,range(1,n+1)); sk=lab==(1+int(np.argmax(sz)))
    sk=ndi.binary_fill_holes(ndi.binary_closing(sk,iterations=4))
    # per-row extents in sock zone; fit lines on 1600-1800 for extrapolation upward
    ys=np.arange(1760,1950); lo=[];hi=[]
    for y in ys: q=np.where(sk[y])[0]; lo.append(q.min() if len(q) else np.nan); hi.append(q.max() if len(q) else np.nan)
    lo=np.array(lo);hi=np.array(hi);g=~np.isnan(lo);kl,bl=np.polyfit(ys[g],lo[g],1); kh,bh=np.polyfit(ys[g],hi[g],1)
    print(s,kl,bl,kh,bh,np.where(sk.any(0))[0][[0,-1]],np.where(sk.any(1))[0][[0,-1]])
    sil=sk.copy()
    for y in range(Y0,YS+20):
        a=kl*y+bl; b=kh*y+bh
        if s=='R': a-=22; b=max(b+10,cut[y]+14)   # inner: cross cut line for overlap
        else: a=min(a-10,cut[y]-14); b+=22
        sil[y,int(a):int(b)+1]=True
    for y in range(YS,H):
        q=np.where(sil[y])[0]
        if len(q): sil[y,q.min():q.max()+1]=True
    sil|=boot&side  # shin continues inside boot
    vis=(sk&~garD&~occ)|(skin&sil&(yy<YS+20))
    vis=ndi.binary_opening(vis,iterations=1)
    hid=sil&~vis
    hid[ (yy>=YS)&~ndi.binary_dilation(sk|(boot&side),iterations=2)&~(yy<YS+20)]=False
    x0=int(np.where(sil.any(0))[0].min())-40; x1=int(np.where(sil.any(0))[0].max())+40
    y0,y1=Y0-30,H
    np.save(f'v4/legs/sil_{s}.npy',sil); np.save(f'v4/legs/vis_{s}.npy',vis); np.save(f'v4/legs/hid_{s}.npy',hid); np.save(f'v4/legs/sock_{s}.npy',sk)
    out[s]=dict(box=[x0,y0,x1,y1],vis=int(vis.sum()),hid=int(hid.sum()))
json.dump(out,open('v4/legs/jobs_meta.json','w')); print(out)
