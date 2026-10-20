# 十五人物正式包（已部署、用户实测正常）

**当前正式 Workshop：[3823495199](https://steamcommunity.com/sharedfiles/filedetails/?id=3823495199)**。Linux 服务器已挂载，15人物配置/资源校验/预缓存通过；用户在本次部署后明确反馈“全部正常”，确认作为正式使用包。

[下载完整上传包](https://github.com/HifumiDaisuki01/CS2-MODEL-CHANGER/releases/download/v0.7.0-fifteen-models/CS2-FifteenModels-Workshop-v1.0.zip) · [更换服务器迁移说明](SERVER_MIGRATION_CN.md)。原Release文件和校验值保持，旧版本保留。ZIP内与部分静态报告仍记录打包时的“待验证”状态，以本页和正式验收记录为当前状态。

用户确认覆盖整体人物使用体验；没有提交逐枪、命中盒、全部动作或多客户端专项验收矩阵，不能扩写为这些项目逐项通过。

原十二人物保留十个，移除 **huohuo（藿藿）、hifumi（日富美）**；新增 **10092（守岸人）、10073（花火）、10096（Elysia）、xmanuka、10052**。当前已实测的 Lime E 不换，新版 Myers 保留。

## 直接上传

1. 先把旧的 `keran_five_models` addon 目录备份到工程外，再把本包 `addon/game/csgo_addons/keran_five_models` 整个目录放进 CS2 对应 game 目录，content 目录按原结构复制。**不要只覆盖旧文件**，否则旧藿藿/日富美文件可能残留。目录名沿用之前名称，本包实际是十五人物。
2. 沿用 Steam 官方 CS2 Workshop Tools 的成功发布流程。这里是已编译资源，不需要重新编译旧人物源码。不要作为可玩地图启动。`workshop-upload/` 只是校验/备用VPK，使用官方Tools上传时无需更改现有结构。
3. 本包已正式发布为 Workshop 3823495199 并部署。现有服务器直接使用该ID；另行发布/更新时先备份，并根据实际下载重新生成资源catalog。旧3823301202保留用于历史回滚，不与新包同时挂载。

可选：`Verify-Workshop-Project.cmd` 检查实际 game addon 内资源，能发现旧模型版本或藿藿/日富美等多余人物残留。本交付包已完成本地/资源校验，无需为了上传重复执行。

## 人物 ID

`!models` 打开菜单，`!model <ID>` 选择，`!model default` 恢复原版。下列15个ID均已在正式服开放。

| ID | 菜单名称 |
|---|---|
| aluona | Aluona（阿洛娜） |
| myers | Myers（新版） |
| pardofelis | Pardofelis（帕朵菲莉丝） |
| vrc_lime | VRC Lime |
| lime_e | Lime E |
| chikari | Chikari |
| serina | Serina |
| baizhouzi | Baizhouzi（白洲梓） |
| mingchao_feibi | 鸣潮·菲比 |
| chiffon_fox | Chiffon Fox |
| 10092 | 守岸人 |
| 10073 | 花火 |
| 10096 | Elysia（爱莉希雅） |
| xmanuka | XManuka |
| 10052 | 10052（Mutsuki，按资源目录标识） |

`10052` 资源引用目录包含 eku_mutsuki，因此附带该来源标识；本次未通过游戏画面核实角色身份。花火使用ID `10073`，并非本次移除的藿藿。

## 实际处理与证据

- **守岸人、花火、xmanuka**：已有 AG2、内嵌第一人称网格及标准手指蒙皮。使用结构化KV3编辑移除旧character_arm_config及唯一对应RERL外部手臂引用；没有伪造缺失文件，没有改变网格。
- **10052**：已有AG2及标准手指蒙皮，但m_refAnimIncludeModels仍包含旧animset_ct。专用工具严格限制输入SHA256、目标引用和唯一包含项；保留AG2图及骨架引用，将旧动画包含数组清空，移除对应RERL项。不是AG2重编译，也不能仅据此宣称游戏动画通过。
- **10096 / Elysia**：原成品静态检查通过，无修改。
- 四项修复均在当前Windows电脑运行；独立Source2Viewer带蒙皮GLB导出前后BIN块完全一致，其他非DATA/RERL资源块逐字节一致，未授权输入拒绝测试通过。
- 原十个人物主模型SHA256全部保留，Lime E仍为v0.5.0成品，新版Myers保持原十二人物包版本。
- 全包 **824个资源**逐一解析通过；15个主模型具备AG2图、标准核心24层级、非空第一人称网格及LOD0。递归依赖闭包、同路径冲突与大小写检查通过，13项明确基础资源由原版游戏提供。VPK校验包含825项（含addoninfo），逐项CRC与资源哈希匹配。
- 藿藿和日富美主模型不在包内，也不在菜单中。资源始终保留实际内部路径。

**当前状态：Workshop 3823495199 已部署，用户手动确认十五人物全部正常。** 四项修复仍属于结构化引用清理，没有新增Valve编译器运行；静态校验、服务端挂载、预缓存与用户游戏反馈是分别记录的证据。逐枪动作、命中盒/伤害等专项矩阵未单独测量。打包阶段报告保留原状态，见 reports/formal-acceptance.json 的后续验收记录。

## 配置、源代码与后续部署

- `configs/PlayerModelChanger.merge.json`：十五人物配置片段，T/CT均开放；合并时先移除 `configs/models-to-remove.json` 中两项，不覆盖其他全局插件设置。
- `configs/resource-catalog.template.json`：只供参考，发布后必须依据实际Steam下载归档路径及哈希重新生成。
- `configs/expected-project-resources.json`：本包已编译资源SHA256清单。
- `reports/`：本次四模型修复/独立导出对比/VPK/资源检查和原十模型哈希证明。
- `tools/arm-reference-repair/`、`tools/anim-include-repair/`：固定VRF 20.1.7467的结构化修复源码，不含自包含运行库。
- `tools/build_fifteen.reference.py`：本次实际组包记录，私有输入路径需要适配，非一键下载器。

正式服更新时保留玩家SQLite；已选中被移除角色的玩家应回退默认人物，不为清理角色删除数据库记录。不要同时挂载旧包和新包。当前正式服已切换至3823495199，当前版本作为正式包保留。

## 人工测试与回滚

普通客户端连接后确认下载新包。新增五个逐一测试 T/CT、第一人称刀/手枪/步枪/AWP/道具、换弹/射击、站走蹲跳、死亡复活及重连；另一名玩家确认第三人称显示，回归KeranStrat。出现异常先取消相应新增模型菜单项；整体回滚恢复先前 Workshop ID、PlayerModelChanger/MultiAddonManager配置和资源catalog，保持SQLite不变。旧Workshop与GitHubRelease保留。
