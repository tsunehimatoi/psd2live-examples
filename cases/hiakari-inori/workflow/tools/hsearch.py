import numpy as np, cv2, sys, json
from PIL import Image
M=np.asarray(Image.open('head_closeup_2.png').convert('RGB')).astype(int)
fg=((M.min(2)<232)).astype(np.uint8)
fg[880:]=0
def search(name, ss, step=6):
    a=np.asarray(Image.open(f'keyed_head/{name}.png'))[...,3]>100
    a=a.astype(np.uint8); a[880:]=a[880:]  # keep
    best=(0,None)
    H,W=a.shape
    for s in ss:
        r=cv2.resize(a,None,fx=s,fy=s,interpolation=cv2.INTER_AREA)
        ys,xs=np.where(r>0)
        # coarse: align bbox centers then search +-40
        cx,cy=(xs.min()+xs.max())/2,(ys.min()+ys.max())/2
        gx,gy=(fg.shape[1]-1)/2, 480
        for dy in range(-60,61,step):
            for dx in range(-60,61,step):
                tx=int(round(gx-cx+dx)); ty=int(round(gy-cy+dy))
                canvas=np.zeros_like(fg); 
                y0,x0=max(0,ty),max(0,tx); y1=min(fg.shape[0],ty+r.shape[0]); x1=min(fg.shape[1],tx+r.shape[1])
                if y1<=y0 or x1<=x0: continue
                canvas[y0:y1,x0:x1]=r[y0-ty:y1-ty,x0-tx:x1-tx]
                canvas[880:]=0
                inter=(canvas&fg).sum(); uni=(canvas|fg).sum()
                iou=inter/uni
                if iou>best[0]: best=(iou,(s,tx-s*0,ty,))
    return best
if __name__=='__main__':
    for n in sys.argv[1:]:
        print(n,search(n,[0.85,0.9,0.95,1.0,1.05]))
