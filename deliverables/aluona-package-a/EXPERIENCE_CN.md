# 阿洛娜本地显示：实现经验与排错记录

## 最终真正成功的路线

**已有编译资源 → 独立 Workshop Tools addon 的松散文件 → 客户端完全入服 → 创建模型预缓存实体 → 等待资源驻留 → 官方 JavaScript SetModel → 真人和 BOT 实际显示。**

本次没有重新编译人物、材质、纹理，没有修改官方 VPK 或 gameinfo，没有安装客户端注入程序，也没有发布创意工坊。只编译了我们新写的一个测试 JavaScript。

成功证据：`ALUONA_STAGED_COLD_THIRDPERSON.png`、`ALUONA_STAGED_COLD_CROUCH.png`、`ALUONA_STAGED_COLD_FIRSTPERSON.png`，以及 `staged-cold-vconsole.log`。截图可见真人、带名字的 BOT、站立持枪和蹲姿；第一人称可见自定义白色手部。用户最终也观察后关闭了游戏。

## 1. 先辨别“启动失败”和“模型失败”

专用服务器旧日志已经出现 `ss_loading -> ss_active`、`Created physics for de_dust2`、`64 player server started`。后来重新运行无 addon、无模型插件的 Dust2 基线，也成功启动。

所以地图光照、visibility、缺少可选 cfg 等警告不能单独当成地图启动失败。上一轮服务器由脚本到时停止，真正没完成的是 addon 挂载和模型应用。

## 2. Tools 崩溃必须读转储，不要只猜显卡

两份旧 minidump 的 Comment 流给出了明确 AbortMessage：测试 addon 的 `pak01.vpk` 加载失败。同一转储同时显示 RTX 5060 已成功创建 DX11 交换链，DXLevel 为 111。

原测试把单文件包放成 `pak01_dir.vpk`。保留旧文件，以 `pak01.vpk` 副本重试，Tools 即越过原崩溃点。这里修的是本次新建 addon，没动官方 pak01 文件。

经验：Source 2 Viewer 能校验一个 VPK，并不等于游戏按当前名称、位置和加载入口就能挂载它。

## 3. 一定查看运行时搜索路径

在本机 dedicated 中，`-addon` 没有进入实际 GAME 搜索路径；自定义 cfg 因此也找不到。

在 `-tools -addon cs2cm_aluona_localtest` 下，日志和 `path` 确认 addon 目录进入了 GAME 搜索路径，但没有样本 VPK 的独立挂载条目。因此最终本地验证采用 **松散编译资源目录**，不是冒充完成了 MAM/Workshop VPK 分发。

从原有 `cs2cm_sample.vpk` 原样提取 14 个 `characters/` 编译资源，保留完整相对路径，逐个对照 VPK CRC32，全部一致。没有加 `-d` 反编译，也没有重编译模型。

阿洛娜使用六个材质：body、face、fuku、hair、morph、s；样本自带七个纹理，包括 face_vmorf。动画图、角色 view/world 骨架，以及三个默认 AO/metal/normal 共享纹理由原版提供。不能因为原包里有同名默认纹理，就把不同版本覆盖进游戏。

## 4. 物理路径与逻辑路径分开

磁盘：`characters/models/aluona/aluona.vmdl_c`。

实际成功的官方 API 调用：

```js
pawn.SetModel("characters/models/aluona/aluona.vmdl");
```

同样的逻辑路径也用于人物插件配置。不要改名去掉磁盘文件的 `_c`，也不要把“插件用逻辑路径”误解为需要生成未编译的 `.vmdl` 源文件。

## 5. 不要沿用旧版实体命令语法

裸写 `ent_create prop_dynamic model ... targetname ...` 在本机创建出的实体没有模型和目标名。实际有效的是花括号 KeyValues 格式：

```text
ent_create prop_dynamic { "model" "characters/models/aluona/aluona.vmdl" "targetname" "cs2cm_aluona_precache" "solid" "0" }
```

本机玩家实体确实列出了 SetModel 输入，但直接 `ent_fire player SetModel ...` 没得到有效模型，实体调试信息显示模型被清空。不能因为命令没有报 unknown 就判定应用成功。

## 6. 从本机官方示例找正确 API

实际读取了：

```text
content/csgo_addons/cs_script_demo/maps/scripts/mdlchange.js
content/csgo_addons/cs_script_demo/maps/scripts/point_script.d.ts
```

官方示例使用 `cs_script/point_script` 模块与 `BaseModelEntity.SetModel`。声明确认 CSPlayerPawn 继承它。

我们据此创建 `aluona_test.js`：查找 `player` 实体，确认是 CSPlayerPawn，调用 SetModel，并用 GetModelName 回读 before/after；注册 `cs2cm_apply` 便于重试，还注册 OnPlayerReset 回调。

只用官方 resourcecompiler 编译这个新 JS，生成 `maps/scripts/aluona_test.vjs_c`。然后运行：

```text
ent_create point_script { "targetname" "cs2cm_aluona_script" "cs_script" "maps/scripts/aluona_test.vjs" }
```

这不是内存注入，也不是 CounterStrikeSharp 插件；是 CS2 自己提供的地图脚本机制。因此本地成功不能被写成“PMC 插件已经运行通过”。

## 7. 最重要的坑：资源驻留与客户端就绪

第一次暖机成功后，做了冷启动复测。固定睡眠并不可靠：cfg 可能在客户端载入完成前执行，甚至 jointeam 尚未可用。

另一次把预缓存实体和玩家应用放在同一帧，并提前移除预缓存实体，触发：

```text
Serialized nonresident asset characters/models/aluona/aluona.vmdl.
```

**最终通过的顺序**：

1. 等 `status` 显示客户端 Connected 且玩家 active，实际已能操作地图。
2. 创建带阿洛娜模型的预缓存实体，让它经历正常资源和网络处理。
3. 等至少 6 秒。
4. 再创建 point_script，调用官方 SetModel。
5. 不在应用同一帧移除预缓存实体。确认人物实际显示后再考虑清理；最简单是退出测试时一起清除。

最终全新进程按该顺序通过，日志记录 1 真人、9 BOT，以及从原版 T/CT 模型变为阿洛娜的 before/after。截图同时确认了 T 真人、带名字的 T BOT；第一轮还确认了 CT 真人。

## 8. 什么算成功，什么仍未证明

本次成功：阿洛娜在本地 Dust2 真人/BOT 实际显示；材质没有紫黑缺图；站立、蹲姿及当前 USP/Glock 第一人称持握画面已观察。

未证明：全部动作、全部武器兼容、碰撞和命中盒不变、独立 VPK 的 MAM 挂载与客户端网络下载、PMC 与现有 Linux CSS 版本兼容、KeranStrat 回放。没有连接远程服务器。

PMC 1.8.6 的真实配置已经核对并保留，但发行二进制引用 CSS API 1.0.255，不能仅凭新版本 CSS 的版本号推断兼容。正式服仍需独立测试与有权分发的资源入口。

## 9. 排错时保留这几类证据

- 基线启动日志：证明游戏本身可以运行。
- minidump 的 AbortMessage：给出 Tools 的具体失败对象。
- `path`：证明真实挂载目录。
- VPK 成员与提取文件 CRC/SHA：证明实际测试的是包内同一套资源。
- SetModel 的 before/after：证明改的是玩家实体，不是只生成了一个道具。
- 带 HUD、玩家/BOT 名字的实际窗口截图：证明客户端确实渲染。
- 冷启动成功日志：证明不是依赖前面试验碰巧留下的缓存状态。

早期失败日志与截图也保留了，不能把它们重新命名成成功证据。最终以 `ALUONA_STAGED_COLD_*` 为准。

## 10. 成品启动器修复：双击启动不等于自动切换

第一版 CMD 只是启动地图，把预缓存和应用两个命令留给用户手动执行。因此用户只双击 CMD 时看到默认人物，不能归咎于模型资源。这是交付流程缺口。

现在默认 `Start-Aluona-Test.cmd` 调用自动版 PowerShell：连接本机测试控制台，等待 status 确认客户端 Connected 且玩家 active，执行预缓存 cfg，等待 6 秒，再执行应用 cfg 并回读玩家模型路径。失败时保留日志并报错，不把启动地图当成完成切换。原手动启动器另存为 `Start-Aluona-Test.manual.ps1`。

实现时还发现端口与协议必须匹配：本机 `-vconsole` 的 29000 端口使用带帧头的消息协议；单独指定 `-netconport 29001` 得到的是纯文本控制台。不能把原来的 VConsole 二进制报文发给纯文本端口。修复后沿用已经实测的 29000 端口与对应 C# 协议助手。

自动版全新启动复测日志：`evidence/AUTO_LAUNCHER_FIXED.log`。截图：`evidence/AUTO_LAUNCHER_FIXED.png`。本次没有人工输入模型切换命令，日志确认 10 个玩家实体应用模型，截图实际显示 CT 真人与 BOT 阿洛娜。启动提示 `AUTO_APPLY_CONFIRMED` 只表示 API 回读确认；实际显示结论由截图补充。
