import sys,numpy as np,cv2
sys.path.insert(0,'/workspace/tools'); import sr as SR
from PIL import Image
m=np.asarray(Image.open('master_1.png').convert('RGB')).astype(np.float32)/255
x0,y0,x1,y1=340,660,700,1536
o4=SR.sr4(m[y0:y1,x0:x1]); o2=SR.down2(o4)
can=np.full((3072,2048,3),255,np.uint8); can[y0*2:y1*2,x0*2:x1*2]=(np.clip(o2,0,1)*255+.5).astype(np.uint8)
Image.fromarray(can).save('legs/master_hr.png'); print('ok')
