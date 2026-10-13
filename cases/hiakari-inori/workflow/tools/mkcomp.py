import numpy as np,cv2,json
from PIL import Image, ImageDraw
d=json.load(open('../layers.json')); names=[l['file'].split('/')[-1][:-4] for l in sorted(d['layers'],key=lambda l:l['z_order']) if l['name']!='mouth open']
def comp(fn,bic=False):
    base=np.ones((1440,1200,3),np.float32)
    for n in names:
        a=np.array(Image.open(fn(n)).convert('RGBA')).astype(np.float32)/255
        if bic:
            p=np.dstack([a[...,:3]*a[...,3:],a[...,3:]])
            p=cv2.resize(p,(1200,1440),interpolation=cv2.INTER_CUBIC)
            p[...,3]=p[...,3].clip(0,1); p[...,:3]=np.clip(p[...,:3],0,p[...,3:])
            base=p[...,:3]+base*(1-p[...,3:])
        else: base=a[...,:3]*a[...,3:]+base*(1-a[...,3:])
    return (base*255+.5).astype(np.uint8)
hr=comp(lambda n:f'../layers_hr/{n}.png'); bic=comp(lambda n:f'../layers/{n}.png',True)
Image.fromarray(hr).save('../composite_hr_check.png')
ref=np.array(Image.open('../composite_check.png').convert('RGB'))
down=cv2.resize(hr,(600,720),interpolation=cv2.INTER_AREA)
print('MAE vs ref',np.abs(down.astype(float)-ref).mean())
def crop(img,b,z): x0,y0,x1,y1=b; return cv2.resize(img[y0:y1,x0:x1],None,fx=z,fy=z,interpolation=cv2.INTER_NEAREST)
def panel(b,z,title):
    A=crop(bic,b,z);B=crop(hr,b,z)
    im=Image.fromarray(np.hstack([A,np.full((A.shape[0],6,3),128,np.uint8),B]))
    pad=Image.new('RGB',(im.width,im.height+22),'white'); pad.paste(im,(0,22))
    ImageDraw.Draw(pad).text((4,4),f'{title} | LEFT: bicubic 2x (premultiplied) | RIGHT: Real-ESRGAN anime 6B -> 2x',fill=(0,0,0)); return pad
ps=[panel((320,40,880,520),1,'head, 1:1 of 1200x1440'),panel((470,230,720,340),2,'eyes, 2x zoom'),panel((560,340,660,420),4,'nose/mouth, 4x zoom')]
w=max(p.width for p in ps); out=Image.new('RGB',(w,sum(p.height for p in ps)),'white'); y=0
for p in ps: out.paste(p,(0,y)); y+=p.height
out.save('../hr_compare.png'); print(out.size)
