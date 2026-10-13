# Prompt lines embedded in /workspace/tools (*.py, *.sh)

See tools/ for full context.

## /workspace/tools/hf_edit.py

```
        return first(c.predict(input_image=f,prompt=a.prompt,seed=a.seed,randomize_seed=False,guidance_scale=2.5,steps=a.steps or 28,api_name='/infer'))
        return first(c.predict(images=[{'image':f}],prompt=a.prompt,seed=a.seed,randomize_seed=False,true_guidance_scale=1.0,num_inference_steps=a.steps or 4,height=H,width=W,rewrite_prompt=False,num_images_per_prompt=1,api_name='/infer'))
        return first(c.predict(images=[{'image':f}],prompt=a.prompt,seed=a.seed,randomize_seed=False,true_guidance_scale=1.0,num_inference_steps=a.steps or 4,height=H,width=W,rewrite_prompt=False,api_name='/infer'))
```

## /workspace/tools/ino_gen.py

```
    prompt=TPL.format(ref=ref,part=part,out=out)
```

## /workspace/tools/try_edit.py

```
    if 'Kontext' in s: r=c.predict(input_image=handle_file(img),prompt=p,seed=0,randomize_seed=False,guidance_scale=2.5,steps=28,api_name='/infer')
    elif 'Qwen-Image-Edit-Fast' in s: r=c.predict(image=handle_file(img),prompt=p,seed=0,randomize_seed=False,true_guidance_scale=1.0,num_inference_steps=8,rewrite_prompt=False,api_name='/infer')
    else: r=c.predict(images=[{'image':handle_file(img)}],prompt=p,seed=0,randomize_seed=False,true_guidance_scale=1.0,num_inference_steps=4,height=720,width=1280,rewrite_prompt=False,api_name='/infer')
```
