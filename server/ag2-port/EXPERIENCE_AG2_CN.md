# AG2 编译、运行验证和快速交接经验

本次延续 aluona/EXPERIENCE_CN.md 与 server/EXPERIENCE_CN.md，补充三个人物的真实编译和本机运行经验。以后开始前先读这三份文件，避免重新试错。

## 一、最快的可靠路线

1. 找完整本地交付包，不以 GitHub 源码归档替代人物 ModelDoc、DMX、材质和贴图。先读 selected-models.json，模型文件名以清单为准。
2. 读取 Steam libraryfolders.vdf 和 appmanifest_730.acf 自动定位真实 CS2；确认 Workshop Tools DLC 与 resourcecompiler.exe、resourcecompiler.dll 存在。
3. 检查 Build-AG2.ps1 的输入和输出路径，在新的带时间戳 addon 中编译，不能覆盖已工作的阿洛娜或其他工程。
4. 同时检查退出码、真实新 .vmdl_c 和完整 stdout/stderr。调用资源编译器成功不等于人物运行完全正确。
5. 执行 Verify-Compiled.ps1，再解析材质、纹理和 PHYS；核对基础 VPK 中依赖、核心骨骼、AG2 引用、旧动画图清除、阿洛娜与原资源哈希和路径冲突。
6. 使用 -tools -addon 指向该独立 addon 的松散编译资源；通过 path 确认实际 GAME 搜索路径。不要把模型包作为 Workshop 地图启动。
7. 等 status 显示 Client Connected 且本地玩家行 active，再执行预缓存 cfg。不能只等待固定启动秒数或看到游戏进程就应用模型。
8. 使用花括号 KeyValues 创建 prop_dynamic，并保留全部预缓存实体。至少等待 6 秒；本次封装为 8 秒。不能在同一帧创建、应用和删除预缓存实体。
9. 创建官方 point_script，调用 CSPlayerPawn.SetModel，并用 GetModelName 记录 before/after。不要把无报错的 setmodel/ent_fire 命令当成正确应用证据。
10. 实际观察三个人物和动作，记录截图、日志与用户手测范围，最后再打包。API 回读与用户画面是两类证据。

## 二、本次具体故障与修复

### Windows PowerShell 默认参数

在 param 的默认表达式中直接使用 PSScriptRoot，曾得到空路径并在 Split-Path 阶段失败，编译器尚未运行。先显式传入 PackageRoot/S2V 可继续；永久修复是在 param 后解析两个默认路径。修复后已通过默认调用方式实际编译三个人物。

记录每次 resourcecompiler 的退出码、输入输出、stdout/stderr 和编译器 SHA256。本机编译器 PE FileVersion 为空，不能编造版本号；使用游戏 patch 1.41.9.1、Steam build 25966348、SourceRevision 11133601 和编译器哈希共同识别。

中文路径的 PowerShell 脚本采用 UTF-8 BOM，或用 PSScriptRoot 推导目录。Windows PowerShell 5 对无 BOM 的中文脚本曾错误解码，导致 GDI+ 保存路径报错。

### 真正读取崩溃原因

不能只看 minidump 的异常地址属于 KERNELBASE.dll 就推断显卡或模型损坏。必须读取 Comment 流中的 AbortMessage。

本次实际 AbortMessage 是 Invalid screenshot path。错误的绝对截图参数被引擎解析为 D，触发主动中止；不是模型加载失败。失败截图命令不再使用。改用外部窗口 CopyFromScreen 保存证据。

旧阿洛娜经验中的另一种 AbortMessage 是 addon pak01.vpk 挂载失败，属于命名和入口问题。两种原因都说明必须读转储，不能靠猜测。

### 游戏窗口和 Asset Browser 属于同一个进程

Get-Process cs2 的 MainWindowHandle 可能返回 Asset Browser，甚至临时 Stall Detected 窗口。截图前枚举并确认标题为 Counter-Strike 2 的窗口，不能只匹配 PID。

调用 Win32 FindWindow 时，PowerShell 的 null 字符串可能被封送成空串。类名应使用 System.Management.Automation.Language.NullString.Value，避免已存在游戏窗口却查询不到。

设置截图进程 DPI aware 后再读取物理窗口矩形；4K 桌面和缩放会让显示图坐标与真实屏幕像素不同。直接截取目标窗口，避免把终端、账户信息或桌面一并发布。

失焦和 Alt 模拟可能打开暂停菜单，导致人物被遮住。只做截图不应模拟 Alt。先激活正确游戏窗口，再通过本机控制台 gameui_hide，立即截图；不能把菜单遮挡画面命名为通过证据。

### 控制台协议与动作观察

本机 Tools 的 VConsole 端口为 29000，使用带帧协议。不是纯文本 netcon，不能发送裸字符串。保持仅连接 127.0.0.1，不做公网转发。

GUI 键盘模拟受焦点、模态框和缩放影响，直接使用已验证的 VConsole 帧协议更可靠。每次命令保存原始帧和解析 PRNT 日志，使用 echo 标记确认请求已被执行。

动作命令后需要经过游戏 tick 才能读取状态；同一条命令中 +duck 后立即读取 IsDucked 可能仍是 false。实际姿态应以之后的截图或延迟回读为准。输入失焦可能被重置，所以动作和截图需在明确激活的游戏窗口中完成。发出 +attack、+duck、+forward 等命令后必须安排对应释放。

## 三、本次最终证据和边界

三项编译退出码 0，实际模型路径来自清单；模型和 AG2 结构检查通过。118 项材质贴图可解析，87 个唯一嵌套引用完整；119 个原文件哈希保留，包括阿洛娜 14 项。三项 PHYS 均含 12 胶囊体、3 球体。

独立 addon 实际进入 GAME 搜索路径。官方 JS 已记录三个模型的玩家路径 before/after，真实游戏截图能看到三个模型；用户随后明确表示“经过我手动测试，都没问题”。该用户确认写入独立 JSON，不伪造成自动测试报告。

早期画面曾有武器位置疑点，不能因后续确认而删除原证据，也不能声称通过了某个不存在的修复。用户没有逐项列出所有武器、死亡、伤害和命中盒对照，报告不扩写这些验收范围。

## 四、交付与发布检查

成品 Release 只包含编译资源、我们编写的 JS/cfg/安装启动工具、必要配置和审核元数据。本次用户已明确要求上传成品；反编译美术工程仍不公开，Steam 转储、原始 DATA/PHYS、账户令牌和个人桌面截图不进入成品。

逐个验证 ZIP 内文件 SHA256，重新下载远端 Release 资产再比对整包 SHA256；不能只看到上传 API 返回成功。保留现有 Release、提交历史、Workshop ID 和正式服数据。

同一路径的第一次编译 addon 与最终 addon 不能同时挂载。复制到独立 addon、比较冲突后才安装。打包成 VPK、Workshop 发布、MAM 双端分发、多客户端和 KeranStrat 兼容性仍各自需要实测。

新自动启动器实现上述固定顺序，并提供三个独立应用命令；本次对其完成语法检查，尚未再次完整冷启动跑通这个新封装。不要将“组成步骤成功”写成“新封装冷启动测试通过”。