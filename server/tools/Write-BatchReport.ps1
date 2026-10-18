param([Parameter(Mandatory=$true)][string]$Output)
$ErrorActionPreference='Stop'
$models=(Get-Content (Join-Path $Output 'models.json') -Raw -Encoding UTF8 | ConvertFrom-Json)
$assets=(Get-Content (Join-Path $Output 'assets.json') -Raw -Encoding UTF8 | ConvertFrom-Json)
$reviewPath=Join-Path $Output 'semantic-review.json'
$review=@{}
if(Test-Path -LiteralPath $reviewPath){Get-Content $reviewPath -Raw -Encoding UTF8 | ConvertFrom-Json | ForEach-Object {foreach($r in $_){$review[$r.Path]=$r}}}
$assetHashes=@{};foreach($a in $assets){$assetHashes[$a.Path]=$a.Hash}
foreach($m in $models){
 if($review.ContainsKey($m.Path)){
  $r=$review[$m.Path]
  if(!$r.SourceSHA256 -or $r.SourceSHA256 -ne $assetHashes[$m.Path+'_c']){throw "Semantic report does not match model content: $($m.Path)"}
  $m | Add-Member -Force -NotePropertyName Semantic -NotePropertyValue $r
  if($m.Status -eq 'path_compatibility_pending' -and @($m.Missing).Count -eq 0 -and @($m.Conflicts).Count -eq 0 -and @($m.CaseMismatch).Count -eq 0 -and @($r.CSBones).Count -ge 6 -and $m.Path.StartsWith('phase2/characters/')){$m.Status='candidate_requires_batch_plugin'}
  if($m.Status -eq 'files_complete_candidate' -and $m.Path -ne 'characters/models/aluona/aluona.vmdl'){
   if($r.BoneCount -eq 0){$m.Status='not_player_model'}
   elseif(@($r.CSBones).Count -lt 6){$m.Status='skeleton_compatibility_pending'}
  }
 }elseif($m.Status -eq 'files_complete_candidate' -and $m.Path -ne 'characters/models/aluona/aluona.vmdl'){$m.Status='semantic_review_pending'}
 if($m.Path -eq 'characters/models/b2/b2.vmdl'){$m.Status='not_player_model'}
}
$repo=Split-Path (Split-Path $PSScriptRoot)
$config=Get-Content (Join-Path $repo 'server\config\PlayerModelChanger.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$allConfig=Get-Content (Join-Path $repo 'server\config\PlayerModelChanger.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$lines=New-Object 'System.Collections.Generic.List[string]'
$lines.Add('# 批量模型检查清单')
$lines.Add('')
$lines.Add('仅离线资源检查；不是游戏内验证。名称来自文件名，未猜测角色中文名。阿洛娜既有服务器资源未修改。')
$lines.Add('')
$lines.Add('| 状态 | 数量 |')
$lines.Add('|---|---:|')
$models | Group-Object Status | ForEach-Object {$lines.Add('| '+$_.Name+' | '+$_.Count+' |')}
$lines.Add('')
$lines.Add('files_complete_candidate：递归 RERL 引用已在本合集或此前确认的原版资源中找到；仍需人物身份、动画、第一人称、碰撞及实际预缓存验证。arms_candidate 为按名称识别的附件候选，不放人物菜单。dependency_pending 和 conflict 不纳入候选菜单。再发布授权均待逐项确认。')
$lines.Add('')
$lines.Add('| 标识 | 路径 | 状态 | 未解决依赖 | 冲突 |')
$lines.Add('|---|---|---|---:|---:|')
$rows=@(); $i=0
foreach($m in $models) {
 $i++; $id='batch_{0:d3}' -f $i
 if($m.Path -eq 'characters/models/aluona/aluona.vmdl') {$id='aluona'}
 if($m.Path -eq 'phase2/characters/models/s2ze/ms/genesis/genesis_ag2.vmdl') {$id='genesis_ag2'}
 $m.Id=$id
 $entry=[pscustomobject]@{name=([IO.Path]::GetFileNameWithoutExtension($m.Path));path=$m.Path;permissions=@();permissionsOr=@();side='All';disableleg=$false;hideinmenu=$true}
 if($id -ne 'aluona') {$allConfig.Models | Add-Member -NotePropertyName $id -NotePropertyValue $entry}
 if($m.Status -in @('files_complete_candidate','candidate_requires_batch_plugin') -and $id -ne 'aluona') {$config.Models | Add-Member -NotePropertyName $id -NotePropertyValue $entry}
 $lines.Add('| '+$id+' | '+$m.Path+' | '+$m.Status+' | '+@($m.Missing).Count+' | '+@($m.Conflicts).Count+' |')
 $rows += [pscustomobject]@{Id=$id;Path=$m.Path;Status=$m.Status;Missing=($m.Missing -join '; ');Conflicts=($m.Conflicts -join '; ');CaseMismatch=($m.CaseMismatch -join '; ');ArmsCandidates=($m.ArmsCandidates -join '; ');Bones=$m.Semantic.BoneCount;CSBones=@($m.Semantic.CSBones).Count;EmbeddedAnimation=$m.Semantic.HasANIM;GameTest=$(if($id -eq 'aluona'){'previous_user_confirmed_commands'}else{'not_tested'});Redistribution='unconfirmed'}
}
$models | ConvertTo-Json -Depth 7 | Set-Content (Join-Path $Output 'models.json') -Encoding UTF8
$rows | Export-Csv (Join-Path $Output '模型清单.csv') -NoTypeInformation -Encoding UTF8
$lines | Set-Content (Join-Path $Output '模型清单.md') -Encoding UTF8
$models | Where-Object {$_.Missing.Count -or $_.Conflicts.Count -or $_.CaseMismatch.Count} | ConvertTo-Json -Depth 8 | Set-Content (Join-Path $Output 'missing-dependencies.json') -Encoding UTF8
$config | ConvertTo-Json -Depth 15 | Set-Content (Join-Path $Output 'PlayerModelChanger.candidates.json') -Encoding UTF8
$allConfig | ConvertTo-Json -Depth 15 | Set-Content (Join-Path $Output 'PlayerModelChanger.inventory-only.json') -Encoding UTF8
$assets | Group-Object Path | Where-Object {$_.Count -gt 1} | ForEach-Object {[pscustomobject]@{Path=$_.Name;Copies=$_.Count;Variants=@($_.Group.Hash | Select-Object -Unique).Count}} | Export-Csv (Join-Path $Output 'duplicates.csv') -NoTypeInformation -Encoding UTF8
$lookup=@{};foreach($a in $assets){$lookup[$a.Path]=$a}
$chosen=@{};foreach($m in $models | Where-Object {$_.Status -in @('files_complete_candidate','candidate_requires_batch_plugin')}){foreach($p in $m.Dependencies){if($lookup.ContainsKey($p)){$chosen[$p]=$lookup[$p]}}}
$targetRoot=Join-Path $Output 'addon\game\csgo_addons\cs2cm_models_batch'
if(Test-Path -LiteralPath $targetRoot){throw 'Final addon already exists; archive it before rebuilding to avoid stale resources'}
New-Item -ItemType Directory -Path $targetRoot -Force | Out-Null
$sums=@();foreach($a in $chosen.Values){$target=Join-Path $targetRoot $a.Path;New-Item -ItemType Directory -Path (Split-Path $target) -Force | Out-Null;Copy-Item -LiteralPath $a.Source -Destination $target; $actual=(Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant();if($actual -ne $a.Hash){throw "Copy mismatch: $($a.Path)"};$sums+=($actual+'  '+$a.Path)}
[IO.File]::WriteAllLines((Join-Path $Output 'SHA256SUMS.txt'),[string[]]($sums | Sort-Object),(New-Object Text.UTF8Encoding($false)))
@'
# 使用说明与验证边界

addon/game/csgo_addons/cs2cm_models_batch 是经过语义筛选的完整闭包人物候选目录；保留原路径，不包含合集地图脚本。inspection-only 为检查中间结果，严禁作为可用人物包部署。SHA256SUMS.txt 为最终资源复制后逐项核对的哈希。未修改或删除原始模型合集。

模型清单.md / CSV 为列表；models.json 包含每项传递依赖、缺失、冲突、大小写问题、同目录手臂候选。assets.json 记录原路径和哈希。手臂候选仅由名称判定，未声称已经绑定。PHYS 块存在不证明命中盒正确。phase2 原路径保留，未擅自去除前缀。

PlayerModelChanger.candidates.json 只含资源闭包完整候选和既有阿洛娜；新增项均 hideinmenu=true，供人工隔离测试，不是正式服直接覆盖配置。inventory-only 配置仅供索引，包含不可用项，严禁部署。正式服当前 PMC 只允许 characters/；本地兼容版 1.8.6-batch.1 增加 phase2/characters/，保留原路径。genesis_ag2 必须使用兼容版并在隔离环境测试，不能直接给正式服旧 DLL 添加配置。

未生成可上线的 resource-catalog.json：它必须针对最终打包、真实挂载 VPK 的 SHA256 生成。未打包新 VPK、未上传 Workshop、未操作 Steam 账户、未修改正式服、未进行客户端测试。不要将本目录直接写进原版 csgo 覆盖文件。

依赖分析解析 Source 2 版本12资源头及 RERL 64位相对字符串引用，递归闭包；无 RERL 块记为空引用，不保证 DATA 动态字符串/运行时选择引用已经穷尽。未知资源头或损坏结构阻断闭包。原版资源白名单为本次在正式服务器4份 VPK 索引中逐条核实的271项引用，其他缺失项即使看起来像官方资源也不猜测通过。

再发布授权记录未随合集提供：二进制仅本地整理，禁止据此自动公开发布；GitHub 仅提交工具和清单。后续逐项确认授权、使用 Source 2 Viewer复核候选的 DATA/骨架/动画与第一人称设置后，再在有CS2的隔离客户端验证。确认后用 Workshop 工具将 game/csgo_addons 下目录作为统一 addon 的资源输入，保留已验证的阿洛娜生产包不动。
'@ | Set-Content (Join-Path $Output 'README.md') -Encoding UTF8
$models | Group-Object Status | Select-Object Name,Count | ConvertTo-Json
