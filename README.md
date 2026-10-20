## 十五人物正式包（用户实测正常）

原十二人移除藿藿/日富美，新增守岸人10092、花火10073、Elysia10096、xmanuka、10052。保留十人原版本与已实测Lime E。824资源静态检查通过，Workshop **3823495199** 已部署，用户确认十五人物全部正常。

[正式包、十五人物ID与修复记录](server/workshop/fifteen-models/README.md) · [更换服务器迁移](server/workshop/fifteen-models/SERVER_MIGRATION_CN.md) · [完整上传包 v0.7.0](https://github.com/HifumiDaisuki01/CS2-MODEL-CHANGER/releases/tag/v0.7.0-fifteen-models)。旧Release保留。

## 新包人物与 Lime E 手部复查

[七个候选可用性与新版 Lime E 对照](server/model-audits/2026-10-20-seven-models/README.md) · [手部绑定、编译及验证经验](server/lime-e-windows/EXPERIENCE_LIME_E_CN.md#7-可复用的手部迁移流程2026-10-20-补充)。10096、10018可优先打包测试；当前已实测 Lime E 保留，本次不改服务器。

## 十二人物 Workshop Tools 包

保留原五人物并更新 Myers，新增 Lime E、Chikari、Serina、白洲梓、日富美、鸣潮菲比和 Chiffon Fox，共 **12 人物**。四个过期外部手臂引用已在当前 Windows 结构化清理；625 资源及 12 个主模型静态检查通过。新增人物游戏验证待完成，正式服未修改。

[上传说明、配置、修复源码和报告](server/workshop/twelve-models/README.md) · [v0.6.0-twelve-models](https://github.com/HifumiDaisuki01/CS2-MODEL-CHANGER/releases/tag/v0.6.0-twelve-models)。第三方模型资源保留在本地交付包，不公开重新分发。

## Lime E 人物与第一人称手臂成品

Lime E 已在 Windows 实际编译，结构/依赖和第一人称网格检查通过；用户进游戏手动确认手臂正常。[下载 v0.5.0-lime-e](https://github.com/HifumiDaisuki01/CS2-MODEL-CHANGER/releases/tag/v0.5.0-lime-e) · [恢复与使用](server/lime-e-windows/README.md) · [手臂测试经验](server/lime-e-windows/EXPERIENCE_LIME_E_CN.md)。本包与此前五人物包中的 VRC Lime 不同，旧版本和现有 Workshop 保留。

## 五人物 Workshop 上传包 v1.1

**Aluona、Myers（新版，含第一人称网格）、Pardofelis、VRC Lime、Huohuo（藿藿）**，不含 Dujiaoshou。

[上传说明、配置和静态检查报告](server/workshop/five-models/README.md) · [下载五合一 v0.4.1-workshop-five](https://github.com/HifumiDaisuki01/CS2-MODEL-CHANGER/releases/tag/v0.4.1-workshop-five)

v1.1 替换旧版 Myers。后续纠正：该角色为藿藿，当前使用 `huohuo`；旧 Release 中的花火名称已过时。底层 `honkai_starrail_huohuo` 路径保留。五个人物均检测到第一人称网格，尚待实际游戏验证。正式服务器未修改，旧包和旧 Release 保留。

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

## Linux 当前状态与 Lime E 独立复核

- [Workshop 3822970980 五人物部署、旧版 Myers 及真实测试边界](server/deployments/3822970980/README.md)。角色确认为 **Huohuo（藿藿）**，使用 `!model huohuo`。
- [Lime E v0.5.0 编译成品独立复核](server/ag2-port/reports/2026-10-19-linux-offline-lime-e-review.md)：140 个资源解析、139 个材质贴图哈希、AG2/骨架/第一人称网格检查通过；本次未追加部署 Lime E。
- 用户使用 **Steam 官方 Workshop Tools**；现有交付结构保留。历史 Release 和二进制不覆盖。
