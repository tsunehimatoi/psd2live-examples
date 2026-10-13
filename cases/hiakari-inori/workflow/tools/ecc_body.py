import numpy as np, cv2, sys, json
from PIL import Image
M=cv2.imread('master_full_1.png',0).astype(np.float32)
def layer_gray(name, box):
    im=np.asarray(Image.open(f'keyed_body/{name}.png').convert('RGBA')).astype(np.float32)
    x0,x1,y0,y1=box
    c=im[y0:y1,x0:x1]; a=c[...,3:4]/255.
    rgb=c[...,:3]*a+255*(1-a)
    return cv2.cvtColor(rgb.astype(np.uint8),cv2.COLOR_RGB2GRAY).astype(np.float32), (c[...,3]>128).astype(np.uint8)
def refine(name, box, s0, tx0, ty0, region, iters=200, mode=cv2.MOTION_AFFINE):
    """layer crop (box) -> master. init: master = s0*(p) + t, where p are layer full-canvas coords (so crop offset added)."""
    x0,x1,y0,y1=box
    g,a=layer_gray(name,box)
    # ECC finds warp W mapping template(master region) coords -> input(layer crop) coords.
    rx0,rx1,ry0,ry1=region
    T=M[ry0:ry1,rx0:rx1]
    # init: layer crop coord u = (master_x - tx - s0*x0 ... ) / s0
    # master (X,Y) = s0*(u+x0)+tx => u=(X-tx)/s0 - x0 ; with X=rx0+xt
    W=np.array([[1/s0,0,(rx0-tx0)/s0-x0],[0,1/s0,(ry0-ty0)/s0-y0]],np.float32)
    # gaussian blur for robustness
    Tb=cv2.GaussianBlur(T,(0,0),1.2); Ib=cv2.GaussianBlur(g,(0,0),1.2/ s0)
    crit=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,iters,1e-5)
    try:
        cc,W=cv2.findTransformECC(Tb,Ib,W,mode,crit,None,5)
    except cv2.error as e:
        return None,str(e)
    # invert: layer u = W*[xt,yt,1], xt=X-rx0 -> X = ... compute affine master = A*(layer full coords)+b
    A=np.vstack([W,[0,0,1]]); Ai=np.linalg.inv(A)  # maps (u) -> (xt,yt)
    # layer full p = u + (x0,y0); master X = xt + rx0
    P=np.array([[1,0,x0],[0,1,y0],[0,0,1]]); R=np.array([[1,0,rx0],[0,1,ry0],[0,0,1]])
    # master = R * Ai * P^-1 * p
    F=R@Ai@np.linalg.inv(P)
    return cc,F[:2]
