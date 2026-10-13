import numpy as np, cv2, sys
from PIL import Image
sys.path.insert(0,'/workspace/tools')
S=2; W,H=2048,3072
M3=np.load('M3.npy'); k=float(np.sqrt(M3[0,0]**2+M3[1,0]**2))*S
dx=float(sys.argv[2]) if len(sys.argv)>2 else 0; dy=float(sys.argv[3]) if len(sys.argv)>3 else 0
p=np.array([543,750,1.0]); q=(M3@p)*S          # where the closeup chin point lands (with M3's rotation), 2x canvas
tx=q[0]-k*543+dx; ty=q[1]-k*750+dy
A=np.float32([[k,0,tx],[0,k,ty]]); print('k',k,'t',tx,ty)
def warp(im):
    a=im[...,3:4]/255.; pm=np.concatenate([im[...,:3]*a,im[...,3:4]],2).astype(np.float32)
    out=cv2.warpAffine(pm,A,(W,H),flags=cv2.INTER_AREA)
    al=np.clip(out[...,3:4],0,255); rgb=np.where(al>1e-3,out[...,:3]/np.maximum(al/255.,1e-3),0)
    return np.concatenate([np.clip(rgb,0,255),al],2).astype(np.uint8)
base=dict(np.load('backup_full_layers_h3.npz')); head=dict(np.load('head3_closeup.npz')); head['neck']=np.asarray(Image.open('keyed_head3/neck_ext.png').convert('RGBA'))
F=float(sys.argv[4]) if len(sys.argv)>4 else 1.0; FC=(543,640)
G=np.float32([[F,0,FC[0]*(1-F)],[0,F,FC[1]*(1-F)],[0,0,1]]); AG=(np.vstack([A,[0,0,1]])@G)[:2].astype(np.float32)
def warpG(im):
    global A
    A0=A; A=AG; o=warp(im); A=A0; return o
FACE={'face_base','mouth','mouth_open','nose','eye_white_L','eye_white_R','iris_L','iris_R','eyelash_L','eyelash_R','eyebrow_L','eyebrow_R'}
neckfile=sys.argv[5] if len(sys.argv)>5 else 'neck'
for key in ['back_hair','front_hair','neck','face_base','mouth','mouth_open','nose','eye_white_L','eye_white_R','iris_L','iris_R','eyelash_L','eyelash_R','eyebrow_L','eyebrow_R']:
    base[key]=(warpG if key in FACE else warp)(head[key])
base['nose']=(lambda im:(im.__setitem__((Ellipsis,3),(im[...,3]*0.4).astype(np.uint8)) or im))(base['nose'])
np.savez_compressed(f'full_layers_{sys.argv[1]}.npz',**base)
