param([string]$Source=$PSScriptRoot,[string]$Output=(Join-Path (Split-Path $PSScriptRoot) 'release-output'),[string]$Version='v0.1.0-alpha')
$ErrorActionPreference='Stop'
$Source=[IO.Path]::GetFullPath($Source).TrimEnd('\')
$Output=[IO.Path]::GetFullPath($Output).TrimEnd('\')
if($Output.StartsWith($Source+'\',[StringComparison]::OrdinalIgnoreCase) -or $Output -eq $Source){throw 'Output must be outside package directory'}
[IO.Directory]::CreateDirectory($Output)|Out-Null
$files=@(Get-ChildItem -LiteralPath $Source -Recurse -File | Where-Object {$_.FullName -notlike "$Source\logs\*" -and $_.FullName -ne "$Source\SHA256SUMS.txt"})
$files|ForEach-Object {(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()+'  '+$_.FullName.Substring($Source.Length+1).Replace('\','/')}|Set-Content (Join-Path $Source 'SHA256SUMS.txt') -Encoding ASCII
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip=Join-Path $Output ('CS2_Aluona_Package_A-'+$Version+'.zip')
if(Test-Path -LiteralPath $zip){throw 'Output archive exists; refusing overwrite'}
$archive=[IO.Compression.ZipFile]::Open($zip,[IO.Compression.ZipArchiveMode]::Create)
try{foreach($f in @($files)+(Get-Item (Join-Path $Source 'SHA256SUMS.txt'))){$entry='CS2_Aluona_Package_A/'+$f.FullName.Substring($Source.Length+1).Replace('\','/');[IO.Compression.ZipFileExtensions]::CreateEntryFromFile($archive,$f.FullName,$entry,[IO.Compression.CompressionLevel]::Optimal)|Out-Null}}finally{$archive.Dispose()}
((Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToLowerInvariant()+'  '+[IO.Path]::GetFileName($zip))|Set-Content ($zip+'.sha256') -Encoding ASCII
Get-Item -LiteralPath $zip | Select-Object FullName,Length
