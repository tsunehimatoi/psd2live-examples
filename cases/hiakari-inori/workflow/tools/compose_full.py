import json, sys, numpy as np, cv2
from PIL import Image
sys.path.insert(0,'/workspace/tools')
S=2; W,H=1024*S,1536*S
bf=json.load(open('bodyfit_e.json')); hf=json.load(open('headfit.json'))
M=np.array([[2.86731095e-01,1.51645388e-02,3.42230424e+02],[-1.51645388e-02,2.86731095e-01,8.83722172e+00],[0,0,1]])
def h3(F): return np.vstack([np.array(F,float),[0,0,1]])
def warp(im,A,size,ds=None):
    a=im[...,3:4]/255.; pm=np.concatenate([im[...,:3]*a,im[...,3:4]],2).astype(np.float32)
    sc=np.sqrt(abs(np.linalg.det(A[:2,:2])))
    out=cv2.warpAffine(pm,A[:2],size,flags=cv2.INTER_AREA if sc<1 else cv2.INTER_CUBIC)
    al=out[...,3:4]; rgb=np.where(al>1e-3,out[...,:3]/np.maximum(al/255.,1e-3),0)
    return np.concatenate([np.clip(rgb,0,255),np.clip(al,0,255)],2).astype(np.uint8)
def load(p): return np.asarray(Image.open(p).convert('RGBA')).copy()
def body(k,S=S):
    f=bf[k]; im=load(f"keyed_body/{f['layer']}.png"); im=colortx.get(k,lambda x:x)(im)
    return warp(im,h3(np.diag([S,S,1.]))@h3(f['F']),(1024*S,1536*S))
def head(k):
    f=hf[k]; im=load(f"keyed_head/{f['layer']}.png")
    x0,x1,y0,y1=f['box']; msk=np.zeros(im.shape[:2],bool); msk[y0:y1,x0:x1]=True; im[~msk]=0
    return warp(im,np.diag([S,S,1.])@M@h3(f['F']),(W,H))
def nose():
    im=load('keyed_head/nose.png'); im[...,3]=(im[...,3]*0.4).astype('uint8'); return warp(im,np.diag([S,S,1.])@M@h3(hf.get('nose',{}).get('F',[[1,0,0],[0,1,0]])),(W,H))
colortx={}
if __name__=='__main__':
    import os
    tag=sys.argv[1]
    cfg=json.load(open('colortx.json')) if os.path.exists('colortx.json') else {}
    for k,(mu_s,sd_s,mu_t,sd_t) in cfg.items():
        mu_s,sd_s,mu_t,sd_t=[np.array(x) for x in (mu_s,sd_s,mu_t,sd_t)]
        def mk(mu_s=mu_s,sd_s=sd_s,mu_t=mu_t,sd_t=sd_t):
            def f(im):
                im=im.copy(); rgb=im[...,:3].astype(np.float32); g=np.clip(sd_t/np.maximum(sd_s,1),.7,1.4)
                rgb=(rgb-mu_s)*g+mu_t; im[...,:3]=np.clip(rgb,0,255).astype(np.uint8); return im
            return f
        colortx[k]=mk()
    L={}
    for k in ['legs','socks','shoes','skirt','topwear','arm_right','arm_left','collar_front','bow']: L[k]=body(k)
    for k in ['back_hair','neck','face_base','eye_white_L','eye_white_R','iris_L','iris_R','eyelash_L','eyelash_R','eyebrow_L','eyebrow_R','mouth','mouth_open','front_hair']: L[k]=head(k)
    L['nose']=nose()
    np.savez_compressed(f'full_layers_{tag}.npz',**L)
    order=['back_hair','legs','socks','shoes','skirt','topwear','arm_right','arm_left','neck','collar_front','bow','face_base','nose','eye_white_L','eye_white_R','iris_L','iris_R','eyelash_L','eyelash_R','eyebrow_L','eyebrow_R','mouth','front_hair']
    c=Image.new('RGBA',(W,H),(255,255,255,255))
    for k in order: c.alpha_composite(Image.fromarray(L[k],'RGBA'))
    c.save(f'full_comp_{tag}.png')
    m=Image.open('master_full_1.png').convert('RGB').resize((W,H),Image.LANCZOS)
    for nm,box in [('head',(500,0,1500,900)),('all',(0,0,W,H))]:
        a=m.crop(box); b=c.convert('RGB').crop(box); B=Image.new('RGB',(a.width*2,a.height)); B.paste(a,(0,0)); B.paste(b,(a.width,0))
        B.thumbnail((1400,1400)); B.save(f'fullcmp_{nm}_{tag}.png')
