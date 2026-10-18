# 给下一台开发电脑的移交：阿洛娜已验证成果

仓库：https://github.com/HifumiDaisuki01/CS2-MODEL-CHANGER

测试版 Release：https://github.com/HifumiDaisuki01/CS2-MODEL-CHANGER/releases/tag/v0.1.0-alpha

**目标：只靠仓库和 Release 恢复成果，不依赖原 Windows 电脑继续在线。** 本地人物已实际显示；Linux 正式部署和 Workshop 分发尚未通过验证。

## 下载与成品列表

- `CS2_Aluona_Package_A-v0.1.0-alpha.zip`：完整可恢复包。含 14 个原编译模型/材质/纹理、JS 源码与 vjs_c、两个 cfg、addoninfo、自动/手动启动器、安装器、C# 控制台助手源码、原样本 VPK、PMC 完整配置、依赖表、技术经验与成功截图/日志。
- `CS2_Aluona_Workshop_Preparation-v0.1.0-alpha.zip`：阿洛娜单模型发布准备工程及候选 VPK；未发布、未完成 Workshop 挂载验收。
- 每个 ZIP 都有同名 `.sha256`；`SHA256SUMS-release.txt` 汇总两个归档的 SHA256。
- 每个 ZIP 解压后的根目录有 `SHA256SUMS.txt`，逐个验证所有包含文件。人物原资源单独使用 `evidence/extracted-resources.csv` 的 SHA256。
- Git 中的 `aluona/` 保存可阅读工程源码、配置、依赖清单和说明；大二进制使用 Release。仓库历史里的旧 ZIP 保留历史，但它是第一版手动启动包，恢复时必须下载这个新 Release。

下载入口：在 Release 页面 Assets 中选择文件，不使用 GitHub 自动生成的 Source code.zip 来代替模型成品。自动源码归档不包含 Release 里的模型二进制。

## 10GB、无 Steam/CS2 的开发机现在应执行

1. 下载两个 ZIP、两份 `.sha256` 和汇总校验文件，总量为几十 MB，无需安装 Steam。
2. 在 Linux：`sha256sum -c SHA256SUMS-release.txt`；Windows：`Get-FileHash .\CS2_Aluona_Package_A-v0.1.0-alpha.zip -Algorithm SHA256`，与同名 .sha256 比对。
3. 解压主包；Windows 运行 `powershell -NoProfile -ExecutionPolicy Bypass -File .\Verify-Package.ps1`；Linux 运行 `bash server/verify-package.sh /path/to/CS2_Aluona_Package_A`。这只验证文件，不宣称模型运行成功。
4. 阅读 `EXPERIENCE_CN.md`、`DEPENDENCIES.md`、`TEST_REPORT.md`、`WORKSHOP_STATUS.md` 和 `server/README.md`。完整模型和 vjs_c 已包含，不需要在这台 10GB 电脑重新编译。
5. 可以通过另行授权的访问方式读取 Linux 测试服现状，先备份现有插件配置、版本和 KeranStrat 设置。当前任务没有连接或修改远程服务器，也不把本文件视为自动执行远程变更的授权。
6. 准备独立服务端测试实例和配置合并方案；不要直接覆盖正式服。Workshop 尚无 ID，先解决资源发布/分发，不要给 MAM 填写虚构 ID。
7. 安排一台空间足够、装有正版 CS2/Workshop Tools 的 Windows 电脑复现和做 Workshop 发布交互。这台 10GB 开发机不能独立运行完整 CS2；但可以完成资源接收、校验、文档、服务端源码和配置工作。

## 在具备 CS2 的 Windows 电脑恢复成功环境

解压主包，关闭 CS2，在 Steam 中安装 Workshop Tools。使用实际游戏根目录（不假定 C 盘）：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Install-Local.ps1 -GamePath "D:\SteamLibrary\steamapps\common\Counter-Strike Global Offensive"
powershell -NoProfile -ExecutionPolicy Bypass -File .\Start-Aluona-Test.ps1 -GamePath "D:\SteamLibrary\steamapps\common\Counter-Strike Global Offensive"
```

原电脑已部署并使用 Z 盘，双击 CMD 即可。其他电脑必须传入正确 GamePath。安装器只允许独立 game/content addon 子目录，同文件跳过、不同文件拒绝覆盖；不会修改官方 VPK 或 gameinfo。

自动启动器会保持本机测试控制台连接，启动 Dust2，等 `status` 确认 Client Connected 且玩家 active，再预缓存、等待至少 6 秒并应用模型。看到绿色 `AUTO_APPLY_CONFIRMED` 后检查画面；若仍在队伍菜单，选择 T/CT 后用 `cs2cm_apply` 重试并检查日志。不要把 API 回读当作视觉验收。

## 关键路径与成功时序

- 磁盘：`characters/models/aluona/aluona.vmdl_c`。
- 引擎 API/PMC：`characters/models/aluona/aluona.vmdl`。
- `-tools -addon cs2cm_aluona_localtest` 让 game/content addon 松散资源参与加载；尚未证明独立 VPK/Workshop 挂载。
- 完全入服后执行 `exec aluona_precache.cfg`，让带模型的 prop_dynamic 存活，等待至少 6 秒。
- 再执行 `exec aluona_apply.cfg` 创建 point_script；JS 使用官方 `CSPlayerPawn.SetModel`，并记录 before/after。
- 不在同一帧应用并删除预缓存实体，曾触发 `Serialized nonresident asset`。
- `firstperson`/`thirdperson` 检查手部和人物；脚本注册 OnPlayerReset，必要时 `cs2cm_apply` 重试。
- VConsole 29000 为当前已验证的带帧协议。纯文本 netcon 不能直接复用该协议。测试监听不要公开转发，退出 CS2 后关闭。

只需使用已编译资源。修改 JS 后可运行 `Rebuild-Script.ps1 -GamePath ...`，仅编译 JS。人物艺术源文件并未提供，不能声称从源模型重建。`Build-Release.ps1` 是归档与校验构建，不反编译/重编译人物。

## Linux / MAM / PMC

前提：Linux CS2、Metamod、CounterStrikeSharp 及匹配版本的 PMC、MAM，并为客户端建立合法可下载的资源分发。仅复制服务端模型文件无法让公网客户端自动得到资源。

- MAM 路径：`game/csgo/cfg/multiaddonmanager/multiaddonmanager.cfg`。`mm_extra_addons` 是逗号分隔的真实 Workshop ID；已有 ID 要保留。人物资源需同时在服务端和客户端挂载，不能仅配置 mm_client_extra_addons。下载/挂载完成后切图，运行 `mm_print_searchpaths` 检查。
- PMC 路径：`game/csgo/addons/counterstrikesharp/configs/plugins/PlayerModelChanger/PlayerModelChanger.json`。使用包内 `PlayerModelChanger-Aluona.json` 的 m0117 条目，side All，BOT T/CT 引用 m0117。合并而非覆盖原配置。
- 先前核对 PMC 1.8.6 二进制引用 CSS API 1.0.255/net8；这不是推荐降级，现场须重新核对兼容性。上游：https://github.com/samyycX/CS2-PlayerModelChanger 。MAM：https://github.com/Source2ZE/MultiAddonManager 。
- Workshop 状态：未发布，ID 无。当前默认打包规则不包含 characters；未修改官方 gameinfo。需要继续研究安全打包支持，并由用户完成 Steam 交互及可见性确认后才能上传。

## KeranStrat 与验证边界

已观察：真人 T/CT、BOT，第三人称、第一人称自定义手部、站立、蹲姿、USP/Glock 持握；分阶段冷启动成功；修复后的默认自动启动器另有全新进程与截图验证。

尚未验证：所有动作/武器/换弹/检视/死亡，命中盒和碰撞不变，Workshop/MAM 网络挂载，Linux PMC 运行，KeranStrat 录制/回放。KeranStrat 可能在重置、出生或回放时改写实体，需在隔离服检查与模型设置的冲突，并测试 BOT、换队和重生。

最后的源码提交、Release 实际下载 SHA256、完整解压和逐文件验证结果，会作为 `FINAL_VERIFICATION.md` 与 `download-verification.json` 上传到仓库。核对它们后，可不再依赖原电脑。
