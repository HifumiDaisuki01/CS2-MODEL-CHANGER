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

## 7. 可复用的手部迁移流程（2026-10-20 补充）

### 先分清三种情况

1. 原人物只有旧外部手臂，内嵌 firstperson_default 为空：需要找真实手臂几何并重绑、编译；当前 Lime E 的旧源工程采用这条路径。
2. 人物已具备 AG2、内嵌第一人称网格和标准手指正权重，只残留缺失的 character_arm_config：可考虑结构化清理旧外部引用。十二人物中的白洲梓、日富美、菲比、Chiffon Fox采用此法；没有改几何，没有模型重编译。见 [修复源码与报告](../workshop/twelve-models/README.md)。不能把此方法用于只有外部手臂的模型。
3. 有AG2节点但同时保留旧图/animset：是混合状态，不能仅看到 vnmgraph 就判完成。本次新版合集 Lime E 就属于此类，仍需处理真实配置/动画包含关系，不能盲删RERL或占位文件。

### Lime E 为什么必须处理绑定矩阵

原始人物与phase2手臂的骨骼名字相似，绑定姿势却不同；只改骨名或把DMX直接塞进人物会产生手臂位移、扭转和持枪错位。实际做法：

- 读取人物和手臂完整父子层级，累乘得到各骨骼世界绑定矩阵，先交叉验证 ModelDoc 与 DMX 的局部绑定姿势一致；本次最大差约4.95e-7。
- 按名字映射骨骼，左右侧与twist必须匹配人物真正采用的大小写；检查一对一，避免重复创建共享twist骨骼。
- 对每个正权重顶点，用刚体绑定转换 `M_i = B_body_world_i * inverse(B_arm_world_i)`，按原权重混合 `p_new = sum(w_i * M_i * p_old)`。这是本次采用的重绑近似流程，不是所有蒙皮/缩放场景的通用精确解。
- 法线和切线只用旋转部分变换，再归一化，切线保留手性w；UV、蒙皮索引/权重与面拓扑保持原值。当前实现假定刚体骨骼变换；含缩放/剪切的模型不能直接套用，需要一般逆矩阵和正确的法线变换。
- 重建与人物一致的父子关系及root_motion，序列化DMX后再读回核对，不能只校验内存对象。本次原phase2手臂48691顶点，42个实际蒙皮骨骼、38个手指骨骼；最大权重和误差约7.45e-9。顶点因重绑产生位移是预期，不等于误差为零；单骨骼影响顶点往返误差小于9e-14，不代表混合权重顶点已通过全部动态姿势验证。
- 把真实手臂网格加入人物的第一人称分组与LOD，第三人称保留人物本体；保留外观组/材质组/附件，核对组索引改变。原139项材质纹理SHA256未变。保留物理和命中盒数值不等同于游戏伤害测试已完成。

源码参考：[prepare_lime.py](source-build-tools/development-reference/prepare_lime.py)、[finish_package.py](source-build-tools/development-reference/finish_package.py)。脚本含原开发路径，明确作为工程记录，不能直接当通用批处理入口。源码阶段证据在 reports/source-stage-*；Windows实际编译报告保持原样。

### 手部验证必须看实际权重

通过 m_meshGroups 找到 firstperson_default 位，结合 m_refMeshGroupMasks 和 LOD0 映射选出实际网格；再在带skin的GLB中解析JOINTS_0/WEIGHTS_0并检查正权重是否影响 hand_L/hand_R、finger_*和arm骨骼。单独看38个骨骼名字、文件名带arms或有网格分组都不够。

本次审计发现 Source2Viewer 普通GLB导出可能不带skin；必须使用 `-d --gltf_export_format glb --gltf_export_animations` 再做骨骼权重检查。带动画导出并不保证外部动画资源完整，导出日志的缺失引用仍必须记录。GLB导出成功与游戏验证不是同一件事。

### 当前版本选择

当前部署的是 v0.5.0 Windows实编译 Lime E，模型SHA256 `981f1d46fa80ad004972d2e04276ed6fde80208993191d47a832d4bf67ca778d`，已合入 Workshop 3823301202。用户确认十二人物包游戏内正常，仍不能扩写为全部枪械/命中盒专项测试。

新版合集另有同路径 Lime E，SHA256 `dc09ec62b0ec86c9da80d54c39af604fc9550b981119eb974ad73a709ae5928a`。它有AG2、标准骨架和48693个第一人称蒙皮顶点，但还保留旧 player_ct.vanmgrph 和 animset_ct.vmdl。没有证据表明比当前版更兼容；保留已实测版。两个版本同路径，不应同时挂载。

[本次七个人物及新包Lime E详细审计](../model-audits/2026-10-20-seven-models/README.md)。未来可以自动化依赖、骨架、蒙皮和分组审查，按实际缺陷分类；重绑与动画行为不能仅靠数量/标签自动判定成功。
