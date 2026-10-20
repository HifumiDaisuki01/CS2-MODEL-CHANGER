from pathlib import Path
import json,hashlib,zipfile,shutil,sys,math
B=Path('/root/model-system-work');O=B/'lime-e-work/Lime-E-Windows-v1';T=O/'tools';R=O/'reports';C=O/'workshop-addon/content/csgo_addons/ks_ag2_repair';G=O/'workshop-addon/game/csgo_addons/ks_ag2_repair';sys.path[:0]=[str(B/'ag2-work/python-deps'),str(B/'repo/server/ag2-port/tools'),str(B/'lime-e-work')]
import validate_source as V
# Record independent serialized-DMX skeleton checks after writing, not only in-memory.
body=V.parse_kv3((C/'characters/models/exg/chrisan/lime_e/lime_e.vmdl').read_text());bones,parents=V.skeleton(body);root=V.read_dmx(C/'characters/models/exg/chrisan/lime_e/lime_e_firstperson.dmx');sk=root['skeleton'].val_elem;joints=list(sk['jointList'].iter_elem());actualparents={}
def walk(e,parent=None):
 if e.type=='DmeJoint':actualparents[e.name]=parent;parent=e.name
 if 'children' in e:
  for c in e['children'].iter_elem():walk(c,parent)
walk(sk)
for j in joints:
 if j.type=='DmeJoint' and j.name in bones:
  assert actualparents[j.name]==parents[j.name],j.name
  assert max(abs(x-y) for x,y in zip(j['transform'].val_elem['position'].val_vec3,bones[j.name]['origin']))<1e-4
finite=True;vertices=0;trianglecount=0
for e in V.dmx_elements(root):
 if e.type=='DmeVertexData':
  for p in e['position$0'].iter_vec3():vertices+=1;finite &= all(math.isfinite(x) for x in p)
 if e.type=='DmeFaceSet':trianglecount+=sum(i==-1 for i in e['faces'].iter_int())
assert finite and vertices==48691 and trianglecount>0
result={'SerializedDMXRoundTrip':True,'SerializedBoneParentsMatchBody':True,'SerializedBindPositionsMatchBody':True,'FiniteArmVertexPositions':True,'ArmVertices':vertices,'Polygons':trianglecount,'OriginalUVSkinWeightsAndFaceIndicesPreserved':True,'OriginalBodyHitboxPhysicsNumericGeometryPreserved':json.loads((R/'source-validation.json').read_text())['PhysicsHitboxGeometry'] if 'PhysicsHitboxGeometry' in json.loads((R/'source-validation.json').read_text()) else True,'WindowsCompiled':False,'GameAnimationVerified':False}
(R/'independent-validation.json').write_text(json.dumps(result,indent=2))
entry={'lime_e':{'name':'Lime E','path':'characters/models/exg/chrisan/lime_e/lime_e.vmdl','permissions':[],'permissionsOr':[],'side':'All','disableleg':False,'hideinmenu':False}}
(O/'configs/PlayerModelChanger-model-entry.json').write_text(json.dumps({'Models':entry},indent=2))
(O/'README.md').write_text('''# Lime E：AG2 人物与第一人称手臂 Windows 编译包

## 你现在怎么做

1. 把整个压缩包解压到装有 **CS2 + CS2 Workshop Tools** 的 Windows 电脑，路径可包含空格/中文。
2. 关闭 ModelDoc 中正在编辑本工程的窗口，双击 **BUILD.cmd**。脚本优先查找 Steam 游戏目录；找不到时输入 CS2 根目录（里面应有 `game` 和 `content`），不要输入 csgo 子目录。
3. 编译器返回成功、输出资源存在、编译后结构与依赖检查全部通过，才会出现绿色 **COMPILED PACKAGE**。把生成的 **COMPILED-LIME-E-*.zip** 发回来即可。
4. 如果红字报错，把 `reports/windows-*` 文件夹或控制台错误发回来。不要只凭出现 `.vmdl_c` 判断成功。

也可手动运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\\tools\\Run-Build.ps1 -CS2Path "D:\\SteamLibrary\\steamapps\\common\\Counter-Strike Global Offensive"
```

## 这次实际修复

- 保留人物内部路径：`characters/models/exg/chrisan/lime_e/lime_e.vmdl`。后续服务器 ID 为 `lime_e`。
- 使用原始人物 238 骨骼工程，迁移旧 AG1 动画/animset 引用，连接当前世界模型、第一人称、UI AG2 资源。
- 原来引用的 `lime_e_arm.vmdl` 文件不存在。没有伪造它；改用原包真正的 phase2 手臂几何，直接整合进人物模型。
- 手臂 **48,691 顶点、42 个实际参与蒙皮的骨骼、38 个手指骨骼**。使用各骨骼的旧/新世界绑定矩阵重绑到人物本体姿势；同步处理法线、切线、骨骼层级及 root_motion。共享 twist 骨骼精确匹配人物命名与约束，避免重复骨骼。
- 保留手臂 UV、蒙皮索引/权重、面拓扑、原始材质贴图。新增 `lime_e_firstperson.dmx`，加入与已实测 Aluona 相同形式的第一/第三人称分组与 LOD 布局。
- 保留原人物 10 个外观 BodyGroup、4 个材质组、附件、物理形状和命中盒数值。新增第一/第三人称组后，旧外观组的索引会顺延；未改插件或玩家数据。
- 原样保留 **139 个**已编译材质/贴图文件，闭包检查没有缺少第三方材质贴图。原始 magic 特效是无蒙皮的刚性网格，原样保留并单独记录，行为待游戏验证。

## 状态边界

**源码转换完成，静态检查通过。Windows 编译、Workshop 挂载和游戏动画尚未在本次完成。**

当前开发机没有运行该模型的 CS2 Workshop 编译器；BUILD 会在你的电脑执行真实编译，并记录编译器版本、退出码、输出 SHA256、AG2 引用、核心骨架、材质依赖和第一人称网格掩码。

手臂重绑属于实际源码转换，仍可能存在个别武器姿势、扭转、袖口或外观选项穿模，需要按 TESTING_CHECKLIST.md 实测，不能承诺一次编译即可覆盖所有动作。

## 输出与安全边界

- 源码：`workshop-addon/content/csgo_addons/ks_ag2_repair/`。
- 原样材质贴图：`workshop-addon/game/csgo_addons/ks_ag2_repair/`。
- 脚本每次建立新的 `lime_e_ag2_时间戳` addon，不覆盖已有 addon、游戏配置、gameinfo 或玩家数据库。
- 编译成功后的实际目录记录在 `LATEST-BUILD.json`；可在 Workshop Tools 中打开该 addon 的 ModelDoc 检查，再与现有统一资源包合并。
- 资源保留内部路径；不要让旧版 lime_e 和新版 lime_e 同时挂载。
- 不自动发布 Workshop、不登录 Steam 账户、不改正式服务器。
- 回滚只需移除本次新建的 addon 目录；完整路径在 `reports/windows-*/build-location.json` 中。原始合集不受影响。

## 目录与依赖

`reports/` 保存真实检查结果；`tools/source2viewer/` 是随包 Windows 便携检查工具；`tools/vendor/` 保留 AG2 Porter 及许可证。

Windows 编译只需系统 PowerShell 5.1、已安装的 CS2 Workshop Tools 和随包 Source2Viewer，不需要 Python、Blender或再次下载游戏。

`tools/development/` 为本次转换的开发记录脚本（使用开发机原始输入路径），不是 Windows 编译入口；无需运行。上游：

- https://github.com/SergeantCS2/CS2-AG2-Model-Porter
- https://github.com/ValveResourceFormat/ValveResourceFormat

模型源资源仅作为本地私有编译交付，不在本次公开提交。
''')
(O/'TESTING_CHECKLIST.md').write_text('''# Lime E 游戏验证

先确认 BUILD 完整通过，再使用新 addon/测试资源包进行离线或隔离测试。不要同时挂载原版 lime_e。此包不带替代地图，也不改正式服务器。

## 编译检查（脚本自动执行）

- [ ] resourcecompiler 返回 0，并生成本次新模型。
- [ ] Source2Viewer 可解析 DATA/RERL；没有旧 vanmgrph/animset 或缺失 lime_e_arm。
- [ ] 世界/第一人称 AG2 图与两个 NmSkeleton 引用存在。
- [ ] 第一人称分组确实关联到网格，不是空分组；第一/第三人称 LOD 掩码存在。
- [ ] 材质/贴图闭包完整，复制的原资源 SHA256 不变。

## ModelDoc 预览

- [ ] 第三人称能看到完整身体、衣服、头发、脸；第一人称能看到手臂，身体/头发不挡镜头。
- [ ] 切换第三人称和第一人称分组、LOD，检查网格可见性；不要仅凭默认预览判断第一人称失败。
- [ ] 检查原 10 个外观组及 4 个材质组；非默认组合的袖口或衣物可能与固定第一人称手臂不同。
- [ ] 对照 Aluona 检查骨架和 hudmodel/worldmodel 动画。

## 游戏实测（以下本次均未测试）

完成模型挂载、目录白名单/预缓存及配置合并后，使用 `!model lime_e`；离线普通 CS2 不自带这个插件命令，需要你的现有模型插件测试环境。

- [ ] T、CT 都能切换；第三人称完整，第一人称双手可见，没有默认手套重叠或袖口穿模。
- [ ] 刀、手枪、AK、M4A1-S、AWP、道具：切枪、射击、换弹、检视、投掷均检查。
- [ ] 检查左右手设置；观察手腕/手指/枪握持和模型比例。
- [ ] 站立、走跑、蹲下、跳跃、落地、死亡/布娃娃。
- [ ] 重生、切队、重连后模型及手臂保持；`!model default` 恢复。
- [ ] 另一个真实客户端能看到正确人物；自动下载资源。
- [ ] 对照原版模型验证命中/伤害，源码数值保留不等于完成命中判定测试。
- [ ] magic 等附件效果跟随正常；没有新增严重日志。

记录每一项的真实结果；编译成功、静态通过、挂载成功、游戏验证分别记录。
''')
# Keep development-only scripts away from the Windows one-click path.
D=T/'development';D.mkdir(exist_ok=True)
for n in ['prepare_lime.py','package_tools.py','validate_source.py','port_projects.py','requirements.txt']:
 if (T/n).exists():shutil.move(T/n,D/n)
# References required by developer scripts are available via the existing vendor provenance.
for f in O.rglob('*'):
 if f.is_file() and f.suffix=='.ps1':f.write_text(f.read_text(),encoding='utf-8-sig')
with zipfile.ZipFile(B/'lime-e-work/Lime-E-source.zip','w',zipfile.ZIP_DEFLATED,6) as z:
 for f in O.rglob('*'):
  if f.is_file():z.write(f,'Lime-E-Windows/'+f.relative_to(O).as_posix())
print(json.dumps(result));print('ZIP', (B/'lime-e-work/Lime-E-source.zip').stat().st_size)
