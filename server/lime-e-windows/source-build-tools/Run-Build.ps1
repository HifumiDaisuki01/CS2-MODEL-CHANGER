param([string]$CS2Path)
$ErrorActionPreference='Stop'
try {
 if(!$CS2Path){
  $steam=(Get-ItemProperty -LiteralPath 'HKCU:\Software\Valve\Steam' -ErrorAction SilentlyContinue).SteamPath
  $libraries=@()
  if($steam){$libraries+= $steam;$vdf=Join-Path $steam 'steamapps\libraryfolders.vdf';if(Test-Path -LiteralPath $vdf){$libraries+=@([regex]::Matches([IO.File]::ReadAllText($vdf),'"path"\s+"([^"]+)"') | ForEach-Object {$_.Groups[1].Value.Replace('\\','\')})}}
  foreach($lib in $libraries){$candidate=Join-Path $lib 'steamapps\common\Counter-Strike Global Offensive';if(Test-Path -LiteralPath (Join-Path $candidate 'game\bin\win64\resourcecompiler.exe')){$CS2Path=$candidate;break}}
 }
 if(!$CS2Path){$CS2Path=(Read-Host 'Enter CS2 folder containing game and content (no quotes)').Trim('"')}
 & (Join-Path $PSScriptRoot 'Build-AG2.ps1') -CS2Path $CS2Path -PackageRoot (Split-Path $PSScriptRoot -Parent)
 if(!$?){throw 'Build did not complete'}
}catch{Write-Host ('FAILED: '+$_.Exception.Message) -ForegroundColor Red;exit 1}
