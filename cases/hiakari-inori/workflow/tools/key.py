import sys, numpy as np
from PIL import Image
def key(inp, out, lo=0.17, hi=0.96):
    im = np.asarray(Image.open(inp).convert('RGB')).astype(np.float32)
    r,g,b = im[...,0],im[...,1],im[...,2]
    # estimate background colour from corners
    c = np.concatenate([im[:8,:8].reshape(-1,3), im[:8,-8:].reshape(-1,3), im[-8:,:8].reshape(-1,3), im[-8:,-8:].reshape(-1,3)]).mean(0)
    G = np.array([0,255,0],np.float32) if c[1]>200 and c[0]<80 and c[2]<80 else c
    d = (g - np.maximum(r,b))
    dbg = G[1]-max(G[0],G[2])
    a = 1 - d/dbg
    a = np.clip((a-lo)/(hi-lo),0,1)
    af = a[...,None]
    fg = (im - (1-af)*G)/np.maximum(af,1e-3)
    fg = np.clip(fg,0,255)
    # despill: limit green to max(r,b) where partially transparent
    spill = np.minimum(fg[...,1], np.maximum(fg[...,0],fg[...,2])+6)
    fg[...,1] = np.where(a<0.999, spill, fg[...,1])
    import cv2
    # remove isolated specks (background noise)
    m=(a>0.02).astype(np.uint8); n,lab,st,_=cv2.connectedComponentsWithStats(m,connectivity=8)
    small=np.zeros(a.shape,bool)
    for i in range(1,n):
        if st[i,4]<40: small|=(lab==i)
    a=np.where(small,0,a)
    fg=np.where((a>0)[...,None],fg,0)
    rgba = np.dstack([fg, a*255]).astype(np.uint8)
    Image.fromarray(rgba,'RGBA').save(out)
if __name__=='__main__':
    key(sys.argv[1], sys.argv[2])
