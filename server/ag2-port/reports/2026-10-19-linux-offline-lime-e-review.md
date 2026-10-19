# Lime E 编译成品独立复核

下载 GitHub `v0.5.0-lime-e` 正式 Release，核对 ZIP SHA256 与 164 个清单文件后，使用 Linux Source2Viewer 独立解析实际二进制，不依赖“文件存在”或原报告代替检查。

- ZIP SHA256：`f75fb4a6efc5e055cadca8d556ea930f93dea4aa1f0f189b4899e572bb8b215f2`。
- 主模型 SHA256：`981f1d46fa80ad004972d2e04276ed6fde80208993191d47a832d4bf67ca778d`。
- 140 个模型/材质/贴图编译资源逐个 DATA 解析通过；139 个原始材质贴图 SHA256 完全匹配。
- 递归依赖无缺失；AG2 世界/第一人称/UI 图及两个 NmSkeleton 引用齐全；无旧 vanmgrph/animset 或不存在的 lime_e_arm 引用。
- 241 根骨骼、38 根手指骨骼；核心 24 根层级通过。
- 19 个渲染网格；第 19 个（索引 18）实际关联 firstperson_default，第一人称 LOD 0 与其他网格 LOD 1 分离。
- Release 编译日志显示退出码 0；其最终报告记录用户已在另一台 Windows 电脑确认手臂正常。这是已有用户反馈，不冒充本次 Linux 游戏实测。

**结论：编译成品静态复核通过，可作为后续官方 Workshop Tools 资源包输入。本次没有发布 Workshop、挂载 Linux、替换现有五人物或完成逐武器动作/命中伤害验证。**

实际资源目录：`addon/game/csgo_addons/lime_e_ag2_20261019_150756_709`；保持内部路径 `characters/models/exg/chrisan/lime_e/lime_e.vmdl`。手臂已内嵌，不创建额外假 arm 模型。
