param([Parameter(Mandatory=$true)][string]$CS2Path,[string]$PackageRoot=(Split-Path $PSScriptRoot -Parent),[string]$S2V=(Join-Path $PSScriptRoot 'source2viewer\Source2Viewer-CLI.exe'))
$ErrorActionPreference='Stop'
$CS2Path=[IO.Path]::GetFullPath($CS2Path).TrimEnd('\')
$PackageRoot=[IO.Path]::GetFullPath($PackageRoot)
$compiler=Join-Path $CS2Path 'game\bin\win64\resourcecompiler.exe'
if(!(Test-Path -LiteralPath $compiler)){throw 'CS2 Workshop Tools resourcecompiler.exe not found. No game or tools will be downloaded.'}
if(!(Test-Path -LiteralPath $S2V)){throw 'Source2Viewer-CLI.exe missing; supply -S2V or extract the complete supplied portable tools directory.'}
$manifest=Join-Path $PackageRoot 'reports\selected-models.json'
$models=Get-Content -LiteralPath $manifest -Raw -Encoding UTF8 | ConvertFrom-Json
if($models.Count -ne 3){throw 'Expected exactly three reviewed models'}
$stage='ks_ag2_repair_'+(Get-Date).ToUniversalTime().ToString('yyyyMMdd_HHmmss_fff')
$content=Join-Path $CS2Path ('content\csgo_addons\'+$stage)
$game=Join-Path $CS2Path ('game\csgo_addons\'+$stage)
foreach($path in @($content,$game)){
 $resolved=[IO.Path]::GetFullPath($path)
 if(!$resolved.StartsWith($CS2Path+'\',[StringComparison]::OrdinalIgnoreCase) -or (Test-Path -LiteralPath $resolved)){throw 'Unsafe or existing build destination'}
}
$logs=Join-Path $PackageRoot ('reports\windows-'+$stage)
New-Item -ItemType Directory -Path $logs,$content,$game -Force | Out-Null
# A fresh addon is the rollback boundary: existing addons, gameinfo and player data are never overwritten.
$sourceContent=Join-Path $PackageRoot 'workshop-addon\content\csgo_addons\ks_ag2_repair'
$sourceGame=Join-Path $PackageRoot 'workshop-addon\game\csgo_addons\ks_ag2_repair'
Get-ChildItem -LiteralPath $sourceContent -Force | Copy-Item -Destination $content -Recurse
Get-ChildItem -LiteralPath $sourceGame -Force | Copy-Item -Destination $game -Recurse
[pscustomobject]@{ContentAddon=$content;GameAddon=$game;CreatedUTC=(Get-Date).ToUniversalTime().ToString('o');ExistingPathsOverwritten=$false;GameinfoModified=$false;ServerModified=$false} | ConvertTo-Json | Set-Content (Join-Path $logs 'build-location.json') -Encoding UTF8
Push-Location (Split-Path $compiler -Parent)
try{
 foreach($m in $models){
  if($m.Path -notmatch '^characters/[a-zA-Z0-9_./-]+\.vmdl$' -or $m.Path.Contains('..')){throw 'Unsafe manifest path'}
  $source=Join-Path $content $m.Path;$output=Join-Path $game ($m.Path+'_c')
  if(!(Test-Path -LiteralPath $source) -or (Test-Path -LiteralPath $output)){throw 'Missing source or stale compiled model in fresh stage'}
  $stdout=Join-Path $logs ($m.Id+'-compiler.log');$stderr=Join-Path $logs ($m.Id+'-compiler.stderr')
  $p=Start-Process -FilePath $compiler -ArgumentList @('-i',('"'+$source+'"')) -WindowStyle Hidden -Wait -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
  if($p.ExitCode -ne 0 -or !(Test-Path -LiteralPath $output)){throw "Compilation failed for $($m.Id); retain stage and logs for diagnosis"}
 }
}finally{Pop-Location}
$preserved=Get-Content -LiteralPath (Join-Path $PackageRoot 'reports\preserved-assets.json') -Raw -Encoding UTF8 | ConvertFrom-Json
foreach($property in $preserved.PSObject.Properties){
 if($property.Name.Contains('..') -or $property.Name.Contains('\') -or $property.Name.Contains(':') -or $property.Name.StartsWith('/')){throw 'Unsafe preserved resource path'}
 $file=Join-Path $game $property.Name
 if(!(Test-Path -LiteralPath $file) -or (Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant() -cne $property.Value){throw "Original material or texture changed during compile: $($property.Name)"}
}
& (Join-Path $PSScriptRoot 'Verify-Compiled.ps1') -GameAddon $game -Manifest $manifest -S2V $S2V -ReportDirectory $logs -CS2Path $CS2Path
Write-Output ('Build directory: '+$game)
Write-Output 'No Workshop item was created or uploaded. No server was changed. Follow TESTING_CHECKLIST.md before deployment.'
