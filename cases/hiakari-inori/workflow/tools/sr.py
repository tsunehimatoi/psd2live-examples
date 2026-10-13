import sys, time, json, numpy as np, torch, cv2
from scipy import ndimage as ndi
from PIL import Image
from spandrel import ModelLoader
torch.set_num_threads(8)
W='/workspace/tools/weights/'
_models={}
def model(name):
    if name not in _models:
        m=ModelLoader().load_from_file(W+name+'.pth'); m.eval(); _models[name]=m
    return _models[name]
def sr4(rgb, name='RealESRGAN_x4plus_anime_6B', tile=128, pad=12):
    """rgb float32 HxWx3 0..1 -> 4x output float32, tiled with overlap"""
    m=model(name); H,Wd,_=rgb.shape; s=m.scale
    out=np.zeros((H*s,Wd*s,3),np.float32); wsum=np.zeros((H*s,Wd*s,1),np.float32)
    x=torch.from_numpy(rgb.transpose(2,0,1))[None]
    ys=list(range(0,H,tile)); xs=list(range(0,Wd,tile))
    for y0 in ys:
        for x0 in xs:
            y1,x1=min(y0+tile,H),min(x0+tile,Wd)
            a,b,c,d=max(y0-pad,0),max(x0-pad,0),min(y1+pad,H),min(x1+pad,Wd)
            with torch.no_grad(): o=m(x[:,:,a:c,b:d])[0].numpy().transpose(1,2,0)
            oy,ox=(y0-a)*s,(x0-b)*s
            out[y0*s:y1*s,x0*s:x1*s]=o[oy:oy+(y1-y0)*s, ox:ox+(x1-x0)*s]
    return np.clip(out,0,1)
def down2(img4):  # 4x -> 2x lanczos (area-ish)
    h,w=img4.shape[:2]
    return cv2.resize(img4,(w//2,h//2),interpolation=cv2.INTER_AREA if False else cv2.INTER_LANCZOS4)
def extend_color(rgb,a,thr=0.5):
    """fill pixels with alpha<thr by nearest opaque pixel color (edge extension), then slight blur only in filled area"""
    solid=a>=thr
    if solid.sum()==0: solid=a>0
    if solid.sum()==0: return rgb.copy()
    idx=ndi.distance_transform_edt(~solid,return_distances=False,return_indices=True)
    ext=rgb[idx[0],idx[1]]
    return ext
def process(path, name='RealESRGAN_x4plus_anime_6B', pad=16, alpha_mode='sr'):
    im=np.array(Image.open(path).convert('RGBA')); H,Wd=im.shape[:2]
    ys,xs=np.nonzero(im[...,3]>0)
    out=np.zeros((H*2,Wd*2,4),np.uint8)
    if len(ys)==0: return out
    y0,y1,x0,x1=max(ys.min()-pad,0),min(ys.max()+1+pad,H),max(xs.min()-pad,0),min(xs.max()+1+pad,Wd)
    c=im[y0:y1,x0:x1].astype(np.float32)/255; rgb,a=c[...,:3],c[...,3]
    # reflect-pad crop so model has context at crop edges
    ext=extend_color(rgb,a)
    # color: opaque pixels keep own color; semi-transparent: blend toward ext at low alpha to avoid noisy color
    w=np.clip(a*2,0,1)[...,None]
    base=rgb*w+ext*(1-w)
    c4=sr4(base,name)
    col=down2(c4)  # 2x
    h2,w2=col.shape[:2]
    # low-frequency colour correction: make SR colour match original colour (alpha-weighted region + ext)
    d1=cv2.resize(col,(a.shape[1],a.shape[0]),interpolation=cv2.INTER_AREA)
    wt=np.clip(a*2,0,1)
    diff=(base-d1)
    num=cv2.GaussianBlur(diff*wt[...,None],(0,0),2.0); den=cv2.GaussianBlur(wt,(0,0),2.0)[...,None]+1e-4
    corr=num/den
    corr=np.where(den>0.02,corr,0)
    col=col+cv2.resize(corr,(w2,h2),interpolation=cv2.INTER_CUBIC)
    # anti-ringing: clamp to local range of Lanczos upscale of the base colour
    lz=cv2.resize(base,(w2,h2),interpolation=cv2.INTER_LANCZOS4).clip(0,1)
    k=np.ones((5,5),np.uint8)
    lo=cv2.erode(lz,k)-0.02; hi=cv2.dilate(lz,k)+0.02
    col=np.clip(col,lo,hi).clip(0,1)
    # alpha
    if alpha_mode=='sr':
        a3=np.repeat(a[...,None],3,2)
        ao=down2(sr4(a3,name).mean(2)).clip(0,1)
        d1a=cv2.resize(ao,(a.shape[1],a.shape[0]),interpolation=cv2.INTER_AREA)
        ca=cv2.GaussianBlur(a-d1a,(0,0),1.0)
        ao=ao+cv2.resize(ca,(w2,h2),interpolation=cv2.INTER_CUBIC)
        # range clamp against bicubic-ish local range (no halo growth)
        az=cv2.resize(a,(w2,h2),interpolation=cv2.INTER_LINEAR)
        ao=np.clip(ao,cv2.erode(az,k)-0.03,cv2.dilate(az,k)+0.03).clip(0,1)
        ao[(cv2.dilate(az,np.ones((7,7),np.uint8))<=0.002)]=0
    else:
        ao=cv2.resize(a,(w2,h2),interpolation=cv2.INTER_CUBIC)
        bl=cv2.GaussianBlur(ao,(0,0),1.0); ao=np.clip(ao+0.6*(ao-bl),0,1)
        az=cv2.resize(a,(w2,h2),interpolation=cv2.INTER_LINEAR)
        ao[(cv2.dilate(az,np.ones((7,7),np.uint8))<=0.002)]=0
        ao=np.clip(ao*(4*a.sum()/max(ao.sum(),1e-6)),0,1)  # keep alpha mass
    res=np.dstack([np.clip(col,0,1),ao])
    out[y0*2:y1*2,x0*2:x1*2]=np.round(res*255).astype(np.uint8)
    return out
BIC_ALPHA={'eyebrow_l','eyebrow_r','mouth','mouth_open','nose'}
if __name__=='__main__':
    import glob,os
    out='/workspace/p2l-test/art/layers_hr/'; rep={}
    T=time.time()
    for f in sorted(glob.glob('/workspace/p2l-test/art/layers/*.png')):
        n=os.path.basename(f)[:-4]; t=time.time()
        o=process(f,'RealESRGAN_x4plus_anime_6B',alpha_mode='bic' if n in BIC_ALPHA else 'sr')
        Image.fromarray(o).save(out+n+'.png'); rep[n]=time.time()-t; print(n,round(rep[n],2),flush=True)
    print('total',time.time()-T); json.dump(rep,open('timings.json','w'))
