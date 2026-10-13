import json, sys, numpy as np, cv2
from PIL import Image
fits=json.load(open('headfit.json'))
W,H=1086,1448
def place(k):
    f=fits[k]; im=np.asarray(Image.open(f"keyed_head/{f['layer']}.png").convert('RGBA')).copy()
    x0,x1,y0,y1=f['box']; msk=np.zeros(im.shape[:2],bool); msk[y0:y1,x0:x1]=True
    im[~msk]=0
    a=im[...,3:4]/255.; pm=np.concatenate([im[...,:3]*a,im[...,3:4]],2).astype(np.float32)
    out=cv2.warpAffine(pm,np.float32(f['F']),(W,H),flags=cv2.INTER_AREA if f['F'][0][0]<1 else cv2.INTER_CUBIC)
    al=out[...,3:4]; rgb=np.where(al>1e-3,out[...,:3]/np.maximum(al/255.,1e-3),0)
    return np.concatenate([np.clip(rgb,0,255),al],2).astype(np.uint8)
order=['back_hair','neck','face_base','eye_white_L','eye_white_R','iris_L','iris_R','eyelash_L','eyelash_R','eyebrow_L','eyebrow_R','mouth','front_hair']
c=Image.new('RGBA',(W,H),(255,255,255,255))
for k in order: c.alpha_composite(Image.fromarray(place(k),'RGBA'))
tag=sys.argv[1]
c.save(f'headcomp_{tag}.png')
m=Image.open('head_closeup_2.png').convert('RGB')
box=(250,380,850,820)
B=Image.new('RGB',(1200,440)); B.paste(m.crop(box),(0,0)); B.paste(c.convert('RGB').crop(box),(600,0)); B.save(f'headcmp_{tag}.png')
