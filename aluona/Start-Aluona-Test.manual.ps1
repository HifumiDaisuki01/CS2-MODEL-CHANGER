param([string]$GamePath='Z:\steam\steamapps\common\Counter-Strike Global Offensive')
$ErrorActionPreference='Stop'
$exe=Join-Path $GamePath 'game\bin\win64\cs2.exe'
$addon=Join-Path $GamePath 'game\csgo_addons\cs2cm_aluona_localtest'
foreach($relative in @('characters\models\aluona\aluona.vmdl_c','maps\scripts\aluona_test.vjs_c','cfg\aluona_precache.cfg','cfg\aluona_apply.cfg')){
 if(!(Test-Path -LiteralPath (Join-Path $addon $relative))){throw ('Missing isolated addon resource: '+$relative)}
}
if(Get-Process cs2 -ErrorAction SilentlyContinue){throw 'Close the existing CS2 session before starting this isolated test.'}
Write-Host 'Starting the existing local test addon. No Workshop upload/download is needed.'
Write-Host 'Wait until Dust2 has fully loaded and you can move as CT or T. Aim at nearby ground.'
Write-Host 'Console step 1: exec aluona_precache.cfg'
Write-Host 'Wait at least 6 seconds with the game running, then step 2: exec aluona_apply.cfg'
Write-Host 'First person: firstperson. Third person: thirdperson. Reapply after spawn if needed: cs2cm_apply'
Write-Host 'This launcher does not enable VConsole or a remote console listener.'
& $exe -tools -addon cs2cm_aluona_localtest -insecure -novid -windowed -w 1024 -h 768 -adapter 0 -dx11 -console -ip 127.0.0.1 -port 27125 +sv_lan 1 +map de_dust2
