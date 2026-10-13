import numpy as np,json
from PIL import Image
from scipy import ndimage as ndi
H,W=3072,2048
M=np.asarray(Image.open('legs/master_hr.png').convert('RGB')).astype(float)
L=lambda n:np.load(f'legs/{n}.npy')
order=['shin_L','thigh_L','shin_R','thigh_R','boot_L','boot_R','garter_L','garter_R']
c=np.full((H,W,3),255.)
for n in order:
  a=np.asarray(Image.open(f'legs/layers/{n}.png')).astype(float)/255; al=a[...,3:4]; c=c*(1-al)+a[...,:3]*255*al
res={}
for nm,mk in [('sock/leg',L('vis_leg_R')|L('vis_leg_L')),('boots',L('vis_boot_R')|L('vis_boot_L')),('garters',L('gar_R')|L('gar_L'))]:
  inn=ndi.binary_erosion(mk,iterations=2); d=np.abs(c-M)[inn]; e=np.abs(c-M)[mk&~inn]
  res[nm]=dict(px=int(inn.sum()),mean=round(float(d.mean()),4),p99=float(np.percentile(d,99)),max=int(d.max()),exact_frac=round(float((d.max(1)==0).mean()),5),edge2px_mean=round(float(e.mean()),2))
# outside: legs must not paint where master is background
bgm=(M.min(2)>238)&((M.max(2)-M.min(2))<10); occ=L('occ')
res['leak_on_master_bg_px']=int(((np.abs(c-255).max(2)>30)&bgm&~occ)[1380:].sum())
print(json.dumps(res,indent=0)); json.dump(res,open('legs/align_diff.json','w'),indent=1)
sk=np.asarray(Image.open('legs/layers/skirt_nogarter.png')).astype(float)/255; al=sk[...,3:4]; c2=c*(1-al)+sk[...,:3]*255*al
o=np.concatenate([c[1300:3072,700:1350],c2[1300:3072,700:1350],M[1300:3072,700:1350],np.clip(np.abs(c2-M)*4,0,255)[1300:3072,700:1350]],1)
Image.fromarray(o.astype(np.uint8)).resize((1300,886)).save('legs/ov_legs_v2.png')
