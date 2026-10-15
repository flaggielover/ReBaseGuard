# Test helper only. No named key, private export, file write, service or collector.
param([switch]$SyntheticOnly, [ValidateSet(2048,3072,4096)][int]$KeyBits=2048)
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
if(-not $SyntheticOnly){throw 'Explicit -SyntheticOnly is required'}
if($PSVersionTable.PSVersion -lt [version]'7.2' -or -not $IsWindows){throw 'Windows PowerShell 7.2+ required'}
[Console]::InputEncoding=[Text.UTF8Encoding]::new($false,$true)
[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false,$true)
function ReadBoundedLine {
 $buffer=[Text.StringBuilder]::new()
 while($true){
  $c=[Console]::In.Read()
  if($c -eq -1){
   if($buffer.Length -ne 0){throw 'Truncated request'}
   return $null
  }
  if($c -eq 10){return $buffer.ToString()}
  if($buffer.Length -ge 1400000){throw 'Request exceeds synthetic budget'}
  [void]$buffer.Append([char]$c)
 }
}
function Emit($value){[Console]::Out.WriteLine(($value | ConvertTo-Json -Depth 6 -Compress));[Console]::Out.Flush()}
$rsa=$null
try {
 $rsa=[Security.Cryptography.RSACng]::new($KeyBits)
 if(-not $rsa.Key.IsEphemeral){throw 'Refuse non-ephemeral key'}
 $public=[Text.Encoding]::ASCII.GetBytes($rsa.ExportSubjectPublicKeyInfoPem())
 Emit ([ordered]@{schema='P309_SYNTHETIC_WINDOWS_SIGNER/1';scope='SYNTHETIC_ONLY';
  public_key_b64=[Convert]::ToBase64String($public);key_bits=$rsa.KeySize;
  key_ephemeral=$rsa.Key.IsEphemeral;key_name=$rsa.Key.KeyName;
  algorithm='RSA-PKCS1-v1_5-SHA256';powershell=$PSVersionTable.PSVersion.ToString();
  runtime=[Environment]::Version.ToString();provider=$rsa.GetType().FullName})
 for($i=0;$i -lt 32;$i++){
  $line=ReadBoundedLine
  if($null -eq $line){break}
  $request=ConvertFrom-Json -InputObject $line -AsHashtable -ErrorAction Stop
  if($request -isnot [Collections.IDictionary] -or $request.Count -ne 2 -or
     -not $request.Contains('synthetic') -or $request.synthetic -isnot [bool] -or -not $request.synthetic -or
     -not $request.Contains('message_b64') -or $request.message_b64 -isnot [string]){throw 'Invalid synthetic request'}
  $message=[Convert]::FromBase64String($request.message_b64)
  if($message.Length -eq 0 -or $message.Length -gt 1048576){throw 'Message exceeds synthetic budget'}
  $signature=$rsa.SignData($message,[Security.Cryptography.HashAlgorithmName]::SHA256,
                         [Security.Cryptography.RSASignaturePadding]::Pkcs1)
  Emit ([ordered]@{message_b64=[Convert]::ToBase64String($message);signature_b64=[Convert]::ToBase64String($signature)})
 }
} finally {if($null -ne $rsa){$rsa.Dispose()}}
