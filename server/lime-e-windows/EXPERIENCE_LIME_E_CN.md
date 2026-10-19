# Lime E 人物与手臂的编译、测试经验

本次以昨日 AG2、阿洛娜的正确流程为基础，避免重新探索已经确认的路径。

## 1. 先认清手臂交付方式

这次是人物本体内嵌第一人称网格，不是寻找另一个不存在的 lime_e_arm.vmdl。读取真实 selected-models.json，逻辑模型路径为 characters/models/exg/chrisan/lime_e/lime_e.vmdl。

原 phase2 手臂有 48691 顶点、42 个实际蒙皮骨骼和 38 个手指骨骼，已经按人物的世界绑定矩阵重绑，保留 UV、蒙皮权重、拓扑和材质。编译机不应擅自重新下载或替换为默认手臂。

## 2. 编译与静态检查

使用完整本地交付的 Run-Build.ps1 / Build-AG2.ps1，在新的 lime_e_ag2_时间戳 addon 编译。本次实际输出退出码 0，1 compiled / 0 failed。

随后执行 Verify-Compiled.ps1。除 AG2 引用、核心骨骼和材质闭包，还必须检查 m_meshGroups 的 firstperson_default / thirdperson_default、实际 m_refMeshGroupMasks，以及第一/第三人称 m_refLODGroupMasks。空分组不算手臂成功。

原有 139 个材质纹理文件重新核对 SHA256，全部未变。原外观 10 组和 4 个材质组保留，但插入第一/第三人称组会改变旧组索引，不能把旧索引配置机械套用。

本机编译器 PE FileVersion 为空；记录其 SHA256、游戏 patch 1.41.9.1、Steam build 25966348、SourceRevision 11133601，不编造独立编译器版本。

## 3. 固定的本地运行流程

- 使用独立 addon 的松散编译资源，启动 -tools -addon；path 实际确认 GAME 搜索路径。
- 等 status 中 Client Connected 且本地玩家 active。
- 在本地离线回合创建带模型的 prop_dynamic，使用花括号 KeyValues，保留实体并等待至少 8 秒。
- 再创建官方 point_script，通过 CSPlayerPawn.SetModel 应用人物，用 GetModelName 记录 before/after。
- 第一人称观察手臂，第三人称观察本体。不要将 API 成功和实际画面混为一谈。

本次以上步骤实际完成，日志确认从原版 CT 模型变为 Lime E。用户随后手动观察，明确确认手臂没有问题。

## 4. 空手不是手臂损坏证据

第一轮自动截图没有武器和手臂，同时日志显示 active weapon=none。该画面不能用于判定人物的手臂几何失败。

测试脚本尝试在同一帧 DestroyWeapons、GiveNamedItem 自动装备，存在装备时序问题。之后使用游戏原生命令 give weapon_m4a1_silencer，并显式 slot1，日志确认实际武器 weapon_m4a1、弹匣 20。武器实体类名不一定与给出的物品名完全相同。

最终交付的测试脚本移除了这套清空武器的临时辅助函数，保留应用、状态回读和动作事件；启动器使用原生命令给刀并选择 slot3。给武器后必须等游戏 tick，再读取或截图，不在同一命令里用即时 none 判失败。

若以后添加弹药测试，按本机 point_script.d.ts 核对 API：GetMaxClipAmmo / GetMaxReserveAmmo 属于 GetData() 返回的武器数据，不应凭记忆直接调用武器实体上的不存在方法。

## 5. 保留昨日有效的工具经验

VConsole 使用本机 29000 带帧协议，不是纯文本 netcon。只连 127.0.0.1，不转发公网。保存 echo 标记、PRNT 文本和原始帧。

游戏和 Asset Browser 属于同一进程，截图必须精确匹配 Counter-Strike 2 窗口；PowerShell FindWindow 的空类名采用 NullString.Value。截图进程启用 DPI aware，按物理窗口矩形截图。

不要用未经验证的绝对路径调用引擎 screenshot；昨天已实际触发 Invalid screenshot path 主动中止。外部窗口 CopyFromScreen 更安全。若退出，读取 minidump Comment 中 AbortMessage，而不只猜显卡或模型。

只在明确激活的游戏窗口内测试输入。+attack、+duck、+forward 等命令必须有对应释放。截图菜单遮挡、未装备武器、未入服均是测试前提不成立，不是模型通过或失败。

## 6. 最终证据与后续

自动验证：真实编译、模型解析、第一人称网格和 LOD、AG2 图与骨架、139 项保留资源哈希、真实 GAME 搜索路径和官方 SetModel 回读。

用户验证：实际进游戏观察并确认手臂正常。用户没有逐项列出全部枪械、换弹、左右手、死亡和命中盒对照，不能把该确认扩写成完整验收矩阵。

用户手测后游戏已关闭，最终复核没有为截图重启打断用户，也没有将早期空手截图冒充成功画面。新的便携启动器完成语法检查，但未再次完整冷启动复测；组成步骤成功不等于新封装已实测。

发布成品到单独 GitHub Release，保留昨日三人物、五人物及 Linux 历史。ModelDoc/DMX 美术源文件仍只留本地；不自动合并现有 Workshop 包，不改现有 ID，不改正式服务器。上传后重新下载 ZIP 和校验文件，核对整包 SHA256。