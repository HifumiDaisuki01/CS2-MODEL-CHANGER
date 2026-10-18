# Local Windows compilation completed: 2026-10-18

All three selected models were compiled using installed Valve resourcecompiler.exe. Every compiler exit code is 0; each log reports 1 compiled, 0 failed. Verify-Compiled.ps1 and Source 2 Viewer passed model parsing, AG2 graph/skeleton bindings, 24 core bones and parent hierarchy, and absence of AG1 references.

Final addon: ks_ag2_repair_20261018_145133_943
CS2: D:\SteamLibrary\steamapps\common\Counter-Strike Global Offensive
Steam build: 25966348; patch 1.41.9.1; SourceRevision 11133601, Oct 15 2026.
Compiler PE FileVersion is not populated. Its SHA256 is 8DF3DDC8825C6CEE980D1C25F2AB9A386E9183AB6AB6BA2C96FE2C59872400F8; no standalone compiler version is claimed.

Models under game/csgo_addons/ks_ag2_repair_20261018_145133_943/:
- characters/models/exg/myers/myers.vmdl_c
- characters/models/exg/aquaz/km_decade/km_decade.vmdl_c
- characters/models/exg/dujiaoshou/dujiaoshou.vmdl_c (read from selected-models.json)

118 materials/textures parsed using Source 2 Viewer; 87 unique nested material/texture references resolve against addon or installed game VPK indices. All 119 original delivery runtime resources remain SHA256-identical, including 14 Aluona resources. Each compiled PHYS parses and retains the original 12 capsules plus 3 spheres. This does not prove in-game ragdoll behavior.

No model source changes were necessary. Build-AG2.ps1 required a Windows PowerShell fix: resolve PackageRoot/S2V after parameter binding. It now records each compiler exit code and compiler identity. Explicit path arguments enabled the first successful build; the fixed default invocation also compiled all three successfully.

Internal filesystem paths have no case-insensitive duplicates. The earlier isolated addon ks_ag2_repair_20261018_145010_507 contains the same three model paths and must not be mounted together with the final addon. No previous addon was overwritten. Arbitrary Workshop VPK mount combinations remain unverified.

Real gameplay: UNVERIFIED for every model. No observed evidence for ERROR/purple textures, T-pose, idle/walk/crouch/jump, weapon holding/shoot/reload, deformation, death/ragdoll, first person, hitboxes or damage. No Workshop upload or ID change was performed; 3821951835 was not modified.

To begin manual testing, select the final addon in CS2 Workshop Tools and open each model in ModelDoc. Use the existing TESTING_CHECKLIST.md. Do not enable all three on a production server based solely on these structural checks.

Full stdout/stderr, exact exit codes, hashes, block dumps and checks are in reports/windows-ks_ag2_repair_20261018_145133_943/. Private resource dumps and model/source binaries remain local only. GitHub receives only the build script and this aggregate report.