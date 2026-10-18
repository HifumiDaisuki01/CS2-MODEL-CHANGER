param([string]$Source,[string]$Output,[string]$SemanticReview)
$ErrorActionPreference='Stop'
if (!$Source -or !$Output) { throw 'Specify -Source and new -Output directory' }
Add-Type -Path (Join-Path $PSScriptRoot 'BatchModels.cs')
[BatchModels]::Run($Source,$Output,(Join-Path $PSScriptRoot 'base-resources-confirmed.txt'))
[BatchModels]::Assets | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $Output 'assets.json') -Encoding UTF8
[BatchModels]::Models | ConvertTo-Json -Depth 7 | Set-Content (Join-Path $Output 'models.json') -Encoding UTF8
[BatchModels]::Conflicts | ConvertTo-Json | Set-Content (Join-Path $Output 'conflicts.json') -Encoding UTF8
if($SemanticReview){Copy-Item -LiteralPath $SemanticReview -Destination (Join-Path $Output 'semantic-review.json')}
& (Join-Path $PSScriptRoot 'Write-BatchReport.ps1') -Output $Output
