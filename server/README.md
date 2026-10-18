# Linux 人物模型部署版 v0.2.0

阿洛娜人物模型系统已经安装到现有 Linux CS2 服务器。用户于 2026-10-18 进服实测，确认模型指令可以正常更换人物。

## 玩家命令

```text
!models
!model aluona
!model default
```

`!models` 打开上游 WASD 选择菜单，当前版本直接列出双方可用模型。`aluona` 同时保存为 T/CT 选择；`default` 同时恢复两队原版选择。支持上游 `!model aluona t/ct` 等分队参数，普通玩家无需管理员权限。

选项保存在 `addons/counterstrikesharp/plugins/PlayerModelChanger/data.db`。出生时读取已保存选择，包含换队和重连后的出生；延迟回调验证控制器、UserId、Pawn 序列号及阵营，避免旧回调写到新玩家。菜单、自动出生、重连与其他玩家视角的验证边界见 [TEST_REPORT.md](TEST_REPORT.md)。

## 实际环境与组件

| 项目 | 已部署版本 |
|---|---|
| 系统 | Debian 12 / glibc 2.36 / Linux x64 |
| CS2 | 1.41.9.1，ServerVersion 2000933 |
| Metamod | 2.0.0-dev+1481 |
| CounterStrikeSharp | 1.0.376，.NET 10 |
| MultiAddonManager | 1.6.2，steamrt3 Linux 构建 |
| PlayerModelChanger | 上游 1.8.6 适配版 `1.8.6-aluona.1` |
| KeranStrat | 0.5.4，原有插件保留 |

Workshop：[`3821951835`](https://steamcommunity.com/sharedfiles/filedetails/?id=3821951835)，公开、未封禁。配置使用 `characters/models/aluona/aluona.vmdl`，包内编译文件为同路径 `.vmdl_c`。

仅使用 `mm_extra_addons "3821951835"` 进行双端资源挂载分发；没有将同一 ID 又塞入 `mm_client_extra_addons`。服务器仍运行 Dust2，没有使用 `host_workshop_map`，未改启动参数或官方 `gameinfo.gi`。

## 成品与恢复

从本仓库 **v0.2.0-linux** Release 下载 Linux 插件包、源码包及 SHA256 校验文件。原来的 `v0.1.0-alpha` 恢复 Release 和模型资源保留，不作覆盖。

Linux 插件包只包含本插件、必要运行依赖、配置模板和操作文档；不重复打包 Workshop VPK，也不包含 RCON、数据库或 SSH 密钥。MultiAddonManager 使用 [上游官方 Release](https://github.com/Source2ZE/MultiAddonManager/releases/tag/v1.6.2)；其准确运行状态和资源分发由实服报告记录。

已有本次部署服务器无需重复安装。迁移或恢复时：

1. 先备份 PMC 的 SQLite 文件、当前配置和 MAM 配置。保留 KeranStrat、地图与其数据目录。
2. 安装与系统匹配的官方 MAM，合并 `cfg/multiaddonmanager/multiaddonmanager.cfg` 中的 ID。不要覆盖已有 ID，也不要改当前地图为模型资源包。
3. 匿名下载 Workshop。默认缓存通常位于 `game/bin/linuxsteamrt64/steamapps/workshop/content/730/3821951835`；以实际 MAM 搜索路径为准。
4. 对实际 `_dir.vpk` 运行 `tools/verify_vpk.py`。完整保留 `_000.vpk` 等所有分卷。
5. 用 `tools/stage_model.py` 生成三个待合并配置；将审核后的配置和 `resource-catalog.json` 放到对应插件位置。目录中的 SHA 必须来自本机实际挂载 VPK。
6. 部署插件包中的 `addons/`，保留已有 `data.db`；首次安装才采用配置模板。必要时重启 `cs2`，检查 `meta list`、`css_plugins list`、`pmc_status` 和 `mm_print_searchpaths`。

`resource-catalog.json` 放在 PMC 插件目录。它包含已核验 VPK 的本机路径、SHA256 和允许使用的模型路径。缺包、包被修改、目录格式无效时不预缓存该模型，安全使用原版人物。Workshop 更新后必须重新校验并生成目录，不能继续使用旧 SHA。

## 上游复用与适配

源码位于 [PlayerModelChanger/](PlayerModelChanger/)，基于 [samyycX/CS2-PlayerModelChanger](https://github.com/samyycX/CS2-PlayerModelChanger) 的 `8c5eb1668e0083392c85826b967d2156e7030ba3`，保留 GPL-3.0 许可证和原作者署名。

- 目标框架和 CSS API 对齐现有服务器，不降级正式服 CSS。
- 保留上游菜单、选择服务和 SQLite；增加普通 `default` 别名及模型标识大小写兼容。
- 保存选择时完成 SQLite 提交，避免异步写入尚未结束就提示成功。
- 资源应用加校验目录和失效回退；出生回调校验完整实体身份。
- SQLite 更新为 Microsoft.Data.Sqlite 10.0.13、SQLitePCLRaw 3.0.5；实测原生 SQLite 3.53.4。
- 默认关闭检视摄像机、透明腿效果和随机模型；训练 BOT 不自动替换模型。
- 只调用人物 `SetModel` 和可选外观组设置；不写血量、装备、位置、碰撞尺寸或武器伤害，不增加伤害拦截。

**外观替换不等于已经证明命中盒完全一致。** 模型自身骨架、物理数据和实战命中仍需专门验证，详见测试报告。上游明确提示存在 GSLT 封禁风险；当前服务器无 GSLT，用户已授权部署，这不代表将来添加 GSLT 后没有风险。

## 后续批量模型

见 [EXPERIENCE_CN.md](EXPERIENCE_CN.md)。`tools/stage_model.py` 只生成暂存文件，可逐个模型合并，不自动写正式服、不更改游戏模式。后续更换路径、添加 Workshop 包、命中盒检查和客户端下载验收均按独立记录执行。

## 编译和独立检查

```bash
dotnet build server/PlayerModelChanger -c Release
dotnet run --project server/tests -c Release
cd server/tools
python3 -m unittest -v test_tools
```

编译环境需要 .NET 10 SDK。`server/refs` 为早期临时参考目录，不是构建输入，也不提交；实际项目固定引用官方 CSS API 1.0.376 NuGet。

模型资源分析使用了 [Source 2 Viewer](https://s2v.app)（[ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat)）。资源作者、历史模型成果和 Windows 恢复包沿用仓库原有记录。
