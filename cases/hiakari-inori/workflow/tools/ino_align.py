import numpy as np, cv2, sys, os, json
from PIL import Image
D='/workspace/art/inori'; os.chdir(D)
HEADS='back_hair ear_L ear_R face_base neck eye_white iris eyelash eyebrow nose mouth mouth_open front_hair ahoge mask ribbon choker'.split()
PAIRS='eye_white iris eyelash eyebrow legwear boots'.split()
REF={'head':cv2.imread('head_1.png',0).astype(np.float32),'body':cv2.imread('master_1.png',0).astype(np.float32)}
os.makedirs('aligned',exist_ok=True)
def gray(im):
    a=im[...,3:4]/255.; rgb=im[...,:3]*a+255*(1-a); return cv2.cvtColor(rgb.astype(np.uint8),cv2.COLOR_RGB2GRAY).astype(np.float32)
def split(im):
    a=(im[...,3]>20).sum(0).astype(float); xs=np.where(a>0)[0]; x0,x1=xs.min(),xs.max()
    lo,hi=int(x0+.3*(x1-x0)),int(x0+.7*(x1-x0)); cut=lo+int(np.argmin(a[lo:hi]))
    l=im.copy(); l[:,cut:,3]=0; r=im.copy(); r[:,:cut,3]=0; return l,r
def fit(im,R,blur):
    a=(im[...,3]>200).astype(np.uint8)
    if a.sum()<30: return np.float32([[1,0,0],[0,1,0]]),-1,'empty'
    g=gray(im); Rb=cv2.GaussianBlur(R,(0,0),blur); gb=cv2.GaussianBlur(g,(0,0),blur)
    m=cv2.dilate(a,np.ones((5,5),np.uint8))
    best=None
    for mode in (cv2.MOTION_AFFINE,cv2.MOTION_TRANSLATION):
        W=np.eye(2,3,dtype=np.float32)
        try: cc,W=cv2.findTransformECC(Rb,gb,W,mode,(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,400,1e-6),m,7)
        except cv2.error: continue
        sc=np.sqrt(abs(np.linalg.det(W[:,:2]))); sh=abs(W[0,1]+W[1,0])
        ok = mode==cv2.MOTION_TRANSLATION or (0.9<sc<1.1 and sh<0.06)
        if ok and (best is None or cc>best[1]+0.0): best=(W.copy(),cc,'aff' if mode==cv2.MOTION_AFFINE else 'tr'); 
        if ok and mode==cv2.MOTION_AFFINE: break
    if best is None: return np.float32([[1,0,0],[0,1,0]]),-1,'fail'
    return best
def warp(im,W):
    # W maps template(ref) coords -> input(layer) coords; warpAffine with WARP_INVERSE_MAP gives layer resampled into ref coords
    a=im[...,3:4]/255.; pm=np.concatenate([im[...,:3]*a,im[...,3:4]],2).astype(np.float32)
    o=cv2.warpAffine(pm,W,(im.shape[1],im.shape[0]),flags=cv2.INTER_LANCZOS4|cv2.WARP_INVERSE_MAP)
    al=np.clip(o[...,3:4],0,255); rgb=np.where(al>1e-3,o[...,:3]/np.maximum(al/255.,1e-3),0)
    return np.concatenate([np.clip(rgb,0,255),al],2).astype(np.uint8)
def run(name):
    im=np.asarray(Image.open(f'keyed/{name}.png').convert('RGBA')).copy(); R=REF['head' if name in HEADS else 'body']
    blur=1.5 if name in ('eyebrow','eyelash','nose','mouth','mouth_open','iris','eye_white') else 2.5
    parts=[im] if name not in PAIRS else list(split(im))
    outs=[]; info=[]
    for p in parts:
        W,cc,mode=fit(p,R,blur); outs.append(warp(p,W)); info.append((round(float(cc),3),mode,np.round(W,3).tolist()))
    res=outs[0] if len(outs)==1 else np.where(outs[0][...,3:4]>=outs[1][...,3:4],outs[0],outs[1])
    if len(outs)==2:
        res=outs[0].copy(); m=outs[1][...,3]>outs[0][...,3]; res[m]=outs[1][m]
    Image.fromarray(res,'RGBA').save(f'aligned/{name}.png')
    for k,o in enumerate(outs) if len(outs)==2 else []: Image.fromarray(o,'RGBA').save(f'aligned/{name}_{"LR"[k]}.png')
    return name,info
if __name__=='__main__':
    names=sys.argv[1:] or sorted(f[:-4] for f in os.listdir('keyed'))
    allinfo={}
    for n in names:
        nm,info=run(n); allinfo[nm]=info; print(nm,[(i[0],i[1],i[2][0][2],i[2][1][2]) for i in info],flush=True)
    json.dump(allinfo,open(f'aligned/info_{"_".join(names[:1])}.json','w'))
