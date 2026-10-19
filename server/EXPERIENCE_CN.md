## 2026-10-19 Lime E 手臂编译与本地验证

Lime E 人物内嵌第一人称手臂已经真实编译，用户手动确认正常。后续处理手臂先读 [Lime E 专项经验](lime-e-windows/EXPERIENCE_LIME_E_CN.md)：检查真实第一人称网格和 LOD，区分空手截图与手臂缺失，先确认实际装备武器，再观察；继续使用预缓存驻留后官方 JS SetModel 路线。

## 2026-10-19 AG2 编译成品补充

三个模型已实际编译、通过官方脚本在本地加载，用户已手测确认正常。后续先读 [AG2 运行与交付经验](ag2-port/EXPERIENCE_AG2_CN.md)，复用预缓存驻留后官方 JS SetModel 的固定流程。[下载成品 Release](https://github.com/HifumiDaisuki01/CS2-MODEL-CHANGER/releases/tag/v0.3.0-ag2)。

# 人物模型集成经验与下一批模型流程

## 本次已经证实的事情

2026-10-18，匿名 SteamCMD 和 Linux MAM 均下载成功，资源进入 MAM 游戏搜索路径；29 个 VPK 条目通过 CRC 校验。PMC 成功加载，用户实测指令换模正常。这些证据解决了此前只有 Windows 本地展示、没有 Linux 分发实测的问题。

用户本次确认的是“模型指令可正常更改”。未据此扩写为所有动作、重生、重连、陌生客户端自动下载、其他玩家视角或完整命中盒对照均已通过。

## 1. Workshop 投稿与下载是两回事

- 页面类型是 Map，不代表必须把作品作为地图启动。角色资源包只挂载，不运行其中地图配置。
- 先调用公开 PublishedFileDetails API，核对 ID、consumer app 730、visibility 0、banned 0 和文件大小。邮箱验证不能代替下载测试。
- 本次最早出现 `invalid ID or server is not logged on Steam`，但 API 已证明 ID 有效；实际原因是下载请求发生在 Steam 登录完成之前。
- `Steam API Activated` 不等于已经登录 Steam。等待 `Connection to Steam servers successful`，再执行 `mm_download_addon <ID>`。不要因此要求用户提供主 Steam 账户。
- 匿名 SteamCMD 可交叉验证：`steamcmd.sh +login anonymous +workshop_download_item 730 <ID> validate +quit`。本次成功下载 8,216,824 bytes。
- 若真的返回权限、审核或访问限制，保存原始错误，继续做离线开发；不绕过审核、不冒充成功。

## 2. MAM 的双端分发

- 人物同时需要服务器和客户端资源，本次仅在 `mm_extra_addons` 添加 ID。
- `mm_client_extra_addons` 是仅客户端资源机制，不能代替服务端模型挂载，也不应机械重复同一 ID。
- 原有 ID 必须保留，使用逗号合并；不覆盖其他模型、声音或地图依赖。
- 安装 Linux 原生插件前核对发行包运行时和 glibc。本次 Debian 12 使用官方 steamrt3 包，验证官方资产摘要后安装。
- 下载完成后重新加载当前地图以预缓存；不调用 `host_workshop_map`，不把模型包地图写进启动参数。
- 用 `mm_print_searchpaths` 核对真实 GAME VPK 路径。看到 `mm_extra_addons` 有 ID 或缓存目录有文件，都不足以宣称挂载成功。
- MAM 服务端搜索路径成功不等于新客户端已经获取资源。首次接入需要没有本地缓存的真实 CS2 客户端，观察下载、重连和最终画面。

## 3. 分卷 VPK、路径和依赖

- `_dir.vpk` 是目录索引；实际数据可能在 `_000.vpk` 等分卷。任何一个缺失都应中止模型接入。
- `verify_vpk.py` 按条目校验 CRC 和长度，并对所有使用的归档计算 SHA256。读取大分卷使用流式读取，避免批量模型时将整个大 VPK 装入内存。
- 路径必须和 VPK 内大小写完全一致。配置用 `.vmdl`，不是 `.vmdl_c`；不能因为菜单显示名称相似就猜路径。
- 校验索引和 CRC 只能证明包结构与内容完整，不证明材质、动画、骨架和碰撞正确。
- 用 Source 2 Viewer 检查真实编译模型的 RERL、DATA、PHYS 等块；逐个核对材质、纹理、动画图和骨架依赖。原版依赖从合法游戏安装提供，不重复打包 Valve 原版资源。
- 本次模型引用原版 worldmodel/viewmodel 骨架和动画图，且包含 face morph 纹理；不要只按旧工程的文件数量判断新 Workshop 包是否完整。
- 命中盒和 ragdoll 物理数据不是同一个验收项目。不能因为 `SetModel` 回读成功或站立外观正确，就宣称命中判定不变。

## 4. 预缓存与应用时序

- 优先使用 CSS 的 `OnServerPrecacheResources` / ResourceManifest 注册资源，再在玩家出生后应用。
- 旧 Windows 恢复工程曾通过保留预缓存实体、等待资源驻留后应用模型解决 `Serialized nonresident asset`。不要同一帧创建、应用并移除临时模型实体。
- 本次服务端复用 PMC 资源预缓存，不引入新的临时预缓存 prop 或额外原生钩子。
- 死亡、换队、重连会创建新的 Pawn。延迟回调必须检查控制器序列号、UserId、Pawn 序列号、阵营和插件/地图代次，不能只记 Slot。
- 和已有武器/皮肤插件共存时，记录各插件出生回调时序。本次在正常装备初始化后延迟 0.35 秒应用真人选择；没有修改 WeaponPaints 配置。

## 5. 复用成熟插件，收敛变更范围

- 保留 PMC 的菜单、权限判断、选择服务与 SQLite；不重新实现一套玩家模型系统。
- 上游旧目标框架和 API 不直接套在新 CSS 上。本次按 CSS 1.0.376 / .NET 10 重编译，修正依赖版本。
- 上游内部默认项是 `@default`，普通 `!model default` 需要显式适配，不能只把菜单文字改成 default。
- 数据库写入完成后再确认选择，验证重新打开数据库仍保留 T/CT 设置。不能把内存缓存里的正确值当作重连持久化证据。
- 禁止未经许可的权限绕过；修正上游设置缓存时忽略 permissionBypass 参数的问题。
- 本次资源目录对 VPK 进行 SHA 校验，资源缺失或变动时安全回退原版。更新任一归档后应重新生成目录，不能使用旧 SHA。
- 默认不替换 BOT，避免 KeranStrat 回放、Defense 和 KSV 的 BOT 被另一插件出生逻辑改写。
- 默认关闭模型检视摄像机和透明腿效果，避免不必要的视角/实体干扰。保留将来按实际需求独立启用的空间。

## 6. 下一批模型的固定接入流程

1. 收到用户指定的模型来源、Workshop ID、希望的名字和实际路径；确认资源使用及再分发范围，不发布新的 Workshop 作品。
2. 逐包记录来源、下载时间、字节数、分卷文件、SHA256、模型路径、材质与骨架依赖。新增模型标识固定为小写，例如 `asuna`，不要复用已有标识映射到别的模型。
3. 仅下载一次官方 Workshop 缓存，优先直接检查 VPK，不批量展开整包，也不把大模型二进制塞进 Git。
4. 使用 `tools/stage_model.py` 合并到独立暂存目录。每次以最新暂存配置为输入，保留所有旧模型、权限、其他配置和 Workshop ID。
5. 检查配置 diff、资源校验目录、磁盘预算和回滚点。服务器至少留出 2 GiB 自由空间，模型库较大时先估算客户端首次下载量。
6. 按包验证挂载与预缓存，再验证新模型应用。分批安装、少量试用；出现错误先停用对应新增条目，保留已稳定模型。
7. 真实客户端分别验证 T/CT、模型菜单、恢复默认、死亡重生、连续换队、断线重连、另一玩家视角；用无缓存客户端确认自动分发。
8. 专门对照人物碰撞、蹲跳、第一人称手臂、武器持握、换弹、死亡、命中盒与伤害，再决定是否推广到所有玩家。
9. 验证 KS、KSD、KSV 及 Xray；保持它们的文件格式、AI 和原生回放逻辑不变。
10. 完成后提交配置、适配源码、测试边界和成品。没有完成的检查明确写“未验证”，不把服务端日志当成客户端验收。

当前白名单资源入口支持 `characters/` 模型路径；如果下一批包采用 `models/` 等其他前缀，应先扩展并测试资源校验规则，不通过改名配置伪造可用路径。

## 7. 批量接入示例（只生成暂存文件）

```bash
python3 server/tools/stage_model.py \
  --id aluona --name 'Aluona（阿洛娜）' --workshop 3821951835 \
  --model characters/models/aluona/aluona.vmdl \
  --vpk /actual/workshop/3821951835/3821951835_dir.vpk \
  --config /current/PlayerModelChanger.json \
  --catalog /current/resource-catalog.json \
  --mam-config /current/multiaddonmanager.cfg \
  --output /new/empty/stage-aluona
```

输出包含 PMC 配置、合并后的资源目录、MAM 配置和 VPK 校验报告。不会自动上传、重启或修改正式服。VPK 内依赖检查与真实客户端验收仍要另行完成。

## 8. 备份和回滚

本次部署前已备份相关配置、KeranStrat 插件及数据；一键回滚脚本保存在服务器：

```bash
bash /root/model-system-backups/20261018T033239Z/rollback.sh
```

它会停止服务，将本次新增的 PMC、MAM 及相关配置移动到备份目录中的 `rollback-removed-时间/`，再启动服务；模型选择数据库跟随保存，不删除。它不覆盖 KeranStrat 当前数据，不操作 Steam 账户，不删除 Workshop 缓存或地图。

批量扩充时另建新的回滚点，不复用“首次安装前不存在”的假设覆盖现有模型库。正式服已经产生的玩家选择必须保留。

## 9. 工具和上游来源

- [MultiAddonManager](https://github.com/Source2ZE/MultiAddonManager)，官方原生发行包。
- [CS2-PlayerModelChanger](https://github.com/samyycX/CS2-PlayerModelChanger)，本部署保留其 GPL-3.0 源码和署名。
- Powered by [Source 2 Viewer](https://s2v.app) ([ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat))，用于编译资源检查。
- 上游 PMC 明确提示 GSLT 封禁风险；无 GSLT 的当前部署不能证明其他认证环境同样没有风险。


## 10. 三人物包实际替换经验（3822432137）

- 旧 ID 替换为新 ID 时，同时从 resource-catalog.json 移除旧归档，保留 aluona ID 和内部路径，新增 myers / mika，避免玩家数据库选择失效。
- 本机实际观察：修改 extra addon 列表、重载同地图之后旧 VPK 仍可能留在进程搜索路径；需干净重启并再次检查，不能只看 cvar 值。
- 当前 map 是用户运行时选的 Workshop aim_map1v1cfg，永久启动入口仍是 Dust2。重启前捕获运行时地图/模式，Steam/RCON 就绪后恢复；人物包 ID 不能用作 host_workshop_map。一次性启动覆盖用后移除。
- 对新 VPK 的 70 项 CRC 校验成功，55 项人物资源哈希与编译交付完全一致。资源包可能由发布器补入 metadata/sound/postprocess，不能只按原 ZIP 文件数判错。
- 诊断工具需区分 Bool / Int32 等 ConVar 类型；通过真实 RCON 快照恢复原值。反射调用当前 PMC 的公开应用 API 可验证服务端模型状态，不应把测试 BOT 的显式复活重应用扩写成真人自动持久化验收。
- 12 项实服 BOT 检查、8 项临时 SQLite/资源测试、183 个原文件及真实玩家库逻辑校验记录见 deployments/3822432137。
