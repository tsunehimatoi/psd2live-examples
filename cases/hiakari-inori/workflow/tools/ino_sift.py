import numpy as np, cv2, sys, os
from PIL import Image
D='/workspace/art/inori'; os.chdir(D)
HEADS='back_hair ear_L ear_R face_base neck eye_white iris eyelash eyebrow nose mouth mouth_open front_hair ahoge mask ribbon choker'.split()
PAIRS='eye_white iris eyelash eyebrow legwear boots'.split()
REFC={'head':cv2.imread('head_1.png'),'body':cv2.imread('master_1.png')}
sift=cv2.SIFT_create(nfeatures=6000,contrastThreshold=0.01)
def split(im):
    a=(im[...,3]>20).sum(0).astype(float); xs=np.where(a>0)[0]; x0,x1=xs.min(),xs.max()
    lo,hi=int(x0+.3*(x1-x0)),int(x0+.7*(x1-x0)); cut=lo+int(np.argmin(a[lo:hi]))
    l=im.copy(); l[:,cut:,3]=0; r=im.copy(); r[:,:cut,3]=0; return l,r
def fit(im,R):
    a=(im[...,3]>200).astype(np.uint8)
    if a.sum()<200: return None
    a=cv2.erode(a,np.ones((5,5),np.uint8))
    g=cv2.cvtColor(cv2.cvtColor(im[...,:3],cv2.COLOR_RGB2BGR),cv2.COLOR_BGR2GRAY); Rg=cv2.cvtColor(R,cv2.COLOR_BGR2GRAY)
    kp1,d1=sift.detectAndCompute(g,a*255); kp2,d2=sift.detectAndCompute(Rg,None)
    if d1 is None or len(kp1)<8: return None
    mt=cv2.BFMatcher().knnMatch(d1,d2,k=2); good=[m for m,n in (x for x in mt if len(x)==2) if m.distance<0.8*n.distance]
    if len(good)<6: return None
    p1=np.float32([kp1[m.queryIdx].pt for m in good]); p2=np.float32([kp2[m.trainIdx].pt for m in good])
    M,inl=cv2.estimateAffinePartial2D(p1,p2,method=cv2.RANSAC,ransacReprojThreshold=4,maxIters=5000,confidence=0.999)
    if M is None: return None
    return M,int(inl.sum()),len(good)
if __name__=='__main__':
    for n in sys.argv[1:] or sorted(f[:-4] for f in os.listdir('keyed')):
        im=np.asarray(Image.open(f'keyed/{n}.png').convert('RGBA')); R=REFC['head' if n in HEADS else 'body']
        parts=[im] if n not in PAIRS else list(split(im))
        for p in parts:
            r=fit(p,R)
            if r is None: print(n,'none'); continue
            M,ni,ng=r; print(n,'inl',ni,'/',ng,'scale',round(float(np.hypot(M[0,0],M[1,0])),3),'rot',round(float(np.degrees(np.arctan2(M[1,0],M[0,0]))),2),'t',np.round(M[:,2],1).tolist())
