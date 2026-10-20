$ErrorActionPreference='Stop'
$root='C:\Users\Administrator\Desktop\新版模型包带手臂（NL和Meme等通用）'
$rows=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'fresh-resource-audit.json') -Raw -Encoding UTF8|ConvertFrom-Json
$skin=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'firstperson-skin-audit.json') -Raw -Encoding UTF8|ConvertFrom-Json
$core=@(Get-Content -LiteralPath 'C:\Users\Administrator\Desktop\Lime-E人物手臂编译包\Lime-E-Windows\tools\vendor\canonical_skeleton.txt' -Encoding UTF8|Select-Object -First 24)
$base=Get-Content -LiteralPath 'C:\Users\Administrator\Desktop\Lime-E人物手臂编译包\Lime-E-Windows\reports\base-resources-confirmed.txt' -Encoding UTF8
$result=@(foreach($row in $rows){
 $id=$row.Id;$data=[IO.File]::ReadAllText((Join-Path $PSScriptRoot ($id+'\DATA.txt')))
 $parents=@([regex]::Matches([regex]::Match($data,'m_modelSkeleton\s*=\s*\{.*?m_nParent\s*=\s*\[(.*?)\]','Singleline').Groups[1].Value,'-?\d+')|ForEach-Object {[int]$_.Value})
 $issues=@(foreach($line in $core){$parts=$line -split '\s+';$name=$parts[0];$parent=$parts[1];$i=[Array]::IndexOf([object[]]$row.BoneNames,$name);if($i -lt 0){'Missing '+$name;continue};$actual=if($parents[$i] -lt 0){'-'}else{$row.BoneNames[$parents[$i]]};if($actual -cne $parent){$name+': '+$actual+' != '+$parent}})
 $s=$skin|Where-Object {$_.Name -eq $id}|Select-Object -First 1
 $unresolved=@($row.Dependencies|Where-Object {-not (Test-Path -LiteralPath (Join-Path $root $_)) -and $_ -notin $base})
 [pscustomobject]@{Id=$id;Path=$row.Path;SHA256=$row.SHA256;Bones=$row.Bones;AG2GraphPresent=$row.AG2;Core24Issues=$issues;UnresolvedInCollection=$unresolved;FirstPersonMeshIndices=$row.FirstPersonMeshIndices;FirstPersonSkinnedVertices=$s.FirstPersonVertices;StandardHandFingerSkinInfluence=$s.CanonicalHandFingerSkinInfluence;LegacyVWeaponWeightedBones=$s.LegacyViewmodelWeightedBones;ArmConfigPresent=$row.HasArmConfig;GameTested=$false;DependencyBasis='Prior recursive dependency inventory, freshly checked against current collection and confirmed base list; root DATA/RERL freshly parsed.'}
})
$result|ConvertTo-Json -Depth 10|Set-Content -LiteralPath (Join-Path $PSScriptRoot 'usability-summary.json') -Encoding UTF8
$result|Select-Object Id,Bones,AG2GraphPresent,@{n='CoreIssues';e={$_.Core24Issues.Count}},FirstPersonSkinnedVertices,@{n='Missing';e={$_.UnresolvedInCollection.Count}}|Format-Table -AutoSize
