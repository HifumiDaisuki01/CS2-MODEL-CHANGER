param([Parameter(Mandatory=$true)][string]$GameAddon,[Parameter(Mandatory=$true)][string]$Manifest,[Parameter(Mandatory=$true)][string]$S2V,[Parameter(Mandatory=$true)][string]$ReportDirectory,[Parameter(Mandatory=$true)][string]$CS2Path)
$ErrorActionPreference='Stop'
function Invoke-Viewer([string]$File,[string]$Block,[string]$Log){
 $err=$Log+'.stderr';$arguments=@('-i',('"'+$File+'"'),'-b',$Block)
 $p=Start-Process -FilePath $S2V -ArgumentList $arguments -WindowStyle Hidden -Wait -PassThru -RedirectStandardOutput $Log -RedirectStandardError $err
 if($p.ExitCode -ne 0){throw "Source 2 Viewer failed: $File ($Block)"}
 return [IO.File]::ReadAllText($Log)
}
New-Item -ItemType Directory -Path $ReportDirectory -Force | Out-Null
$models=Get-Content -LiteralPath $Manifest -Raw -Encoding UTF8 | ConvertFrom-Json
$critical=@('root_motion','pelvis','spine_0','spine_1','spine_2','spine_3','neck_0','head_0','clavicle_L','clavicle_R','arm_upper_L','arm_upper_R','arm_lower_L','arm_lower_R','hand_L','hand_R','leg_upper_L','leg_upper_R','leg_lower_L','leg_lower_R','ankle_L','ankle_R','wpnPivot','wpn')
$parents=@{root_motion='';pelvis='root_motion';spine_0='pelvis';spine_1='spine_0';spine_2='spine_1';spine_3='spine_2';neck_0='spine_3';head_0='neck_0';clavicle_L='spine_3';clavicle_R='spine_3';arm_upper_L='clavicle_L';arm_upper_R='clavicle_R';arm_lower_L='arm_upper_L';arm_lower_R='arm_upper_R';hand_L='arm_lower_L';hand_R='arm_lower_R';leg_upper_L='pelvis';leg_upper_R='pelvis';leg_lower_L='leg_upper_L';leg_lower_R='leg_upper_R';ankle_L='leg_lower_L';ankle_R='leg_lower_R';wpnPivot='root_motion';wpn='wpnPivot'}
$results=@()
if(!('Ag2VpkDirectory' -as [type])){Add-Type -Path (Join-Path $PSScriptRoot 'ResourcePaths.cs')}
$base=New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::Ordinal)
foreach($area in @('csgo','core','csgo_core')){
 $dir=Join-Path $CS2Path ('game\'+$area)
 if(Test-Path -LiteralPath $dir){foreach($vpk in Get-ChildItem -LiteralPath $dir -Filter '*_dir.vpk' -File){foreach($name in [Ag2VpkDirectory]::Read($vpk.FullName)){[void]$base.Add($name)}}}
}
if($base.Count -eq 0){throw 'No original game VPK resources available for dependency validation'}
$addonNames=New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::Ordinal)
$addonRoot=[IO.Path]::GetFullPath($GameAddon).TrimEnd('\')
foreach($file in Get-ChildItem -LiteralPath $addonRoot -Recurse -File){[void]$addonNames.Add($file.FullName.Substring($addonRoot.Length+1).Replace('\','/'))}
foreach($m in $models){
 if($m.Path -notmatch '^characters/[a-zA-Z0-9_./-]+\.vmdl$' -or $m.Path.Contains('..')){throw 'Unsafe manifest path'}
 $file=Join-Path $GameAddon ($m.Path+'_c')
 if(!$addonNames.Contains($m.Path+'_c')){throw "Compiled model path casing differs: $($m.Path)"}
 if(!(Test-Path -LiteralPath $file) -or (Get-Item -LiteralPath $file).Length -lt 64){throw "Compiled model absent: $($m.Id)"}
 $data=Invoke-Viewer $file 'DATA' (Join-Path $ReportDirectory ($m.Id+'-compiled-DATA.txt'))
 $rerl=Invoke-Viewer $file 'RERL' (Join-Path $ReportDirectory ($m.Id+'-compiled-RERL.txt'))
 if(($data+$rerl) -match '\.vanmgrph|animsets/animset_'){throw "Legacy animation reference remains: $($m.Id)"}
 $refs=@([regex]::Matches($rerl,'(?m)^\s*[0-9A-Fa-f]{16}\s+(.+?\.(?:vnmgraph|vnmskel|vmat|vtex|vmdl|vpcf|vsnd|vanim))\s*$') | ForEach-Object {$_.Groups[1].Value} | Sort-Object -Unique)
 if($refs.Count -eq 0){throw 'Compiled RERL dependency table not recognized'}
 foreach($ref in $refs){if($ref.Contains('..')){throw 'Unsafe compiled reference'};$compiled=$ref+'_c';if(!$addonNames.Contains($compiled) -and !$base.Contains($compiled)){throw "Compiled dependency unavailable or casing differs: $ref"}}
 foreach($required in @('animation/graphs/worldmodel/worldmodel.vnmgraph','animation/graphs/ui/uimodel.vnmgraph','animation/graphs/viewmodel/viewmodel.vnmgraph','animation/skeletons/characters/worldmodel.vnmskel','animation/skeletons/characters/viewmodel.vnmskel')){if($refs -cnotcontains $required){throw "Compiled model missing AG2 binding: $required"}}
 $bm=[regex]::Match($data,'m_modelSkeleton\s*=\s*\{\s*m_boneName\s*=\s*\[(.*?)\]','Singleline')
 if(!$bm.Success){throw 'Compiled skeleton missing'}
 $names=@([regex]::Matches($bm.Groups[1].Value,'"([^"]+)"') | ForEach-Object {$_.Groups[1].Value})
 foreach($bone in $critical){if($names -cnotcontains $bone){throw "Compiled critical bone missing: $bone"}}
 $pm=[regex]::Match($data,'m_nParent\s*=\s*\[(.*?)\]','Singleline');if(!$pm.Success){throw 'Compiled parent table missing'}
 $indices=@([regex]::Matches($pm.Groups[1].Value,'-?\d+') | ForEach-Object {[int]$_.Value});if($indices.Count -ne $names.Count){throw 'Compiled skeleton parent count mismatch'}
 for($i=0;$i -lt $names.Count;$i++){
  if($indices[$i] -ge $names.Count -or $indices[$i] -lt -1){throw 'Invalid parent index'}
  if($critical -ccontains $names[$i]){$actual=if($indices[$i] -eq -1){''}else{$names[$indices[$i]]};if($actual -cne $parents[$names[$i]]){throw "Compiled core hierarchy mismatch: $($names[$i])"}}
 }
 # First-person geometry must survive compilation as an actual mesh mask.
 $gm=[regex]::Match($data,'m_meshGroups\s*=\s*\[(.*?)\]','Singleline')
 $groups=@([regex]::Matches($gm.Groups[1].Value,'"([^"]+)"') | ForEach-Object {$_.Groups[1].Value})
 $first=-1;$third=-1
 for($gi=0;$gi -lt $groups.Count;$gi++){if($groups[$gi] -match '#&firstperson_default$'){$first=$gi};if($groups[$gi] -match '#&thirdperson_default$'){$third=$gi}}
 if($first -lt 0 -or $third -lt 0 -or $first -ge 63){throw 'Compiled first/third-person group names missing or invalid'}
 $maskText=[regex]::Match($data,'m_refMeshGroupMasks\s*=\s*\[(.*?)\]','Singleline')
 $masks=@([regex]::Matches($maskText.Groups[1].Value,'\d+') | ForEach-Object {[uint64]$_.Value})
 $firstMask=[uint64]1 -shl $first
 if(@($masks | Where-Object {($_ -band $firstMask) -ne 0}).Count -lt 1){throw 'First-person group contains no mesh'}
 $lodText=[regex]::Match($data,'m_refLODGroupMasks\s*=\s*\[(.*?)\]','Singleline')
 $lodMasks=@([regex]::Matches($lodText.Groups[1].Value,'\d+') | ForEach-Object {[uint64]$_.Value})
 if($masks.Count -ne $lodMasks.Count -or @($lodMasks | Where-Object {($_ -band 1) -ne 0}).Count -lt 1 -or @($lodMasks | Where-Object {($_ -band 2) -ne 0}).Count -lt 1){throw 'Compiled Aluona-style first/third-person LOD layout missing'}
 for($mi=0;$mi -lt $masks.Count;$mi++){
  if(($masks[$mi] -band $firstMask) -ne 0 -and ($lodMasks[$mi] -band 1) -eq 0){throw 'First-person mesh absent from first-person LOD'}
 }
 # Validate dependency closure of preserved materials too, including paths with spaces.
 $preserved=Get-Content -LiteralPath (Join-Path (Split-Path $Manifest -Parent) 'preserved-assets.json') -Raw -Encoding UTF8 | ConvertFrom-Json
 foreach($asset in $preserved.PSObject.Properties){
  if($asset.Name -notmatch '\.vmat_c$'){continue}
  $assetFile=Join-Path $GameAddon $asset.Name
  $assetLog=Join-Path $ReportDirectory ('material-'+[IO.Path]::GetFileNameWithoutExtension($asset.Name)+'-RERL.txt')
  $materialRerl=Invoke-Viewer $assetFile 'RERL' $assetLog
  foreach($match in [regex]::Matches($materialRerl,'(?m)^\s*[0-9A-Fa-f]{16}\s+(.+?\.(?:vmat|vtex))\s*$')){
   $dep=$match.Groups[1].Value+'_c'
   if(!$addonNames.Contains($dep) -and !$base.Contains($dep)){throw ('Material dependency unavailable: '+$dep)}
  }
 }
 [pscustomobject]@{Groups=$groups;FirstPersonGroupIndex=$first;MeshMasks=$masks;LODMasks=$lodMasks;MeshMaskValidated=$true;GameRenderingVerified=$false} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $ReportDirectory 'firstperson-compiled-validation.json') -Encoding UTF8
 $results += [pscustomobject]@{Id=$m.Id;Path=$m.Path;CompiledResourceParsed=$true;AG2ReferencesPresent=$true;CoreHierarchyValid=$true;SHA256=(Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant();Mounted=$false;GameAnimationVerified=$false;Note='Compiled/static only; client animation, hitboxes and damage remain unverified'}
}
$results | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $ReportDirectory 'compiled-validation.json') -Encoding UTF8
Write-Output 'Compiled resources parsed and structural checks passed. Mounting and gameplay have NOT been tested.'
