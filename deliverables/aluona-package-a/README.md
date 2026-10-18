# 阿洛娜成品包 A

**已在本机 CS2 实际显示，并完成分阶段冷启动复测。** 请优先阅读 `EXPERIENCE_CN.md`，其中记录了如何实现、失败原因和关键时序。

## 使用

1. 解压后运行 `Install-Local.ps1`：只安装到独立 addon 目录，已有相同文件会跳过；不同文件会拒绝覆盖。当前电脑已经部署好，可直接下一步。
2. Steam 正常运行，关闭其他 CS2，双击 `Start-Aluona-Test.cmd`。
3. 等 Dust2 完全进入可操作画面，加入 T 或 CT，瞄准附近地面。
4. 游戏控制台执行 `exec aluona_precache.cfg`，让游戏继续运行至少 **6 秒**。
5. 再执行 `exec aluona_apply.cfg`，关闭控制台查看第三人称。
6. `firstperson` 查看手部，`thirdperson` 切回人物；`+duck` / `-duck` 查看蹲姿。需要重试可执行 `cs2cm_apply`。

不要把两个 exec 连在同一帧；不要在加载画面执行。预缓存实体可暂留，退出游戏即清除。

默认游戏路径为本次确认的 `Z:\steam\steamapps\common\Counter-Strike Global Offensive`。其他位置可用 `-GamePath` 参数指定，例如：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Install-Local.ps1 -GamePath "D:\SteamLibrary\steamapps\common\Counter-Strike Global Offensive"
powershell -NoProfile -ExecutionPolicy Bypass -File .\Start-Aluona-Test.ps1 -GamePath "D:\SteamLibrary\steamapps\common\Counter-Strike Global Offensive"
```

## 内容

- `addon/`：14 个原编译模型/材质/纹理、一个测试脚本的源文件和编译文件、两个 cfg；保留真实相对路径。
- `packages/cs2cm_sample.vpk`：上一阶段已经构建的样本原包，本次未重新打包模型。
- `evidence/`：最终第三人称、蹲姿、第一人称截图、成功日志及失败排错证据。
- `PlayerModelChanger-Aluona.json`：已核对格式的人物插件样本配置。本次本地成功实际使用官方 cs_script，不依赖这个插件。
- `SHA256SUMS.txt`：包内文件哈希。

本机客户端和 listen server 使用同一个本地 addon 读取资源。本包没有 Workshop ID，不会自行完成社区服资源分发，也不代表 Linux/CSS/KeranStrat 已测试。

没有修改官方 VPK、官方 gameinfo 或原始模型包，没有公开发布 Workshop，没有连接远程服务器。本次调试游戏已由用户关闭；启动器不启用 VConsole 监听。

移除本次新建的 `game/csgo_addons/cs2cm_aluona_localtest` 和对应 content addon 目录即可撤销。不要删除官方 csgo 目录。
