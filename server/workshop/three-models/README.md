# MIKA + Myers + Aluona — Workshop 三人物上传包

三个模型合在一个独立资源包。发布一次、一个 Workshop ID；阿洛娜原作品 3821951835 保留，不删除、不覆盖。服务器接入新包后移除旧阿洛娜挂载项，避免同路径资源重复挂载。

## 立即上传

1. 解压本 ZIP。
2. 用之前发布阿洛娜的 GWSteam / Workshop 工具，新建作品。
3. 上传内容目录选 workshop-upload；里面的 pak01_dir.vpk、pak01_000.vpk 必须一起上传，不能只选索引文件。
4. 标题建议 MIKA, Myers and Aluona - CS2 AG2 Player Models。预览图用实际游戏内截图。
5. 沿用阿洛娜的资源包发布流程。不要把模型包作为可玩地图启动；不要更新或覆盖阿洛娜原作品。
6. 发布、邮箱确认且可下载后，将新 Workshop ID 或链接发给我，再接入服务器。

如果工具要求 addon 工程，已编译目录为 addon/game/csgo_addons/keran_three_models，配套 content 在 addon/content/csgo_addons/keran_three_models。优先上传已检查的 VPK，避免 Tools 默认目录白名单漏打 characters。无需重新编译或修改官方 gameinfo。

## 三个模型

| 菜单显示名 | 计划指令 | 实际内部路径 |
|---|---|---|
| MIKA（用户指定 dujiaoshou） | !model mika | characters/models/exg/dujiaoshou/dujiaoshou.vmdl |
| Myers | !model myers | characters/models/exg/myers/myers.vmdl |
| Aluona | !model aluona | characters/models/aluona/aluona.vmdl |

内部路径未重命名。命令将在服务器接入后生效；本次未修改正式服务器。

## 已完成检查

- 原始 GitHub v0.3.0-ag2 ZIP SHA256 匹配；149 个清单文件全部一致。
- 三个主模型是真正已编译 .vmdl_c；独立解析证明 AG2 动画图和骨架存在，无旧动画图/animset 引用。
- 55 个编译模型、材质和纹理逐个解析成功；递归引用完整，8 项原版依赖有原游戏索引确认。
- VPK 有 56 个成员（含 addoninfo.txt）；所有 CRC/SHA256 与编译源文件一致；Source 2 Viewer 独立通过 VPK MD5 和分块哈希验证。
- 未混入 km_decade、测试脚本、地图、原版游戏文件或玩家数据。
- 用户确认 Windows 实际运行良好。Workshop 发布、挂载及远端客户端下载尚待发布后验证；不能用本次文件检查代替网络分发验收。

## 目录与校验

workshop-upload/ 是直接上传目录；addon/ 是松散资源工程；configs/ 是服务器合并片段；reports/ 是检查结果。Windows 可运行 powershell -NoProfile -ExecutionPolicy Bypass -File .\Verify-Package.ps1 验证文件完整性。

服务器接入时合并而非覆盖 PlayerModelChanger 配置：T/CT 双方可用、保留阿洛娜、保留 SQLite 玩家数据；追加新 MAM Workshop ID 并更新资源白名单。
