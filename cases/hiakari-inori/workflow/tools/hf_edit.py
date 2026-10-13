#!/usr/bin/env python3
"""HF Space image edit via gradio_client.
usage: python3 hf_edit.py in.png out.png "prompt" [--space NAME] [--seed N] [--steps N] [--size WxH]
Spaces tried in order (fallback on quota/errors): lpx55 (Qwen-Image-Edit-2511 Lightning), kontext (FLUX.1-Kontext-Dev).
Run with /workspace/tools/venv-hf/bin/python (needs gradio_client). Optional HF token: env HF_TOKEN (more ZeroGPU quota).
"""
import sys,os,time,shutil,argparse
from gradio_client import Client, handle_file
from PIL import Image
ap=argparse.ArgumentParser(); ap.add_argument('inp'); ap.add_argument('out'); ap.add_argument('prompt')
ap.add_argument('--space',default='auto'); ap.add_argument('--seed',type=int,default=0); ap.add_argument('--steps',type=int,default=0)
ap.add_argument('--size',default=''); ap.add_argument('--no-align',action='store_true',help='skip SIFT+RANSAC re-registration of output back onto the input frame'); ap.add_argument('--retries',type=int,default=2)
a=ap.parse_args()
W,H=Image.open(a.inp).size
if a.size: W,H=map(int,a.size.lower().split('x'))
tok=os.environ.get('HF_TOKEN')
def first(r):
    while isinstance(r,(list,tuple)): r=r[0]
    if isinstance(r,dict): r=r.get('image',r.get('path',r)); 
    if isinstance(r,dict): r=r.get('path')
    return r
def run(space):
    c=Client(space,hf_token=tok) if tok else Client(space)
    f=handle_file(a.inp)
    if space=='black-forest-labs/FLUX.1-Kontext-Dev':
        return first(c.predict(input_image=f,prompt=a.prompt,seed=a.seed,randomize_seed=False,guidance_scale=2.5,steps=a.steps or 28,api_name='/infer'))
    if space=='LPX55/Qwen-Image-Edit-2511-Turbo-Lightning':
        return first(c.predict(images=[{'image':f}],prompt=a.prompt,seed=a.seed,randomize_seed=False,true_guidance_scale=1.0,num_inference_steps=a.steps or 4,height=H,width=W,rewrite_prompt=False,num_images_per_prompt=1,api_name='/infer'))
    if space.startswith('linoyts/Qwen-Image-Edit-2511-Fast'):
        return first(c.predict(images=[{'image':f}],prompt=a.prompt,seed=a.seed,randomize_seed=False,true_guidance_scale=1.0,num_inference_steps=a.steps or 4,height=H,width=W,rewrite_prompt=False,api_name='/infer'))
    raise SystemExit('unknown space')
order={'auto':['black-forest-labs/FLUX.1-Kontext-Dev','LPX55/Qwen-Image-Edit-2511-Turbo-Lightning'],
 'lpx55':['LPX55/Qwen-Image-Edit-2511-Turbo-Lightning'],'kontext':['black-forest-labs/FLUX.1-Kontext-Dev'],'linoyts':['linoyts/Qwen-Image-Edit-2511-Fast']}.get(a.space,[a.space])
def align(out_path,in_path):
    """Outputs are NOT pixel aligned (Kontext: anisotropic ~2-8% scale + shift that varies per prompt; LPX55: center-crop zoom 1.34x).
    Estimate affine from unchanged regions (SIFT + RANSAC) and warp output onto the input frame. Returns inlier count."""
    import cv2, numpy as np
    ref=cv2.imread(in_path); o=cv2.imread(out_path); Hh,Ww=ref.shape[:2]
    o=cv2.resize(o,(Ww,Hh),interpolation=cv2.INTER_LANCZOS4)
    sift=cv2.SIFT_create(4000); gr=cv2.cvtColor(ref,cv2.COLOR_BGR2GRAY); go=cv2.cvtColor(o,cv2.COLOR_BGR2GRAY)
    kr,dr=sift.detectAndCompute(gr,None); ko,do=sift.detectAndCompute(go,None)
    ms=[m for m,n in cv2.BFMatcher().knnMatch(dr,do,k=2) if m.distance<0.75*n.distance]
    if len(ms)<12: print('align: too few matches',len(ms)); return 0
    A=np.float32([kr[m.queryIdx].pt for m in ms]); B=np.float32([ko[m.trainIdx].pt for m in ms])
    M,inl=cv2.estimateAffine2D(B,A,ransacReprojThreshold=2.0)
    if M is None or inl.sum()<12: print('align: failed'); return 0
    w=cv2.warpAffine(o,M,(Ww,Hh),flags=cv2.INTER_LANCZOS4,borderMode=cv2.BORDER_REPLICATE)
    cv2.imwrite(out_path,w); print('align: inliers',int(inl.sum()),'M',M.round(3).tolist()); return int(inl.sum())
for sp in order:
    for k in range(a.retries):
        try:
            t=time.time(); p=run(sp)
            im=Image.open(p); im.load(); im.save(a.out)
            if not a.no_align:
                raw=a.out.rsplit('.',1)[0]+'_raw.png'; im.save(raw); align(a.out,a.inp)
            print('OK',sp,im.size,round(time.time()-t,1),'s ->',a.out); sys.exit(0)
        except Exception as e:
            print('fail',sp,type(e).__name__,str(e)[:200],file=sys.stderr); time.sleep(45 if 'limit' in str(e) or 'quota' in str(e) else 3)
sys.exit(1)
