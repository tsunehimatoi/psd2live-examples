import sys,numpy as np
from PIL import Image
def comp(job,f):
    a=np.asarray(Image.open(f'{job}/input.png').convert('RGB')).copy()
    m=np.asarray(Image.open(f'{job}/mask.png'))>127
    g=np.asarray(Image.open(f).convert('RGB').resize((a.shape[1],a.shape[0]),Image.LANCZOS))
    a[m]=g[m]; return a
if __name__=='__main__':
    job=sys.argv[1]; out=sys.argv[2]; ims=[comp(job,f) for f in sys.argv[3:]]
    Image.fromarray(np.concatenate([np.pad(i,((0,0),(0,6),(0,0)),constant_values=255) for i in ims],1)).save(out)
