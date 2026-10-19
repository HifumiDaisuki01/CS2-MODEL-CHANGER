# 五人物 Linux 部署 · Workshop 3822970980

用户确认本次先部署 Steam 上实际已发布的旧版 Myers，用于测试藿藿；不把它声称为上传包 v1.1 新版 Myers。

## 玩家命令

- `!models`：模型菜单。
- `!model aluona`、`!model myers`、`!model pardofelis`、`!model vrc_lime`、`!model huohuo`。
- `!model default`：恢复默认。

藿藿身份由用户确认，显示名/ID 使用 Huohuo / huohuo，底层路径仍为 `characters/models/exg/honkai_starrail_huohuo/honkai_starrail_huohuo.vmdl`，没有破坏资源引用。

## 资源版本与检查

- Steam Workshop 公开可下载，app 730。
- 222 个 VPK 成员 CRC 验证通过。五人物相关资源共 207 个：204 个与 v1.1 相同；Myers 主模型和两张法线纹理是用户批准的旧版本。
- 实际 Myers SHA256：`ec542ea2c9f48fe913ed104372970ecde0fa95c2eb61464109dae9b9d8630c0a`，第一人称手臂问题未修复。
- `3822970980` 替换 `3822432137`；旧包缓存保留用于回滚，避免重复挂载。
- 预缓存/白名单以本次 Steam 实际下载的 VPK 哈希生成，不能使用本地 v1.1 的哈希冒充。
- 保留玩家 SQLite、原插件和战术数据；菜单移除 mika，不删除数据库中的历史偏好。

## 测试边界与发现的问题

服务端资源和加载检查见 reports。新增人物的第一人称显示、动作、真人换模/复活/重连及客户端下载，需要用户进服验证。

临时 BOT 检测未通过：首次因未能在无人竞技模式获得两个存活测试 BOT 而超时，零项换模检查。重试涉及临时插件的热重载，出现同名程序集加载异常，并在该时段发生服务端 SIGSEGV/自动重启；因果尚未独立定位。已停止此项检测并移除临时插件，不将它记录为成功。正式资源部署使用原 PMC DLL。

## 发布工具与目录

用户使用 **Steam 官方 CS2 Workshop Tools**，不是 GWSteam。本次沿用既有 addon/content、addon/game 与 workshop-upload 目录，后续说明以官方 Tools 的工程流程为准，不要求改变目录结构或改用 VPK 上传工具。

## 回滚

服务器已保存模型配置、MAM 配置、玩家库及 SQLite 一致备份。回滚脚本恢复旧模型配置/挂载并重启，保留当前玩家库。实际私有路径记录在服务器 `/root/five-model-deploy/backup-path`；备份内 `rollback.sh` 一键执行。脚本经语法检查，未实际回滚。

## 最新名称修正

用户再次确认角色为《崩坏：星穹铁道》藿藿（Huohuo）。菜单和 ID 已改为 `huohuo`，通过 PMC 自带 `css_modeladmin reload` 生效，未重启服务端、未改模型路径或玩家数据库。

最终清理后原 11 个插件正常加载，临时检测插件不在正式 plugins 目录；无继续 BOT 补测。跟踪的 203 个原文件中 202 个哈希不变，KeranStrat 在启动恢复时自行消费了唯一的 practice-recovery.json 标记，未删除战术。bot_dont_shoot 从 1 随 sv_cheats 恢复 0 而归零；当前无人无 BOT，其余记录的参数恢复原值。
