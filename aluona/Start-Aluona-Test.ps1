param([string]$GamePath='Z:\steam\steamapps\common\Counter-Strike Global Offensive')
$ErrorActionPreference='Stop'
$exe=Join-Path $GamePath 'game\bin\win64\cs2.exe'
$addon=Join-Path $GamePath 'game\csgo_addons\cs2cm_aluona_localtest'
if(Get-Process cs2 -ErrorAction SilentlyContinue){throw 'Close CS2 first, then run this launcher again. Existing games are never stopped automatically.'}
foreach($relative in @('characters\models\aluona\aluona.vmdl_c','maps\scripts\aluona_test.vjs_c','cfg\aluona_precache.cfg','cfg\aluona_apply.cfg')){
 if(!(Test-Path -LiteralPath (Join-Path $addon $relative))){throw ('Missing addon file; run Install-Local.ps1 first: '+$relative)}
}
Add-Type -Path (Join-Path $PSScriptRoot 'tools\LocalVConsole.cs')
$logs=Join-Path $PSScriptRoot 'logs'
[IO.Directory]::CreateDirectory($logs)|Out-Null
$stamp=Get-Date -Format 'yyyyMMdd-HHmmss'
$log=Join-Path $logs ($stamp+'-auto-console.log')
$port=29000
$probe=[Net.Sockets.TcpListener]::new([Net.IPAddress]::Any,$port)
try{$probe.Start()}finally{$probe.Stop()}
$arguments='-tools -addon cs2cm_aluona_localtest -insecure -novid -windowed -w 1024 -h 768 -adapter 0 -dx11 -vconsole -netconport '+$port+' -ip 127.0.0.1 -port 27125 -dev -console +sv_lan 1'
Write-Host 'Starting CS2. Model switching will run automatically after the map is ready.'
Write-Host 'Keep this window open until AUTO_APPLY_CONFIRMED. No manual console commands required.'
$proc=Start-Process -FilePath $exe -ArgumentList $arguments -WorkingDirectory (Split-Path $exe) -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $logs ($stamp+'-stdout.txt')) -RedirectStandardError (Join-Path $logs ($stamp+'-stderr.txt'))
[pscustomobject]@{PID=$proc.Id;Port=$port;Log=$log;Started=(Get-Date).ToString('o')}|ConvertTo-Json|Set-Content (Join-Path $logs 'latest-session.json') -Encoding UTF8
$connection=$null
function Send([string]$command){$connection.Send($command);Start-Sleep -Milliseconds 350}
function Read-Log {
 $fs=[IO.File]::Open($log,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::ReadWrite)
 $reader=[IO.StreamReader]::new($fs)
 try{$reader.ReadToEnd()}finally{$reader.Dispose()}
}
try{
 for($i=0;$i -lt 45;$i++){
  $proc.Refresh();if($proc.HasExited){throw 'CS2 exited during startup. See logs folder.'}
  try{$connection=[LocalVConsole]::new($port,$log);break}catch{Start-Sleep -Seconds 2}
 }
 if(!$connection){throw 'Local console connection unavailable. See logs; no model switch was attempted.'}
 Send 'echo CS2CM_AUTO_START'
 Send 'sv_lan 1'
 Send 'sv_cheats 1'
 Send 'sv_hibernate_when_empty 0'
 Send 'map de_dust2'
 $ready=$false
 for($i=0;$i -lt 60;$i++){
  $proc.Refresh();if($proc.HasExited){throw 'CS2 exited while loading map.'}
  $marker='CS2CM_AUTO_READY_'+$i
  Send ('echo '+$marker);Send 'status';Start-Sleep -Seconds 2
  $text=Read-Log;$last=$text.LastIndexOf($marker)
  if($last -ge 0 -and $text.Substring($last) -match '(?s)Client:\s+Connected.*\bactive\b'){$ready=$true;break}
 }
 if(!$ready){throw 'Map/client never became active. Model application was not attempted.'}
 Write-Host 'Map ready. Creating model precache entity and waiting 6 seconds...'
 Send 'sv_cheats 1'
 Send 'mp_ignore_round_win_conditions 1'
 Send 'exec aluona_precache.cfg'
 Start-Sleep -Seconds 6
 Send 'echo CS2CM_AUTO_PRECACHE_SETTLED'
 Send 'exec aluona_apply.cfg'
 Start-Sleep -Seconds 6
 Send 'cs2cm_apply'
 Send 'thirdperson'
 Send 'cam_idealdist 100'
 Start-Sleep -Seconds 2
 $text=Read-Log
 if($text -match 'Serialized nonresident asset'){throw 'Model residency assertion detected; see console log.'}
 if($text -notmatch '\[CS2CM\] player model before=.*after=characters/models/aluona/aluona.vmdl'){throw 'Model application was not confirmed by script. See log; do not treat this run as successful.'}
 Send 'echo CS2CM_AUTO_APPLY_CONFIRMED'
 Write-Host 'AUTO_APPLY_CONFIRMED: player model API confirmed. Check actual appearance in the game.' -ForegroundColor Green
 Write-Host 'thirdperson = character view; firstperson = hands. Console: cs2cm_apply to reapply.'
 Write-Host ('Log: '+$log)
}finally{if($connection){$connection.Dispose()}}
