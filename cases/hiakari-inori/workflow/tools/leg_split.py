import numpy as np,cv2,json
from PIL import Image
from scipy import ndimage as ndi
A=lambda n:np.asarray(Image.open(f'final/{n}.png').convert('RGBA'))
M=np.asarray(Image.open('legs/master_hr.png')).astype(int)
H,W=3072,2048
sk=A('skirt'); occ=np.load('legs/occ.npy')
leg=np.load('legs/vis_leg.npy'); boot=np.load('legs/vis_boot.npy')
yy,xx=np.mgrid[:H,:W]
# garters
win=(xx>=760)&(xx<1245)&(yy>=1494)&(yy<1900)
gar=(sk[...,3]>40)&win
garR=gar&(xx<1020); garL=gar&(xx>=1020)
# leg visible: remove whitish bg in leg zone
whiteish=(M.min(2)>200)&((M.max(2)-M.min(2))<22)
red=(M[...,0]>120)&(M[...,1]<100)&(M[...,0]-M[...,2]>50)&(yy<1950)&(yy>1450)
gold=(M[...,0]>150)&(M[...,1]>110)&(M[...,2]<110)&(M[...,0]-M[...,2]>70)&(yy<1950)&(yy>1450)&win
gauze=(M.min(2)>140)&((M.max(2)-M.min(2))<30)&(yy<2000)
redg=ndi.binary_dilation(red|gold,iterations=2)&leg
gar=gar|(redg&win); garR=gar&(xx<1020); garL=gar&(xx>=1020)
leg=leg&~whiteish&~gar&~gauze&~redg; leg=ndi.binary_opening(leg,iterations=2)
# keep big comps
lab,n=ndi.label(leg); sz=ndi.sum(leg,lab,range(1,n+1)); leg=np.isin(lab,1+np.where(sz>2000)[0])
# cut line per row
def cutline(mask,y0,y1,xa=950,xb=1090):
    cut=np.full(H,-1.0)
    for y in range(y0,y1):
        r=mask[y,xa:xb]
        if r.any() and (~r).any():
            g=np.where(~r)[0]
            # largest gap run between filled
            runs=np.split(g,np.where(np.diff(g)>1)[0]+1)
            runs=[q for q in runs if q[0]>0 and q[-1]<len(r)-1]
            if runs: q=max(runs,key=len); cut[y]=xa+(q[0]+q[-1])/2
    ok=cut>=0; ys=np.arange(H)
    idx=ys[(ys>=y0)&(ys<y1)]
    c=np.interp(idx,ys[ok],cut[ok]); c=ndi.uniform_filter1d(c,31)
    out=np.full(H,np.nan); out[idx]=c; return out
cl=cutline(leg,1380,3072); cb=cutline(boot,2440,3072)
gap_rows_leg=int(((~np.isnan(cl)))[1380:2600].sum())
np.save('legs/cut_leg.npy',cl); np.save('legs/cut_boot.npy',cb)
def side(mask,c,left):
    cc=np.where(np.isnan(c),1020,c)[:,None]
    return mask&((xx<cc) if left else (xx>=cc))
OL=A('legwear').astype(int)
oldred=((OL[...,0]>110)&(OL[...,1]<100)&(OL[...,0]-OL[...,2]>50))|((OL[...,0]>140)&(OL[...,1]>100)&(OL[...,2]<110)&(OL[...,0]-OL[...,2]>60))
old=(OL[...,3]>128)&~ndi.binary_dilation(oldred,iterations=3)
oldb=A('boots')[...,3]>128
BAND=16
res={}
for nm,vis,oldm,c in [('leg',leg,old,cl),('boot',boot,oldb,cb)]:
    cc=np.where(np.isnan(c),1020,c)[:,None]
    for s,left in [('R',True),('L',False)]:
        v=side(vis,c,left)
        sil=side(oldm|vis,c,left)
        if s=='L':  # lower layer: extend band under R
            band=(xx>=cc-BAND)&(xx<cc)&(ndi.binary_dilation(oldm|vis,iterations=3))
            sil=sil|band
        sil=ndi.binary_closing(sil,iterations=3)
        if nm=='leg':
            sil=ndi.binary_opening(sil,iterations=4); lb,_=ndi.label(sil); bc=np.bincount(lb.ravel()); bc[0]=0; sil=np.isin(lb,np.where(bc>5000)[0])
            for y in range(1380,2450):
                pass
            sil=ndi.binary_closing(sil,iterations=12)
            for y in range(1380,2450):
                q=np.where(sil[y])[0]
                if len(q): sil[y,q.min():q.max()+1]=True
        v=v&sil if nm=='leg' else v
        hid=sil&~v
        if nm=='leg': hid&=~(ndi.binary_dilation(boot,iterations=0)&False)  # keep foot under boot
        np.save(f'legs/vis_{nm}_{s}.npy',v); np.save(f'legs/hid_{nm}_{s}.npy',hid)
        res[f'{nm}_{s}']=dict(vis=int(v.sum()),hid=int(hid.sum()))
np.save('legs/gar_R.npy',garR); np.save('legs/gar_L.npy',garL)
print(res, 'gar',garR.sum(),garL.sum())
v=np.zeros((H,W,3),np.uint8)
for s,col in [('R',0),('L',2)]:
    v[np.load(f'legs/vis_leg_{s}.npy'),col]=255; v[np.load(f'legs/hid_leg_{s}.npy'),col]=110
    v[np.load(f'legs/vis_boot_{s}.npy'),1]=255; v[np.load(f'legs/hid_boot_{s}.npy'),1]=110
v[gar]=(255,255,0)
Image.fromarray(v[1300:3072,700:1350]).resize((325,886)).save('/tmp/m3.png')
