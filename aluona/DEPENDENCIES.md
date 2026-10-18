# 资源与工具依赖

交付包含实际显示使用的 14 个原编译资源：1 个 vmdl_c、6 个 vmat_c、7 个 vtex_c。它们的逐文件 SHA256 保存在 `evidence/extracted-resources.csv`，完整相对路径不变。所有需要的自定义材质和纹理都在 Release 中；仓库中只保存清单，二进制由 Release 下载。

`evidence/dependencies-normalized.csv` 为最终闭包：包内依赖标记 bundled；依赖原版的标记 installed-CS2。旧 `aluona-dependencies.csv` 中三个默认纹理标为 local，是原模型包扫描时的来源分类，不代表当前松散 addon 仍需覆盖这些默认资源。

原版依赖包括 UI/viewmodel/worldmodel 三个动画图、viewmodel/worldmodel 两个骨架，以及 default_ao、default_metal、default_normal 三个共享纹理。它们由当前正版 CS2 提供，不把官方资源拷入松散 addon。原样本 VPK 中保留的默认纹理不代表已经通过独立 VPK 挂载测试。

本地已验证环境：Windows x64、Steam CS2 buildid 25966348、Workshop Tools、DX11。构建号来自本机 appmanifest，只记录版本而不备份账户文件。升级游戏后应重做本地验收。

`aluona_test.js` 导入引擎提供的 `cs_script/point_script`。对应 `aluona_test.vjs_c` 已包含；默认安装无需编译。仅修改 JS 时才运行 `Rebuild-Script.ps1 -GamePath ...`。人物原始建模源文件、未编译 vmdl/vmat、纹理 PSD 不在原包内，不能声称能够从艺术源文件重建人物。

无 Steam/CS2 的 10GB 开发电脑可以下载、解压、校验、阅读和开发服务端配置；无法在这台开发机运行完整 CS2 或官方 resourcecompiler。无需安装 Steam 来接收备份。

服务端依赖另外安装：Linux CS2、匹配版本的 Metamod、CounterStrikeSharp、MultiAddonManager、PlayerModelChanger。当前交付不包含未经测试的插件二进制；配置参考不代表 Linux 运行验证。
