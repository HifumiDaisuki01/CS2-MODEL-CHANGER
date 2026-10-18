param([string]$Root=$PSScriptRoot)
$ErrorActionPreference='Stop'
$count=0
foreach($line in [IO.File]::ReadAllLines((Join-Path $Root 'SHA256SUMS.txt'))){
 if($line -notmatch '^([0-9a-fA-F]{64})  (.+)$'){throw 'Invalid checksum manifest'}
 $hash=$Matches[1];$rel=$Matches[2]
 $file=Join-Path $Root $rel
 if((Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash -ne $hash){throw ('SHA256 mismatch: '+$rel)}
 $count++
}
$addon=Join-Path $Root 'addon\game\csgo_addons\cs2cm_aluona_localtest'
$resources=Import-Csv (Join-Path $Root 'evidence\extracted-resources.csv')
foreach($r in $resources){if((Get-FileHash -LiteralPath (Join-Path $addon $r.Path) -Algorithm SHA256).Hash -ne $r.SHA256){throw ('Original resource mismatch: '+$r.Path)}}
foreach($r in Import-Csv (Join-Path $Root 'evidence\dependencies-normalized.csv')){
 if($r.Resolution -eq 'bundled' -and !(Test-Path -LiteralPath (Join-Path $addon $r.CompiledPath))){throw ('Missing bundled dependency: '+$r.CompiledPath)}
}
Write-Host ('PASS: '+$count+' file checksums; '+$resources.Count+' original compiled resources verified.')
Write-Host 'Stock CS2 skeletons, animation graphs and shared textures are required from Steam; see dependencies-normalized.csv.'
Write-Host 'This verifies files, not live rendering. Screenshots and test reports record the actual local tests.'
