import sys,os,numpy as np
sys.path.insert(0,'/workspace/tools'); import sr as SR
from PIL import Image
os.chdir('/workspace/art/inori')
m=np.asarray(Image.open('v4/master_v4.png').convert('RGB')).astype(np.float32)/255
x0,y0,x1,y1=300,560,724,1536
o2=SR.down2(SR.sr4(m[y0:y1,x0:x1]))
can=np.full((3072,2048,3),255,np.uint8); can[y0*2:y1*2,x0*2:x1*2]=(np.clip(o2,0,1)*255+.5).astype(np.uint8)
Image.fromarray(can).save('v4/legs/master_hr.png'); print('ok')
