# 十二人物 Workshop 上传包

本包供 Steam 官方 CS2 Workshop Tools 使用，沿用之前的目录结构。当前服务器未修改，Workshop 未代为发布。

## 上传步骤

1. 先备份另一台电脑中的旧 addon。把 `addon/game/csgo_addons/keran_five_models/` 内文件覆盖到 **CS2 安装目录**的 `game/csgo_addons/keran_five_models/`；对应 content 目录中的 addoninfo 也可复制。名称仍为 keran_five_models 是为了沿用旧工程，不代表只有五个人物。
2. 不要重新编译旧的五人物源文件覆盖这些已编译资源。用包内 `Verify-Workshop-Project.cmd`，输入实际 **game/csgo_addons/keran_five_models** 目录，确认全部资源哈希一致，尤其 Myers 与 Lime E。
3. 在官方 Workshop Tools 打开这个 addon，按之前成功的流程上传/更新。上传资源包，不要作为地图启动。`workshop-upload/` 中 VPK 是校验及备用产物，官方 Tools 工作流无需改用 VPK 上传。
4. 发布完成后提供 Workshop ID，再备份服务器配置/数据库并更新挂载、资源目录和菜单。本次不部署正式服。

## 人物与命令

部署更新菜单后，`!models` 打开菜单，`!model default` 恢复原版，`!model <ID>` 选择下列人物。配置为 T/CT 双队可用。

| ID | 显示名称 | 本次处理 |
|---|---|---|
| aluona | Aluona（阿洛娜） | 保留已编译资源 |
| myers | Myers（新版） | 保留已编译资源 |
| pardofelis | Pardofelis（帕朵菲莉丝） | 保留已编译资源 |
| vrc_lime | VRC Lime | 保留已编译资源 |
| huohuo | Huohuo（藿藿） | 保留已编译资源 |
| lime_e | Lime E | 已接收 Windows 编译成品 |
| chikari | Chikari | 保留已编译资源 |
| serina | Serina | 保留已编译资源 |
| baizhouzi | Baizhouzi（白洲梓） | 结构化清理旧手臂引用，待游戏验证 |
| hifumi | Hifumi（日富美） | 结构化清理旧手臂引用，待游戏验证 |
| mingchao_feibi | 鸣潮·菲比 | 结构化清理旧手臂引用，待游戏验证 |
| chiffon_fox | Chiffon Fox | 结构化清理旧手臂引用，待游戏验证 |

Huohuo 是《崩坏：星穹铁道》的藿藿。白洲梓使用菜单 ID baizhouzi，内部路径仍为 baizhouxin；日富美 ID hifumi，内部路径仍为 hihumi。保留资源路径以免破坏引用。本包不含 xinghui、dujiaoshou。

## 已验证与未验证

- 625 个编译资源逐个经 Source2Viewer 解析；12 个人物具备 AG2 图、标准核心 24 骨骼层级和第一人称网格。依赖闭包、大小写、同路径内容冲突均通过检查；12 项动画/基础资源由原版 CS2 提供，不重复打包。
- Myers 使用新包中的版本，SHA256 为 `f155aba7d3e9da2719ae2c43710e7be1d1c79a1dd716e62147e0cc603822c6c5`；Lime E 为用户已完成 Windows 编译的 v0.5.0 成品，SHA256 为 `981f1d46fa80ad004972d2e04276ed6fde80208993191d47a832d4bf67ca778d`。
- baizhouzi、hifumi、mingchao_feibi、chiffon_fox 本身已有 AG2 与内嵌手臂。本次用 VRF 结构化解析并移除过期 character_arm_config 和对应缺失 RERL 外部手臂引用，重新序列化 DATA/RERL；其他资源块逐字节保留。没有创建假依赖，没有重新编译模型。
- 四个人物均已在这台 Windows 运行修复工具；独立 glTF 导出前后网格/蒙皮/动画二进制完全一致，负面测试 3 项通过。详细证据在 reports/。
- **本十二人物包尚未完成 Workshop 挂载和游戏内验证。** 有第一人称网格不等同于每种武器手臂表现均正常，也不保证第一人称腿部。模型比例、视角、动作、死亡、命中判定均需实测；静态检查不证明这些游戏行为通过。

## 文件说明

- `addon/`：官方 Tools 工程可复制的已编译资源。
- `configs/PlayerModelChanger.merge.json`：合并用配置片段，不能覆盖整个现有配置或数据库。
- `configs/resource-catalog.template.json`：新包模板；Workshop ID 应在发布后填写并按服务端实际资源重新生成。
- `configs/expected-project-resources.json`：625 项资源的精确哈希清单。
- `reports/`：资源、VPK、结构化修复、Windows 运行及独立导出比对报告。
- `tools/resource-repair/`：修复工具源码，固定 VRF 20.1.7467，需要 .NET 10 SDK 构建；不含 190MB 自包含运行库。
- `Verify-Package.ps1`：核对交付包完整性。

## 游戏验收与回滚

上传后用普通账号验证自动下载；逐一选择 12 人物，检查 T/CT、出生、重连、默认模型、第一人称各种武器、第三人称站走蹲跳、射击换弹及死亡动画；另由第二名玩家确认可见。保留 KeranStrat 并回归训练。发现问题先回退该人物菜单条目；需要整体回滚时恢复旧 Workshop ID、旧配置与资源目录。不要覆盖 SQLite，不删除旧 Workshop/Release。

## 授权与分发

第三方人物资源仅保留在本地交付包，不提交公开 Git 仓库或新 Release。GitHub 同步工具源码、配置、报告与说明。Workshop 发布应沿用用户已有授权范围。
