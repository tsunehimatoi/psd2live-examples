import numpy as np, cv2, json, sys
from PIL import Image
M=cv2.imread('head_closeup_3b.png',0).astype(np.float32)
W,H=1086,1448
MID=545
# split pair layers into screen-left (L) / screen-right (R)
for k in ['eye_white','iris','eyelash','eyebrow']:
    im=np.asarray(Image.open(f'keyed_head3/{k}.png').convert('RGBA')).copy()
    for s,sl in (('L',slice(0,MID)),('R',slice(MID,W))):
        o=im.copy(); msk=np.zeros(im.shape[:2],bool); msk[:,sl]=True; o[~msk]=0
        Image.fromarray(o,'RGBA').save(f'keyed_head3/{k}_{s}.png')
def gray(name,box):
    im=np.asarray(Image.open(f'keyed_head3/{name}.png').convert('RGBA')).astype(np.float32)
    x0,x1,y0,y1=box; c=im[y0:y1,x0:x1]; a=c[...,3:4]/255.
    return cv2.cvtColor((c[...,:3]*a+255*(1-a)).astype(np.uint8),cv2.COLOR_RGB2GRAY).astype(np.float32)
def refine(name,mode,pad=30,iters=400,blur=1.2):
    im=np.asarray(Image.open(f'keyed_head3/{name}.png'))[...,3]; ys,xs=np.where(im>40)
    x0,x1,y0,y1=max(0,xs.min()-pad),min(W,xs.max()+pad),max(0,ys.min()-pad),min(H,ys.max()+pad)
    T=cv2.GaussianBlur(M[y0:y1,x0:x1],(0,0),blur); I=cv2.GaussianBlur(gray(name,(x0,x1,y0,y1)),(0,0),blur)
    Wm=np.eye(2,3,dtype=np.float32)
    try: cc,Wm=cv2.findTransformECC(T,I,Wm,mode,(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,iters,1e-6),None,5)
    except cv2.error as e: return None,None
    # Wm maps template(master crop) coords -> layer crop coords (same offset) => layer->master = inverse; same crop origin so offset cancels
    A=np.vstack([Wm,[0,0,1]]); Ai=np.linalg.inv(A)
    # master crop coords xt=X-x0; layer crop coords u=x-x0 ; (u)=A*(xt) => X-x0 = Ai*(x-x0)
    P=np.array([[1,0,-x0],[0,1,-y0],[0,0,1]]); R=np.array([[1,0,x0],[0,1,y0],[0,0,1]])
    F=R@Ai@P
    return cc,F[:2]

def refine_s(name,pad=30,blur=1.2,scales=np.arange(0.84,1.17,0.02)):
    im=np.asarray(Image.open(f'keyed_head3/{name}.png').convert('RGBA')).astype(np.float32); ys,xs=np.where(im[...,3]>40)
    cx,cy=(xs.min()+xs.max())/2,(ys.min()+ys.max())/2
    best=(-2,None)
    for sc in scales:
        S=np.array([[sc,0,cx-sc*cx],[0,sc,cy-sc*cy]],np.float32)
        a=im[...,3:4]/255.; pm=np.concatenate([im[...,:3]*a,im[...,3:4]],2)
        o=cv2.warpAffine(pm,S,(W,H),flags=cv2.INTER_CUBIC); al=np.clip(o[...,3:4],0,255)
        x0,x1,y0,y1=max(0,int(cx-(cx-xs.min())*sc-pad)),min(W,int(cx+(xs.max()-cx)*sc+pad)),max(0,int(cy-(cy-ys.min())*sc-pad)),min(H,int(cy+(ys.max()-cy)*sc+pad))
        a2=al/255.; rgb=np.where(al>1e-3,o[...,:3]/np.maximum(a2,1e-3),0)
        g=cv2.cvtColor((rgb*a2+255*(1-a2))[y0:y1,x0:x1].astype(np.uint8),cv2.COLOR_RGB2GRAY).astype(np.float32)
        T=cv2.GaussianBlur(M[y0:y1,x0:x1],(0,0),blur); I=cv2.GaussianBlur(g,(0,0),blur)
        Wm=np.eye(2,3,dtype=np.float32)
        try: cc,Wm=cv2.findTransformECC(T,I,Wm,cv2.MOTION_TRANSLATION,(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,300,1e-6),None,5)
        except cv2.error: continue
        if cc>best[0]:
            # layer->master: first S then translate by -Wm t (I(x+t)=T(x) => master X = layer x - t)
            F=np.array([[sc,0,cx-sc*cx-Wm[0,2]],[0,sc,cy-sc*cy-Wm[1,2]]])
            best=(cc,F,sc)
    return best
fits={}
for k in ['eye_white_L','eye_white_R','iris_L','iris_R','eyelash_L','eyelash_R','eyebrow_L','eyebrow_R','mouth','face_base','neck']:
    b=refine_s(k)
    print(k,round(b[0],3),'scale',round(b[2],2),np.round(b[1],2).tolist()); fits[k]=b[1].tolist()
json.dump(fits,open('headfit3.json','w'),indent=1)
