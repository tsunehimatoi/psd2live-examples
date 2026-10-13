import sys, json, base64
sys.path.insert(0,'/workspace/notes')
import mcp_client as c
c.rpc("initialize",{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"t","version":"1"}})
c.rpc("notifications/initialized",notif=True)
name=sys.argv[1]; args=json.loads(sys.argv[2]); out=sys.argv[3]
r=c.rpc("tools/call",{"name":name,"arguments":args})["result"]
k=0
for it in r.get("content",[]):
    if it.get("type")=="image":
        open(f"{out}_{k}.png","wb").write(base64.b64decode(it["data"])); k+=1
    elif it.get("type")=="text": print(it["text"][:800])
print("images",k)
