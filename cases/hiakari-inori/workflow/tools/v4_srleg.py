import sys; sys.path.insert(0,'/workspace/tools'); import sr as SR, numpy as np
from PIL import Image
for d in ['R_w4','L_w8']:
    o=SR.process(f'/workspace/art/inori/v4/wleg/{d}/aligned.png')
    Image.fromarray(np.clip(o,0,255).astype(np.uint8) if o.dtype!=np.uint8 else o,'RGBA').save(f'/workspace/art/inori/v4/wleg/{d}/hr.png'); print(d,o.shape,o.dtype,o.max())
