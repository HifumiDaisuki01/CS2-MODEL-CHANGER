# 人物/武器模型交接 — 2026-10-21

备份前 main：6dc22c7。正式十五人物包 Workshop ID **3823495199**，服主已确认全部人物正常；该结论针对当时真人反馈，不能推断未来 CS2 更新全部兼容。本次不改 Workshop、正式服或稳定 Release。

## 已有项目和经验

server/PlayerModelChanger 是适配源码；server/config、server/deployments 为配置和部署记录；server/workshop 为多阶段包配置与工具；server/ag2-port、server/lime-e-windows 为旧模型迁移工程及 Windows 编译包；server/batch5、server/model-audits 为静态资源报告。

优先阅读 server/lime-e-windows/EXPERIENCE_LIME_E_CN.md、server/ag2-port/EXPERIENCE_AG2_CN.md、server/EXPERIENCE_CN.md。Lime_E 曾在另一台有 CS2 Workshop Tools 的 Windows 电脑完成真实编译并由服主游戏验证身体及手部。不要把 Linux 静态解析或 DATA/RERL 引用调整等同于 Workshop Tools 编译成功。

Source2 Viewer / ValveResourceFormat 20.1.7467 可在 Linux .NET 中做解析、依赖/块校验和结构化资源处理；真正需要重建 DMX/ModelDoc 的模型仍需 Windows Workshop Tools。AG2 Porter 不是所有模型的通用修复器，适用范围和真实失败案例见已有报告。

## 未解决：10052 在 T 方为原版手臂

CT 正常，T 出现原版手臂及手套，更新前已有。双方配置指向 characters/exg/10052/10052.vmdl。资源 SHA256=529749f458e98d6c5622a94af469bcdfda2362eaa22803726362a232fc135ddd，313 骨骼；第一人称 mesh index25 mask4，默认 mask5444375057 不含 bit2。仅对当前 T 玩家临时 OR4 试验到5444375061，**服主截图证实无效**，不得标记已修复，不得推广该补丁。

原版 Aluona 的组结构与10052不同，不能直接照抄组号。没有改模型二进制或 Workshop，也没有永久修改正常模型配置。

此前临时 Model10052Audit 诊断插件仍可能留在正式服（1.0.0，两个控制台命令，只读 audit 及一次性 trial，无定时器）。本次禁止正式服修改，因此没有为备份任务卸载它。下一次正式服维护时先核实再按服主授权清理；不要声称已清理。

未提交诊断工程和输出在私有备份 LinuxBuild/root/model-system-work/10052-inspect、10052-live-audit，以及原始10052-audit.vmdl_c（仅私有素材备份）。

## 武器替换研究的真实边界

桌面 武器模型包、AG2武器模型、武器模型审查、ks-weapon-probe 均纳入私有备份。已找到上游56dz/CS2-WeaponModelChanger 的项目树与 KSWeaponProbe 源码；本次尚未发现独立 WeaponModelChanger 自研仓库或完整本地实现，不能虚构研究已成功。下一位先阅读原始探针、上游引用与报告，再确认实际自研源码是否另存；不要把人物替换的成功推断为武器替换也已成功。

## 恢复和接续

私有 https://github.com/HifumiDaisuki01/CS2-SERVER 的备份 Release 保存原模型、贴图、修复前后版本、工程及原始目录 SHA256；公开仓库只放工具、配置、文档及授权内容。

先还原到新目录并核对 SHA，不覆盖本机已有数据。玩家 SQLite 数据库不可被测试库覆盖。要迁移服务器时，除了插件还须迁移兼容 Metamod/CSS/MAM、配置、资源目录/预缓存和玩家数据库，并验证 Workshop 下载挂载；不能只复制单 DLL。

优先处理备份完整性，随后等待服主指示再继续10052问题。不动 KSV（已被服主取消）、BOT AI、其他正常人物或稳定 Release。
