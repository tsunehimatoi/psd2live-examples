# usage: venv-sr python v5_align.py name...   (dir gen/<name>/out.png)
import sys,os,json,subprocess,cv2,numpy as np
sys.path.insert(0,'/workspace/tools'); import sr as SR
from PIL import Image
from scipy import ndimage as ndi
os.chdir('/workspace/art/inori/v5')
REF={'body':'base_master.png','cloth':'../v4/master_v4.png'}
sift=cv2.SIFT_create(8000,contrastThreshold=0.01)
res=json.load(open('align.json')) if os.path.exists('align.json') else {}
for n in sys.argv[1:]:
    d=f'gen/{n}'; kind='body' if n.split('_')[0] in('torso','legs') else 'cloth'
    ref=cv2.imread(REF[kind]); H,W=ref.shape[:2]
    subprocess.run(['python3','/workspace/tools/key.py',f'{d}/out.png',f'{d}/keyed.png'],check=True)
    k=np.asarray(Image.open(f'{d}/keyed.png').convert('RGBA'))
    if k.shape[:2]!=(H,W): k=np.asarray(Image.fromarray(k).resize((W,int(round(k.shape[0]*W/k.shape[1]))),Image.LANCZOS))
    k=k[:H] if k.shape[0]>=H else np.pad(k,((0,H-k.shape[0]),(0,0),(0,0)))
    a=k[...,3]
    lab,nn=ndi.label(a>60); sz=ndi.sum(a>60,lab,range(1,nn+1)); keep=np.isin(lab,1+np.where(sz>max(150,0.01*sz.max()))[0]); k=k.copy(); k[~ndi.binary_dilation(keep,iterations=3),3]=0; a=k[...,3]
    Image.fromarray(k).save(f'{d}/keyed1x.png')
    g=cv2.cvtColor(np.ascontiguousarray(k[...,:3]),cv2.COLOR_RGB2GRAY); g=np.where(a>128,g,128).astype(np.uint8)
    m0=ndi.binary_dilation(a>60,iterations=60).astype(np.uint8)*255
    k0,d0=sift.detectAndCompute(cv2.cvtColor(ref,cv2.COLOR_BGR2GRAY),m0)
    k1,d1=sift.detectAndCompute(g,(ndi.binary_erosion(a>128,iterations=2)).astype(np.uint8)*255)
    mt=[p for p,q in cv2.BFMatcher().knnMatch(d1,d0,k=2) if p.distance<.8*q.distance]
    M,inl=cv2.estimateAffinePartial2D(np.float32([k1[p.queryIdx].pt for p in mt]),np.float32([k0[p.trainIdx].pt for p in mt]),ransacReprojThreshold=3)
    s=float(np.hypot(*M[0,:2]))
    hr=SR.process(f'{d}/keyed1x.png').astype(np.float32)
    M2=M.copy(); M2[:,2]*=2
    al=hr[...,3:]/255; pm=np.dstack([hr[...,:3]*al,hr[...,3:]])
    w=cv2.warpAffine(pm,M2,(2*W,2*H),flags=cv2.INTER_LANCZOS4); A=np.clip(w[...,3],0,255)
    rgb=np.where(A[...,None]>0,w[...,:3]/np.maximum(A[...,None],1e-3)*255,0)
    out=np.dstack([np.clip(rgb,0,255),A]).astype(np.uint8); Image.fromarray(out).save(f'layers/{n}.png')
    # visible-diff vs ref where alpha high
    w1=cv2.warpAffine(k.astype(np.float32),M,(W,H)); msk=w1[...,3]>230
    diff=np.abs(w1[...,:3][...,::-1]-ref)[msk].max(1) if msk.any() else np.array([255.])
    res[n]=dict(inl=int(inl.sum()),scale=round(s,3),rot=round(float(np.degrees(np.arctan2(M[1,0],M[0,0]))),2),med_diff=float(np.median(diff)),lt20=round(float((diff<20).mean()),3))
    print(n,res[n],flush=True)
json.dump(res,open('align.json','w'),indent=1)
