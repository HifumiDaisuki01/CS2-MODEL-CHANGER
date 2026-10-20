# 新版合集七个人物与 Lime E 对照复查（2026-10-20）

本次只读检查本地新版合集，未修改正式服务器、未生成修复后新人物，未运行客户端/BOT 测试。用户已确认当前十二人物包游戏内整体正常；这不替代下面七个未部署模型的验证。

| 人物 ID | 资源线索（非已核实角色身份） | 骨骼 | 第一人称蒙皮顶点 | 结论 |
|---|---|---:|---:|---|
| 10096 | cs2ze/elysia2 | 544 | 8770 | 优先直接打包测试：AG2、核心24层级、标准手/指蒙皮、依赖均通过静态检查 |
| 10018 | aquaz/maemi | 291 | 29481 | 优先直接打包测试：AG2、核心24层级、标准手/指蒙皮、依赖均通过静态检查 |
| 10032 | cs2ze/leilv | 487 | 未匹配到人物 firstperson_default 分组 | 旧 AG1；17项核心层级不符，缺旧图/animset及外部手臂；需完整迁移 |
| 10052 | ruiyiwelkin/eku_mutsuki | 313 | 19605 | 已有AG2/标准手指蒙皮，仍在 m_refAnimIncludeModels 引用旧 animset_ct；不能标记原包依赖通过 |
| 10073 | tioplato/xingqiongtiedao_huahuo | 268 | 25543 | AG2/核心24/内嵌手指蒙皮通过；缺旧 huahuo_arms.vmdl，结构化清理候选 |
| 10092 | qiliu/shouanren | 230 | 29312 | AG2/核心24/内嵌手指蒙皮通过；缺旧 shouanren_arms.vmdl，结构化清理候选 |
| xmanuka | neon/xmanuka | 258 | 8660 | AG2/核心24/内嵌手指蒙皮通过；缺旧 xmanuka_arms.vmdl，结构化清理候选 |

10032 另外有两项纹理在本合集与已确认基础资源清单中无法解析：materials/default/default_mask_tga_cac76a2f.vtex_c、materials/default/default_skin_diffusewarp_tga_e58a9ed.vtex_c。本次没有读取当前游戏原版 VPK 验证它们是否随游戏提供，因此标为未解决，不断言一定缺于游戏。其 AG1 和手臂缺失已足以阻止直接使用。

同名 `phase2/weapons/exg/<编号>/<编号>.vmdl_c` 是手臂/附件候选，**不能直接作为 PlayerModelChanger 人物路径**；它们不具备完整人物核心骨架/动画图。这不表示其手臂资源自身错误。已检查并单独记录，避免把附件当人物。

## 新包 Lime E：为什么暂不替换

新包 `characters/models/exg/chrisan/lime_e/lime_e.vmdl_c` SHA256：
`dc09ec62b0ec86c9da80d54c39af604fc9550b981119eb974ad73a709ae5928a`

它确实已有 AG2 世界/第一人称图、核心24骨架、236骨骼、48693个第一人称蒙皮顶点及标准手指权重，已经不是单纯 AG1 原件；但 DATA 中仍有 `anim_graph_resource = ...player_ct.vanmgrph` 与旧 animset include，RERL 也记录这两个依赖；合集里均不存在。因此“有AG2”不等于完成了干净迁移。GLB导出日志也报告这两项加载失败；GLB可以生成不等于游戏可用。

当前服务器版本是实际 Workshop Tools 重新编译的 v0.5.0 成品，241骨骼，SHA256：
`981f1d46fa80ad004972d2e04276ed6fde80208993191d47a832d4bf67ca778d`

当前版本使用从原 phase2 手臂重绑到人物本体后的内嵌第一人称网格，旧动画资源已清理，139项原材质/纹理保留；已有用户手部实测及十二人物部署后的正面反馈。**建议维持当前版，不为“新版”标签更换。** 两者同一路径，不能同时挂载比较；若将来A/B，必须隔离addon，重新核对包哈希并逐枪检查。

## 检查方法与边界

1. 重新读取14个实际资源：7个人物、Lime E和6个同号phase2文件的 DATA/RERL，计算SHA256。
2. 用 Source2Viewer 20.1.7467 真实导出带动画/蒙皮的GLB。必须使用 `-d --gltf_export_format glb --gltf_export_animations`；不带导出动画选项的普通GLB可能没有skin，不能据此断言原模型没蒙皮。
3. 解析firstperson_default、meshGroupMasks和LOD0映射；读取JOINTS_0与WEIGHTS_0，只统计正权重骨骼；确认标准hand/finger、arm影响，检查是否仍绑定v_weapon旧骨骼。七个有第一人称分组的AG2人物（含Lime E）均有标准手/指影响，无v_weapon正权重。
4. 核对标准核心24骨骼父子层级。骨骼总数不同不等于不兼容。
5. 使用先前递归依赖清单，重新对当前合集逐文件验证存在性，排除明确已确认的基础资源。该步骤不等于逐材质重新解码或完整原版资源普查；未解决列表保存在报告中。
6. 第一人称网格已覆盖手部，不表示每种武器、手套、腿部、碰撞箱或伤害行为游戏验证通过。上述新候选均待游戏验证。

工具脚本中的本地路径反映本次实际输入，迁移到别处需要修改。它们是审计工具，不是自动修复或部署入口。
