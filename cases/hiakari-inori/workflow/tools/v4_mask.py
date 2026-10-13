import numpy as np,os
from PIL import Image
from scipy import ndimage as ndi
os.chdir('/workspace/art/inori')
A=lambda p:np.asarray(Image.open(p).convert('RGBA'))
M=np.asarray(Image.open('v4/legs/master_hr.png').convert('RGB')).astype(int)
H,W=3072,2048; yy,xx=np.mgrid[:H,:W]
occ=A('legs/layers3/skirt_nogarter.png')[...,3]>8
for n in ['obi','sleeve_L','sleeve_R']: occ|=A(f'final/{n}.png')[...,3]>40
bgc=(M.min(2)>232)&((M.max(2)-M.min(2))<14)
lab,_=ndi.label(bgc); bgl=set(np.unique(lab[:, :690]))|set(np.unique(lab[:, 1380:]))|set(np.unique(lab[3060:]))
bg=np.isin(lab,list(bgl-{0}))
zone=(((xx>760)&(xx<1300))|((yy>2380)&(xx>690)&(xx<1370)))&(yy>1250)
fg=zone&~bg; fg=ndi.binary_opening(fg,iterations=1)
lab,n=ndi.label(fg); sz=ndi.sum(fg,lab,range(1,n+1)); fg=np.isin(lab,1+np.where(sz>3000)[0])
# split by gap column per row
cut=np.full(H,np.nan)
for y in range(1250,H):
    r=fg[y,900:1150]; g=np.where(~r)[0]
    if len(g): 
        runs=np.split(g,np.where(np.diff(g)>1)[0]+1); q=max(runs,key=len); cut[y]=900+(q[0]+q[-1])/2
ok=~np.isnan(cut); ys=np.arange(H); cut=np.interp(ys,ys[ok],cut[ok]); cut=ndi.uniform_filter1d(cut,41)
R=fg&(xx<cut[:,None]); L=fg&(xx>=cut[:,None])
red=(M[...,0]>110)&(M[...,0]-M[...,2]>50)&(M[...,0]-M[...,1]>50)
gold=(M[...,0]>140)&(M[...,1]>100)&(M[...,2]<120)&(M[...,0]-M[...,2]>60)
white=(M.min(2)>170)
# boot: below boot top line
bootzone=yy>2380
boot=fg&bootzone&(yy>2440)
boot|=fg&bootzone&ndi.binary_dilation((white|red)&bootzone,iterations=6)
lab,n=ndi.label(boot); sz=ndi.sum(boot,lab,range(1,n+1)); boot=np.isin(lab,1+np.where(sz>5000)[0]); boot=ndi.binary_fill_holes(ndi.binary_closing(boot,iterations=4))
gar=fg&(yy<2000)&~bootzone&ndi.binary_dilation(red|gold,iterations=2)
gar=ndi.binary_closing(gar,iterations=2)&fg
leg=fg&~boot
np.savez_compressed('v4/legs/masks.npz',occ=occ,fg=fg,cut=cut,boot=boot,gar=gar,leg=leg,R=R,L=L)
v=np.zeros((H,W,3),np.uint8); v[occ]=(90,0,0); v[leg&R]=(0,0,255); v[leg&L]=(0,255,255); v[boot]=(0,255,0); v[gar]=(255,255,0)
print({k:int(x.sum()) for k,x in dict(occ=occ,leg=leg,boot=boot,gar=gar).items()}, 'cut@1500',cut[1500],'cut@2200',cut[2200])
Image.fromarray(np.hstack([v[1100:3072,650:1400],M[1100:3072,650:1400].astype(np.uint8)])).resize((750,986)).save('v4/legs/mask_view.png')
