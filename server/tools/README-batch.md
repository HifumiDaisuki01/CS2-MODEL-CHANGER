# 批量人物资源离线流程

本流程不挂载资源、不修改正式服、不操作Steam、不上传Workshop。所有输出必须独立于原始模型目录。只读解析原编译文件，不将glTF当作可用CS2资源。

1. 仅在用户指定合集内检查：`Prepare-Batch.ps1 -Source <合集父目录> -Output <新的输出目录>`。当前目录识别规则为：父目录下含characters的集合根，以及既有阿洛娜恢复包的addon根。phase2前缀保留。VPK单独使用verify_vpk.py检查，不盲目解包覆盖。
2. 从正式服只读提取原版VPK目录索引，核对外部引用；`base-resources-confirmed.txt`为本批已确认的271项路径，`base-index-provenance.json`记录4个目录文件的SHA。游戏升级后必须重新核对，不能把它当作所有版本的永久白名单。
3. 在安装Python和Source 2 Viewer的开发环境运行：`python inspect_batch5.py --input <保持内部路径的模型输入根> --output <新的独立报告目录> --cli <Source2Viewer-CLI> --threads 4`。不会改输入目录。只解析DATA并保存骨骼、动画块、外部引用和工具原始输出；每个模型记录SourceSHA256。可直接读取本批的“新版人物模型(推荐)”目录；远程检查仅传输模型文件和必要目录结构，无需下载CS2。
4. 用新目录重新运行 `Prepare-Batch.ps1 -Source <原合集父目录> -Output <另一新目录> -SemanticReview <semantic-review.json>`。报告SHA必须匹配真实模型，缺依赖或解析失败时不纳入候选。手臂命名、人物骨骼和资源分类均为筛选规则，不能替代实际客户端测试。
5. 查看模型总表、models.json、缺失报告和配置。新增标识一旦上线应固定；本批只有aluona、genesis_ag2进入候选配置，其余batch编号只是离线清单索引，未来不要据编号顺序覆盖已上线标识。
6. 人工确认授权，复核DATA中的动态依赖、动画与手臂；使用Workshop工具对最终addon打包，检查所有VPK条目CRC，针对真实挂载VPK生成资源白名单。只准备局部补丁不足以证明分发成功。
7. 经授权再隔离测试预缓存、T/CT、第一人称、动作、重生、重连、另一客户端和命中盒。不能将文件完整、PHYS存在、命令注册或服务端SetModel回读写成客户端验证通过。

本批交付见 `../batch5/整理结果.md`。本地完整资源和301项原始工具输出在桌面“模型整理-追加5”；GitHub仅包含代码、配置与审查元数据，未公开授权待确认的模型二进制。
