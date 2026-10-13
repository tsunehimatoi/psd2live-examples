import cv2, numpy as np, sys, json
from PIL import Image
M=cv2.imread('gpt/master_gpt.png')  # BGR
Mg=cv2.cvtColor(M,cv2.COLOR_BGR2GRAY).astype(np.float32)
def prep(p):
    im=np.asarray(Image.open(p).convert('RGBA'))
    return im
def search(name, scales, region=None):
    im=prep(f'keyed/{name}.png'); a=im[...,3]
    ys,xs=np.where(a>40); x0,x1,y0,y1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
    crop=im[y0:y1,x0:x1]
    best=None
    for s in scales:
        w=max(8,int(round(crop.shape[1]*s))); h=max(8,int(round(crop.shape[0]*s)))
        c=cv2.resize(crop,(w,h),interpolation=cv2.INTER_AREA)
        if h>=M.shape[0] or w>=M.shape[1]: continue
        mask=(c[...,3]>230).astype(np.uint8)
        mask=cv2.erode(mask,np.ones((3,3),np.uint8))
        if mask.sum()<30: continue
        g=cv2.cvtColor(c[...,:3],cv2.COLOR_RGB2GRAY).astype(np.float32)
        mk=np.dstack([mask]*1).astype(np.float32)
        # use TM_CCOEFF_NORMED with mask
        r=cv2.matchTemplate(Mg,g,cv2.TM_CCOEFF_NORMED,mask=mask.astype(np.float32))
        r=np.nan_to_num(r,nan=-1,posinf=-1,neginf=-1)
        _,mx,_,loc=cv2.minMaxLoc(r)
        if best is None or mx>best[0]: best=(mx,s,loc,(x0,y0))
    mx,s,loc,(x0,y0)=best
    # transform layer->master: p' = s*(p - (x0,y0)) + loc
    tx=loc[0]-s*x0; ty=loc[1]-s*y0
    return dict(score=float(mx),s=float(s),tx=float(tx),ty=float(ty))
if __name__=='__main__':
    res={}
    for n in sys.argv[1:]:
        r=search(n, np.arange(0.4,0.95,0.01)); res[n]=r; print(n,r)
    json.dump(res,open('keyed/tm_result.json','w'),indent=1)
