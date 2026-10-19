# Linux 三人物模型包部署 · Workshop 3822432137

状态：**已部署，服务端验证通过；真实客户端联网分发与生命周期验收待完成。**

## 玩家使用

- `!models` 打开菜单。
- `!model aluona` / `!model myers` / `!model mika`。MIKA 按用户确认对应 dujiaoshou，内部路径不改名。
- `!model default` 恢复默认。

三个角色均配置为 T/CT 开放、无附加权限。SQLite 持久化、普通真人出生后的延迟应用和 default 适配沿用已在使用的 PMC，不改写玩家数据库，不自动改 BOT 模型。

## 实际验证结果

| 项目 | 结果 |
|---|---|
| 公开 Workshop / app 730 / 未封禁 | Steam API 通过 |
| Linux MAM 下载新 ID | 成功，25,814,806 字节 VPK |
| VPK 目录与内容 CRC | 70 项全部通过 |
| 三角色模型、材质、贴图 | 55 个资源 SHA256 与 GitHub 编译交付完全匹配 |
| 新挂载 / 旧挂载清除 | 实际搜索路径有 3822432137，无 3821951835 |
| PMC 资源目录 | configured=3，verifiedResources=3，resourceError=none |
| 模型预缓存 | 三个 .vmdl 均有 Precache 日志 |
| 实际 PMC 模型 API / T、CT BOT | 3 模型 × 2 阵营 × 初次/复活后显式重应用 = 12 项通过 |
| 每次应用前后碰撞边界、血量、护甲 | 12 项一致 |
| 测试 BOT 原版模型恢复 | 通过 |
| SQLite 重开实例与默认项持久化 | 8 项独立回归检查通过；在临时测试库运行 |
| 正式玩家 SQLite | integrity_check=ok，逻辑内容 SHA256 未变 |
| 原插件与配置保护 | 183 个原有文件 SHA256 未变；PMC DLL 也未替换 |
| KeranStrat / 原插件 | 原有 11 个插件 LOADED，KS 0.5.5 / BotController ABI 22 |
| 地图、模式最终状态 | aim_map1v1cfg，game_type=3、game_mode=0，与部署前相同 |

`reports/server-probe-report.json` 来自服务器实际执行，不是模拟成功。它明确标记未做客户端验收；12 项只证明对测试 BOT 调用同一 PMC API 后的服务端状态，以及 Respawn 后的显式再次应用，不能等同真人自动出生/重连。碰撞边界一致也不证明全部命中盒、伤害或 ragdoll 等价。

## 挂载处理与遇到的问题

仅修改 mm_extra_addons 和重载当前地图时，旧 VPK 在本版引擎/MAM 的搜索路径里仍然存在。为真正清除旧资源执行进程重启。一次仅以 host_workshop_map 冷启动的尝试未初始化网络地图；随后使用原有 de_dust2 入口完成启动，再在 Steam/RCON 就绪后恢复原 Workshop 地图 3418431100（aim_map1v1cfg）与原模式。**期间短暂加载了 de_dust2 作为启动过渡，最终地图和模式已恢复。** 未把人物包作为地图启动。

一次性 systemd override 已删除、daemon-reload 完成；永久启动脚本与服务配置保持原状。旧 Workshop 缓存保留用于回滚，不在挂载或新资源白名单中。

临时 ThreeModelProbe 初期两次在读取 ConVar 类型时中止，尚未应用任何模型；失败报告保留在 reports/probe-attempt1-fail.json 和 probe-attempt2-fail.json。最终使用真实 RCON 快照 baseline.json 恢复参数的版本完成 12 项检查。临时插件已卸载并移出 plugins；CSS 注册表仍显示一条 UNLOADED 历史记录，实际原有 11 个插件处于加载状态。BOT 已清理，5 项测试参数恢复原值，人数 0/0。

## 客户端待验收

MAM 的 mm_extra_addons 已设置为新 ID，mm_client_extra_addons 沿用空值，没有重复配置两种下载方式。它负责新连接的资源分发；当前机器未实际启动 CS2 客户端，因此以下均为**未验证**：

1. 无本地缓存客户端入服自动下载并显示三模型。
2. 真人菜单逐项切换、T/CT、!model default。
3. 真人死亡重生、连续换队、断线重连后保持选择。
4. 其他玩家看到相同人物、第一人称手臂和各类武器动作。
5. 多人 KS/KSV/KSD/Xray 完整运行回归与命中盒/伤害对照。

## 回滚

服务器备份含原 PMC/MAM 配置、原 PMC 插件目录、原玩家库文件及 SQLite 一致快照：

```sh
bash /root/model-system-backups/20261019T013330Z-three-models/rollback.sh
```

该脚本恢复旧配置和旧资源白名单，并通过干净进程启动清除新挂载、请求恢复原 aim_map1v1cfg 与 3/0 模式；保留当前玩家数据库，不把升级后玩家选择回退为旧快照。脚本已生成并审阅，未在正式服实际执行回滚。私有一次性启动资料留在服务器，不提交 GitHub。

configs/ 是本次实际配置快照；其他服务器应合并设置，不覆盖自己的数据库、权限、其他 addon 和启动配置。
