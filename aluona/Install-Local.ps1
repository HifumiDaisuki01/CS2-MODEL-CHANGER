param([string]$GamePath='Z:\steam\steamapps\common\Counter-Strike Global Offensive')
$ErrorActionPreference='Stop'
if(!(Test-Path -LiteralPath (Join-Path $GamePath 'game\bin\win64\cs2.exe'))){throw 'CS2 executable not found at GamePath'}
if(Get-Process cs2 -ErrorAction SilentlyContinue){throw 'Close CS2 before installing the local test addon'}
$bundle=Join-Path $PSScriptRoot 'addon'
$files=@(Get-ChildItem -LiteralPath $bundle -Recurse -File)
foreach($f in $files){$rel=$f.FullName.Substring($bundle.Length+1);if($rel -notmatch '^(game|content)\\csgo_addons\\cs2cm_aluona_localtest\\'){throw 'Unexpected package path'};$dest=Join-Path $GamePath $rel;if(Test-Path -LiteralPath $dest){if((Get-FileHash -LiteralPath $dest).Hash -ne (Get-FileHash -LiteralPath $f.FullName).Hash){throw ('Existing different file; refusing overwrite: '+$dest)}}}
foreach($f in $files){$dest=Join-Path $GamePath $f.FullName.Substring($bundle.Length+1);if(!(Test-Path -LiteralPath $dest)){[IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($dest))|Out-Null;[IO.File]::Copy($f.FullName,$dest,$false)}}
Write-Host 'Isolated Aluona addon ready. Follow README.md: fully load map, precache, wait, apply.'
