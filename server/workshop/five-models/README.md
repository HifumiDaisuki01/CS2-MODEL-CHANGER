# CS2 五人物 Workshop 上传包

包含 **Aluona、Myers、Pardofelis、VRC Lime、Huohuo（藿藿）**。不含 Dujiaoshou/MIKA。

## 官方 Workshop Tools 发布

用户使用 Steam 官方 CS2 Workshop Tools，继续沿用现有 addon 工程流程，目录结构保持不变；不要求使用 GWSteam 或改为 VPK 上传。

- `addon/game/csgo_addons/keran_five_models`：已编译人物及材质贴图。
- `addon/content/csgo_addons/keran_five_models`：配套 addoninfo。
- `workshop-upload`：额外保留的已校验 VPK，作为备用产物。

本地 v1.1 上传包含新版 Myers；目前 Workshop 3822970980 实际发布的是用户同意先测试的旧版 Myers，详见 [正式服部署记录](../../deployments/3822970980/README.md)。历史 Release 不改写。

## 五个人物与计划指令

| 人物 | 接入后指令 | 内部路径 |
|---|---|---|
| Aluona | !model aluona | characters/models/aluona/aluona.vmdl |
| Myers | !model myers | characters/models/exg/myers/myers.vmdl |
| Pardofelis | !model pardofelis | characters/models/exg/pardofelis/pardofelis.vmdl |
| VRC Lime | !model vrc_lime | characters/models/exg/vrc_lime/vrc_lime.vmdl |
| 藿藿 | !model huohuo | characters/models/exg/honkai_starrail_huohuo/honkai_starrail_huohuo.vmdl |

Pardofelis、VRC Lime、藿藿和 Myers 均来自桌面新版模型包；Aluona 逐字节保留现用成品。VRC Lime 与 lime_e 不同。

**v1.1 已将 Myers 换为新版包中的成品，包含实际第一人称网格，AG2 和依赖检查通过；手臂持枪/换弹效果待游戏验证。藿藿名称由用户确认，菜单/ID 改为 huohuo，内部 honkai_starrail_huohuo 路径保留，未修改二进制引用。**

## 真实验证范围

- 五个主模型及所有自定义依赖逐一解析；AG2 图/骨架引用存在，无旧 animgraph/animset。
- 递归闭包不缺自定义依赖；原版依赖根据既有正式游戏 VPK 索引确认，未把原版游戏资源打入包。
- 新版 Myers 和另外三个新版人物的第一人称分组实际关联到网格。此项不是手臂持枪/换弹的游戏验证。
- Aluona SHA256 与服务器现用成品一致；Myers SHA256 与桌面新版包一致，与旧版不同；没有重新编译或修改资源二进制。
- 无同路径不同内容冲突、大小写冲突；未混入 Dujiaoshou、测试地图、脚本、玩家数据库。
- VPK 每个资源的 CRC/SHA256 与输入一致；Source2Viewer 独立验证 VPK MD5/分块哈希。
- **本五合一尚未上传 Workshop、未挂载到服务器、未完成客户端自动下载与新版四个人物游戏实测。正式服务器未修改。**

## 配置与后续接入

configs/PlayerModelChanger.merge.json 是五人物合并片段，T/CT 均开放。保留原配置其他选项和 SQLite；不要整份覆盖配置。

configs/resource-catalog.template.json 仅提供模型路径；Archives 要在实际 Workshop 下载后重新生成，不能作为正式白名单直接覆盖。

服务器正式切换时用新包 ID 替换当前三合一 ID 3822432137；不要同时挂载两个含 Aluona/Myers 同路径的包。移除旧菜单 mika 的具体处理与玩家持久化兼容，应在接入时备份后执行，不删除玩家数据库。

回滚：保留当前三合一 Workshop 3822432137 及其配置/数据库备份；发生问题恢复原挂载 ID 与配置。包上传阶段无需服务器回滚，因为尚未修改正式服。

## 本地校验

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Verify-Package.ps1
```

reports/ 保存资源依赖、哈希与 VPK 验证结果。发布后的客户端需逐个检查第三/第一人称、持枪/换弹、重生/重连、T/CT 及恢复默认。静态检查不代替这些测试。

最新菜单/指令名称为 Huohuo（藿藿）/ `!model huohuo`。历史 v1.1 ZIP 中的 huahuo 配置名称已过时，可按当前合并配置修正；模型二进制路径始终保持 huohuo，无需改名。
