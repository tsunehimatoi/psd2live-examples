import cv2, numpy as np, sys
from PIL import Image
def load_on_white(p):
    im=Image.open(p).convert('RGBA'); bg=Image.new('RGBA',im.size,(255,255,255,255)); bg.alpha_composite(im)
    return cv2.cvtColor(np.asarray(bg.convert('RGB')),cv2.COLOR_RGB2GRAY)
def reg(layer_path, master_path='gpt/master_gpt.png'):
    L=load_on_white(layer_path); M=cv2.cvtColor(cv2.imread(master_path),cv2.COLOR_BGR2GRAY)
    sift=cv2.SIFT_create(4000)
    k1,d1=sift.detectAndCompute(L,None); k2,d2=sift.detectAndCompute(M,None)
    if d1 is None or d2 is None: return None
    bf=cv2.BFMatcher(); mt=bf.knnMatch(d1,d2,k=2)
    good=[m for m,n in mt if m.distance<0.8*n.distance]
    if len(good)<6: return (None,len(good))
    src=np.float32([k1[m.queryIdx].pt for m in good]); dst=np.float32([k2[m.trainIdx].pt for m in good])
    A,inl=cv2.estimateAffinePartial2D(src,dst,ransacReprojThreshold=4)
    return A,int(inl.sum()) if inl is not None else 0,len(good)
if __name__=='__main__':
    for n in sys.argv[1:]:
        print(n, reg(f'keyed/{n}.png'))
