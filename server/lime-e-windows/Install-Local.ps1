param([Parameter(Mandatory=$true)][string]$GamePath)
$ErrorActionPreference='Stop'
if(Get-Process cs2 -ErrorAction SilentlyContinue){throw 'Close CS2 before installing this isolated test addon.'}
if(!(Test-Path -LiteralPath (Join-Path $GamePath 'game\bin\win64\cs2.exe'))){throw 'CS2 executable missing'}
$bundle=Join-Path $PSScriptRoot 'addon'
$files=@(Get-ChildItem -LiteralPath $bundle -Recurse -File)
foreach($f in $files){
 $relative=$f.FullName.Substring($bundle.Length+1)
 if($relative -notmatch '^(game|content)\\csgo_addons\\lime_e_ag2_20261019_150756_709\\' -or $relative.Contains('..')){throw 'Unexpected package path'}
 $dest=Join-Path $GamePath $relative
 if((Test-Path -LiteralPath $dest) -and (Get-FileHash -LiteralPath $dest).Hash -ne (Get-FileHash -LiteralPath $f.FullName).Hash){throw ('Existing different file; refusing overwrite: '+$dest)}
}
foreach($f in $files){$dest=Join-Path $GamePath $f.FullName.Substring($bundle.Length+1);if(!(Test-Path -LiteralPath $dest)){[IO.Directory]::CreateDirectory((Split-Path $dest -Parent))|Out-Null;[IO.File]::Copy($f.FullName,$dest,$false)}}
Write-Output 'Isolated AG2 addon ready. No existing different files overwritten.'