## Unreleased — batch model preparation (2026-10-18)

## v0.7.0 正式验收 — 2026-10-20

- Workshop 3823495199 deployed: fifteen configured/verified/precached models; actual 824 resource hashes match, old Huohuo/Hifumi removed.
- User manually confirmed all models work normally; designated this package for formal use. No exhaustive weapon/hitbox validation claimed.
- Added server-migration guide covering complete plugin/config/SQLite transfer, MAM and absolute-path resource catalog regeneration. Existing release assets and older releases unchanged.


## v0.7.0-fifteen-models — 2026-10-20

- Removed Huohuo and Hifumi from the upload package; preserved all ten retained model hashes, current Lime E and latest Myers.
- Added 10092/Shorekeeper, 10073/Sparkle, 10096/Elysia, xmanuka and 10052; repaired three stale external-arm settings and the audited 10052 legacy animset include using structured serialization.
- All 824 resources parsed, fifteen AG2/core skeleton/FP meshes verified; four repairs preserve independent glTF binary data. Added clean-addon upload guidance and stale-model rejection.
- New five client/Workshop validation pending; production remains unchanged. Preserved prior releases.


## 2026-10-20 — Model audit and Lime E hand-repair record

- Audited seven new-collection player models and corresponding phase2 resources; distinguished complete AG2 candidates, obsolete arm references, mixed AG1/AG2 dependencies and full AG1 migration.
- Compared new-collection Lime E with deployed v0.5.0; retain game-tested build while collection build retains legacy dependencies.
- Published actual bind-pose rebind development references, stage reports and explicit glTF skin-export validation requirements. No server/model changes or new client tests in this audit.


## v0.6.0-twelve-models — 2026-10-19

- Prepared 12-character official Workshop Tools package; retained existing five, selected latest Myers, added compiled Lime E and Chikari/Serina/Baizhouzi/Hifumi/Feibi/Chiffon Fox.
- Repaired four obsolete external arm configurations with structured KV3/RERL editing, preserving all other compiled blocks; Windows execution and independent glTF binary comparisons passed.
- Added exact project hash verifier, merge configuration and transparent static-test reports: 625 resources, 12 primary models. Workshop/client testing remains pending; production server unchanged.
- Third-party model binaries remain in private local delivery, not public Git or this release.



- Audit 301 unique models; preserve original compiled paths and Aluona; stage one Genesis AG2 test candidate and report blocked resources.
- Add repeatable local inventory, RERL closure, SHA256 copy checks and Source 2 Viewer semantic inspection tools.
- Allow verified phase2/characters/ resources in the staged PMC compatibility build; keep production and existing Releases unchanged.

# Linux 部署版 0.2.0

- 部署 MAM 1.6.2 与 PMC 1.8.6 适配版，验证 Workshop 下载、挂载及真人指令换模。
- SQLite 同步提交、default 别名、资源白名单与失效回退、实体身份保护。
- 保留 KeranStrat，普通玩家双队可选，训练 BOT 不自动换模。
- 新增流式 VPK 校验、只输出暂存配置的合并工具、测试和批量模型经验。
- 原 Windows 恢复包及 Release 不修改。
