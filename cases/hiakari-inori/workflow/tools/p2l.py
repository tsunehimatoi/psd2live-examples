import sys,json,time
sys.path.insert(0,'/workspace/notes'); import mcp_client as c
c.rpc("initialize",{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"t","version":"1"}}); c.rpc("notifications/initialized",notif=True)
def st():
    d=c.call('workspace_inspect',{'request':{'scope':'project'}})['data']; return d['project_id'],d['state']
def job(tool,op,req,wait=600):
    r=c.call(tool,{'op':op,'request':req})
    d=r.get('data',r) if isinstance(r,dict) else r
    t0=time.time()
    while isinstance(d,dict) and d.get('terminal') is False and time.time()-t0<wait:
        time.sleep(3); d=c.call('job',{'op':'get','request':{'id':d['id']}}); d=d.get('data',d)
    return r if not isinstance(d,dict) else d
if __name__=='__main__':
    pass
