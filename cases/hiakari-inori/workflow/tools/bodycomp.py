import json, sys, numpy as np, cv2
from PIL import Image
fits=json.load(open(sys.argv[2] if len(sys.argv)>2 else 'bodyfit.json'))
W,H=1024,1536
def place(k):
    f=fits[k]; im=np.asarray(Image.open(f"keyed_body/{f['layer']}.png").convert('RGBA')).copy()
    a=im[...,3:4]/255.; pm=np.concatenate([im[...,:3]*a,im[...,3:4]],2).astype(np.float32)
    out=cv2.warpAffine(pm,np.float32(f['F']),(W,H),flags=cv2.INTER_AREA if f['F'][0][0]<1 else cv2.INTER_CUBIC)
    al=out[...,3:4]; rgb=np.where(al>1e-3,out[...,:3]/np.maximum(al/255.,1e-3),0)
    return np.concatenate([np.clip(rgb,0,255),al],2).astype(np.uint8)
order=[k for k in ['socks','skirt','shoes','topwear','arm_right','arm_left','collar_front','bow'] if k in fits]
c=Image.new('RGBA',(W,H),(255,255,255,255))
for k in order: c.alpha_composite(Image.fromarray(place(k),'RGBA'))
tag=sys.argv[1]; c.save(f'bodycomp_{tag}.png')
m=Image.open('master_full_1.png').convert('RGB'); box=(180,260,880,1536)
B=Image.new('RGB',(1400,1276)); B.paste(m.crop(box),(0,0)); B.paste(c.convert('RGB').crop(box),(700,0)); B=B.resize((1050,957)); B.save(f'bodycmp_{tag}.png')
