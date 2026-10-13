import numpy as np,os,sys
from PIL import Image
os.chdir('/workspace/art/inori')
from psd_tools import PSDImage
H,W=3072,2048
def over(c,a):
    a=a.astype(np.float32)/255; al=a[...,3:4]; return c*(1-al)+a[...,:3]*255*al
P=lambda n:np.asarray(Image.open(f'v4/legs/layers/{n}.png'))
legs=['shin_L','thigh_L','shin_R','thigh_R','boot_L','boot_R','shorts','garter_L','garter_R']
c=np.full((H,W,3),255.)
for n in legs: c=over(c,P(n))
sk=np.asarray(Image.open('legs/layers3/skirt_nogarter.png'))
c2=over(c.copy(),sk)
for n in ['obi','sleeve_L','sleeve_R']: c2=over(c2,np.asarray(Image.open(f'final/{n}.png')))
M=np.asarray(Image.open('v4/legs/master_hr.png').convert('RGB')).astype(float)
o=np.concatenate([c[1100:3072,650:1400],c2[1100:3072,650:1400],M[1100:3072,650:1400]],1)
Image.fromarray(o.astype(np.uint8)).resize((1125,986)).save(sys.argv[1])
np.save('/tmp/v4_legcomp.npy',c.astype(np.uint8))
