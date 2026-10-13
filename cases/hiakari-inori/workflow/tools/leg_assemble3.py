import numpy as np,json,os,cv2,sys
from PIL import Image
from scipy import ndimage as ndi
os.chdir('/workspace/art/inori')
M=np.asarray(Image.open('legs/master_hr.png').convert('RGB'))
L=lambda n:np.load(f'legs/{n}.npy'); H,W=3072,2048
sel=json.loads(sys.argv[1])  # {"thigh_R":"thigh_R_c2","thigh_L":..., "knee":...}
meta=json.load(open('legs/jobs/meta.json'))
fill={k:np.zeros((H,W,3),np.uint8) for k in ['leg_R','leg_L','boot_R','boot_L']}
have={k:np.zeros((H,W),bool) for k in fill}
def isgreen(o): o=o.astype(int); return (o[...,1]>150)&(o[...,1]-np.maximum(o[...,0],o[...,2])>60)
def isMag(o): o=o.astype(int); return (o[...,0]>200)&(o[...,2]>200)&(o[...,1]<80)
# v3 jobs first (priority)
m3=json.load(open('legs/jobs3/meta.json'))
for s in 'RL':
    x0,y0,x1,y1=m3[f'thigh_{s}']['box']; o=np.asarray(Image.open(f'legs/jobs3/{sel["thigh_"+s]}/output.png').convert('RGB').resize((x1-x0,y1-y0),Image.LANCZOS))
    h=L(f'hid4_thigh_{s}')[y0:y1,x0:x1]&~isgreen(o)&~isMag(o)
    fill[f'leg_{s}'][y0:y1,x0:x1][h]=o[h]; have[f'leg_{s}'][y0:y1,x0:x1]|=h
x0,y0,x1,y1=960,1880,1100,2470
o=np.asarray(Image.open(f'legs/jobs3/{sel["knee"]}/output.png').convert('RGB'))
hk=L('hid3_knee3')[y0:y1,x0:x1]&~isgreen(o)&~isMag(o)
# knee seam belongs to screen-right leg (leg_L)
fill['leg_L'][y0:y1,x0:x1][hk]=o[hk]; have['leg_L'][y0:y1,x0:x1]|=hk
KNEE=np.zeros((H,W),bool); KNEE[y0:y1,x0:x1]=hk
for j,m in meta.items():
    x0,y0,x1,y1=m['box']; o=np.asarray(Image.open(f'legs/jobs/{j}/output.png').convert('RGB').resize((x1-x0,y1-y0),Image.LANCZOS))
    h=L('hid_'+m['layer'])[y0:y1,x0:x1]; hv=have[m['layer']][y0:y1,x0:x1]; nh=h&~hv
    fill[m['layer']][y0:y1,x0:x1][nh]=o[nh]; hv|=nh
os.makedirs('legs/layers3',exist_ok=True); stats={}
def mk(vis,hidm,fillimg):
    rgb=np.zeros((H,W,3),np.uint8); rgb[vis]=M[vis]; rgb[hidm]=fillimg[hidm]
    a=(vis|hidm).astype(np.float32); a=cv2.GaussianBlur(a,(0,0),0.6); a[ndi.binary_erosion(vis|hidm)]=1
    return np.dstack([rgb,(a*255+.5).astype(np.uint8)])
yy=np.arange(H)[:,None]; xx=np.arange(W)[None]; out={}
cl=np.where(np.isnan(L('cut_leg')),1020,L('cut_leg'))[:,None]
for s in 'RL':
    v=L(f'vis_leg_{s}'); light=L('seam_light') if s=='L' else np.zeros_like(v)
    Z=np.zeros((H,W),bool)
    v=v&~(KNEE if s=='L' else Z)&~L(f'hid4_thigh_{s}')
    hid=(L(f'hid_leg_{s}')|L(f'hid4_thigh_{s}')|(KNEE if s=='L' else Z))&~v
    h=hid&have[f'leg_{s}']&~isgreen(fill[f'leg_{s}'])
    if s=='R': h&=~KNEE
    stats[f'leg_{s}_hidden_uncovered']=int((hid&~h&(yy<1960)).sum())
    x0,y0,x1,y1=m3[f'thigh_{s}']['box']; YC=1650
    o=np.asarray(Image.open(f'legs/jobs3/{sel["thigh_"+s]}/output.png').convert('RGB'))[:YC-y0]
    ok=~isgreen(o)&~isMag(o); R=np.zeros((H,W),bool); R[y0:YC,x0:x1]=True
    v=v&~R; h=h&~R; f=fill[f'leg_{s}']; f[y0:YC,x0:x1][ok]=o[ok]; h[y0:YC,x0:x1]|=ok
    full=mk(v,h,f)
    th=full.copy(); fade=np.clip((2060-yy)/40,0,1); th[...,3]=(th[...,3]*fade).astype(np.uint8)
    sh=full.copy(); sh[:1980,:,3]=0
    out[f'thigh_{s}']=th; out[f'shin_{s}']=sh
for k in ['boot_R','boot_L','garter_R','garter_L']: out[k]=np.asarray(Image.open(f'legs/layers/{k}.png').convert('RGBA'))
for k,a in out.items(): Image.fromarray(a,'RGBA').save(f'legs/layers3/{k}.png')
os.system('cp legs/layers/skirt_nogarter.png legs/layers3/')
json.dump(stats,open('legs/assemble3_stats.json','w')); print(stats)
