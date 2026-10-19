## 五人物 Workshop 上传包 v1.1

**Aluona、Myers（新版，含第一人称网格）、Pardofelis、VRC Lime、Huahuo（花火）**，不含 Dujiaoshou。

[上传说明、配置和静态检查报告](server/workshop/five-models/README.md) · [下载五合一 v0.4.1-workshop-five](https://github.com/HifumiDaisuki01/CS2-MODEL-CHANGER/releases/tag/v0.4.1-workshop-five)

v1.1 替换旧版 Myers，并按用户确认将角色显示名/指令更正为花火 / `huahuo`；底层 `honkai_starrail_huohuo` 路径保留。五个人物均检测到第一人称网格，尚待实际游戏验证。正式服务器未修改，旧包和旧 Release 保留。

## 三个人物 AG2 编译成品

Myers、KM Decade、Dujiaoshou 已实际编译并由用户手动测试确认正常。[下载 v0.3.0-ag2 成品](https://github.com/HifumiDaisuki01/CS2-MODEL-CHANGER/releases/tag/v0.3.0-ag2) · [后续必读经验](server/ag2-port/EXPERIENCE_AG2_CN.md)。历史 Linux 和阿洛娜版本保留。

# CS2 人物模型系统

Linux 正式服部署版：**v0.2.0-linux**。阿洛娜已完成 Workshop 下载、Linux 挂载与真人指令换模验证。

- [服务端安装、命令和恢复](server/README.md)
- [本次实测范围与待验证项](server/TEST_REPORT.md)
- [批量提取、检查和实装经验](server/EXPERIENCE_CN.md)
- [兼容适配源码](server/PlayerModelChanger/)
- [后续模型暂存合并工具](server/tools/stage_model.py)

历史 Windows 恢复成果和原有 v0.1.0-alpha Release 保留如下。

# CS2-MODEL-CHANGER

## Verified Aluona recovery and handoff

- [Handoff](HANDOFF_TO_SERVER_CODEX.md)
- [Source and configs](aluona/)
- [Release assets and SHA256](RELEASE_ASSETS.md)
- [v0.1.0-alpha recovery release](https://github.com/HifumiDaisuki01/CS2-MODEL-CHANGER/releases/tag/v0.1.0-alpha)

Use the Release for all compiled model assets and the fixed automatic launcher. The historical ZIP under deliverables is the older manual-launch build.


## 三人物 Workshop 资源包

[MIKA（dujiaoshou）+ Myers + Aluona 发布包](server/workshop/three-models/README.md)：保留已验证的内部路径，单个 Workshop ID 分发三个人物。工具与检查报告在上述目录，资源二进制通过新 Release 提供，原 Release 和阿洛娜作品保留。


## 三人物 Linux 部署结果

新 Workshop **3822432137** 已替换旧阿洛娜挂载，开放 `!model aluona`、`!model myers`、`!model mika`。服务端资源及 12 项 T/CT BOT 检查通过，玩家数据库保留；真实客户端自动下载、菜单、重生与重连待进服验收。见 [完整部署报告](server/deployments/3822432137/README.md)。
