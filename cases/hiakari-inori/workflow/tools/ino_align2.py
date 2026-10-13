import numpy as np, cv2, sys, os, json
from PIL import Image
D='/workspace/art/inori'; os.chdir(D)
HEADS='back_hair ear_L ear_R face_base neck eye_white iris eyelash eyebrow nose mouth mouth_open front_hair ahoge mask ribbon choker'.split()
PAIRS='eye_white iris eyelash eyebrow legwear boots'.split()
REFC={'head':cv2.imread('head_1.png'),'body':cv2.imread('master_1.png')}
os.makedirs('aligned2',exist_ok=True)
def gray_over(im,bgv=None):
    a=im[...,3:4]/255.; 
    m=(im[...,:3]*a).sum((0,1))/max(a.sum(),1) if bgv is None else bgv
    rgb=im[...,:3]*a+np.asarray(m)*(1-a); return cv2.cvtColor(rgb.astype(np.uint8),cv2.COLOR_RGB2GRAY).astype(np.float32)
def edge(g,b):
    g=cv2.GaussianBlur(g,(0,0),b); gx=cv2.Sobel(g,cv2.CV_32F,1,0); gy=cv2.Sobel(g,cv2.CV_32F,0,1); return np.sqrt(gx**2+gy**2)
def split(im):
    a=(im[...,3]>20).sum(0).astype(float); xs=np.where(a>0)[0]; x0,x1=xs.min(),xs.max()
    lo,hi=int(x0+.3*(x1-x0)),int(x0+.7*(x1-x0)); cut=lo+int(np.argmin(a[lo:hi]))
    l=im.copy(); l[:,cut:,3]=0; r=im.copy(); r[:,:cut,3]=0; return l,r
def affine_of(s,tx,ty,cx,cy):  # layer point p -> ref point s*(p-c)+c+t
    return np.float32([[s,0,cx-s*cx+tx],[0,s,cy-s*cy+ty]])
def fit(im,R,blur,search):
    a=(im[...,3]>200).astype(np.uint8)
    if a.sum()<30: return affine_of(1,0,0,0,0),0
    ys,xs=np.where(a>0); cx,cy=(xs.min()+xs.max())/2,(ys.min()+ys.max())/2
    Rg=cv2.cvtColor(R,cv2.COLOR_BGR2GRAY).astype(np.float32); Re=edge(Rg,blur)
    best=(-2,)
    H,W=a.shape
    for s in np.arange(0.93,1.075,0.01):
        M=affine_of(s,0,0,cx,cy)
        wl=cv2.warpAffine(im,M,(W,H),flags=cv2.INTER_LINEAR); wa=(wl[...,3]>200).astype(np.uint8)
        if wa.sum()<30: continue
        yy,xx=np.where(wa>0); x0,x1,y0,y1=max(xx.min()-2,0),xx.max()+3,max(yy.min()-2,0),yy.max()+3
        tg=gray_over(wl); te=edge(tg,blur)[y0:y1,x0:x1]; tm=cv2.erode(wa,np.ones((3,3),np.uint8))[y0:y1,x0:x1].astype(np.float32)
        te=te*tm
        # search window: pad ref
        pad=search
        P=cv2.copyMakeBorder(Re,pad,pad,pad,pad,cv2.BORDER_CONSTANT,value=0)
        sub=P[max(y0,0):y1+2*pad, max(x0,0):x1+2*pad]
        if sub.shape[0]<te.shape[0] or sub.shape[1]<te.shape[1]: continue
        r=cv2.matchTemplate(sub,te.astype(np.float32),cv2.TM_CCORR_NORMED,mask=np.dstack([tm]*1)[...,0])
        _,mx,_,loc=cv2.minMaxLoc(r)
        # location loc in sub coords: sub origin at padded coords (x0,y0)-> ref coords (x0+loc[0]-pad, ...)
        tx=loc[0]-pad; ty=loc[1]-pad
        if mx>best[0]: best=(mx,s,tx,ty)
    mx,s,tx,ty=best
    return affine_of(s,tx,ty,cx,cy),mx
def warp(im,M):
    a=im[...,3:4]/255.; pm=np.concatenate([im[...,:3]*a,im[...,3:4]],2).astype(np.float32)
    o=cv2.warpAffine(pm,M,(im.shape[1],im.shape[0]),flags=cv2.INTER_LANCZOS4)
    al=np.clip(o[...,3:4],0,255); rgb=np.where(al>1e-3,o[...,:3]/np.maximum(al/255.,1e-3),0)
    return np.concatenate([np.clip(rgb,0,255),al],2).astype(np.uint8)
def run(name):
    im=np.asarray(Image.open(f'keyed/{name}.png').convert('RGBA')).copy(); R=REFC['head' if name in HEADS else 'body']
    blur=1.6 if name in ('eyebrow','eyelash','nose','mouth','mouth_open','iris','eye_white') else 3.0
    search=40 if name in ('eyebrow','eyelash','nose','mouth','mouth_open','iris','eye_white','ear_L','ear_R','ribbon','mask','choker') else 110
    parts=[im] if name not in PAIRS else list(split(im)); outs=[]; info=[]
    for p in parts:
        M,sc=fit(p,R,blur,search); outs.append(warp(p,M)); info.append((round(float(sc),3),round(float(M[0,0]),3),round(float(M[0,2]-(1-M[0,0])*0),1),round(float(M[1,2]),1)))
    res=outs[0].copy()
    if len(outs)==2: m=outs[1][...,3]>outs[0][...,3]; res[m]=outs[1][m]
    Image.fromarray(res,'RGBA').save(f'aligned2/{name}.png')
    if len(outs)==2:
        for k,o in enumerate(outs): Image.fromarray(o,'RGBA').save(f'aligned2/{name}_{"LR"[k]}.png')
    return info
if __name__=='__main__':
    names=sys.argv[1:] or sorted(f[:-4] for f in os.listdir('keyed'))
    for n in names: print(n,run(n),flush=True)
