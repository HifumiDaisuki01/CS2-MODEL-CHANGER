# 最终远端恢复校验

时间：2026-10-18T09:17:01.0989747+08:00

结论：成功成果已完整保存在 GitHub，可不依赖原 Windows 电脑恢复。

- Release 页面实际 HTTP 状态：200，非草稿，预发布：True。
- Release：https://github.com/HifumiDaisuki01/CS2-MODEL-CHANGER/releases/tag/v0.1.0-alpha
- 已从公开 Release 下载全部 5 个资产，每个与本地原成品 SHA256 一致。
- 两个 ZIP 均实际完整解压；每个内部 SHA256SUMS.txt 中的所有文件再次逐项核验通过。
- 从重新下载的主包运行 Verify-Package.ps1，通过 58 个文件校验和 14 个原编译资源哈希校验。
- 恢复包含人物 vmdl_c、6 个 vmat_c、7 个 vtex_c、JS 源码及 vjs_c、预缓存/应用 cfg、addoninfo、自动启动器/控制台助手源码、安装与构建脚本、原样本 VPK、PMC/MAM 配置、经验文档、真实成功截图和日志。
- 自定义依赖闭包完整；8 个原版依赖（动画图、骨架、默认纹理）须由合法 CS2 安装提供。它们的存在由先前本地实测支持；本次不再启动游戏。
- 根目录 HANDOFF_TO_SERVER_CODEX.md 已上传；旧提交、历史 ZIP 与原 README 内容保留。
- 二进制归档放 Release Assets；新增 Git 提交只包含源码、配置、小型脚本编译产物、清单和说明。没有把新模型二进制 ZIP 放进 Git 历史。
- Workshop 没有发布，无 Workshop ID；已保存可继续发布的样本工程。当前 Tools 默认打包缺少 characters 收录规则，需要在不修改官方文件的条件下解决，发布前仍需用户 Steam 交互和可见性确认。
- Linux PMC/MAM 运行、网络分发、KeranStrat 集成及全部动作/命中盒仍未验证。没有连接远程服务器。

逐资产 SHA256 与完整解压文件数见 download-verification.json；两份归档的校验也保存在 SHA256SUMS-release.txt。

本报告随后使用普通 git commit 与 git push 保存；推送后执行 git status --porcelain、git ls-remote 和 GitHub API 远端 HEAD 对照。最终提交 SHA 由 GitHub 本报告所在提交提供，避免在报告中写入自身尚未生成的 SHA。