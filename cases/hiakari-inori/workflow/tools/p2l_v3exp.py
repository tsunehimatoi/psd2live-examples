import sys,uuid,os
sys.path.insert(0,'/workspace/tools'); from p2l_w import c,st,W,R
D='/workspace/deliver_inori'
pid,s=st()
print('save',str(W(c.call('project',{'op':'save_as','request':{'path':D+'/hiakari_inori_v3.psd2live','request_id':R(),'project_id':pid,'state':s}})))[:200])
for tgt,out in [('moc3','export_cubism'),('vtube-studio','export_vtube_studio'),('webm','preview')]:
    os.makedirs(D+'/'+out+'_v3tmp',exist_ok=True); pid,s=st()
    r=W(c.call('workspace_call',{'operation':'project_export_target','request':{'request_id':R(),'state':s,'target':tgt,'output_directory':D+'/'+out+'_v3tmp'},'wait_ms':30000}))
    print(tgt,str(r)[:400])
