param([string]$AddonPath)
$ErrorActionPreference = 'Stop'
if (-not $AddonPath) { $AddonPath = Read-Host 'Enter game/csgo_addons/keran_five_models directory' }
$AddonPath = $AddonPath.Trim().Trim('"')
$root = (Resolve-Path -LiteralPath $AddonPath).Path.TrimEnd('\','/')
if (-not (Test-Path -LiteralPath $root -PathType Container)) { throw 'Not an addon directory' }
$manifest = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'configs/expected-project-resources.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$count = 0
foreach ($p in $manifest.PSObject.Properties) {
 $file = [IO.Path]::GetFullPath((Join-Path $root $p.Name))
 if (-not $file.StartsWith($root + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe manifest path' }
 if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw ('Missing: ' + $p.Name) }
 if ((Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant() -ne $p.Value) { throw ('Hash mismatch: ' + $p.Name + '; copy package compiled resources again, do not rebuild old sources') }
 $count++
}
$allowed = @($manifest.PSObject.Properties.Name | Where-Object { $_ -like '*.vmdl_c' })
foreach ($model in Get-ChildItem -LiteralPath $root -Filter *.vmdl_c -Recurse -File) {
 $relative = $model.FullName.Substring($root.Length + 1).Replace('\','/')
 if ($relative -notin $allowed) { throw ('Unexpected old/player model: ' + $relative + '; replace the addon with the clean package directory') }
}
Write-Host ('PASS: ' + $count + ' compiled resources match. Workshop/game tests remain separate.')
