import os, sys, numpy as np
from PIL import Image
os.chdir('/workspace/art/inori')
ORDER=['tail_C','tail_L','tail_R','back_hair','ear_L','ear_R','legwear','boots','skirt','neck','arm_L','arm_R','top','obi','sleeve_L','sleeve_R','choker','face_base','nose','eyebrow','mouth','front_hair','eye_white','iris','eyelash','ahoge','ribbon','mask','braid','twintail']
def comp(d='final',bg='white'):
    c=Image.new('RGBA',(2048,3072),bg)
    for k in ORDER: c.alpha_composite(Image.open(f'{d}/{k}.png'))
    return c
if __name__=='__main__':
    c=comp(); c.convert('RGB').save('comp_full.png')
    c.convert('RGB').resize((683,1024)).save('comp_full_s.png'); c.convert('RGB').crop((500,0,1500,1100)).save('comp_head_zoom.png')
