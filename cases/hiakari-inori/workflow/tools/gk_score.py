import glob,sys,numpy as np
from PIL import Image
def score(job,f):
    a=np.asarray(Image.open(f'{job}/input.png').convert('RGB')).astype(int)
    m=np.asarray(Image.open(f'{job}/mask.png'))>127
    g=np.asarray(Image.open(f).convert('RGB').resize((a.shape[1],a.shape[0]),Image.LANCZOS)).astype(int)
    vis=~m&~((a[...,1]>200)&(a[...,0]<60)&(a[...,2]<60))
    d=np.abs(g-a)[vis].mean()
    gg=(g[...,1]>150)&(g[...,1]-np.maximum(g[...,0],g[...,2])>60); mg=(g[...,0]>200)&(g[...,2]>200)&(g[...,1]<80)
    return d, (gg&m).mean()/m.mean(), (mg&m).mean()/m.mean()
if __name__=='__main__':
    for f in sys.argv[2:]: print(f[-60:], ['%.3f'%x for x in score(sys.argv[1],f)])
