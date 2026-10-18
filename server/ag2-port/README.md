# 三个旧人物模型的 AG2 转换

> 2026-10-18 最新状态：三个模型均实际编译成功，退出码均为 0；详情见 [本机编译报告](reports/2026-10-18-local-compilation.md)。118 项材质贴图解析及 87 个嵌套引用检查通过，阿洛娜等原资源哈希未变。下方涉及“尚未编译”的内容为此前源码交付阶段记录，以最新报告为准；实际游戏动作全部未验证。

实际转换了 **3 个不同的旧版人物模型**，不是把已有AG2模型算入数量。三项均完成ModelDoc/DMX源码转换，且已于 2026-10-18 使用本机 Valve resourcecompiler 实际编译出新版 `.vmdl_c`，通过编译后资源验证。**尚未挂载或进入游戏验证**。

| 模型（原文件名） | 指令ID | 骨骼数：原始→转换源 | 原始动画依赖 |
|---|---|---:|---|
| Myers | ag2_myers | 129→131 | player_ct.vanmgrph + animset_ct.vmdl |
| KM Decade | ag2_km_decade | 156→158 | player_t.vanmgrph + animset_t.vmdl |
| Dujiaoshou | ag2_dujiaoshou | 171→173 | player_ct.vanmgrph + animset_ct.vmdl |

三个模型材质和贴图齐全，原始差项均只有这两项旧动画资源。实际路径和哈希见 `reports/selected-models.json`，未重命名资源目录。阿洛娜仅作对照，不计入三个修复目标。

## 已经实际做完

- 从真实 `.vmdl_c` 读取DATA、RERL、PHYS、CTRL，并反编译为ModelDoc与11份DMX；不是空文件或二进制路径替换。
- 复用 MIT 开源 [CS2-AG2-Model-Porter](https://github.com/SergeantCS2/CS2-AG2-Model-Porter)，固定 `ff9b878ced21d68dacbfc29cef564945b03a52f4`。只调用其转换函数，不调用Steam、setup、gameinfo修改或占位材质逻辑。
- 移除旧图与AnimIncludeModel，加入4项AG2绑定和2项骨架绑定；新引用来自当前游戏已有的worldmodel/uimodel/viewmodel图与worldmodel/viewmodel骨架。
- 将pelvis接到root_motion并转换坐标，增加wpnPivot/`wpn`。还原到世界空间后，位置误差约`2.7e-15`、旋转矩阵误差约`1.9e-16`。
- 修正Linux脚本只覆盖核心左右骨骼的限制：按完整74骨参考统一54个名称（含手指），同步修改DMX；另修正7处物理蒙皮骨骼名引用。物理形状自身名称未改。
- 三项核心骨骼24/24，所存在的规范骨骼父级无差异，实际带权重的网格关节无缺失。11份DMX除规定的骨名大小写外，二进制数值载荷和长度不变。
- 原始物理/命中形状数量分别34、33、34，源码中的名称和数值几何保留。**这不证明重新编译后的PHYS或游戏命中判定相同**，必须继续验收。
- 材质与纹理保留原编译文件，不改目录、不重编码、不降级默认着色器；105项文件哈希核对。官方原版依赖由游戏提供，不重复打包。
- 本地工程保留阿洛娜资源和配置，三项新增配置为All双队、不限制普通玩家，且默认隐藏，防止未编译项目进入正式菜单。

## 当前编译限制及可执行交付

当前Windows开发机没有CS2/Workshop Tools，已实际运行编译预检并确认 `resourcecompiler.exe` 缺失。只读检查Linux服务器bin目录也未发现可用模型编译器。

Porter最终明确调用Valve的Windows `resourcecompiler.exe`；Source 2 Viewer是解析/导出/反编译工具，不替代这个模型编译步骤。Linux版的`--no-compile`正是为这种情况提供交接；未发现本任务现有工具中能在不获得编译器的情况下生成正确AG2模型二进制的流程。没有安装完整CS2或尝试下载未经许可的游戏文件。更换另外三个模型不会解决同一个编译器缺失问题。

已按要求准备另一台装有CS2和Workshop Tools的Windows电脑上可运行的工程。**本地完整交付：桌面 `AG2模型修复/交付/`**，包含第三方模型的实际源码、DMX、原编译材质、阿洛娜对照及完整Windows Source 2 Viewer 20.1便携工具（核对GitHub资产SHA）。

在另一台电脑打开PowerShell，进入完整交付目录：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\Build-AG2.ps1 -CS2Path "D:\SteamLibrary\steamapps\common\Counter-Strike Global Offensive"
```

只需改CS2目录。脚本不登录Steam，不下载游戏，不上传Workshop；创建一个全新的带时间戳addon，保留原安装与其他addon。保留编译日志，并要求每个模型实际生成新文件；编译后检查AG2依赖、24根核心骨骼与层级、路径大小写、原材质/纹理SHA，绝不把没有错误文字当作编译成功。

**编译辅助脚本已通过PowerShell语法和依赖预检测试，但真实resourcecompiler执行仍未验证。** 若编译器报告缺源、材质搜索路径或版本问题，保留该次日志继续修复，不得凭静态报告跳过。

## 可以现在合并什么

完整交付中的 `workshop-addon/game/csgo_addons/ks_ag2_repair/` 含原编译材质/贴图及保留的阿洛娜，可作为资源输入。`content/`含三个已转换工程与DMX，需先编译；**不能把 `.vmdl` 源文件当作可直接运行的人物**。

编译成功后，将新时间戳addon中的game资源合并到统一Workshop工程，先查同路径哈希冲突。不要同时挂载带相同人物路径的旧包。不要改现服SQLite。最终VPK生成、CRC验证、挂载白名单、客户端分发和实测仍分别待完成；本次没有生成虚假的catalog。

## 游戏验收边界

站立、行走、蹲跳、持枪、开火、换弹、死亡、第一人称、命中盒与伤害 **全部待游戏验证**。AG2图、骨架、权重和源几何检查只能提供必要条件；独立手臂未移植，默认使用CS2标准手臂。KeranStrat兼容性也必须在隔离服验证，不能以未改代码替代运行验收。

完整步骤见 `TESTING_CHECKLIST.md`；真实状态见 `reports/results.json`。现服、地图、MAM配置、玩家库和旧Release均未修改，未上传Workshop。

## 重复执行与公开范围

`tools/port_projects.py` 可批量生成独立工程；参数显式指定输入、选择清单、原版路径证据、Source 2 Viewer、固定上游转换库、规范骨架和新的输出目录。需要Python3.11及`tools/requirements.txt`依赖。原始目录只读，输出不得包含输入或覆盖既有输出。

`tools/test_port.py`包含路径、损坏资源、骨骼、物理保真、缺材质阻断及真实三工程集成检查。测试日志随附。不能推广为所有旧包都能自动成功，换骨架、缺材质、特殊手臂或权重错误仍应阻断。

GitHub只提交代码、清单、配置和审查元数据。模型二进制及反编译美术源文件、原始模型DATA/PHYS输出仅保存在本地完整交付，不因转换而获得再发布授权。上游MIT许可证保留于`tools/vendor/`；Source 2 Viewer声明随本地工具附带。
