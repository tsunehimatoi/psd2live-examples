import sys, numpy as np
sys.path.insert(0,'/workspace/tools')
from mkpsd import write
def split_pair(rgba):
    a=(rgba[...,3]>20).sum(0).astype(float); xs=np.where(a>0)[0]; x0,x1=xs.min(),xs.max()
    lo,hi=int(x0+.35*(x1-x0)),int(x0+.65*(x1-x0)); cut=lo+int(np.argmin(a[lo:hi])); print('cut',cut,a[cut])
    l=rgba.copy(); l[:,cut:,3]=0; r=rgba.copy(); r[:,:cut,3]=0; return [l,r]
tag=sys.argv[1]; out=sys.argv[2]
L=dict(np.load(f'full_layers_{tag}.npz'))
layers=[('back hair',L['back_hair'])]
for nm,k in [('legwear 1','legs'),('legwear 2','socks'),('footwear','shoes')]:
    r,l=split_pair(L[k]); layers+=[(nm+'-r',r),(nm+'-l',l)]
layers+=[('bottomwear',L['skirt']),('topwear',L['topwear']),('handwear-r',L['arm_right']),('handwear-l',L['arm_left']),
 ('neck',L['neck']),('neckwear 1',L['collar_front']),('neckwear 2',L['bow']),('face',L['face_base']),('nose',L['nose'])]
layers+=[('eyebrow-r',L['eyebrow_L']),('eyebrow-l',L['eyebrow_R']),('mouth close',L['mouth']),('mouth open',L['mouth_open']),('front hair',L['front_hair'])]
for nm,k in [('eyewhite','eye_white'),('irides','iris'),('eyelash','eyelash')]:
    layers+=[(nm+'-r',L[k+'_L']),(nm+'-l',L[k+'_R'])]
write(layers,(2048,3072),out)
