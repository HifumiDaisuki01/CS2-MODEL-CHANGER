$ErrorActionPreference='Stop'
$cli='C:\Users\Administrator\Desktop\AG2模型修复\交付\tools\source2viewer\Source2Viewer-CLI.exe'
$beforeRoot='C:\Users\Administrator\Desktop\七模型及LimeE复查'
$runtime='C:\Users\Administrator\Desktop\十二人物Workshop上传包\开发工具\ResourceRepair'
$paths=@{'10052'='characters/exg/10052/10052.vmdl_c';'10073'='characters/exg/10073/10073.vmdl_c';'10092'='characters/exg/10092/10092.vmdl_c';xmanuka='characters/models/neon/xmanuka/xmanuka.vmdl_c'}
function Get-BinHash([string]$file){$b=[IO.File]::ReadAllBytes($file);if([BitConverter]::ToUInt32($b,0) -ne 0x46546c67){throw 'Not GLB'};$p=12;while($p -lt $b.Length){$size=[BitConverter]::ToUInt32($b,$p);$type=[BitConverter]::ToUInt32($b,$p+4);if($type -eq 0x004e4942){$h=[Security.Cryptography.SHA256]::Create();try{return ([BitConverter]::ToString($h.ComputeHash($b,$p+8,$size))).Replace('-','').ToLowerInvariant()}finally{$h.Dispose()}};$p+=8+$size};throw 'Missing BIN chunk'}
$rows=@(foreach($id in @('10052','10073','10092','xmanuka')){
 $source=Join-Path $PSScriptRoot ('repaired/'+$paths[$id]);$out=Join-Path $PSScriptRoot ('修复记录/'+$id+'-after.glb')
 $ErrorActionPreference='Continue';& $cli -d -i $source -o $out --gltf_export_format glb --gltf_export_animations *> (Join-Path $PSScriptRoot ('修复记录/'+$id+'-gltf.log'));$exit=$LASTEXITCODE;$ErrorActionPreference='Stop';if($exit -ne 0){throw "Export failed $id"}
 $old=Get-BinHash (Join-Path $beforeRoot ($id+'/'+$id+'-rigged.glb'));$new=Get-BinHash $out;if($old -ne $new){throw "Geometry/skin/animation buffer changed $id"}
 [pscustomobject]@{Id=$id;BeforeBinarySHA256=$old;AfterBinarySHA256=$new;MeshSkinAnimationBinaryIdentical=$true;GameTested=$false}
})
$rows|ConvertTo-Json -Depth 6|Set-Content -LiteralPath (Join-Path $PSScriptRoot '修复记录\independent-gltf-comparison.json') -Encoding UTF8
# Reject an unrelated AG2 model even when a caller supplies the approved animset name.
$test=Join-Path $PSScriptRoot '修复记录\negative-should-not-exist.vmdl_c';$ErrorActionPreference='Continue';& (Join-Path $runtime 'AnimIncludeRepair.exe') 'C:\Users\Administrator\Desktop\新版模型包带手臂（NL和Meme等通用）\characters\exg\10096\10096.vmdl_c' $test 'characters/models/shared/animsets/animset_ct.vmdl' (Join-Path $PSScriptRoot '修复记录\negative-should-not-exist.json') *> (Join-Path $PSScriptRoot '修复记录\negative-test.log');$exit=$LASTEXITCODE;$ErrorActionPreference='Stop';if($exit -eq 0 -or (Test-Path -LiteralPath $test)){throw 'Negative test failed'}
[pscustomobject]@{FourRepairGLTFBuffersIdentical=$true;UnrelatedModelRejected=$true;RepairsPerformedOnCurrentWindows=$true;GameTested=$false}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $PSScriptRoot '修复记录\windows-repair-tests.json') -Encoding UTF8
$rows|Select-Object Id,MeshSkinAnimationBinaryIdentical|Format-Table -AutoSize
