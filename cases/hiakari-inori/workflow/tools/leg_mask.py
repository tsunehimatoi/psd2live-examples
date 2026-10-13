import numpy as np,cv2
from PIL import Image
from scipy import ndimage as ndi
A=lambda n:np.asarray(Image.open(f'final/{n}.png').convert('RGBA'))
M=np.asarray(Image.open('legs/master_hr.png')).astype(int)
occ=np.zeros((3072,2048),bool)
for n in ['skirt','obi','sleeve_L','sleeve_R']: occ|=A(n)[...,3]>(8 if n=='skirt' else 40)
near=(M.min(2)>240)&((M.max(2)-M.min(2))<10)
lab,_=ndi.label(near); 
cand=(A('legwear')[...,3]>0)|(A('boots')[...,3]>0); cand=ndi.binary_dilation(cand,iterations=25)
bgl=set(np.unique(lab[~cand]))-{0}
bg=np.isin(lab,list(bgl))
S=~bg&~occ&cand; S[:1380]=False
S=ndi.binary_opening(S,iterations=1)
bt=ndi.binary_dilation(A('boots')[...,3]>100,iterations=4)
boot=S&bt; leg=S&~boot
np.save('legs/occ.npy',occ); np.save('legs/vis_leg.npy',leg); np.save('legs/vis_boot.npy',boot)
print(leg.sum(),boot.sum())
v=np.zeros((3072,2048,3),np.uint8); v[...,0]=occ*255; v[...,1]=leg*255; v[...,2]=boot*255
Image.fromarray(v[1300:3072,700:1350]).resize((325,886)).save('/tmp/m2.png')
