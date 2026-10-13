import sys,numpy as np; sys.path.insert(0,'/workspace/tools'); import sr as SR
from PIL import Image
m=np.asarray(Image.open('/workspace/art/inori/v5/base_master.png').convert('RGB')).astype(np.float32)/255
o=SR.down2(SR.sr4(m)); Image.fromarray((np.clip(o,0,1)*255+.5).astype(np.uint8)).save('/workspace/art/inori/v5/base_hr.png'); print(o.shape)
