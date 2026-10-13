import cv2, numpy as np, json, sys
from PIL import Image
W,H=1086,1448
def blobs(a, k=25, n=2):
    m=(a>128).astype(np.uint8); d=cv2.dilate(m,np.ones((k,k),np.uint8))
    cnt,lab,st,cen=cv2.connectedComponentsWithStats(d)
    idx=sorted(range(1,cnt),key=lambda i:-st[i,4])[:n]
    out=[]
    for i in idx:
        mm=(lab==i)&(m>0); ys,xs=np.where(mm)
        out.append((xs.min(),xs.max()+1,ys.min(),ys.max()+1))
    return sorted(out)  # by x
def place(name, T, src=None, mode='pair'):
    """T: dict target. pair: centers [(cx,cy),(cx,cy)], width w. single: center, width"""
    im=Image.open(f'keyed/{src or name}.png').convert('RGBA'); a=np.asarray(im)[...,3]
    if mode=='pair':
        b=blobs(a); (l,r)=b
        lc=((l[0]+l[1])/2,(l[2]+l[3])/2); rc=((r[0]+r[1])/2,(r[2]+r[3])/2)
        lw=l[1]-l[0]; rw=r[1]-r[0]
        # scale: match blob mean width AND centre distance (average)
        s_w=T['w']/((lw+rw)/2); s_d=(T['c'][1][0]-T['c'][0][0])/(rc[0]-lc[0])
        s=T.get('mix',0.5)*s_w+(1-T.get('mix',0.5))*s_d
        cx=(lc[0]+rc[0])/2; cy=(lc[1]+rc[1])/2
        tcx=(T['c'][0][0]+T['c'][1][0])/2; tcy=(T['c'][0][1]+T['c'][1][1])/2
    else:
        ys,xs=np.where(a>128); x0,x1,y0,y1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
        s=T['w']/(x1-x0); cx=(x0+x1)/2; cy=(y0+y1)/2; tcx,tcy=T['c']
    M=np.float32([[s,0,tcx-s*cx],[0,s,tcy-s*cy]])
    out=cv2.warpAffine(np.asarray(im),M,(W,H),flags=cv2.INTER_AREA if s<1 else cv2.INTER_CUBIC,borderValue=(0,0,0,0))
    # premultiplied-safe: fix colour fringe by warping premult
    Image.fromarray(out).save(f'aligned/{name}.png')
    return dict(s=float(s),M=M.tolist())
if __name__=='__main__':
    res={}
    res['eye_white']=place('eye_white',dict(c=[(440,369),(627,369)],w=82))
    res['iris']=place('iris',dict(c=[(442,360),(622,360)],w=48))
    res['eyelash']=place('eyelash',dict(c=[(423.5,346),(645,346)],w=107))
    res['eyebrow']=place('eyebrow',dict(c=[(440,292),(625,292)],w=95))
    res['eye_closed']=place('eye_closed',dict(c=[(425,362),(645,362)],w=100))
    res['mouth_closed']=place('mouth_closed',dict(c=(532,481),w=62),mode='single')
    res['mouth_open']=place('mouth_open',dict(c=(532,486),w=56),mode='single')
    # hair + face by fixed similarity
    def fixed(name,s,tx,ty):
        im=Image.open(f'keyed/{name}.png').convert('RGBA')
        M=np.float32([[s,0,tx],[0,s,ty]])
        out=cv2.warpAffine(np.asarray(im),M,(W,H),flags=cv2.INTER_AREA,borderValue=(0,0,0,0))
        Image.fromarray(out).save(f'aligned/{name}.png'); return dict(s=s,M=M.tolist())
    res['back_hair']=fixed('back_hair',0.631,189.7,-104.7)
    res['front_hair']=fixed('front_hair',0.6275,194.0,-88.0)
    res['face_base']=fixed('face_base',0.54,252.0,80.0)
    json.dump(res,open('aligned/transforms.json','w'),indent=1)
    for k,v in res.items(): print(k,round(v['s'],3))
