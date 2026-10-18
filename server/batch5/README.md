# 使用说明与验证边界

addon/game/csgo_addons/cs2cm_models_batch 是经过语义筛选的完整闭包人物候选目录；保留原路径，不包含合集地图脚本。inspection-only 为检查中间结果，严禁作为可用人物包部署。SHA256SUMS.txt 为最终资源复制后逐项核对的哈希。未修改或删除原始模型合集。

模型清单.md / CSV 为列表；models.json 包含每项传递依赖、缺失、冲突、大小写问题、同目录手臂候选。assets.json 记录原路径和哈希。手臂候选仅由名称判定，未声称已经绑定。PHYS 块存在不证明命中盒正确。phase2 原路径保留，未擅自去除前缀。

PlayerModelChanger.candidates.json 只含资源闭包完整候选和既有阿洛娜；新增项均 hideinmenu=true，供人工隔离测试，不是正式服直接覆盖配置。inventory-only 配置仅供索引，包含不可用项，严禁部署。正式服当前 PMC 只允许 characters/；本地兼容版 1.8.6-batch.1 增加 phase2/characters/，保留原路径。genesis_ag2 必须使用兼容版并在隔离环境测试，不能直接给正式服旧 DLL 添加配置。

未生成可上线的 resource-catalog.json：它必须针对最终打包、真实挂载 VPK 的 SHA256 生成。未打包新 VPK、未上传 Workshop、未操作 Steam 账户、未修改正式服、未进行客户端测试。不要将本目录直接写进原版 csgo 覆盖文件。

依赖分析解析 Source 2 版本12资源头及 RERL 64位相对字符串引用，递归闭包；无 RERL 块记为空引用，不保证 DATA 动态字符串/运行时选择引用已经穷尽。未知资源头或损坏结构阻断闭包。原版资源白名单为本次在正式服务器4份 VPK 索引中逐条核实的271项引用，其他缺失项即使看起来像官方资源也不猜测通过。

再发布授权记录未随合集提供：二进制仅本地整理，禁止据此自动公开发布；GitHub 仅提交工具和清单。后续逐项确认授权、使用 Source 2 Viewer复核候选的 DATA/骨架/动画与第一人称设置后，再在有CS2的隔离客户端验证。确认后用 Workshop 工具将 game/csgo_addons 下目录作为统一 addon 的资源输入，保留已验证的阿洛娜生产包不动。
