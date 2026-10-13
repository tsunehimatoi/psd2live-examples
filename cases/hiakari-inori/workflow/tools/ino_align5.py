import numpy as np, cv2, sys, os, json
from PIL import Image
sys.path.insert(0,'/workspace/tools')
import ino_align3 as A
os.chdir('/workspace/art/inori')
def scale_about(im,s,cx,cy):
    M=np.float32([[s,0,cx-s*cx],[0,s,cy-s*cy]]); return A.warp(im,np.linalg.inv(np.vstack([M,[0,0,1]]))[:2].astype(np.float32)),M
def fit_scale(p,R,blur,scales,grid,margin=60):
    a=(p[...,3]>200); ys,xs=np.where(a); cx,cy=(xs.min()+xs.max())/2,(ys.min()+ys.max())/2
    best=(-2,)
    for s in scales:
        q,M=scale_about(p,s,cx,cy)
        W,cc,mode=A.fit(q,R,blur,margin,grid)
        if cc>best[0]: best=(cc,s,W,M)
    cc,s,W,M=best
    out=A.warp(scale_about(p,s,cx,cy)[0],W)
    return out,cc,s,W
if __name__=='__main__':
    for name in sys.argv[1:]:
        im=np.asarray(Image.open(f'keyed/{name}.png').convert('RGBA')).copy(); R=A.REF['head']
        parts=list(A.split(im)) if name in A.PAIRS else [im]; outs=[]
        for p in parts:
            o,cc,s,W=fit_scale(p,R,1.4,np.arange(0.7,1.31,0.04),(-40,-20,0,20,40)); outs.append(o)
            ys,xs=np.where(o[...,3]>128); print(name,'cc',round(float(cc),3),'s',round(float(s),2),'bbox',(xs.min(),ys.min(),xs.max(),ys.max()),flush=True)
        res=outs[0].copy()
        for o in outs[1:]: m=o[...,3]>res[...,3]; res[m]=o[m]
        Image.fromarray(res,'RGBA').save(f'aligned5/{name}.png')
