import numpy as np, cv2, json, sys
from PIL import Image
W,H=1086,1448; AX=543.0
def load(k): return np.asarray(Image.open(f'keyed_head3/{k}.png').convert('RGBA')).copy()
def warp(im,F,size=(W,H)):
    a=im[...,3:4]/255.; pm=np.concatenate([im[...,:3]*a,im[...,3:4]],2).astype(np.float32)
    out=cv2.warpAffine(pm,np.float32(F),size,flags=cv2.INTER_CUBIC)
    al=np.clip(out[...,3:4],0,255); rgb=np.where(al>1e-3,out[...,:3]/np.maximum(al/255.,1e-3),0)
    return np.concatenate([np.clip(rgb,0,255),al],2).astype(np.uint8)
def bbox_c(im,th=40,xr=None):
    a=im[...,3]>th
    if xr is not None: m=np.zeros_like(a); m[:,xr[0]:xr[1]]=1; a=a&m
    ys,xs=np.where(a); return (xs.min()+xs.max())/2,(ys.min()+ys.max())/2
def fit(im,s,target,xr=None):
    c=bbox_c(im,xr=xr); return [[s,0,target[0]-s*c[0]],[0,s,target[1]-s*c[1]]]
def mirror(im): return warp(im,[[-1,0,2*AX],[0,1,0]])
def half(im,right=True):
    o=im.copy(); 
    if right: o[:,:int(AX)]=0
    else: o[:,int(AX):]=0
    return o
P=json.load(open('headparams3.json'))
out={}
for k in ['back_hair','front_hair']: out[k]=load(k)
out['neck']=load('neck_v2')
# face base: mirror right half onto left for symmetry
fb=warp(load('face_base_v2'),[[.92,0,543-.92*543],[0,.81,-4]]); fl=mirror(fb); x=int(AX); o=fb.copy(); o[:,:x]=fl[:,:x]; out['face_base']=o
for k,(s,tx,ty) in P.items():
    im=load(k); 
    if k=='iris':
        r=warp(half(im,True),fit(half(im,True),s,(tx,ty),xr=(int(AX),W)))
        l=warp(half(im,False),fit(half(im,False),s,(2*AX-tx,ty),xr=(0,int(AX))))
        out['iris_R']=r; out['iris_L']=l
    elif k in('eye_white','eyelash','eyebrow'):
        r=warp(half(im,True),fit(half(im,True),s,(tx,ty),xr=(int(AX),W))); out[k+'_R']=r; out[k+'_L']=mirror(r)
    else:  # mouth, mouth_open, nose centred on axis
        out[k]=warp(im,fit(im,s,(AX,ty)))
np.savez_compressed('head3_closeup.npz',**out)
order=['back_hair','neck','face_base','eyebrow_L','eyebrow_R','mouth','front_hair','eye_white_L','eye_white_R','iris_L','iris_R','eyelash_L','eyelash_R']
c=Image.new('RGBA',(W,H),(255,255,255,255))
for k in order: c.alpha_composite(Image.fromarray(out[k],'RGBA'))
tag=sys.argv[1]; c.save(f'head3_comp_{tag}.png')
m=Image.open('head_closeup_3b.png').convert('RGB'); box=(150,250,950,850)
B=Image.new('RGB',(1600,600)); B.paste(m.crop(box),(0,0)); B.paste(c.convert('RGB').crop(box),(800,0)); B.save(f'head3_cmp_{tag}.png')
