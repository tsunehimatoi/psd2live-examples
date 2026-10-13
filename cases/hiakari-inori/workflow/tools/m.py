import sys, json
sys.path.insert(0,'/workspace/notes')
import mcp_client as c
c.rpc("initialize",{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"t","version":"1"}})
c.rpc("notifications/initialized",notif=True)
name=sys.argv[1]; args=json.loads(sys.argv[2]) if len(sys.argv)>2 else {}
r=c.call(name,args)
s=json.dumps(r,ensure_ascii=False)
print(s[:int(sys.argv[3]) if len(sys.argv)>3 else 6000])
