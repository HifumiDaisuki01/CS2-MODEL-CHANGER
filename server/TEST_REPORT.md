# Linux 集成测试报告

日期：2026-10-18。部署范围为已有 Linux CS2 服务器上的人物选择、Workshop 资源挂载与持久化适配。

## 已完成

| 检查 | 证据与结论 |
|---|---|
| 环境检查与备份 | CS2 1.41.9.1、MM 1481、CSS 1.0.376；配置、KeranStrat 与数据已备份，一键回滚脚本已生成 |
| 原生插件加载 | MM 列出 MultiAddonManager 1.6.2，保留 CSS 与 BotController |
| Workshop 公开状态 | API result=1、app=730、visibility=0、banned=0；作品 Aluona Model |
| 匿名下载 | SteamCMD 成功下载 8,216,824 bytes；MAM 亦报告下载成功 |
| VPK 结构 | VPK v2，29 个条目 CRC/长度有效，目录和数据分卷均计算 SHA256 |
| 模型实际路径 | `characters/models/aluona/aluona.vmdl_c`，配置使用 `.vmdl` |
| 依赖检查 | 21 个模型/材质资源引用：13 个在包内、8 个由原版游戏提供；骨架引用另外由 Source 2 Viewer RERL 核对 |
| Linux 挂载 | `mm_print_searchpaths` 包含该 Workshop 的 GAME VPK 搜索路径；仍运行 Dust2 |
| PMC 加载 | `Player Model Changer 1.8.6-aluona.1` 加载，configured=1、verifiedResources=1、resourceError=none |
| 命令注册 | RCON 调用 `css_models`、`css_model aluona` 返回仅限客户端执行，证明命令已注册 |
| 真人换模 | 用户进服实测，明确确认模型指令可正常更换人物 |
| 持久化独立检查 | SQLite 的 T/CT 选择、新实例读取、默认选择、SQL 参数化检查通过 |
| 资源保护独立检查 | 已校验归档允许模型；被修改、缺失、坏 JSON 和非法路径安全拒绝 |
| 工具检查 | 8 项 Python 测试通过：预加载字节、分卷、CRC、缺包、配置保留、路径不匹配、防覆盖、重复 MAM 指令 |
| 编译 | 对齐 CSS 1.0.376 / .NET 10，最终构建 0 警告、0 错误；6 项 .NET 检查通过，SQLite 3.53.4 |
| 运行健康 | 最终 `cs2` active；11 个 CSS 插件加载；当前主进程日志未发现 FATAL ERROR 或 Unhandled exception |

服务端 MAM 搜索路径、命令注册和用户的换模确认，是三种不同的证据，没有互相替代。

## 未完成，不作为成功宣称

- Windows 开发机没有 Steam/CS2 客户端，自动化代理没有进行真正的客户端连接或画面观察。
- 用户确认换模正常，未单独明确确认无缓存客户端首次下载、不同玩家视角、完整菜单操作、连续换队、死亡重生和重连后的自动恢复。
- 自动 BOT 生命周期检查首次因空服等待/休眠条件超时，尚未应用模型，不能据此宣称 T/CT 生命周期检查通过。辅助检查逻辑已补充临时解除并恢复等待/休眠设置；用户开始自行测试后没有再运行长时间自动化检查。
- 不能宣称人物命中盒、完整碰撞行为和所有武器伤害已经和原版逐项一致。代码不修改血量、装备、碰撞尺寸和伤害钩子，但模型自身的骨架与物理/命中数据仍需实战对照。
- 现有 KeranStrat 保留并加载；本次没有重复完整 KS/KSD/KSV/Xray 回归。

## 数据保护

原有插件二进制和正式配置的摘要未改变。备份快照覆盖的 488 项文件中，有 1 份 `.ks` 战术归档在用户活动间隔中改变；当前版本原样保留，没有将旧备份覆盖回去，未将其记作“全部数据摘要不变”。见机器记录 `reports/final-server-state.json`。

没有修改 CS2 启动参数、官方 gameinfo、现有皮肤插件设置，也没有操作 Steam 主账户。新增 PMC 数据库与配置位于其独立目录；默认不给训练 BOT 换模。

## 后续人工检查步骤

1. 用没有缓存本作品的客户端加入，确认自动下载与重连完成。
2. `!models` 选择 Aluona，另一玩家检查第三人称、第一人称手臂、材质和动作。
3. `!model default` 恢复默认，然后分别在 T/CT 选择，死亡重生、连续换队、断线重连后确认选择。
4. 对照模型应用前后的碰撞、蹲跳、头身四肢命中及同武器伤害，不把视觉大小当作命中盒证据。
5. 进入 KS、KSD、KSV，检查真人模型、训练 BOT、回放和 Xray，确认无新增严重日志。

出现缺资源时先检查 `pmc_status`、VPK SHA 和 MAM 搜索路径，不删除玩家选择数据库；先恢复默认外观，再排查对应新增包。
