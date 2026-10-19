# CS2 五人物 Workshop 上传包

包含 **Aluona、Myers、Pardofelis、VRC Lime、Huohuo（藿藿）**。不含 Dujiaoshou/MIKA。

## 直接上传

1. 解压 ZIP，用之前的 GWSteam / Workshop 发布工具。
2. 上传内容目录选择 **workshop-upload**，同时包含 **pak01_dir.vpk 与 pak01_000.vpk**；不能只上传索引。
3. 新建作品或由你明确选择更新作品；保留旧作品作为回滚资源。本次没有操作 Steam。
4. 标题可用：Aluona, Myers, Pardofelis, Lime and Huohuo - CS2 Player Models。
5. 发布并可下载后，把 **Workshop ID / 链接** 发回来，再备份并切换服务器。

这是人物资源包，不是可玩地图；不要用 host_workshop_map 启动它。沿用此前阿洛娜资源包上传流程，无需重新编译。工程目录为 addon/game/csgo_addons/keran_five_models，配套 content 只含 addoninfo。优先直接上传已校验 VPK，避免 Workshop Tools 默认白名单漏收 characters。

## 五个人物与计划指令

| 人物 | 接入后指令 | 内部路径 |
|---|---|---|
| Aluona | !model aluona | characters/models/aluona/aluona.vmdl |
| Myers | !model myers | characters/models/exg/myers/myers.vmdl |
| Pardofelis | !model pardofelis | characters/models/exg/pardofelis/pardofelis.vmdl |
| VRC Lime | !model vrc_lime | characters/models/exg/vrc_lime/vrc_lime.vmdl |
| 藿藿 | !model huohuo | characters/models/exg/honkai_starrail_huohuo/honkai_starrail_huohuo.vmdl |

新增三个来自桌面新版模型包；Aluona、Myers 逐字节保留现用三合一成品版本。VRC Lime 与 lime_e 不同。

**Myers 现用版本之前第一人称手臂不可见，本次保留该版本，没有将它换成新版包中的 Myers，也没有声称修好了它的手臂。**

## 真实验证范围

- 五个主模型及所有自定义依赖逐一解析；AG2 图/骨架引用存在，无旧 animgraph/animset。
- 递归闭包不缺自定义依赖；原版依赖根据既有正式游戏 VPK 索引确认，未把原版游戏资源打入包。
- 新增三个人物的第一人称分组实际关联到网格。此项不是手臂持枪/换弹的游戏验证。
- Aluona 与 Myers 的主文件 SHA256 与服务器现用成品一致；没有更改其编译资源。
- 无同路径不同内容冲突、大小写冲突；未混入 Dujiaoshou、测试地图、脚本、玩家数据库。
- VPK 每个资源的 CRC/SHA256 与输入一致；Source2Viewer 独立验证 VPK MD5/分块哈希。
- **本五合一尚未上传 Workshop、未挂载到服务器、未完成客户端自动下载与新增三个人物游戏实测。正式服务器未修改。**

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
