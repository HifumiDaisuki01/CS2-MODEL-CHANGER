# 三个 AG2 人物成品：2026-10-18

Myers、KM Decade、Dujiaoshou 均使用本机 Valve resourcecompiler 实际编译成功，退出码全部为 0。Source 2 Viewer 和 Verify-Compiled.ps1 检查通过。三个模型已经在本地 Dust2 通过官方 cs_script 切换并回读真实玩家模型路径；用户随后手动测试并确认“三个都没问题”。

## 使用

安装 Steam、CS2 和 Workshop Tools，保持 Steam 正常运行并关闭已有 CS2。解压后双击 Start-AG2-Test.cmd：自动寻找 Steam 库、检查安装冲突、启动独立 addon、等待客户端完全入服、创建三个预缓存实体并等待至少 8 秒，再应用 Myers。已有不同文件会拒绝覆盖。

无法自动定位时：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Start-AG2-Test.ps1 -GamePath "实际CS2目录" -Model km_decade
```

Model 可选 myers、km_decade、dujiaoshou。切换命令：ag2_apply_myers、ag2_apply_km_decade、ag2_apply_dujiaoshou；回读命令 ag2_verify。firstperson / thirdperson 用于切换观察视角。

自动启动器复用了本次已实际成功的分阶段命令；新整合的启动器只进行了语法检查，尚未重新完整冷启动复测。API 确认提示不能替代亲眼观察。

## 实际路径

所有运行资源位于 addon/game/csgo_addons/ks_ag2_repair_20261018_145133_943/：

- characters/models/exg/myers/myers.vmdl_c
- characters/models/exg/aquaz/km_decade/km_decade.vmdl_c
- characters/models/exg/dujiaoshou/dujiaoshou.vmdl_c

游戏 API 和配置使用同路径的 .vmdl 逻辑名。阿洛娜及原有材质贴图作为对照保留，未修改其文件。

## 验证与边界

- 编译、三个模型解析、AG2 引用、核心骨骼和父子层级通过，旧动画图引用已清除。
- 118 项原材质贴图解析通过，87 个唯一嵌套引用齐全；119 个原资源哈希未变，其中阿洛娜 14 项。
- 三个 PHYS 块解析通过，各保留 12 个胶囊体和 3 个球体。
- 官方脚本记录三个模型 SetModel before/after，实际游戏窗口已观察三个人物；用户后续手测确认正常。
- 用户未逐项列举全部武器、动作和碰撞测试；不将该确认扩写为完整命中盒、伤害、联网分发、多客户端或 KeranStrat 验收通过。
- 早期自动截图存在武器位置疑点；后续用户手测确认正常，保留原始证据，未据此修改模型骨骼或物理数据。

不要同时挂载此前第一次编译的 addon 或其他包含相同人物路径的旧包。这个包是松散文件本地测试/打包输入，并不证明独立 VPK、MAM 或 Workshop 分发已验证。没有发布 Workshop，没有修改 ID 3821951835。

## 包内容与授权边界

本次按用户明确指令发布编译成品。包含编译模型、材质、纹理、我们编写的官方 JS 测试源码及编译脚本、cfg、暂存配置和验证元数据。反编译 ModelDoc/DMX 美术工程、原始 DATA/PHYS 转储、Steam 崩溃转储、账户令牌不在公开包内。

reports/FINAL_LOCAL_REPORT.md 是用户手测确认前的编译阶段历史记录；最新状态以本 README 和 reports/user-manual-test-confirmation.json 为准。完整操作经验见 EXPERIENCE_AG2_CN.md。SHA256SUMS.txt 用于逐文件校验。