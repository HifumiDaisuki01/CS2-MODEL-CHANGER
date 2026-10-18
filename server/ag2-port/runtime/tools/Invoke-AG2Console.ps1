param([Parameter(Mandatory=$true)][string]$Command,[string]$Label='console',[int]$Seconds=4)
$ErrorActionPreference='Stop'
$root=Join-Path (Split-Path $PSScriptRoot -Parent) 'reports\game-test-20261018'
[IO.Directory]::CreateDirectory($root) | Out-Null
$client=New-Object Net.Sockets.TcpClient
$client.Connect('127.0.0.1',29000)
$stream=$client.GetStream();$stream.ReadTimeout=500
$received=New-Object IO.MemoryStream
function Read-Console([int]$duration){$deadline=[DateTime]::UtcNow.AddSeconds($duration);$buffer=New-Object byte[] 65536;while([DateTime]::UtcNow -lt $deadline){if($stream.DataAvailable){$n=$stream.Read($buffer,0,$buffer.Length);if($n -le 0){break};$received.Write($buffer,0,$n)}else{Start-Sleep -Milliseconds 40}}}
try{
 [byte[]]$hello=0x56,0x46,0x43,0x53,0,0xd4,0,0,0,13,0,0,0
 $stream.Write($hello,0,$hello.Length)
 Read-Console 2
 $received.SetLength(0)
 $body=[Text.Encoding]::UTF8.GetBytes($Command+[char]0)
 $length=12+$body.Length;if($length -gt 65535){throw 'Command too long'}
 [byte[]]$packet=0x43,0x4d,0x4e,0x44,0,0xd4,0,0,([byte]($length -shr 8)),([byte]($length -band 255)),0,0
 $packet+=$body;$stream.Write($packet,0,$packet.Length)
 Read-Console $Seconds
 $bytes=$received.ToArray();[IO.File]::WriteAllBytes((Join-Path $root ($Label+'.vconsole.bin')),$bytes)
 $lines=New-Object 'System.Collections.Generic.List[string]'
 for($i=0;$i+12 -le $bytes.Length;){$size=([int]$bytes[$i+8]*256)+$bytes[$i+9];if($size -lt 12 -or $i+$size -gt $bytes.Length){break};$type=[Text.Encoding]::ASCII.GetString($bytes,$i,4);if($type -eq 'PRNT' -and $size -gt 40){$line=[Text.Encoding]::UTF8.GetString($bytes,$i+40,$size-40).TrimEnd([char]0);$lines.Add($line)};$i+=$size}
 $text=$lines -join "`r`n";[IO.File]::WriteAllText((Join-Path $root ($Label+'.log')),$text,(New-Object Text.UTF8Encoding($true)));[IO.File]::AppendAllText((Join-Path $root 'commands.log'),([DateTime]::UtcNow.ToString('o')+' '+$Command+"`r`n"));Write-Output $text
}finally{$stream.Dispose();$client.Dispose();$received.Dispose()}