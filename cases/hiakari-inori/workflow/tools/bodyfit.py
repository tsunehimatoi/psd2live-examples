import sys, json, numpy as np, cv2
sys.path.insert(0,'/workspace/tools')
from ecc_body import *
def init_s(layer_pt, master_pt, s): return s, master_pt[0]-s*layer_pt[0], master_pt[1]-s*layer_pt[1]
jobs={
 'topwear':('topwear',(260,765,420,1015),init_s((512.5,716.5),(512.5,425),.47),(380,650,280,570)),
 'collar_front':('collar_front',(262,765,345,585),init_s((513,464),(513,375),.53),(370,660,270,480)),
 'bow':('bow',(285,740,480,990),init_s((511,733),(514,428),.35),(430,600,320,540)),
 'skirt':('skirt',(250,775,515,945),init_s((512,932),(511,835),.7),(310,710,540,850)),
 'arm_right':('arm_right',(90,560,235,1300),init_s((323,1290),(325,822),.5),(215,440,280,830)),
 'arm_left':('arm_left',(540,825,265,890),init_s((682,877),(700,822),.88),(580,830,280,830)),
 'shoes':('shoes',(385,640,1255,1525),init_s((511,1515),(511.5,1511),.75),(410,615,1340,1530)),
}
out={}
for k,(nm,box,init,reg) in jobs.items():
    cc,F=refine(nm,box,*init,reg,iters=300)
    if F is None or isinstance(F,str):
        print(k,'ECC failed'); s_,tx_,ty_=init; F=np.array([[s_,0,tx_],[0,s_,ty_]]); cc=-1
    print(k,round(cc,3),np.round(F,3).tolist())
    out[k]=dict(layer=nm,box=box,init=init,cc=cc,F=np.asarray(F).tolist())
json.dump(out,open('bodyfit.json','w'),indent=1)
