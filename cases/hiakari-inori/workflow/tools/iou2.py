import numpy as np, cv2, sys
from PIL import Image
M=np.asarray(Image.open('head_closeup_2.png').convert('RGB')).astype(int)
R,G,B=M[...,0],M[...,1],M[...,2]
nonwhite=M.min(2)<232
hair=(nonwhite&((R-B)<14))|((B-R)>60)
skin=nonwhite&((R-B)>=14)&(R>180)
masks={'hair':hair,'silh':nonwhite,'headfull':hair|skin}
for k in masks: masks[k][900:]=False
def search(name,mk,s_rng,step_px=3,cx0=None):
    a=(np.asarray(Image.open(f'keyed_head/{name}.png'))[...,3]>100).astype(np.uint8)
    t=masks[mk].astype(np.uint8); best=(0,)
    for s in s_rng:
        r=cv2.resize(a,None,fx=s,fy=s,interpolation=cv2.INTER_AREA); h,w=r.shape
        ys,xs=np.where(r>0); bx,by=xs.min(),ys.min()
        # coarse by FFT cross-correlation of r with t
        rr=r.astype(np.float32); tt=t.astype(np.float32)
        # correlation score = sum(r*t); IoU = inter/(sum r + sum t - inter)
        res=cv2.matchTemplate(tt,rr,cv2.TM_CCORR)  # inter at each offset
        sr=rr.sum(); st=tt.sum()
        iou=res/(sr+st-res)
        _,mx,_,loc=cv2.minMaxLoc(iou)
        if mx>best[0]: best=(mx,s,loc[0],loc[1])
    return best
if __name__=='__main__':
    n,mk=sys.argv[1],sys.argv[2]; lo,hi,stp=map(float,sys.argv[3:6])
    print(n,mk,[round(float(v),3) for v in search(n,mk,np.arange(lo,hi+1e-6,stp))])
