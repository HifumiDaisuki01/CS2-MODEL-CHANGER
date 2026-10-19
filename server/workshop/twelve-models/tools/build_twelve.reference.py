from pathlib import Path
import json,sys,hashlib,zipfile,shutil,subprocess,re,struct
B=Path('/root/model-system-work');R=B/'repo';W=B/'twelve-work';D=W/'CS2-TwelveModels-Workshop';ADDON='keran_five_models';OUT=D/'addon/game/csgo_addons'/ADDON;CONTENT=D/'addon/content/csgo_addons'/ADDON;REPORT=D/'reports';ORIG=W/'originals';FIX=W/'repaired';LIME=next((B/'lime-e-compiled-review/extracted/LIME-E-Release-v0.5.0/addon/game/csgo_addons').iterdir());PUBLIC=R/'server/workshop/twelve-models'
sys.path[:0]=[str(R/'server/tools'),str(R/'server/ag2-port/tools')];from pack_workshop import pack;from verify_vpk import inspect;from port_projects import refs,safe_relative
for p in [OUT,CONTENT,REPORT,D/'configs',PUBLIC]:p.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(W/'repaired-four.zip') as z:
 for n in z.namelist():safe_relative(n);p=FIX/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(n))
# Explicit menu IDs and unchanged resource names.
MODELS={
 'aluona':('Aluona（阿洛娜）','characters/models/aluona/aluona.vmdl',False),
 'myers':('Myers（新版）','characters/models/exg/myers/myers.vmdl',False),
 'pardofelis':('Pardofelis（帕朵菲莉丝）','characters/models/exg/pardofelis/pardofelis.vmdl',False),
 'vrc_lime':('VRC Lime','characters/models/exg/vrc_lime/vrc_lime.vmdl',False),
 'huohuo':('Huohuo（藿藿）','characters/models/exg/honkai_starrail_huohuo/honkai_starrail_huohuo.vmdl',False),
 'lime_e':('Lime E','characters/models/exg/chrisan/lime_e/lime_e.vmdl',False),
 'chikari':('Chikari','characters/models/chikari/chikari.vmdl',False),
 'serina':('Serina','characters/models/exg/serina/serina.vmdl',False),
 'baizhouzi':('Baizhouzi（白洲梓）','characters/models/cs2ze/baizhouxin/baizhouxin.vmdl',True),
 'hifumi':('Hifumi（日富美）','characters/models/exg/hihumi/hihumi.vmdl',True),
 'mingchao_feibi':('鸣潮·菲比','characters/exg/10089/10089.vmdl',True),
 'chiffon_fox':('Chiffon Fox','characters/models/chiffon_fox/chiffon_fox.vmdl',True)}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def blocks(p):
 b=p.read_bytes();table=8+struct.unpack_from('<I',b,8)[0];num=struct.unpack_from('<I',b,12)[0];return [(b[q:q+4].decode(),hashlib.sha256(b[q+4+struct.unpack_from('<I',b,q+4)[0]:q+4+struct.unpack_from('<I',b,q+4)[0]+struct.unpack_from('<I',b,q+8)[0]]).hexdigest()) for q in range(table,table+num*12,12)]
proof=[]
for id,(_,path,changed) in MODELS.items():
 if not changed:continue
 report=json.loads((FIX/'reports'/(id+'.json')).read_text());assert report['StaticRepairPassed'] and report['StructuredKV3Editing'] and not report['Recompiled'];assert report['InputSHA256']==sha(ORIG/(path+'_c')) and report['OutputSHA256']==sha(FIX/'resources'/(path+'_c'))
 before=blocks(ORIG/(path+'_c'));after=blocks(FIX/'resources'/(path+'_c'));assert len(before)==len(after)
 for a,b in zip(before,after):assert a[0]==b[0] and (a[0] in ['DATA','RERL'] or a[1]==b[1])
 shutil.copy2(FIX/'reports'/(id+'.json'),REPORT/(id+'-structured-repair.json'));proof.append(id)
assert len(proof)==4
for n in ['independent-gltf-comparison.json','windows-repair-tests.json']:shutil.copy2(FIX/'reports'/n,REPORT/n)
comparison=json.loads((REPORT/'independent-gltf-comparison.json').read_text(encoding='utf-8-sig'));assert len(comparison)==4 and all(x['MeshSkeletonAnimationBinaryIdentical'] for x in comparison)
base=set((R/'server/tools/base-resources-confirmed.txt').read_text().splitlines())|set((B/'ag2-work/reports/base-resources-confirmed.txt').read_text().splitlines());roots={v[1]+'_c' for v in MODELS.values()};queue=[(v[1]+'_c','lime' if k=='lime_e' else 'new') for k,v in MODELS.items()];seen=set();included={};official=set();fold={};edges={}
while queue:
 name,source=queue.pop();safe_relative(name)
 if name in base and name not in roots:official.add(name);continue
 key=(name,source)
 if key in seen:continue
 seen.add(key)
 if source=='lime':p=LIME/name
 else:p=FIX/'resources'/name if (FIX/'resources'/name).is_file() else ORIG/name
 assert p.is_file(),('Missing resource',name,source)
 h=sha(p)
 if name.lower() in fold:assert fold[name.lower()]==name,('Case collision',name)
 fold[name.lower()]=name
 if name in included:assert included[name]==h,('Conflicting resource bytes',name)
 included[name]=h;out=OUT/name;out.parent.mkdir(parents=True,exist_ok=True)
 if not out.exists():shutil.copy2(p,out)
 assert sha(out)==h
 dependencies=refs(p);edges[name]=dependencies;queue.extend((r,source) for r in dependencies)
assert not any('dujiaoshou' in n or '/xinghui/' in n for n in included)
assert included[MODELS['myers'][1]+'_c']=='f155aba7d3e9da2719ae2c43710e7be1d1c79a1dd716e62147e0cc603822c6c5'
assert included[MODELS['lime_e'][1]+'_c']=='981f1d46fa80ad004972d2e04276ed6fde80208993191d47a832d4bf67ca778d'
print('Dependency closure:',len(included),'resources,',len(official),'official refs',flush=True)
cli=str(B/'vrf/Source2Viewer-CLI');parsed=[];models=[];missing=[];canonical=dict(line.split() for line in (R/'server/ag2-port/tools/vendor/canonical_skeleton.txt').read_text().splitlines() if len(line.split())==2)
for index,name in enumerate(sorted(included)):
 p=OUT/name;r=subprocess.run([cli,'-i',str(p),'-b','DATA'],capture_output=True,text=True);assert r.returncode==0,(name,r.stderr);parsed.append(name)
 if (index+1)%100==0:print('Parsed',index+1,'resources',flush=True)
 if name not in roots:continue
 id=next(k for k,v in MODELS.items() if v[1]+'_c'==name);t=r.stdout;assert '.vanmgrph' not in t and '/animsets/' not in t
 for required in ['animation/graphs/worldmodel/worldmodel.vnmgraph_c','animation/graphs/viewmodel/viewmodel.vnmgraph_c','animation/skeletons/characters/worldmodel.vnmskel_c','animation/skeletons/characters/viewmodel.vnmskel_c']:assert required in edges[name],(id,required)
 if MODELS[id][2]:assert 'character_arm_config =' not in t
 arr=lambda key:re.search(r'\b'+key+r'\s*=\s*\[(.*?)\]',t,re.S)[1]
 bones=re.findall(r'"([^"]+)"',arr('m_boneName'));parents=[int(v) for v in re.findall(r'-?\d+',arr('m_nParent'))];assert len(bones)==len(parents)
 for bone in list(canonical)[:24]:
  assert bone in bones;(i:=bones.index(bone));parent='-' if parents[i]<0 else bones[parents[i]];assert parent==canonical[bone],(id,bone,parent)
 groups=re.findall(r'"([^"]+)"',arr('m_meshGroups'));masks=[int(v) for v in re.findall(r'\d+',arr('m_refMeshGroupMasks'))];lod=[int(v) for v in re.findall(r'\d+',arr('m_refLODGroupMasks'))];fp=next(i for i,g in enumerate(groups) if g.endswith('#&firstperson_default'));indices=[i for i,m in enumerate(masks) if m&(1<<fp)];assert indices and all(lod[i]&1 for i in indices)
 models.append({'Id':id,'Name':MODELS[id][0],'Path':MODELS[id][1],'SHA256':included[name],'Bones':len(bones),'AG2AndCore24HierarchyPassed':True,'FirstPersonMeshIndices':indices,'FirstPersonGeometryPresent':True,'StructuredArmReferenceCleanup':MODELS[id][2],'PackageGameTested':False})
print('All',len(parsed),'resources parsed; 12 primary model checks passed',flush=True)
config={'Models':{k:{'name':v[0],'path':v[1],'permissions':[],'permissionsOr':[],'side':'All','disableleg':False,'hideinmenu':False} for k,v in MODELS.items()}};dump(D/'configs/PlayerModelChanger.merge.json',config);dump(D/'configs/resource-catalog.template.json',{'Archives':{},'Models':sorted(v[1] for v in MODELS.values()),'Note':'Regenerate archive paths/hashes from the actual Steam download when deploying. This template is not a live catalog.'})
info='"AddonInfo"\n{\n "addonname" "keran_five_models"\n "addontitle" "Keran Twelve Player Models"\n "addonversion" "2.0"\n "addonauthor" "HifumiDaisuki01"\n "addondescription" "Twelve CS2 player model resources. Resource package, not a playable map."\n}\n';(OUT/'addoninfo.txt').write_text(info);(CONTENT/'addoninfo.txt').write_text(info)
report={'PrimaryPlayerModels':12,'Models':models,'ResourceCount':len(included),'ResourceBytes':sum((OUT/n).stat().st_size for n in included),'RuntimeFiles':included,'OriginalGameReferences':sorted(official),'MissingDependencies':missing,'PathConflicts':[],'StructuredRepairs':proof,'RepairsPerformedOnCurrentWindows':True,'ValveCompilerUsedForTheseFour':False,'UnrelatedResourceBlocksByteIdenticalForFour':True,'IndependentGLTFGeometrySkinAnimationBinaryIdenticalForFour':True,'AllCompiledResourcesParsed':True,'MyersUsesLatestPack':True,'LimeEUsesV050CompiledRelease':True,'ExcludedPlayers':['dujiaoshou','xinghui'],'WorkshopPublished':False,'WorkshopMounted':False,'ProductionServerChanged':False,'GameValidationForThisPackage':False,'PriorUserReports':{'AluonaKnownWorking':True,'HuohuoVrcLimePardofelisFirstPersonLegsConfirmedByUser':True,'LimeEArmsWindowsConfirmedByUser':True},'InternalAddonDirectoryRetained':'keran_five_models'};dump(REPORT/'resource-review.json',report);dump(D/'configs/expected-project-resources.json',included)
pack(OUT,D/'workshop-upload');v=inspect(D/'workshop-upload/pak01_dir.vpk');assert {e['Path'] for e in v['Entries']}==set(included)|{'addoninfo.txt'}
for e in v['Entries']:
 if e['Path'] in included:assert e['SHA256']==included[e['Path']]
dump(REPORT/'vpk-validation.json',v);r=subprocess.run([cli,'-i',str(D/'workshop-upload/pak01_dir.vpk'),'--vpk_verify'],capture_output=True,text=True);(REPORT/'source2viewer-vpk-verify.log').write_text(r.stdout+r.stderr);assert r.returncode==0 and 'Success.' in r.stdout
shutil.copy2(B/'mika-work/MIKA-dujiaoshou-Workshop/Verify-Package.ps1',D/'Verify-Package.ps1')
# Add final docs and checks separately before sealing the archive.
dump(W/'build-result.json',{'ResourceCount':len(included),'VPKEntries':len(v['Entries']),'PrimaryPlayerModels':12,'ResourceBytes':report['ResourceBytes'],'StaticChecksPassed':True});print('READY',json.dumps(json.loads((W/'build-result.json').read_text())),flush=True)
