import sys,json,urllib.request,concurrent.futures as cf
qs=sys.argv[1:]
seen={}
for q in qs:
    for srt in ['likes','trendingScore']:
        try:
            d=json.load(urllib.request.urlopen(f'https://huggingface.co/api/spaces?search={q.replace(" ","%20")}&limit=60&sort={srt}&direction=-1&full=true',timeout=30))
        except Exception as e: print('err',q,e); continue
        for s in d: seen[s['id']]=s
def hw(s):
    r=s.get('runtime') or {}
    return r.get('stage'),(r.get('hardware') or {}).get('current')
for k,s in seen.items():
    st,h=hw(s)
    if st=='RUNNING' and h not in ('zero-a10g',None) and s.get('sdk')=='gradio': print(k,s.get('likes'),h)
print(len(seen))
