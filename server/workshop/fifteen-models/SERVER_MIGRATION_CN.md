# 人物系统更换服务器说明

## 结论

可以复用本包及现有插件，不需要重新编译人物或重新上传Workshop；但**不能只复制一个插件DLL**。新机器必须准备兼容的基础环境、挂载相同Workshop、迁移配置/选择数据库，并重新核对资源catalog。

## 需要迁移/准备的内容

| 内容 | 路径（相对 game/csgo）或设置 | 用途 |
|---|---|---|
| Linux CS2 + 兼容的 Metamod、CounterStrikeSharp | 原安装流程；新版本先检查兼容性 | 运行环境，不盲拷 Windows 原生库 |
| MultiAddonManager | addons/multiaddonmanager/、addons/metamod/multiaddonmanager.vdf | 下载与挂载资源 |
| MAM配置 | cfg/multiaddonmanager/multiaddonmanager.cfg | `mm_extra_addons "3823495199"`；保留其他已有必要设置 |
| 完整PlayerModelChanger目录 | addons/counterstrikesharp/plugins/PlayerModelChanger/ | DLL、依赖、语言资源及SQLite数据库等全部保留 |
| 人物配置 | addons/counterstrikesharp/configs/plugins/PlayerModelChanger/PlayerModelChanger.json | 十五人物ID、权限、T/CT设置 |
| 选择数据库 | PlayerModelChanger目录内data.db | 按SteamID保留玩家选择；停服复制或SQLite在线backup，不能随意只拷活跃数据库主文件 |
| 实际下载归档对应的资源目录 | PlayerModelChanger/resource-catalog.json | VPK实际路径与SHA256，迁机后可能必须重建 |

当前模型菜单不应混挂旧人物Workshop ID。`mm_client_extra_addons` 不需要为了这套方案再重复添加同ID。不要用host_workshop_map加载人物资源包，不改地图或游戏模式。

## 关键坑：catalog里的绝对路径

本项目 `ResourceCatalog.cs` 会逐个打开 `Archives` 中的**实际文件路径**，计算SHA256；路径错误、文件不存在或哈希变化，就安全禁用自定义模型。因此新服务器安装目录不同，不能机械复制旧catalog后就算完成。

在新服务器通过MAM下载3823495199，定位真实的 `3823495199_dir.vpk` 及分卷；使用 [verify_vpk.py](../../tools/verify_vpk.py) 检查所有entry CRC并得到ArchiveSHA256，核对已部署人物资源清单后重新生成catalog的Archives与Models。使用包内配置模板不能替代这一步。若实际路径、内容哈希完全相同，旧catalog可复用，但仍应核对。

## 建议迁移顺序

1. 备份原服插件目录、PMC/MAM配置和一致性SQLite备份。新服安装兼容环境，保留原服作回滚点。
2. 安装MAM，迁移完整PMC及配置/数据库，修正归属和读写权限，使运行CS2的账号可写数据库。
3. 仅挂载当前人物Workshop ID，等待真正下载完成；不能把“已加入下载队列”当成完成。无须操作Steam主账户。
4. 校验实际VPK并生成新catalog，再启动/必要时重启CS2，确认当前地图/模式正确。
5. 控制台检查 `meta list`、`css_plugins list`、`pmc_status`。人物插件应报告 `configured=15; verifiedResources=15; resourceError=none`，启动日志应显示挂载3823495199与15个人物预缓存。
6. 普通客户端进服验证下载、`!models`、`!model default`，换队/重生/重连后保留选择。角色选择使用SteamID，不依赖旧服务器IP；数据库正确迁移后可延续。

## 与其他插件的关系

KeranStrat和人物系统是分开的。若整台服务器也要迁移KeranStrat，必须另行保留其插件、战术数据、配置、原生BotController桥接及依赖；只迁人物插件不会自动带走战术。武器皮肤/邮件/网页系统等也各自有独立数据，不能把本清单当成整机备份。

不必为了更换服务器重新上传这些人物。只要Workshop可访问、当前游戏/插件版本兼容、配置和资源路径正确，就可以在新服继续使用。实际迁移时按上面的检查点验证；未来CS2更新可能需要同步兼容插件版本。
