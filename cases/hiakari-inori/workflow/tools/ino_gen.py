import subprocess, sys, os, json, concurrent.futures as cf
D='/workspace/art/inori'
HEAD=f'{D}/head_1.png'; BODY=f'{D}/master_1.png'
TPL=("Use your image generation/editing tool with the reference image {ref} (open and look at it). Produce ONE image containing ONLY: {part}. "
"Rules: the output canvas has the same aspect ratio and the SAME framing as the reference, and the element must sit at exactly the same position, same size and same scale as in the reference (pixel-aligned, as if everything else were deleted from the same picture). "
"This is a Live2D layer: paint in naturally any part of the element that is hidden behind other things in the reference, so the element is complete. "
"Pure flat chroma-green background #00FF00 everywhere else; no shadows, no gradient, no text, no other characters or objects, do not recolor, keep the exact same art style, colors and details. "
"Save it as {out} (PNG) and print the path.")
P={
 'back_hair':(HEAD,"the hair mass BEHIND the head and shoulders (the long white hair with red gradient tips that lies behind the head, neck and shoulders), no face, no skin, no ears, no bangs, no front locks, no braid, no twin-tail, no mask, no ornaments; fill the area hidden behind the head and neck with continuous hair"),
 'ear_L':(HEAD,"the fox ear on the viewer's LEFT of the head (white fur outside with red tip, pink inside), complete including the root hidden under the hair, nothing else"),
 'ear_R':(HEAD,"the fox ear on the viewer's RIGHT of the head (white fur, red tip, pink inside) including its gold bell earring, complete including the root hidden under hair and mask, nothing else"),
 'face_base':(HEAD,"the bald face skin only: forehead, temples, cheeks (keep the blush), chin; complete full face oval with the parts hidden by hair filled in; no eyes, no eyebrows, no nose, no mouth, no hair, no ears, no neck, no clothing"),
 'neck':(HEAD,"the neck, collarbone and upper chest skin only, with the neck extended upward as a complete column behind the jaw (flat horizontal top edge hidden behind the chin, soft chin shadow); no face, no hair, no choker, no clothing"),
 'eye_white':(HEAD,"only the two eye whites (sclera shapes with their soft shading) of both eyes, no iris, no lashes, no brows"),
 'iris':(HEAD,"only the two irises as COMPLETE circles including the part hidden under the eyelids (viewer's-left gold, viewer's-right crimson), with highlights and pupils, no eye white, no lashes"),
 'eyelash':(HEAD,"only the upper eyelashes and eyeliner of both eyes (dark), no iris, no eye white, no brows"),
 'eyebrow':(HEAD,"only the two eyebrows, fully visible (including the part covered by bangs), nothing else"),
 'nose':(HEAD,"only the tiny nose (the small nose highlight/line) at the same place, nothing else"),
 'mouth':(HEAD,"only the closed gentle-smile mouth/lips at the same place, nothing else"),
 'mouth_open':(HEAD,"only an open smiling mouth (teeth and tongue visible), same position, size and style as the closed smile mouth in the reference, nothing else"),
 'front_hair':(HEAD,"only the front hair: the diagonal-parted bangs and the side locks hanging in front of the face and shoulders, and the hair parting on top; no ahoge, no braid, no twin-tail, no ears, no mask, no ornaments, no face skin; complete strands (parts hidden behind the face are not needed)"),
 'ahoge':(HEAD,"only the single ahoge (the lone curled antenna hair strand on top of the head), complete with its root"),
 'mask':(HEAD,"only the white-and-red fox half-mask on the viewer's right side of the head with its red tassels and cord, complete including parts hidden by hair"),
 'ribbon':(HEAD,"only the red knot ornament with the gold bell and red tassels on the viewer's LEFT side of the head, complete including hidden parts"),
 'choker':(HEAD,"only the black choker with its small gold bell and the red cross chest cords around the neck/chest, complete band including the hidden back portion"),
 'braid':(BODY,"only the long braid (white hair with red gradient) hanging over the chest on the viewer's LEFT of the character, from the shoulder down to its tip with the red tie, complete including parts hidden under other items"),
 'twintail':(BODY,"only the long low twin-tail on the viewer's RIGHT of the character, from the red hair tie near the shoulder down to its tip, complete including parts hidden"),
 'tail_L':(BODY,"only the large fluffy white fox tail with red tip on the viewer's LEFT behind the character, complete including the part hidden behind the body, no body"),
 'tail_R':(BODY,"only the large fluffy white fox tail with red tip on the viewer's RIGHT behind the character, complete including the part hidden behind the body, no body"),
 'tail_C':(BODY,"only the third (middle/back) fluffy white fox tail with red tip that is behind the body between the two big tails (mostly hidden in the reference); paint it complete as a full tail in the same style, hanging down, same scale as the other tails, no body"),
 'sleeve_L':(BODY,"only the large detached wide white sleeve with red lining, gold patterns, red tassels and the cord on the viewer's LEFT arm, complete including the inside hidden by the arm; no arm skin, no hand"),
 'sleeve_R':(BODY,"only the large detached wide white sleeve with red lining, gold patterns, red tassels and the cord on the viewer's RIGHT arm, complete including the inside hidden by the arm; no arm skin, no hand"),
 'arm_L':(BODY,"only the bare arm (shoulder, upper arm, forearm, open hand) of the viewer's LEFT arm as skin, complete including the part hidden inside the sleeve and under the strap; no sleeve, no clothing, no jewelry other than skin"),
 'arm_R':(BODY,"only the bare arm (shoulder, upper arm, forearm, open hand) of the viewer's RIGHT arm as skin, complete including the part hidden inside the sleeve and under the strap; no sleeve, no clothing"),
 'top':(BODY,"only the white modified miko top (bodice) with its red trim, gold patterns, chest cord with ring, black buckled shoulder straps and the bare chest skin inside the neckline, complete; no head, no neck choker, no arms, no sleeves, no skirt, no obi"),
 'obi':(BODY,"only the wide red obi waist sash with its big bow, gold bell, tassels and cords hanging at the side, complete including the hidden back part of the sash; nothing else"),
 'skirt':(BODY,"only the red-to-white gradient pleated micro skirt together with its translucent white tulle overskirt (render the tulle as it looks over white), and the red/black garter belts attached to it, complete including the part hidden behind the obi; no legs"),
 'legwear':(BODY,"only the pair of black over-the-knee stockings with red garter straps and their thigh skin gap (zettai ryouiki skin band at the top), complete full legs including the parts hidden under the skirt and inside the boots; no skirt, no boots"),
 'boots':(BODY,"only the pair of white-soled red-strapped platform short boots with gold tassels, complete including the parts hidden under the stockings; nothing else"),
}
def run(name):
    ref,part=P[name]; out=f'{D}/gen/{name}.png'
    if os.path.exists(out): return name,'exists'
    prompt=TPL.format(ref=ref,part=part,out=out)
    for t in range(2):
        r=subprocess.run(['codex','exec','--skip-git-repo-check','-s','workspace-write','-C',D,prompt],stdin=subprocess.DEVNULL,capture_output=True,text=True,timeout=900)
        open(f'{D}/gen/{name}.log','w').write(r.stdout[-2000:]+r.stderr[-500:])
        if os.path.exists(out): return name,'ok'
    return name,'FAIL'
if __name__=='__main__':
    names=sys.argv[2:] or list(P); n=int(sys.argv[1])
    with cf.ThreadPoolExecutor(n) as ex:
        for nm,st in ex.map(run,names): print(nm,st,flush=True)
