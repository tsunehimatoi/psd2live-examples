import numpy as np, cv2, sys, os, json
from PIL import Image
D='/workspace/art/inori'; os.chdir(D)
HEADS='back_hair ear_L ear_R face_base neck eye_white iris eyelash eyebrow nose mouth mouth_open front_hair ahoge mask ribbon choker'.split()
PAIRS='eye_white iris eyelash eyebrow legwear boots'.split()
REF={'head':cv2.imread('head_1.png',0).astype(np.float32),'body':cv2.imread('master_1.png',0).astype(np.float32)}
os.makedirs('aligned3',exist_ok=True)
def gray(im,bg=255.):
    a=im[...,3:4]/255.; rgb=im[...,:3]*a+bg*(1-a); return cv2.cvtColor(rgb.astype(np.uint8),cv2.COLOR_RGB2GRAY).astype(np.float32)
def split(im):
    a=(im[...,3]>20).sum(0).astype(float); xs=np.where(a>0)[0]; x0,x1=xs.min(),xs.max()
    lo,hi=int(x0+.3*(x1-x0)),int(x0+.7*(x1-x0)); cut=lo+int(np.argmin(a[lo:hi]))
    l=im.copy(); l[:,cut:,3]=0; r=im.copy(); r[:,:cut,3]=0; return l,r
def ecc(T,I,m,W,mode,it=300):
    try: cc,W=cv2.findTransformECC(T,I,W,mode,(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,it,1e-6),m,5); return cc,W
    except cv2.error: return -1,W
def fit(im,R,blur,margin=130,grid=(-90,-45,0,45,90)):
    a=(im[...,3]>200).astype(np.uint8)
    if a.sum()<30: return np.float32([[1,0,0],[0,1,0]]),-9,'empty'
    ys,xs=np.where(a>0); H,Wd=a.shape
    x0,x1,y0,y1=max(xs.min()-margin,0),min(xs.max()+margin,Wd),max(ys.min()-margin,0),min(ys.max()+margin,H)
    T=cv2.GaussianBlur(R[y0:y1,x0:x1],(0,0),blur); I=cv2.GaussianBlur(gray(im)[y0:y1,x0:x1],(0,0),blur)
    m=cv2.erode(a[y0:y1,x0:x1],np.ones((3,3),np.uint8))
    best=(-2,None)
    for dy in grid:
        for dx in grid:
            W=np.float32([[1,0,dx],[0,1,dy]])  # template->input : input = template + (dx,dy) ; layer needs to move by -d
            cc,W2=ecc(T,I,m,W,cv2.MOTION_TRANSLATION,150)
            if cc>best[0]: best=(cc,W2.copy())
    cc,Wt=best; mode='tr'
    if Wt is None: return np.float32([[1,0,0],[0,1,0]]),-9,'fail'
    cc2,Wa=ecc(T,I,m,Wt.copy(),cv2.MOTION_AFFINE,400)
    if cc2>cc-0.02:
        sc=np.sqrt(abs(np.linalg.det(Wa[:,:2]))); sh=abs(Wa[0,1]+Wa[1,0])
        if 0.94<sc<1.06 and sh<0.05: cc,Wt,mode=cc2,Wa,'aff'
    # to full-image coords: input_full = W_full @ template_full ; crop offset o
    A=np.vstack([Wt,[0,0,1]]); P=np.array([[1,0,x0],[0,1,y0],[0,0,1]],np.float64)
    Wf=(P@A@np.linalg.inv(P))[:2].astype(np.float32)
    return Wf,cc,mode
def warp(im,W):
    a=im[...,3:4]/255.; pm=np.concatenate([im[...,:3]*a,im[...,3:4]],2).astype(np.float32)
    o=cv2.warpAffine(pm,W,(im.shape[1],im.shape[0]),flags=cv2.INTER_LANCZOS4|cv2.WARP_INVERSE_MAP)
    al=np.clip(o[...,3:4],0,255); rgb=np.where(al>1e-3,o[...,:3]/np.maximum(al/255.,1e-3),0)
    return np.concatenate([np.clip(rgb,0,255),al],2).astype(np.uint8)
def run(name):
    im=np.asarray(Image.open(f'keyed/{name}.png').convert('RGBA')).copy(); R=REF['head' if name in HEADS else 'body']
    small=name in ('eyebrow','eyelash','nose','mouth','mouth_open','iris','eye_white')
    blur=1.4 if small else 2.5; grid=(-30,-15,0,15,30) if small else (-90,-45,0,45,90)
    parts=[im] if name not in PAIRS else list(split(im)); outs=[]; info=[]
    for p in parts:
        W,cc,mode=fit(p,R,blur,100 if small else 130,grid); outs.append(warp(p,W)); info.append((round(float(cc),3),mode,round(float(W[0,2]),1),round(float(W[1,2]),1),round(float(W[0,0]),3)))
    res=outs[0].copy()
    if len(outs)==2: m=outs[1][...,3]>outs[0][...,3]; res[m]=outs[1][m]
    Image.fromarray(res,'RGBA').save(f'aligned3/{name}.png')
    return info
if __name__=='__main__':
    names=sys.argv[1:] or sorted(f[:-4] for f in os.listdir('keyed'))
    for n in names: print(n,run(n),flush=True)
