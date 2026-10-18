# Linux 接手与配置

本目录不执行部署，不包含服务器地址、口令、GSLT 或 Steam token。使用 `bash server/verify-package.sh /path/to/CS2_Aluona_Package_A` 可离线校验资源。其他配置步骤先在独立测试实例进行。

PlayerModelChanger 配置位置：`game/csgo/addons/counterstrikesharp/configs/plugins/PlayerModelChanger/PlayerModelChanger.json`。根目录的 `PlayerModelChanger-Aluona.json` 是完整示例：m0117，模型逻辑路径 `characters/models/aluona/aluona.vmdl`，side All，T/CT BOT 数组都引用 m0117。把该 Models 条目合并到现有配置，不覆盖服务器已有模型和权限设置。

插件通过官方上游 https://github.com/samyycX/CS2-PlayerModelChanger 获取。先前检查 1.8.6 发行版引用 CounterStrikeSharp API 1.0.255/net8；这只是检查记录，不是要求把正式服降级。先核对现场 CSS/API 和插件兼容性，必要时从对应 tag 编译并测试。真实配置依赖发行版本，不套用 CS:GO 配置。上游文档也声明存在 GSLT 风险，应由服主管理正式服策略。

MultiAddonManager：https://github.com/Source2ZE/MultiAddonManager 。其 `mm_extra_addons` 为逗号分隔的 Workshop ID；配置文件位于 `game/csgo/cfg/multiaddonmanager/multiaddonmanager.cfg`。只有成功发布并验证 ID 后才能填写。模型应在服务端和客户端均挂载；不能只使用 mm_client_extra_addons。切图后用 mm_print_searchpaths 与控制台确认挂载及预缓存。

本地成功使用的是 listen server + Tools 松散资源 + 官方 cs_script，不是 PMC。未取得 Workshop ID 前，仅把文件复制到 Linux addon 目录不能解决公网客户端资源获取。不要因此声称正式部署完成。

KeranStrat：当前没有实测集成或战术录制回放。确认它是否会在出生、重置、换队、回放阶段写入模型；应避免两个插件交替 SetModel。先保持录制和武器/经济逻辑原样，在副本中分别测试录制、回放、BOT 重建、换队和多轮出生。不要为模型去修改碰撞、命中盒或原版武器属性。

验收：记录 meta list、css_plugins list 和对应版本；确认客户端完成资源下载；真人 T/CT 与 BOT 分别检查第三人称、第一人称手部、蹲姿、持枪、换弹、死亡/重生；比对模型错误日志；最后做 KeranStrat 录制/回放。所有尚未实测项继续标为待验收。
