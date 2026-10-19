# Lime E AG2 人物与第一人称手臂：Windows 成品

2026-10-19 使用本机 Valve resourcecompiler 实际编译成功，退出码 0，编译后结构与依赖检查通过。用户实际进入游戏观察后确认：手臂没有问题。

## 使用

安装合法 CS2 和 Workshop Tools，保持 Steam 正常运行，关闭已有 CS2，解压后双击 Start-Lime-E-Test.cmd。启动器自动查找 Steam 游戏库，安装到独立 addon，等待本地玩家 active，创建预缓存实体并等待至少 8 秒，然后通过官方 cs_script 应用模型，默认进入第一人称。

无法自动识别时：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Start-Lime-E-Test.ps1 -GamePath "实际 CS2 根目录"
```

如仍在游戏菜单，点继续游戏。控制台命令 lime_e_apply 重新应用，lime_e_verify 回读模型与武器；firstperson / thirdperson 切换视角。刀、枪需实际装备：give weapon_knife 后 slot3，步枪给出后 slot1，手枪 slot2。不要用清空全部武器后的空手画面判断手臂失败。

新打包启动器由本次实际成功的分阶段流程整理，已通过 PowerShell 语法检查，未再做一次完整冷启动自动验收。API 回读成功不等于亲眼验证全部动作。

## 核心产物

addon/game/csgo_addons/lime_e_ag2_20261019_150756_709/characters/models/exg/chrisan/lime_e/lime_e.vmdl_c

模型 SHA256：981f1d46fa80ad004972d2e04276ed6fde80208993191d47a832d4bf67ca778d。

配置/API 使用同路径的 lime_e.vmdl 逻辑名。第一人称手臂已经内嵌于人物模型；不需要也不应创建缺失的 lime_e_arm.vmdl。

- 人物与第一人称网格、AG2 图、骨架和核心层级已通过编译后检查。
- firstperson_default 分组确实包含网格，第一/第三人称 LOD 掩码有效。
- 原始 139 个已编译材质与贴图 SHA256 全部保持不变，材质依赖闭包完整。
- 官方 JS 在本地 Dust2 将原版玩家模型改为 Lime E，并回读准确路径。
- 用户手动确认第一人称手臂正常；自动流程未完成独立、逐武器、逐动作的完整矩阵。

不把以上结论扩写为所有武器换弹、左右手、命中盒伤害、多客户端分发、MAM 或 KeranStrat 均通过。

## 原外观与安装边界

保留原人物 10 个外观组、4 个材质组、附件和物理数据。第一/第三人称组加入后，旧外观组索引顺延；非默认外观和袖口仍建议另外检查。magic 原始刚性网格保留，其具体游戏行为未独立验收。

本包安装器拒绝覆盖已有不同文件，不修改官方 VPK、gameinfo、Steam 全局启动配置或现有 Workshop ID。不要同时挂载旧版同路径 Lime E。没有发布 Steam Workshop，也没有合并到此前的五人物资源包或改正式服。

## 包内容

运行时编译资源、官方 JS 测试源码及 vjs_c、cfg、安装/启动工具、独立模型配置及审核报告。反编译 ModelDoc/DMX 美术工程、原始 DATA/PHYS 转储、Steam 转储、账户凭据和失败截图不公开。

reports/compiled-validation.json 等为编译阶段快照，仍标记当时游戏未验证；最新状态以 reports/final-validation.json 为准。EXPERIENCE_LIME_E_CN.md 记录完整经验；SHA256SUMS.txt 用于逐文件校验。