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
 $refs=@([regex]::Matches($rerl,'[a-zA-Z0-9_./-]+\.(?:vnmgraph|vnmskel|vmat|vtex|vmdl|vpcf|vsnd|vanim)\b') | ForEach-Object {$_.Value} | Sort-Object -Unique)
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
 $results += [pscustomobject]@{Id=$m.Id;Path=$m.Path;CompiledResourceParsed=$true;AG2ReferencesPresent=$true;CoreHierarchyValid=$true;SHA256=(Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant();Mounted=$false;GameAnimationVerified=$false;Note='Compiled/static only; client animation, hitboxes and damage remain unverified'}
}
$results | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $ReportDirectory 'compiled-validation.json') -Encoding UTF8
Write-Output 'Compiled resources parsed and structural checks passed. Mounting and gameplay have NOT been tested.'
