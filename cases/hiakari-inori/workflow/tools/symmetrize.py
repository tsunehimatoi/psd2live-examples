import sys, numpy as np, cv2
src,dst=sys.argv[1],sys.argv[2]; AX=float(sys.argv[3]) if len(sys.argv)>3 else 1026.5
L=dict(np.load(src)); H,W=L['face_base'].shape[:2]
MF=np.float32([[-1,0,2*AX],[0,1,0]])
def flip(im):
    a=im[...,3:4]/255.; pm=np.concatenate([im[...,:3]*a,im[...,3:4]],2).astype(np.float32)
    out=cv2.warpAffine(pm,MF,(W,H),flags=cv2.INTER_CUBIC)
    al=np.clip(out[...,3:4],0,255); rgb=np.where(al>1e-3,out[...,:3]/np.maximum(al/255.,1e-3),0)
    return np.concatenate([np.clip(rgb,0,255),al],2).astype(np.uint8)
# eyes: viewer-right (R) is the reference, rebuild viewer-left (L) by mirroring
for k in ['eye_white','eyelash','eyebrow']:
    L[k+'_L']=flip(L[k+'_R'])
# iris: keep original L iris but move its centre to the mirrored position of R iris centre
def cen(im):
    ys,xs=np.where(im[...,3]>128); return xs.mean(),ys.mean()
cr=cen(L['iris_R']); cl=cen(L['iris_L']); tx,ty=2*AX-cr[0]-cl[0],cr[1]-cl[1]
M=np.float32([[1,0,tx],[0,1,ty]])
im=L['iris_L']; a=im[...,3:4]/255.; pm=np.concatenate([im[...,:3]*a,im[...,3:4]],2).astype(np.float32)
out=cv2.warpAffine(pm,M,(W,H),flags=cv2.INTER_CUBIC); al=np.clip(out[...,3:4],0,255); rgb=np.where(al>1e-3,out[...,:3]/np.maximum(al/255.,1e-3),0)
L['iris_L']=np.concatenate([np.clip(rgb,0,255),al],2).astype(np.uint8)
# face base: mirror viewer-right half onto the left half
fb=L['face_base']; fl=flip(fb); x=int(round(AX)); out=fb.copy(); out[:,:x]=fl[:,:x]; L['face_base']=out
np.savez_compressed(dst,**L)
