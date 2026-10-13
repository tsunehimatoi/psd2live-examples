import numpy as np,os
from PIL import Image
from scipy import ndimage as ndi
os.chdir('/workspace/art/inori')
H,W=3072,2048; yy=np.arange(H)[:,None]
P=lambda n:np.asarray(Image.open(f'v4/legs/layers/{n}.png')).copy()
sh=P('shorts').astype(float)
for s in 'RL':
    t=P(f'thigh_{s}'); sock=np.load(f'v4/legs/sock_{s}.npy'); top=int(np.where(sock.any(1))[0].min())
    st=t.copy(); st[:top-4,:,3]=0; Image.fromarray(st).save(f'v5/layers/stock_thigh_{s}.png')
    dark=(t[...,:3].max(2)<95)&(t[...,3]>0)&(yy<1530); dark=ndi.binary_closing(dark,iterations=2)
    lab,n=ndi.label(dark); sz=ndi.sum(dark,lab,range(1,n+1)); dark=np.isin(lab,1+np.where(sz>3000)[0])
    part=t.astype(float); part[~dark,3]=0
    a1=part[...,3:]/255; a0=sh[...,3:]/255; ao=a1+a0*(1-a1)
    sh[...,:3]=np.where(ao>0,(part[...,:3]*a1+sh[...,:3]*a0*(1-a1))/np.maximum(ao,1e-6),0); sh[...,3:]=ao*255
    print(s,'band top',top)
Image.fromarray(sh.astype(np.uint8)).save('v5/layers/shorts_full.png')
