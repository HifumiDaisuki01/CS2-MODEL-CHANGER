# Workshop 状态与发布工程

状态：**未发布，Workshop ID 尚不存在；仅本地松散 addon 实际显示通过。** 用户已确认模型发布授权，但尚未确认本次 Steam 发布可见性；因此没有点击发布，也没有尝试账号登录或绕过权限。

本机已安装 CS2 Workshop Tools：`game/bin/win64/csgocfg.exe`、`resourcecompiler.exe`、`vconsole2.exe` 与相关 Asset Browser DLL 均存在。Tools 的本地测试启动与 JS 编译已经成功；没有为本次移交再启动非必要试验。

独立 Release 资产 `CS2_Aluona_Workshop_Preparation-v0.1.0-alpha.zip` 保存可继续处理的 game/content addon 工程，包含 14 个原编译人物资源、JS 源码和编译产物、cfg、addoninfo、原样本 VPK、预览截图与校验文件。逻辑路径始终为 `characters/models/aluona/aluona.vmdl`。

## 继续发布前的实际障碍

本机官方 gameinfo.gi 的 `AddonConfig/VpkDirectories` 只包含 maps、materials、models 等目录，没有 characters。因此不能假定默认 Workshop 打包会收录人物。上游 PMC 的打包说明建议修改官方 gameinfo.gi 添加 characters；本任务明确要求不修改官方文件，所以未采用该方法。也没有臆造 addoninfo 字段或未验证的 CLI 参数来声称解决了它。

现有 cs2cm_sample.vpk 可读取、资源齐全，但未证明它能以 Workshop/MAM 的独立资源分发方式被挂载。候选 VPK 的通过标准必须是：上传前核对包内路径 → 私密测试项下载 → 服务端/客户端实际 searchpaths 挂载 → 冷启动加载及真人/BOT 视觉验收。ZIP 校验和本地 Tools 成功不能代替这些步骤。

## 下一位操作者的步骤

1. 在装有 Steam、CS2 和 Workshop Tools 的 Windows 电脑下载完整恢复包，并先复现本地成功。
2. 打开官方 Tools/Asset Browser 的 Workshop Manager。不要使用武器饰面 Item Editor 发布人物资源，也不要假定资源包必须伪装成官方库存物品。
3. 使用保存的 addon 工程，研究当前 Tools 对额外 characters 路径的打包支持或可信的资源包上传方法。不得改写官方文件。检查实际导出的 VPK 是否完整保留人物路径；如 UI 要求地图，不能谎称我们已经提供经过编译验收的地图。
4. 在任何提交上传前，让用户完成 Steam 账号交互、必要的 Steam Guard/协议，并确认标题、描述、预览和可见性。优先申请 Private 测试；本次没有得到这个最终确认。
5. 获得真实 Workshop ID 后记录到本文件及交接文档，再进行 MAM 下载、挂载和远端客户端验收。需要用户再次明确确认才可公开。

## 参考来源

- Valve Workshop 入口：https://www.counter-strike.net/workshop/workshop
- Valve Workshop FAQ：https://www.counter-strike.net/workshop/workshopfaq/?l=english
- PMC 原项目：https://github.com/samyycX/CS2-PlayerModelChanger （打包章节含修改官方 gameinfo 的方案，本次没有执行）
- MAM：https://github.com/Source2ZE/MultiAddonManager

这些是继续研究的来源，不代表本交付完成了 Workshop 发布验收。
