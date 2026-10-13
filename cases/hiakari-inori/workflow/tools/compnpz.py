import sys, numpy as np
from PIL import Image, ImageDraw
tag=sys.argv[1]; L=dict(np.load(f'full_layers_{tag}.npz'))
order=['back_hair','legs','socks','shoes','skirt','topwear','arm_right','arm_left','neck','collar_front','bow','face_base','nose','eye_white_L','eye_white_R','iris_L','iris_R','eyelash_L','eyelash_R','eyebrow_L','eyebrow_R','mouth','front_hair']
c=Image.new('RGBA',(2048,3072),(255,255,255,255))
for k in order: c.alpha_composite(Image.fromarray(L[k],'RGBA'))
c.save(f'full_comp_{tag}.png')
h=c.crop((750,0,1350,640)).convert('RGB'); d=ImageDraw.Draw(h)
d.line([(1026-750,0),(1026-750,640)],fill=(255,0,0),width=1); d.line([(0,312),(600,312)],fill=(0,160,0),width=1)
h=h.resize((1200,1280)); h.save(f'headchk_{tag}.png')
