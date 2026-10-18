param([Parameter(Mandatory=$true)][string]$GamePath)
$ErrorActionPreference='Stop'
if(Get-Process cs2 -ErrorAction SilentlyContinue){throw 'Close CS2 before compiling the test script'}
$source=Join-Path $GamePath 'content\csgo_addons\cs2cm_aluona_localtest\maps\scripts\aluona_test.js'
$compiler=Join-Path $GamePath 'game\bin\win64\resourcecompiler.exe'
$game=Join-Path $GamePath 'game\csgo'
if(!(Test-Path -LiteralPath $source)){throw 'Install-Local.ps1 must be run first'}
if(!(Test-Path -LiteralPath $compiler)){throw 'Official CS2 Workshop Tools resourcecompiler is required'}
$target=Join-Path $GamePath 'game\csgo_addons\cs2cm_aluona_localtest\maps\scripts\aluona_test.vjs_c'
if(Test-Path -LiteralPath $target){Copy-Item -LiteralPath $target -Destination ($target+'.before-rebuild-'+(Get-Date -Format yyyyMMdd-HHmmss))}
& $compiler -i $source -game $game
if($LASTEXITCODE -ne 0){throw 'resourcecompiler failed'}
if(!(Test-Path -LiteralPath $target)){throw 'Compiled VJS output missing'}
Get-FileHash -LiteralPath $target -Algorithm SHA256
