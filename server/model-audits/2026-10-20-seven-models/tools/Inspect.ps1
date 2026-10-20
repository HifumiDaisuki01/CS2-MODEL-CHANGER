$ErrorActionPreference='Stop'
$root='C:\Users\Administrator\Desktop\新版模型包带手臂（NL和Meme等通用）'
$cli='C:\Users\Administrator\Desktop\AG2模型修复\交付\tools\source2viewer\Source2Viewer-CLI.exe'
$all=Get-Content -LiteralPath 'C:\Users\Administrator\Desktop\新版模型包检查\models.json' -Raw -Encoding UTF8|ConvertFrom-Json
$items=@($all|Where-Object {$_.Path -match '/(10096|10018|10032|10052|10073|10092|xmanuka|lime_e)\.vmdl$'})
$rows=@(foreach($m in $items){
 $rel=$m.Path+'_c';$inputFile=Join-Path $root $rel;$id=if($rel.StartsWith('phase2/')){'phase2_'+[IO.Path]::GetFileNameWithoutExtension($m.Path)}else{[IO.Path]::GetFileNameWithoutExtension($m.Path)}
 $out=Join-Path $PSScriptRoot $id;New-Item -ItemType Directory -Path $out -Force|Out-Null
 $data=(& $cli -i $inputFile -b DATA 2>&1|Out-String);if($LASTEXITCODE -ne 0){throw "DATA parse failed $id"};[IO.File]::WriteAllText((Join-Path $out 'DATA.txt'),$data)
 $rerl=(& $cli -i $inputFile -b RERL 2>&1|Out-String);if($LASTEXITCODE -ne 0){throw "RERL parse failed $id"};[IO.File]::WriteAllText((Join-Path $out 'RERL.txt'),$rerl)
 $groups=@([regex]::Matches([regex]::Match($data,'m_meshGroups\s*=\s*\[(.*?)\]','Singleline').Groups[1].Value,'"([^"]+)"')|ForEach-Object {$_.Groups[1].Value})
 $masks=@([regex]::Matches([regex]::Match($data,'m_refMeshGroupMasks\s*=\s*\[(.*?)\]','Singleline').Groups[1].Value,'\d+')|ForEach-Object {[uint64]$_.Value})
 $fp=@();for($g=0;$g -lt $groups.Count;$g++){if($groups[$g] -match '#&firstperson_default$'){for($i=0;$i -lt $masks.Count;$i++){if(($masks[$i] -band ([uint64]1 -shl $g)) -ne 0){$fp+=$i}}}}
 $names=[regex]::Match($data,'m_modelSkeleton\s*=\s*\{.*?m_boneName\s*=\s*\[(.*?)\]','Singleline').Groups[1].Value
 $bones=@([regex]::Matches($names,'"([^"]+)"')|ForEach-Object {$_.Groups[1].Value})
 $glb=Join-Path $out ($id+'-rigged.glb');$ErrorActionPreference='Continue';& $cli -d -i $inputFile -o $glb --gltf_export_format glb --gltf_export_animations *> (Join-Path $out 'gltf-export.log');$ErrorActionPreference='Stop';$export=$LASTEXITCODE -eq 0 -and (Test-Path -LiteralPath $glb)
 [pscustomobject]@{Id=$id;Path=$rel;SHA256=(Get-FileHash -LiteralPath $inputFile -Algorithm SHA256).Hash.ToLowerInvariant();Missing=@($m.Missing);Dependencies=@($m.Dependencies);AG2=($data -match 'worldmodel.vnmgraph');LegacyReferences=@([regex]::Matches($rerl,'[^\s"]+(?:vanmgrph|animset)[^\s"]*')|ForEach-Object {$_.Value});Bones=$bones.Count;BoneNames=$bones;MeshGroups=$groups;FirstPersonMeshIndices=$fp;HasArmConfig=($data -match 'character_arm_config');GLTFExportSucceeded=$export;GameTested=$false}
})
$rows|ConvertTo-Json -Depth 10|Set-Content -LiteralPath (Join-Path $PSScriptRoot 'fresh-resource-audit.json') -Encoding UTF8
$rows|Select-Object Id,Bones,AG2,FirstPersonMeshIndices,HasArmConfig,GLTFExportSucceeded|Format-Table -AutoSize
