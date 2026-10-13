import json, sys, numpy as np, cv2
from PIL import Image
S=2; W,H=1086*S,1448*S
T=json.load(open('aligned/transforms.json')); META=json.load(open('up4/meta.json'))
def load_up(n): return np.asarray(Image.open(f'up4/{n}_x4.png').convert('RGBA')).astype(np.float32)
def warp(n, s, tx, ty, flip=False, cx=538, shade=None):
    """orig-coord transform p'=s*p+t (1x canvas) -> 2x canvas from x4 upscaled crop."""
    im=load_up(n); m=META[n]; x0,y0=m['x0'],m['y0']
    a=im[...,3:4]/255.; pm=np.concatenate([im[...,:3]*a, im[...,3:4]],axis=2)
    k=s*S/4.0
    M=np.float32([[k,0,S*s*x0+S*tx],[0,k,S*s*y0+S*ty]])
    out=cv2.warpAffine(pm,M,(W,H),flags=cv2.INTER_AREA if k<1 else cv2.INTER_CUBIC,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
    al=out[...,3:4]; rgb=np.where(al>1e-3,out[...,:3]/np.maximum(al/255.,1e-3),0)
    res=np.concatenate([np.clip(rgb,0,255),al],axis=2)
    if flip:
        res=res[:,::-1]; shift=int(round(S*(2*cx-(1086-1))))
        res=np.roll(res,shift,axis=1)
        if shift>0: res[:,:shift]=0
        elif shift<0: res[:,shift:]=0
    return res.astype(np.uint8)
def M_to_st(M):  # place() returns M = [[s,0,tx],[0,s,ty]]
    return M[0][0],M[0][2],M[1][2]
