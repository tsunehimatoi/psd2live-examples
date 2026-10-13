import numpy as np,os
from PIL import Image
from scipy import ndimage as ndi
M=np.asarray(Image.open('legs/master_hr.png').convert('RGB')).astype(int)
L=lambda n:np.load(f'legs/{n}.npy'); H,W=3072,2048
cl=L('cut_leg'); cl=np.where(np.isnan(cl),1020,cl)
xx=np.arange(W)[None]; yy=np.arange(H)[:,None]
near=(np.abs(xx-cl[:,None])<=6)&(yy>=1880)&(yy<2470)
lum=M.mean(2); bg=ndi.uniform_filter(lum,15)
light=near&(lum>bg+8)
light=ndi.binary_dilation(light,iterations=1)&near
np.save('legs/seam_light.npy',light); print('seam light px',light.sum())
x0,y0,x1,y1=960,1880,1100,2470
vL=L('vis_leg_L'); vR=L('vis_leg_R'); hL=L('hid_leg_L')
vis=(vL|vR)&~light; hid=(light|hL)&~vis
im=np.zeros((y1-y0,x1-x0,3),np.uint8); im[:]=(0,255,0)
s=(slice(y0,y1),slice(x0,x1)); v=vis[s]; h=hid[s]
im[v]=M[s][v]; im[h]=(255,0,255)
d='legs/jobs3/knee'; os.makedirs(d,exist_ok=True)
Image.fromarray(im.astype(np.uint8)).save(f'{d}/input.png'); Image.fromarray((h*255).astype(np.uint8)).save(f'{d}/mask.png')
np.save('legs/hid3_knee.npy',hid)
open(f'{d}/prompt.txt','w').write(f"""Files here: input.png ({x1-x0}x{y1-y0}) and mask.png (white = area to paint). input.png is a crop of an anime illustration showing two legs in black semi-sheer stockings touching at the knees and shins (front view). The MAGENTA pixels are a thin seam between the legs plus the inner edge of the right-hand leg. Using your built-in image generation/editing, inpaint ONLY the magenta pixels with the continuous dark black-stocking shading of the leg on the right side of the seam, so there is no light line or gap along the seam. Do not change non-magenta pixels; keep the exact canvas size and framing. Save as output.png here (resize to exactly {x1-x0}x{y1-y0}). Then stop.""")
