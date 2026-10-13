import numpy as np,json,os
from PIL import Image
M=np.asarray(Image.open('legs/master_hr.png').convert('RGB'))
L=lambda n:np.load(f'legs/{n}.npy')
jobs={
 'thigh_R':('leg_R',(740,1370,1050,1910),'the upper thigh of the character\'s right leg (left side of image): pale anime skin above a black semi-sheer thigh-high stocking with a plain black top band; the area was hidden under a skirt and red garter straps'),
 'thigh_L':('leg_L',(990,1370,1300,1910),'the upper thigh of the character\'s left leg (right side of image): pale anime skin above a black semi-sheer thigh-high stocking with a plain black top band; the area was hidden under a skirt and garter strap'),
 'knee_L':('leg_L',(960,1880,1110,2470),'the inner edge of a leg in a black semi-sheer stocking (knee and shin); continue the stocking shading smoothly where it was hidden behind the other leg'),
 'foot_R':('leg_R',(820,2380,1040,2940),'the lower shin, ankle and foot of a leg in a black semi-sheer stocking, as it would look inside a boot (no boot, just stocking-covered leg and foot)'),
 'foot_L':('leg_L',(990,2380,1190,2940),'the lower shin, ankle and foot of a leg in a black semi-sheer stocking, as it would look inside a boot (no boot, just stocking-covered leg and foot)'),
 'boot_L':('boot_L',(950,2430,1100,3030),'the inner side of a white platform boot with red straps and red/black sole; continue the boot where it was hidden behind the other boot'),
}
os.makedirs('legs/jobs',exist_ok=True); meta={}
for k,(lay,(x0,y0,x1,y1),desc) in jobs.items():
    v=L('vis_'+lay)[y0:y1,x0:x1]; h=L('hid_'+lay)[y0:y1,x0:x1]
    im=np.zeros((y1-y0,x1-x0,3),np.uint8); im[:]=(0,255,0)
    im[v]=M[y0:y1,x0:x1][v]; im[h]=(255,0,255)
    d=f'legs/jobs/{k}'; os.makedirs(d,exist_ok=True)
    Image.fromarray(im).save(f'{d}/input.png'); Image.fromarray((h*255).astype(np.uint8)).save(f'{d}/mask.png')
    meta[k]=dict(layer=lay,box=[x0,y0,x1,y1],desc=desc,hid=int(h.sum()))
    open(f'{d}/prompt.txt','w').write(f"""In this directory there is input.png ({x1-x0}x{y1-y0} px) and mask.png (white = region to fill). input.png shows {desc}. Visible original artwork pixels are kept; the MAGENTA (#FF00FF) region is the hidden area that must be painted in (occlusion completion / inpainting). The bright green (#00FF00) is flat chroma background and must stay pure #00FF00.
Use your built-in image generation/editing tool to edit input.png: inpaint ONLY the magenta region so it seamlessly continues the existing anime cel-shaded artwork (same colors, shading, line style, lighting), matching the leg/boot anatomy. Do not change any non-magenta pixel, do not move, crop, rescale or reframe; keep exactly the same canvas size {x1-x0}x{y1-y0} and position. No magenta may remain. No text.
Save the result as output.png in this directory (resize back to exactly {x1-x0}x{y1-y0} if the generator returns another size). Then stop.""")
json.dump(meta,open('legs/jobs/meta.json','w'),indent=1); print(json.dumps(meta,indent=0))
