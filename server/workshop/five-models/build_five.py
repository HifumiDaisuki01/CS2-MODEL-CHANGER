from pathlib import Path
import sys,json,zipfile,hashlib,shutil,subprocess,re,collections
B=Path('/root/model-system-work'); REPO=B/'repo';W=B/'five-work-v1.1';NEW=W/'new-inputs';D=W/'CS2-FiveModels-Workshop';RES=D/'addon/game/csgo_addons/keran_five_models';REPORT=D/'reports';PUBLIC=REPO/'server/workshop/five-models'
sys.path[:0]=[str(REPO/'server/tools'),str(REPO/'server/ag2-port/tools')]
from port_projects import refs,safe_relative
from pack_workshop import pack
from verify_vpk import inspect
for p in [NEW,RES,REPORT,D/'configs',PUBLIC]:p.mkdir(parents=True,exist_ok=True)
for archive in [B/'new-three-inputs.zip',B/'new-myers-inputs.zip']:
 with zipfile.ZipFile(archive) as z:
  for n in z.namelist():
   safe_relative(n);p=NEW/n;data=z.read(n)
   if p.exists():assert p.read_bytes()==data,'Input resource collision: '+n
   p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
OLD=B/'mika-work/CS2-ThreeModels-Workshop/addon/game/csgo_addons/keran_three_models'
MODELS={
 'aluona':('Aluona（阿洛娜）','characters/models/aluona/aluona.vmdl',OLD),
 'myers':('Myers','characters/models/exg/myers/myers.vmdl',NEW),
 'pardofelis':('Pardofelis（帕朵菲莉丝）','characters/models/exg/pardofelis/pardofelis.vmdl',NEW),
 'vrc_lime':('VRC Lime','characters/models/exg/vrc_lime/vrc_lime.vmdl',NEW),
 'huohuo':('Huohuo（藿藿）','characters/models/exg/honkai_starrail_huohuo/honkai_starrail_huohuo.vmdl',NEW)}
base=set((REPO/'server/tools/base-resources-confirmed.txt').read_text().splitlines())|set((B/'ag2-work/reports/base-resources-confirmed.txt').read_text().splitlines())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
roots={v[1]+'_c' for v in MODELS.values()};queue=[(v[1]+'_c',v[2]) for v in MODELS.values()];seen=set();assets={};origin={};official=set();edges={};folded={}
while queue:
 name,source=queue.pop();safe_relative(name)
 if name in base and name not in roots:official.add(name);continue
 key=(name,str(source))
 if key in seen:continue
 seen.add(key);f=source/name
 if not f.is_file():raise ValueError('Missing custom dependency: '+name)
 digest=sha(f)
 if name.lower() in folded and folded[name.lower()]!=name:raise ValueError('Case collision: '+name)
 folded[name.lower()]=name
 if name in assets and assets[name]!=digest:raise ValueError('Conflicting resource bytes: '+name)
 target=RES/name;target.parent.mkdir(parents=True,exist_ok=True)
 if not target.exists():shutil.copy2(f,target)
 assert sha(target)==digest;assets[name]=digest;origin.setdefault(name,[]).append('existing-live-three-model-package' if source==OLD else 'desktop-new-model-pack')
 deps=refs(f);edges[name]=deps;queue.extend((n,source) for n in deps)
assert not any('dujiaoshou' in n.lower() for n in assets)
assert {n for n in assets if n.endswith('.vmdl_c')}==roots
assert assets['characters/models/aluona/aluona.vmdl_c']=='18954d150f6bad965c6d7449ca21632f6e7fa1b0270033f7a54eb4f7a712363a'
assert assets['characters/models/exg/myers/myers.vmdl_c']=='f155aba7d3e9da2719ae2c43710e7be1d1c79a1dd716e62147e0cc603822c6c5'
deployed=json.loads((REPO/'server/deployments/3822432137/reports/vpk-validation.json').read_text());deployed_hashes={e['Path']:e['SHA256'] for e in deployed['Entries']}
for id in ['aluona']:assert assets[MODELS[id][1]+'_c']==deployed_hashes[MODELS[id][1]+'_c']
print('Closure:',len(assets),'resources,',len(official),'official refs',flush=True)
viewer=str(B/'vrf/Source2Viewer-CLI');modelreports=[];parsed=[]
for n in sorted(assets):
 r=subprocess.run([viewer,'-i',str(RES/n),'-b','DATA'],capture_output=True,text=True);assert r.returncode==0,(n,r.stderr);parsed.append(n)
 if n not in roots:continue
 t=r.stdout;id=next(k for k,v in MODELS.items() if v[1]+'_c'==n);(REPORT/(id+'-DATA.txt')).write_text(t)
 for ref in ['animation/graphs/worldmodel/worldmodel.vnmgraph','animation/graphs/viewmodel/viewmodel.vnmgraph','animation/skeletons/characters/worldmodel.vnmskel','animation/skeletons/characters/viewmodel.vnmskel']:assert ref+'_c' in edges[n],(n,ref)
 assert not re.search(r'characters/models/shared/(animgraphs|animsets)/',t)
 gm=re.search(r'\bm_meshGroups\s*=\s*\[(.*?)\]',t,re.S);groups=re.findall(r'"([^"]+)"',gm[1]) if gm else [];m=re.search(r'\bm_refMeshGroupMasks\s*=\s*\[(.*?)\]',t,re.S);masks=[int(v) for v in re.findall(r'\d+',m[1])] if m else []
 fp=[i for i,g in enumerate(groups) if 'firstperson' in g];actual=any(mask&(1<<i) for i in fp for mask in masks)
 if id in ['pardofelis','vrc_lime','huohuo','myers']:assert actual,(id,'no first-person mesh')
 bm=re.search(r'\bm_boneName\s*=\s*\[(.*?)\]',t,re.S);bones=re.findall(r'"([^"]+)"',bm[1]);assert all(n in bones for n in ['root_motion','pelvis','hand_L','hand_R','head_0'])
 modelreports.append({'Id':id,'Name':MODELS[id][0],'Path':n.removesuffix('_c'),'SHA256':assets[n],'Source':origin[n],'AG2BindingsVerified':True,'BoneCount':len(bones),'FirstPersonMeshMaskPresent':actual,'FirstPersonGroups':[groups[i] for i in fp],'GameTestedForThisPackage':False,'Note':'Static resource checks only; first-person animation requires client testing'})
print('Parsed all',len(parsed),'compiled resources',flush=True)
info='"AddonInfo"\n{\n "addonname" "keran_five_models"\n "addontitle" "Aluona, Myers, Pardofelis, Lime and Huohuo - CS2 Player Models"\n "addonversion" "1.1"\n "addonauthor" "HifumiDaisuki01"\n "addondescription" "Five player-model resources, not a playable map. No Dujiaoshou."\n}\n'
(RES/'addoninfo.txt').write_text(info);content=D/'addon/content/csgo_addons/keran_five_models';content.mkdir(parents=True,exist_ok=True);(content/'addoninfo.txt').write_text(info)
config={'Models':{k:{'name':v[0],'path':v[1],'permissions':[],'permissionsOr':[],'side':'All','disableleg':False,'hideinmenu':False} for k,v in MODELS.items()}}
dump(D/'configs/PlayerModelChanger.merge.json',config)
dump(D/'configs/resource-catalog.template.json',{'Archives':{},'Models':sorted(v[1] for v in MODELS.values()),'Note':'Template only. After Workshop download regenerate archive paths/hashes from actual downloaded VPK. Do not overwrite live catalog with this template.'})
report={'Models':modelreports,'ResourceCount':len(assets),'ResourceBytes':sum((RES/n).stat().st_size for n in assets),'RuntimeFiles':assets,'OriginalGameReferences':sorted(official),'DependencyGraph':edges,'MissingReferences':[],'PathConflicts':[],'CaseCollisions':[],'AllCompiledResourcesParsed':True,'SourceBytesPreserved':True,'ExistingAluonaHashPreserved':True,'MyersReplacedWithNewPack':True,'DujiaoshouIncluded':False,'WorkshopPublished':False,'WorkshopMounted':False,'ProductionServerChanged':False,'NewThreeClientAnimationsTested':False,'MyersFirstPersonMeshPresent':True,'MyersFirstPersonGameVerified':False,'CharacterNameConfirmedByUser':'Huohuo (Honkai: Star Rail), original internal path kept','SourceMainCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO).decode().strip()}
dump(REPORT/'resource-review.json',report)
pack(RES,D/'workshop-upload');vp=inspect(D/'workshop-upload/pak01_dir.vpk');assert {e['Path'] for e in vp['Entries']}==set(assets)|{'addoninfo.txt'}
for e in vp['Entries']:
 if e['Path'] in assets:assert e['SHA256']==assets[e['Path']]
dump(REPORT/'vpk-validation.json',vp)
r=subprocess.run([viewer,'-i',str(D/'workshop-upload/pak01_dir.vpk'),'--vpk_verify'],capture_output=True,text=True);(REPORT/'source2viewer-vpk-verify.log').write_text(r.stdout+r.stderr);assert r.returncode==0 and 'Success.' in r.stdout
shutil.copy2(B/'mika-work/MIKA-dujiaoshou-Workshop/Verify-Package.ps1',D/'Verify-Package.ps1')
readme='''# CS2 五人物 Workshop 上传包

包含 **Aluona、Myers、Pardofelis、VRC Lime、Huohuo（藿藿）**。不含 Dujiaoshou/MIKA。

## 直接上传

1. 解压 ZIP，用之前的 GWSteam / Workshop 发布工具。
2. 上传内容目录选择 **workshop-upload**，同时包含 **pak01_dir.vpk 与 pak01_000.vpk**；不能只上传索引。
3. 新建作品或由你明确选择更新作品；保留旧作品作为回滚资源。本次没有操作 Steam。
4. 标题可用：Aluona, Myers, Pardofelis, Lime and Huohuo - CS2 Player Models。
5. 发布并可下载后，把 **Workshop ID / 链接** 发回来，再备份并切换服务器。

这是人物资源包，不是可玩地图；不要用 host_workshop_map 启动它。沿用此前阿洛娜资源包上传流程，无需重新编译。工程目录为 addon/game/csgo_addons/keran_five_models，配套 content 只含 addoninfo。优先直接上传已校验 VPK，避免 Workshop Tools 默认白名单漏收 characters。

## 五个人物与计划指令

| 人物 | 接入后指令 | 内部路径 |
|---|---|---|
| Aluona | !model aluona | characters/models/aluona/aluona.vmdl |
| Myers | !model myers | characters/models/exg/myers/myers.vmdl |
| Pardofelis | !model pardofelis | characters/models/exg/pardofelis/pardofelis.vmdl |
| VRC Lime | !model vrc_lime | characters/models/exg/vrc_lime/vrc_lime.vmdl |
| 藿藿 | !model huohuo | characters/models/exg/honkai_starrail_huohuo/honkai_starrail_huohuo.vmdl |

Pardofelis、VRC Lime、藿藿和 Myers 均来自桌面新版模型包；Aluona 逐字节保留现用成品。VRC Lime 与 lime_e 不同。

**v1.1 已将 Myers 换为新版包中的成品，包含实际第一人称网格，AG2 和依赖检查通过；手臂持枪/换弹效果待游戏验证。藿藿名称由用户确认，菜单/ID 改为 huohuo，内部 honkai_starrail_huohuo 路径保留，未修改二进制引用。**

## 真实验证范围

- 五个主模型及所有自定义依赖逐一解析；AG2 图/骨架引用存在，无旧 animgraph/animset。
- 递归闭包不缺自定义依赖；原版依赖根据既有正式游戏 VPK 索引确认，未把原版游戏资源打入包。
- 新版 Myers 和另外三个新版人物的第一人称分组实际关联到网格。此项不是手臂持枪/换弹的游戏验证。
- Aluona SHA256 与服务器现用成品一致；Myers SHA256 与桌面新版包一致，与旧版不同；没有重新编译或修改资源二进制。
- 无同路径不同内容冲突、大小写冲突；未混入 Dujiaoshou、测试地图、脚本、玩家数据库。
- VPK 每个资源的 CRC/SHA256 与输入一致；Source2Viewer 独立验证 VPK MD5/分块哈希。
- **本五合一尚未上传 Workshop、未挂载到服务器、未完成客户端自动下载与新版四个人物游戏实测。正式服务器未修改。**

## 配置与后续接入

configs/PlayerModelChanger.merge.json 是五人物合并片段，T/CT 均开放。保留原配置其他选项和 SQLite；不要整份覆盖配置。

configs/resource-catalog.template.json 仅提供模型路径；Archives 要在实际 Workshop 下载后重新生成，不能作为正式白名单直接覆盖。

服务器正式切换时用新包 ID 替换当前三合一 ID 3822432137；不要同时挂载两个含 Aluona/Myers 同路径的包。移除旧菜单 mika 的具体处理与玩家持久化兼容，应在接入时备份后执行，不删除玩家数据库。

回滚：保留当前三合一 Workshop 3822432137 及其配置/数据库备份；发生问题恢复原挂载 ID 与配置。包上传阶段无需服务器回滚，因为尚未修改正式服。

## 本地校验

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\\Verify-Package.ps1
```

reports/ 保存资源依赖、哈希与 VPK 验证结果。发布后的客户端需逐个检查第三/第一人称、持枪/换弹、重生/重连、T/CT 及恢复默认。静态检查不代替这些测试。
'''
(D/'README.md').write_text(readme,encoding='utf-8-sig');(D/'上传说明.txt').write_text('GWSteam 上传内容目录：workshop-upload\n必须将 pak01_dir.vpk 与 pak01_000.vpk 一起上传。\n五人物：Aluona / Myers / Pardofelis / VRC Lime / 藿藿；不含 Dujiaoshou。\n发布后把新 Workshop ID 发回来，正式服务器目前未改。\nMyers 已换新版，具备第一人称网格，游戏手臂效果待验证。藿藿指令：!model huohuo。\n',encoding='utf-8-sig')
manifest=[sha(p)+'  '+p.relative_to(D).as_posix() for p in sorted(D.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.txt'];(D/'SHA256SUMS.txt').write_text('\n'.join(manifest)+'\n')
archive=W/'CS2-FiveModels-Workshop-v1.1.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,6) as z:
 for p in sorted(D.rglob('*')):
  if p.is_file():z.write(p,D.name+'/'+p.relative_to(D).as_posix())
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
archive.with_suffix('.zip.sha256').write_text(sha(archive)+'  '+archive.name+'\n')
for src,name in [(D/'README.md','README.md'),(D/'configs/PlayerModelChanger.merge.json','PlayerModelChanger.merge.json'),(D/'configs/resource-catalog.template.json','resource-catalog.template.json'),(REPORT/'resource-review.json','resource-review.json'),(REPORT/'source2viewer-vpk-verify.log','source2viewer-vpk-verify.log')]:shutil.copy2(src,PUBLIC/name)
shutil.copy2(W/'build_five.py',PUBLIC/'build_five.py')
summary={'Zip':archive.name,'Bytes':archive.stat().st_size,'SHA256':sha(archive),'Resources':len(assets),'VPKEntries':len(vp['Entries']),'ZipManifestFiles':len(manifest),'WorkshopPublished':False,'ProductionServerChanged':False}
dump(PUBLIC/'package.json',summary);dump(W/'package.json',summary);print('FINAL',json.dumps(summary),flush=True)
