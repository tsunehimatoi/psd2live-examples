import sys,time
from gradio_client import Client, handle_file
s=sys.argv[1]; img='/workspace/art/head_H0.jpg'; p='change background to flat green #00FF00'
t=time.time()
try:
    c=Client(s)
    if 'Kontext' in s: r=c.predict(input_image=handle_file(img),prompt=p,seed=0,randomize_seed=False,guidance_scale=2.5,steps=28,api_name='/infer')
    elif 'Qwen-Image-Edit-Fast' in s: r=c.predict(image=handle_file(img),prompt=p,seed=0,randomize_seed=False,true_guidance_scale=1.0,num_inference_steps=8,rewrite_prompt=False,api_name='/infer')
    else: r=c.predict(images=[{'image':handle_file(img)}],prompt=p,seed=0,randomize_seed=False,true_guidance_scale=1.0,num_inference_steps=4,height=720,width=1280,rewrite_prompt=False,api_name='/infer')
    print('OK',str(r)[:300])
except Exception as e: print('ERR',type(e).__name__,str(e)[:300])
print(s,round(time.time()-t,1))
