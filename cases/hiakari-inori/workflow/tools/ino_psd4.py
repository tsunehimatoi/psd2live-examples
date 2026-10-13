import sys, os, numpy as np
sys.path.insert(0,'/workspace/tools'); os.chdir('/workspace/art/inori')
from PIL import Image
from mkpsd import write
def L(n): return np.asarray(Image.open(f'final/{n}.png').convert('RGBA')).copy()
def split(rgba):
    a=(rgba[...,3]>20).sum(0).astype(float); xs=np.where(a>0)[0]; x0,x1=xs.min(),xs.max()
    lo,hi=int(x0+.3*(x1-x0)),int(x0+.7*(x1-x0)); cut=lo+int(np.argmin(a[lo:hi]))
    l=rgba.copy(); l[:,cut:,3]=0; r=rgba.copy(); r[:,:cut,3]=0; return [l,r]   # [screen-left (char R) ,screen-right (char L)]
lay=[]
lay+=[('tail 3',L('tail_C_v4')),('tail 1',L('tail_L')),('tail 2',L('tail_R')),('back hair',L('back_hair')),('ears-r',L('ear_L')),('ears-l',L('ear_R'))]
G=lambda n:np.asarray(Image.open(f'v4/legs/layers/{n}.png').convert('RGBA')).copy()
lay+=[('legwear 1-l',G('shin_L')),('legwear 2-l',G('thigh_L')),('legwear 1-r',G('shin_R')),('legwear 2-r',G('thigh_R')),
      ('footwear-l',G('boot_L')),('footwear-r',G('boot_R')),('bottomwear 3',G('shorts')),('legwear 3-l',G('garter_L')),('legwear 3-r',G('garter_R'))]
lay+=[('bottomwear',np.asarray(Image.open('legs/layers3/skirt_nogarter.png').convert('RGBA')).copy()),('neck',L('neck')),('handwear 1-r',L('arm_L')),('handwear 1-l',L('arm_R')),('topwear',L('top')),('bottomwear 2',L('obi')),
      ('handwear 2-r',L('sleeve_L')),('handwear 2-l',L('sleeve_R')),('neckwear',L('choker')),('face',L('face_base')),('nose',L('nose'))]
r,l=split(L('eyebrow')); lay+=[('eyebrow-r',r),('eyebrow-l',l)]
lay+=[('mouth close',L('mouth')),('mouth open',L('mouth_open')),('front hair',L('front_hair'))]
for nm,k in [('eyewhite','eye_white'),('irides','iris'),('eyelash','eyelash')]:
    r,l=split(L(k)); lay+=[(nm+'-r',r),(nm+'-l',l)]
lay+=[('front hair 2',L('ahoge')),('headwear 2',L('ribbon')),('headwear 1',L('mask')),('back hair 2',L('braid')),('back hair 3',L('twintail'))]
write(lay,(2048,3072),sys.argv[1])
