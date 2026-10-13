import json, sys, numpy as np, cv2
from PIL import Image
sys.path.insert(0,'/workspace/tools')
from mkpsd import split_pair, write
BASE=(1086,1448)
def run(S, mode, out_prefix):
    W,H=BASE[0]*S,BASE[1]*S
    META=json.load(open('up4/meta.json')) if mode=='up4' else {}
    def load(n):
        if mode=='up4': return np.asarray(Image.open(f'up4/{n}_x4.png').convert('RGBA')).astype(np.float32), META[n]['x0'], META[n]['y0'], 4.0
        return np.asarray(Image.open(f'keyed/{n}.png').convert('RGBA')).astype(np.float32), 0, 0, 1.0
    def warp(n,s,tx,ty,flip=False,cx=538):
        im,x0,y0,up=load(n)
        a=im[...,3:4]/255.; pm=np.concatenate([im[...,:3]*a, im[...,3:4]],axis=2)
        k=s*S/up
        M=np.float32([[k,0,S*s*x0+S*tx],[0,k,S*s*y0+S*ty]])
        out=cv2.warpAffine(pm,M,(W,H),flags=cv2.INTER_AREA if k<1 else cv2.INTER_CUBIC,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
        al=out[...,3:4]; rgb=np.where(al>1e-3,out[...,:3]/np.maximum(al/255.,1e-3),0)
        res=np.concatenate([np.clip(rgb,0,255),al],axis=2)
        if flip:
            res=res[:,::-1]; shift=int(round(S*(2*cx-(BASE[0]-1))))
            res=np.roll(res,shift,axis=1)
            if shift>0: res[:,:shift]=0
            elif shift<0: res[:,shift:]=0
        return res.astype(np.uint8)
    # --- transforms (s, tx, ty) in 1x canvas coords of the ORIGINAL (gpt) layer images
    def pair_T(n,c,w,mix=0.5):
        a=np.asarray(Image.open(f'keyed/{n}.png'))[...,3]
        m=(a>128).astype(np.uint8); d=cv2.dilate(m,np.ones((25,25),np.uint8)); cnt,lab,st,cen=cv2.connectedComponentsWithStats(d)
        idx=sorted(sorted(range(1,cnt),key=lambda i:-st[i,4])[:2],key=lambda i:cen[i][0]); bb=[]
        for i in idx:
            ys,xs=np.where((lab==i)&(m>0)); bb.append((xs.min(),xs.max()+1,ys.min(),ys.max()+1))
        (l,r)=bb; lc=((l[0]+l[1])/2,(l[2]+l[3])/2); rc=((r[0]+r[1])/2,(r[2]+r[3])/2)
        s=mix*(w/(((l[1]-l[0])+(r[1]-r[0]))/2))+(1-mix)*((c[1][0]-c[0][0])/(rc[0]-lc[0]))
        cx=(lc[0]+rc[0])/2; cy=(lc[1]+rc[1])/2; tcx=(c[0][0]+c[1][0])/2; tcy=(c[0][1]+c[1][1])/2
        return s, tcx-s*cx, tcy-s*cy
    def single_T(n,c,w):
        a=np.asarray(Image.open(f'keyed/{n}.png'))[...,3]; ys,xs=np.where(a>128)
        x0,x1,y0,y1=xs.min(),xs.max()+1,ys.min(),ys.max()+1; s=w/(x1-x0)
        return s, c[0]-s*(x0+x1)/2, c[1]-s*(y0+y1)/2
    P=json.load(open('params.json')) if __import__('os').path.exists('params.json') else {}
    g=lambda k,d: P.get(k,d)
    L={}
    L['back_hair']=warp('back_hair',0.631,189.7,-104.7)
    L['front_hair']=warp('front_hair',0.6275,194.0,-88.0)
    L['face']=warp('face_base2',0.64,196,-37)
    L['neck']=warp('neck',0.73,137.6,174)
    L['torso']=warp('torso',0.94,27,282)
    L['collar']=warp('collar_front',0.73,137.6,174)
    L['bow']=warp('bow',0.62,535-0.62*543,1044-0.62*963)
    L['arm_r']=warp('arm_right',0.8,-12.2,304)
    L['arm_l']=warp('arm_right',0.8,-12.2,304,flip=True)
    L['eye_white']=warp('eye_white',*pair_T('eye_white',[(441,366),(626,366)],g('ew_w',70)))
    L['iris']=warp('iris',*pair_T('iris',[(442,360),(622,360)],g('iris_w',44)))
    L['eyelash']=warp('eyelash',*pair_T('eyelash',[(423.5,346),(645,346)],g('lash_w',118)))
    L['eyebrow']=warp('eyebrow',*pair_T('eyebrow',[(440,292),(625,292)],g('brow_w',95)))
    L['mouth']=warp('mouth_closed',*single_T('mouth_closed',(532,481),g('mouth_w',62)))
    L['mouth_open']=warp('mouth_open',*single_T('mouth_open',(532,488),g('mouth_open_w',58)))
    L['eye_close']=warp('eye_closed',*pair_T('eye_closed',[(425,362),(645,362)],100))
    L['nose']=warp('nose',*single_T('nose',(536,414),g('nose_w',17)))
    # ---- tweaks
    # neck: fade out below y=640 (1x coords), so chest comes from the torso layer
    yy=np.arange(H)[:,None]/S
    fade=np.clip((690-yy)/60.0,0,1)
    L['neck'][...,3]=(L['neck'][...,3]*fade).astype(np.uint8)
    for k,dv in (('face',(0,7,6)),('neck',(0,8,5))):
        rgb=L[k][...,:3].astype(np.float32)+np.array(dv,np.float32); L[k][...,:3]=np.clip(rgb,0,255).astype(np.uint8)
    # arms: tone down saturation a bit
    for k in ('arm_r','arm_l'):
        rgb=L[k][...,:3].astype(np.float32); lum=rgb.mean(2,keepdims=True)
        L[k][...,:3]=np.clip(lum+(rgb-lum)*g('arm_sat',0.85),0,255).astype(np.uint8)
    # mouth: recolour to soft rose-brown keeping alpha shape
    for k in ('mouth',):
        a=L[k][...,3:4].astype(np.float32); col=np.array(g('mouth_rgb',[176,104,108]),np.float32)
        L[k][...,:3]=np.clip(col,0,255).astype(np.uint8)
    # nose: keep only the bright core as a soft white diamond
    n_=L['nose']; lum=n_[...,:3].astype(np.float32).mean(2)
    core=np.clip((lum-215)/30.0,0,1)*(n_[...,3]/255.)
    n_[...,:3]=255; n_[...,3]=(core*g('nose_a',0.8)*255).astype(np.uint8)
    # eyelash: deepen
    e=L['eyelash'][...,:3].astype(np.float32)*g('lash_dark',0.82); L['eyelash'][...,:3]=np.clip(e,0,255).astype(np.uint8)
    json.dump({k:int((v[...,3]>0).sum()) for k,v in L.items()},open(f'{out_prefix}_counts.json','w'))
    # composite (stack order)
    order=['back_hair','arm_r','arm_l','torso','neck','face','nose','eye_white','iris','eyelash','eyebrow','mouth','collar','bow','front_hair']
    c=Image.new('RGBA',(W,H),(255,255,255,255))
    for n in order: c.alpha_composite(Image.fromarray(L[n],'RGBA'))
    c.save(f'{out_prefix}_composite.png')
    # PSD
    layers=[('back hair',L['back_hair']),('handwear-r',L['arm_r']),('handwear-l',L['arm_l']),('topwear',L['torso']),('neck',L['neck']),('face',L['face']),('nose',L['nose'])]
    for nm,key in [('eyewhite','eye_white'),('irides','iris'),('eyelash','eyelash'),('eyebrow','eyebrow')]:
        r,l=split_pair(L[key]); layers+=[(nm+'-r',r),(nm+'-l',l)]
    layers+=([('mouth close',L['mouth']),('mouth open',L['mouth_open'])] if g('mouth_mode','single')=='pair' else [('mouth',L['mouth'])])
    layers+=[('neckwear 1',L['collar']),('neckwear 2',L['bow']),('front hair',L['front_hair'])]
    write(layers,(W,H),f'{out_prefix}.psd')
    np.savez_compressed(f'{out_prefix}_extra.npz',mouth_open=L['mouth_open'],eye_close=L['eye_close'])
    return L
if __name__=='__main__':
    S=int(sys.argv[1]); mode=sys.argv[2]; run(S,mode,sys.argv[3])
