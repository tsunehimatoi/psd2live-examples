import sys, numpy as np, cv2, math
src,dst=sys.argv[1],sys.argv[2]; rot=float(sys.argv[3]); dx=float(sys.argv[4]); rot_b=float(sys.argv[5]); dxb=float(sys.argv[6]) if len(sys.argv)>6 else dx
L=dict(np.load(src))
def tf(im,ang,cx,cy,tx):
    M=cv2.getRotationMatrix2D((cx,cy),-ang,1.0); M[0,2]+=tx   # ang>0 => rotate clockwise on screen (right side goes down)... see note
    a=im[...,3:4]/255.; pm=np.concatenate([im[...,:3]*a,im[...,3:4]],2).astype(np.float32)
    out=cv2.warpAffine(pm,M,(im.shape[1],im.shape[0]),flags=cv2.INTER_CUBIC)
    al=np.clip(out[...,3:4],0,255); rgb=np.where(al>1e-3,out[...,:3]/np.maximum(al/255.,1e-3),0)
    return np.concatenate([np.clip(rgb,0,255),al],2).astype(np.uint8)
cx,cy=1013.5,312.5
for k in ['eye_white_L','eye_white_R','iris_L','iris_R','eyelash_L','eyelash_R']: L[k]=tf(L[k],rot,cx,cy,dx)
for k in ['eyebrow_L','eyebrow_R']: L[k]=tf(L[k],rot_b,cx,260,dxb)
np.savez_compressed(dst,**L)
