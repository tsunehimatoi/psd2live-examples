import sys, numpy as np, cv2
from PIL import Image
from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer
def split_pair(rgba):
    a=rgba[...,3]; m=(a>20).astype(np.uint8); d=cv2.dilate(m,np.ones((31,31),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(d)
    idx=sorted(range(1,n),key=lambda i:-st[i,4])[:2]
    idx=sorted(idx,key=lambda i:cen[i][0])  # by x: first = screen-left = character right
    outs=[]
    for i in idx:
        o=rgba.copy(); o[...,3]=np.where(lab==i,o[...,3],0); outs.append(o)
    return outs  # [screen-left (char R), screen-right (char L)]
def write(layers, size, path):
    """layers: list of (name, RGBA uint8 array) bottom->top"""
    psd=PSDImage.new('RGBA',size)
    for name,arr in layers:
        a=arr[...,3]; ys,xs=np.where(a>0)
        if len(xs)==0: print('empty',name); continue
        x0,y0,x1,y1=xs.min(),ys.min(),xs.max()+1,ys.max()+1
        im=Image.fromarray(np.ascontiguousarray(arr[y0:y1,x0:x1]),'RGBA')
        psd.append(PixelLayer.frompil(im,psd,name,top=int(y0),left=int(x0)))
    psd.save(path); print('saved',path,len(layers))
