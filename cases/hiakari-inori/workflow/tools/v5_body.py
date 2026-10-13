import numpy as np,os,cv2
from PIL import Image
from scipy import ndimage as ndi
os.chdir('/workspace/art/inori')
H,W=3072,2048; yy,xx=np.mgrid[:H,:W]
B=np.asarray(Image.open('v5/base_hr.png').convert('RGB')).astype(int)
A=lambda p:np.asarray(Image.open(p).convert('RGBA'))[...,3]
white=(B.min(2)>236)&((B.max(2)-B.min(2))<12)
lab,_=ndi.label(white); bg=np.isin(lab,list(set(np.unique(lab[:5]))|set(np.unique(lab[-5:]))|set(np.unique(lab[:,:5]))|set(np.unique(lab[:,-5:]))-{0}))
fg=~bg
excl=np.zeros((H,W),bool)
for n in ['tail_L','tail_R','tail_C','back_hair','braid','twintail','front_hair']: excl|=A(f'final/{n}.png')>60
armR=A('final/arm_L.png')>0; armL=A('final/arm_R.png')>0   # names as in psd: handwear 1-r=arm_L
arms=ndi.binary_dilation(armR|armL,iterations=3)
# hair/tail pixel colours in base: white fur/hair & red tips – remove from torso by colour too where outside clothes area
neckY=520   # below chin approx (2x)
hipY=1500
torso=fg&~excl&~arms&(yy>=neckY)&(yy<1560)&(xx>760)&(xx<1290)
legs=fg&(yy>=1380)&(xx>700)&(xx<1350)&~excl
cut=np.load('v4/legs/masks.npz')['cut']
np.savez_compressed('v5/body_masks.npz',fg=fg,torso=torso,legs=legs,excl=excl)
v=B.copy().astype(np.uint8); v[torso]=(v[torso]*.5+np.array([255,0,0])*.5).astype(np.uint8); v[legs]=(v[legs]*.5+np.array([0,0,255])*.5).astype(np.uint8); v[excl&fg]=(v[excl&fg]*.5+np.array([0,255,0])*.5).astype(np.uint8)
for y in range(0,H,100): v[y,:]=(0,0,0)
Image.fromarray(v[300:3072,500:1550]).resize((525,1386)).save('/tmp/v5seg_a.png')
