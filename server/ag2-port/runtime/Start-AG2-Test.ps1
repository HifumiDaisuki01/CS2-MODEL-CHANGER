param([string]$GamePath,[ValidateSet('myers','km_decade','dujiaoshou')][string]$Model='myers')
$ErrorActionPreference='Stop'
if(!$GamePath){
 $steam=(Get-ItemProperty -LiteralPath 'HKCU:\Software\Valve\Steam' -ErrorAction SilentlyContinue).SteamPath
 if(!$steam){$steam=Join-Path ${env:ProgramFiles(x86)} 'Steam'}
 $libraries=@($steam);$vdf=Join-Path $steam 'steamapps\libraryfolders.vdf'
 if(Test-Path -LiteralPath $vdf){$libraries+=@([regex]::Matches([IO.File]::ReadAllText($vdf),'"path"\s+"([^"]+)"')|ForEach-Object {$_.Groups[1].Value.Replace('\\','\')})}
 foreach($lib in $libraries){$candidate=Join-Path $lib 'steamapps\common\Counter-Strike Global Offensive';if(Test-Path -LiteralPath (Join-Path $candidate 'game\bin\win64\cs2.exe')){$GamePath=$candidate;break}}
}
if(!$GamePath){throw 'CS2 not found. Run with -GamePath pointing to the installed CS2 directory.'}
& (Join-Path $PSScriptRoot 'Install-Local.ps1') -GamePath $GamePath
$exe=Join-Path $GamePath 'game\bin\win64\cs2.exe'
$logs=Join-Path $PSScriptRoot 'reports\game-test-20261018';[IO.Directory]::CreateDirectory($logs)|Out-Null
$stamp=Get-Date -Format 'yyyyMMdd-HHmmss';$console=Join-Path $PSScriptRoot 'tools\Invoke-AG2Console.ps1'
$args=@('-tools','-addon','ks_ag2_repair_20261018_145133_943','-insecure','-novid','-windowed','-w','1024','-h','768','-adapter','0','-dx11','-dev','-ip','127.0.0.1','-port','27125','+sv_lan','1','+sv_cheats','1','+map','de_dust2')
$proc=Start-Process -FilePath $exe -ArgumentList $args -WorkingDirectory (Split-Path $exe -Parent) -PassThru -RedirectStandardOutput (Join-Path $logs ($stamp+'-stdout.log')) -RedirectStandardError (Join-Path $logs ($stamp+'-stderr.log'))
$ready=$false;$deadline=[DateTime]::UtcNow.AddMinutes(12)
Write-Host 'Waiting for the local client to become Connected and player 0 active. Keep this launcher open.'
while([DateTime]::UtcNow -lt $deadline){
 $proc.Refresh();if($proc.HasExited){throw 'CS2 exited during loading; inspect logs and the minidump AbortMessage.'}
 try{$text=(& $console -Command 'status' -Label ($stamp+'-ready') -Seconds 2)|Out-String;if($text -match 'Client:\s+Connected' -and $text -match '(?m)^\s*0\s+.*\bactive\b'){$ready=$true;break}}catch{Write-Host 'Still loading...'}
 Start-Sleep -Seconds 2
}
if(!$ready){throw 'Client readiness not confirmed. No model was applied.'}
& $console -Command 'sv_cheats 1;bot_kick;bot_quota 0;mp_ignore_round_win_conditions 1;mp_limitteams 0;mp_autoteambalance 0;mp_freezetime 0;jointeam 3;mp_warmup_end;mp_restartgame 1' -Label ($stamp+'-setup') -Seconds 4
Write-Host 'Creating retained precache props and waiting at least 8 seconds...'
$pre=(& $console -Command 'exec ag2_precache.cfg' -Label ($stamp+'-precache') -Seconds 8)|Out-String
if($pre -notmatch 'AG2_PRECACHE_PROPS_CREATED_KEEP_ALIVE' -or $pre -match 'Serialized nonresident asset'){throw 'Precache stage not confirmed; do not apply.'}
& $console -Command 'exec ag2_apply.cfg' -Label ($stamp+'-script') -Seconds 4
$text=(& $console -Command ('ag2_apply_'+$Model+';ag2_verify;thirdperson;cam_idealdist 110') -Label ($stamp+'-apply') -Seconds 3)|Out-String
Write-Output $text
$expected=@{myers='characters/models/exg/myers/myers.vmdl';km_decade='characters/models/exg/aquaz/km_decade/km_decade.vmdl';dujiaoshou='characters/models/exg/dujiaoshou/dujiaoshou.vmdl'}[$Model]
if(!$text.Contains('after='+$expected) -or $text -match 'Serialized nonresident asset'){throw 'Official API model readback was not confirmed.'}
Write-Host 'AUTO_APPLY_CONFIRMED: API readback only. Inspect the actual model, materials, animations and weapon poses.' -ForegroundColor Green
Write-Host 'Commands: ag2_apply_myers / ag2_apply_km_decade / ag2_apply_dujiaoshou / ag2_verify'
Write-Host 'Precache entities remain alive. No Workshop upload or Steam launch-setting edit was performed.'