import sys, json, numpy as np, cv2
sys.path.insert(0,'/workspace/tools')
from ecc import *
def init_c(box,target,s):  # box center -> target center with scale s
    x0,x1,y0,y1=box; cx,cy=(x0+x1)/2,(y0+y1)/2
    return s, target[0]-s*cx, target[1]-s*cy
jobs={
 'iris_L':('iris',(130,420,520,815),(0.27,345.82,374.25),(350,490,490,625)),
 'iris_R':('iris',(655,945,520,815),(0.27,453.8,368.25),(600,740,490,620)),
 'eye_white_L':('eye_white',(322,472,512,606),init_c((328,468,518,600),(408,557),.89),(340,490,500,620)),
 'eye_white_R':('eye_white',(615,764,512,605),init_c((621,758,518,599),(679,551),.88),(600,760,495,615)),
 'eyelash_L':('eyelash',(197,470,575,745),init_c((203,465,581,739),(386,545),.62),(290,490,480,610)),
 'eyelash_R':('eyelash',(620,885,572,744),init_c((626,879,578,738),(690,541),.58),(600,790,480,610)),
 'eyebrow_L':('eyebrow',(276,489,440,494),init_c((282,483,446,488),(396,454),.86),(290,520,425,490)),
 'eyebrow_R':('eyebrow',(597,810,440,494),init_c((603,804,446,488),(662,455),.8),(590,760,425,490)),

 'back_hair':('back_hair',(0,1086,0,1448),(0.97,10,0),(0,1086,0,1000)),
 'front_hair':('front_hair',(0,1086,0,1448),(0.97,10,0),(0,1086,0,1000)),
 'face_base':('face_base',(240,850,250,960),(0.88,574.5-0.88*544,808-0.88*949),(230,860,240,830)),
 'mouth':('mouth',(470,615,700,750),init_c((481,605,714,738),(556,728),.56),(500,620,690,770)),
 'mouth_open':('mouth_open',(445,640,690,800),init_c((456,631,698,789),(556,732),.56),(480,640,690,790)),
 'neck':('neck',(280,805,660,1180),(1.0,0,0),(250,860,700,1140)),
}
out={}
for k,(nm,box,init,reg) in jobs.items():
    mode=cv2.MOTION_TRANSLATION if nm in ('eye_white','eyebrow','mouth','mouth_open') else cv2.MOTION_AFFINE
    cc,F=refine(nm,box,*init,reg,mode=mode)
    if F is None or isinstance(F,str):
        print(k,'ECC failed',F); s_,tx_,ty_=init; F=np.array([[s_,0,tx_],[0,s_,ty_]]); cc=-1
    print(k,cc,None if F is None else np.round(F,3).tolist())
    out[k]=dict(layer=nm,box=box,init=init,cc=cc,F=None if F is None else F.tolist())
json.dump(out,open('headfit.json','w'),indent=1)
