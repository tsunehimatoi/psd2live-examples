import json, sys, numpy as np, cv2
from PIL import Image
W,H=1086,1448
def place(k,fits):
    f=fits.get(k); im=np.asarray(Image.open(f"keyed_head3/{k}.png").convert('RGBA')).copy()
    if f is None: return im
    a=im[...,3:4]/255.; pm=np.concatenate([im[...,:3]*a,im[...,3:4]],2).astype(np.float32)
    out=cv2.warpAffine(pm,np.float32(f),(W,H),flags=cv2.INTER_CUBIC)
    al=np.clip(out[...,3:4],0,255); rgb=np.where(al>1e-3,out[...,:3]/np.maximum(al/255.,1e-3),0)
    return np.concatenate([np.clip(rgb,0,255),al],2).astype(np.uint8)
order=['back_hair','neck','face_base','eye_white','iris','eyelash','eyebrow','mouth','front_hair']
if __name__=='__main__':
    fits=json.load(open(sys.argv[2])) if len(sys.argv)>2 else {}
    c=Image.new('RGBA',(W,H),(255,255,255,255))
    for k in order: c.alpha_composite(Image.fromarray(place(k,fits),'RGBA'))
    tag=sys.argv[1]; c.save(f'headcomp3_{tag}.png')
    m=Image.open('head_closeup_3b.png').convert('RGB'); box=(150,250,950,850)
    B=Image.new('RGB',(1600,600)); B.paste(m.crop(box),(0,0)); B.paste(c.convert('RGB').crop(box),(800,0)); B.save(f'headcmp3_{tag}.png')
    Image.blend(m,c.convert('RGB'),.5).crop(box).save(f'headbl3_{tag}.png')
