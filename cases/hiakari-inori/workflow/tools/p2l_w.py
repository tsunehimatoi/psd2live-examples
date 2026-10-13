import sys,json,time,uuid
sys.path.insert(0,'/workspace/tools'); from p2l import c,st,job
R=lambda:str(uuid.uuid4())
def W(r):
    d=r.get('data',r) if isinstance(r,dict) else r
    t0=time.time()
    while isinstance(d,dict) and d.get('terminal') is False and time.time()-t0<900:
        d=c.call('job',{'op':'wait','request':{'id':d['id'],'timeout_ms':30000}}); d=d.get('data',d)
    return d
