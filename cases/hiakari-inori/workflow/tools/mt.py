import numpy as np, cv2, sys, json
from PIL import Image
M=cv2.cvtColor(np.asarray(Image.open('head_closeup_2.png').convert('RGB')),cv2.COLOR_RGB2BGR)
def blobs(a,k=15,minarea=300):
    m=(a>128).astype(np.uint8); d=cv2.dilate(m,np.ones((k,k),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(d); out=[]
    for i in range(1,n):
        if st[i,4]>minarea:
            ys,xs=np.where((lab==i)&(m>0)); out.append((xs.min(),xs.max()+1,ys.min(),ys.max()+1))
    return sorted(out)
def match(rgba, box, scales, search=None):
    """box=(x0,x1,y0,y1) crop of layer; returns best (score,s,tx,ty) mapping layer px p -> master px s*p+t"""
    x0,x1,y0,y1=box; pad=4
    x0=max(0,x0-pad);y0=max(0,y0-pad);x1=min(rgba.shape[1],x1+pad);y1=min(rgba.shape[0],y1+pad)
    crop=rgba[y0:y1,x0:x1]; best=(-1e18,)
    for s in scales:
        t=cv2.resize(crop,None,fx=s,fy=s,interpolation=cv2.INTER_AREA)
        if t.shape[0]>=M.shape[0] or t.shape[1]>=M.shape[1]: continue
        mask=(t[...,3]>200).astype(np.float32)
        if mask.sum()<50: continue
        tb=cv2.cvtColor(t[...,:3],cv2.COLOR_RGB2BGR)
        res=cv2.matchTemplate(M,tb,cv2.TM_SQDIFF,mask=np.dstack([mask]*3))
        mn,_,loc,_=cv2.minMaxLoc(res)
        sc=-(mn/(mask.sum()*3))**0.5
        if sc>best[0]: best=(sc,s,loc[0]-s*x0,loc[1]-s*y0)
    return best
if __name__=='__main__':
    name=sys.argv[1]; lo,hi,stp=float(sys.argv[2]),float(sys.argv[3]),float(sys.argv[4])
    img=np.asarray(Image.open(f'keyed_head/{name}.png').convert('RGBA'))
    scales=np.arange(lo,hi+1e-6,stp)
    bl=blobs(img[...,3]) if len(sys.argv)>5 and sys.argv[5]=='pair' else [(0,img.shape[1],0,img.shape[0])]
    for b in bl:
        print(name,b,[round(float(v),3) for v in match(img,b,scales)])
