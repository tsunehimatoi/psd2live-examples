import sys,json,time,uuid
sys.path.insert(0,'/workspace/tools'); from p2l import c,st,job
R=lambda:str(uuid.uuid4())
def W(r):
    d=r.get('data',r) if isinstance(r,dict) else r
    t0=time.time()
    while isinstance(d,dict) and d.get('terminal') is False and time.time()-t0<900:
        d=c.call('job',{'op':'wait','request':{'id':d['id'],'timeout_ms':30000}}); d=d.get('data',d)
    return d
pid,s=st()
d=W(c.call('project',{'op':'import_psd','request':{'path':'/workspace/art/inori/inori_v4_noskirt.psd','discard_unsaved':True,'request_id':R(),'project_id':pid,'state':s}}))
print('import',str(d)[:400])
pid,s=st()
for T,P in [('ArtMeshTail','ParamTailA'),('ArtMeshTail2','ParamTailB'),('ArtMeshTail3','ParamTailC')]:
    r=c.call('swing',{'op':'put','request':{'id':'swing_'+P,'name':'swing '+P,'state':s,'targets':[T],'motions':[{'kind':'lateral','parameters':[P],'magnitude':0.25,'lift':0.04,'softness':0.6,'zoom':0.0,'parallel':0.7,'physics':{'length':16.0,'mobility':0.92,'delay':0.9,'acceleration':1.3,'output_scale':1.6}}]}})
    print(P,str(r)[:300]); pid,s=st()
r=W(c.call('physics',{'op':'put','request':{'id':'PhysicsTails','name':'尾巴摆动','state':s,'enabled':True,
  'inputs':[{'parameter':'ParamAngleX','weight':40,'type':'x'},{'parameter':'ParamBodyAngleX','weight':60,'type':'x'},{'parameter':'ParamBodyAngleZ','weight':50,'type':'angle'}],
  'outputs':[{'parameter':'ParamTailA','vertex':1,'scale':1.0},{'parameter':'ParamTailB','vertex':1,'scale':1.0,'reflect':True},{'parameter':'ParamTailC','vertex':1,'scale':0.7}],
  'segments':[{'length':18.0,'mobility':0.85,'delay':0.9,'acceleration':1.2}]}}))
print('phys',str(r)[:300])
pid,s=st()
r=c.call('swing',{'op':'put','request':{'id':'swing_ParamLegSway','name':'腿部摆动 ParamLegSway','state':s,'targets':['DeformLegs'],'kind':'lateral','parameters':['ParamLegSway'],'magnitude':0.04,'softness':0.8,'parallel':0.3,'physics_enabled':False}})
print('legs',str(r)[:600])
