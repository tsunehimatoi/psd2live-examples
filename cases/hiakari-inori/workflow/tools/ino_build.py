import sys, os, numpy as np, cv2, json
sys.path.insert(0,'/workspace/tools')
os.chdir('/workspace/art/inori')
from PIL import Image
import sr as SR, ino_sift as S
os.makedirs('hr',exist_ok=True); os.makedirs('final',exist_ok=True)
Wc,Hc=2048,3072
def L1(n): return np.asarray(Image.open(f'keyed/{n}.png').convert('RGBA')).copy()
def sc2(M): M=np.vstack([np.float32(M),[0,0,1]]); S2=np.diag([2,2,1]).astype(np.float32); return (S2@M@np.linalg.inv(S2))[:2]
def warp2(im,M2,size=(Wc,Hc)):
    a=im[...,3:4]/255.; pm=np.concatenate([im[...,:3]*a,im[...,3:4]],2).astype(np.float32)
    o=cv2.warpAffine(pm,np.float32(M2),size,flags=cv2.INTER_AREA if abs(M2[0,0])<1 else cv2.INTER_LANCZOS4)
    al=np.clip(o[...,3:4],0,255); rgb=np.where(al>1e-3,o[...,:3]/np.maximum(al/255.,1e-3),0)
    return np.concatenate([np.clip(rgb,0,255),al],2).astype(np.uint8)
def merge(outs):
    r=outs[0].copy()
    for o in outs[1:]: m=o[...,3]>r[...,3]; r[m]=o[m]
    return r
def hr(name,arr):
    p=f'hr/{name}.png'
    if os.path.exists(p): return np.asarray(Image.open(p))
    Image.fromarray(arr,'RGBA').save(f'hr/{name}_in.png'); o=SR.process(f'hr/{name}_in.png'); Image.fromarray(o,'RGBA').save(p); return o
IDENT=np.float32([[1,0,0],[0,1,0]])
body={}
# (name, source array provider, list of parts transforms) ; transform None = SIFT per part, array = given
arm=L1('arm_L'); armR=arm[:,::-1].copy()
specs=[('tail_C',None,[np.float32([[.6,0,512-.6*514],[0,.6,640-.6*370]])]),
 ('tail_L',None,['sift']),('tail_R',None,['sift']),
 ('legwear',None,['sift','sift']),('boots',None,['sift','sift']),('skirt',None,['sift']),
 ('arm_L',None,[IDENT]),('arm_R',armR,[IDENT]),
 ('top',None,['sift']),('obi',None,['sift']),('sleeve_L',None,['sift']),('sleeve_R',None,[IDENT]),
 ('braid',None,[IDENT]),('twintail',None,[IDENT])]
R=S.REFC['body']
for name,src,tfs in specs:
    im=L1(name) if src is None else src
    parts=list(S.split(im)) if len(tfs)==2 else [im]
    outs=[]
    for p,t in zip(parts,tfs):
        if isinstance(t,str):
            r=S.fit(p,R); M=r[0]; print(name,'sift inl',r[1]) 
        else: M=t
        h=hr(f'{name}_{len(outs)}',p); outs.append(warp2(h,sc2(M)))
    Image.fromarray(merge(outs),'RGBA').save(f'final/{name}.png'); print(name,'done',flush=True)
# head layers
Mh=np.load('Mhead2body.npy'); Ah=np.float32([[Mh[0,0]*2,0,Mh[0,2]*2],[0,Mh[0,0]*2,Mh[1,2]*2]])
for n in ['back_hair','ear_L','ear_R','face_base','neck','choker','eye_white','iris','eyelash','eyebrow','nose','mouth','mouth_open','front_hair','ahoge','ribbon','mask']:
    im=np.asarray(Image.open(f'headfinal/{n}.png').convert('RGBA')); Image.fromarray(warp2(im,Ah),'RGBA').save(f'final/{n}.png')
print('all done')
