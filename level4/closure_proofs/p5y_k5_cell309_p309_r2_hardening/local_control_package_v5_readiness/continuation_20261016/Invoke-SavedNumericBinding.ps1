$ErrorActionPreference='Stop';Set-StrictMode -Version Latest
if($PSVersionTable.PSVersion.ToString() -notlike '5.1.*'){throw 'WinPS5.1 required'}
$root=Join-Path $PSScriptRoot 'p309-offline-derivation-binding-v1'
if([IO.Directory]::Exists($root)-or[IO.File]::Exists($root)){throw 'fresh offline output required'}
[void][IO.Directory]::CreateDirectory($root)
function Save([string]$name,$value){$s=$value|ConvertTo-Json -Depth 12;$f=[IO.FileStream]::new((Join-Path $root $name),[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read);try{$b=[Text.Encoding]::UTF8.GetBytes($s);$f.Write($b,0,$b.Length);$f.Flush($true)}finally{$f.Dispose()}}
$base='D:\ReBaseGuard-309\workspace\p309-local-vm-diagnostic-dev-20261016\level4\closure_proofs\p5y_k5_cell309_p309_r2_hardening'
$launcher=[IO.File]::ReadAllText((Join-Path $base 'local_control_package_v5_readiness\Launch-Approved.ps1'))
$tokens=$null;$errors=$null;$ast=[Management.Automation.Language.Parser]::ParseInput($launcher,[ref]$tokens,[ref]$errors)
if($errors.Count){throw 'source parse'}
$literal=@($ast.FindAll({param($n)$n -is [Management.Automation.Language.StringConstantExpressionAst] -and $n.Value.Contains('public sealed class P309PinnedEntry')},$true))
if($literal.Count -ne 1){throw 'unique file-only pin helper required'}
# File-only helper correction. No launcher, native entry, token, ETW-control or VM call.
$native=$literal[0].Value.Replace('CreateFileW(p,0,1,','CreateFileW(p,0x80000000,1,')
if($native -ceq $literal[0].Value){throw 'expected ancestor access patch not found'}
$env:TEMP=$root;$env:TMP=$root
Add-Type -TypeDefinition $native
$etl='D:\ReBaseGuard-309\records\p309-i2-root-v3-attempt-20261016-01\capture\capture.etl'
$csv='D:\ReBaseGuard-309\records\p309-i2-root-v3-attempt-20261016-01\offline\qpc-prefix.csv'
$exe='C:\Users\Lenovo\P309-I2-offline-qpc-20261016-v1\OfflineQpc.exe'
$source=Join-Path $base 'local_control_package_v4_offline\OfflineQpc.cpp'
$held=[Collections.Generic.List[object]]::new()
function Pin([string]$p){$pin=[P309PinnedEntry]::new($p);$held.Add($pin);$pin}
function Digest($pin){$pin.File.Position=0;$h=[Security.Cryptography.SHA256]::Create();try{[BitConverter]::ToString($h.ComputeHash($pin.File)).Replace('-','').ToLowerInvariant()}finally{$h.Dispose();$pin.File.Position=0}}
try{
 $ep=Pin $etl;$xp=Pin $exe;$sp=Pin $source;$cp=Pin $csv
 $eh=Digest $ep;$xh=Digest $xp;$sh=Digest $sp;$old=Digest $cp
 if($eh-cne'3faee3bd46a7fd33b046edce00da058f630296a0b73d1893c3281c250e1d6870'-or$xh-cne'81e55e9c1e8c1181d94f0320aea16b07a144a91aadb189eae1d417d588da7eaf'-or$sh-cne'f26addc5f51a2a9f9ac2f1b1de4590438a44c00488765ac231b1f1ed41a4ffb6'){throw 'fixed ETL/decoder/source differs'}
 Save 'BEFORE.json' @{utc=[DateTime]::UtcNow.ToString('o');etl_sha256=$eh;decoder_sha256=$xh;source_sha256=$sh;saved_numeric_sha256=$old;scope='FRESH_SAVED_FILE_DERIVATION_NOT_RETROACTIVE_EXECUTION_BINDING';ancestor_access='GENERIC_READ';share='READ_ONLY';admission='BLOCKED'}
 $out=Join-Path $root 'qpc-prefix.rederived.csv'
 $si=[Diagnostics.ProcessStartInfo]::new();$si.FileName=$exe;$si.Arguments='"'+$etl+'" "'+$out+'"';$si.WorkingDirectory=$root;$si.UseShellExecute=$false;$si.CreateNoWindow=$true;$si.RedirectStandardOutput=$true;$si.RedirectStandardError=$true
 $si.EnvironmentVariables.Clear();$si.EnvironmentVariables['SystemRoot']='C:\Windows';$si.EnvironmentVariables['WINDIR']='C:\Windows';$si.EnvironmentVariables['PATH']='C:\Windows\System32';$si.EnvironmentVariables['TEMP']=$root;$si.EnvironmentVariables['TMP']=$root
 $p=[Diagnostics.Process]::Start($si);$stdout=$p.StandardOutput.ReadToEndAsync();$stderr=$p.StandardError.ReadToEndAsync()
 if(-not $p.WaitForExit(60000)){Save 'TIMEOUT.json' @{pid=$p.Id;status='UNKNOWN';automatic_retry=$false;admission='BLOCKED'};throw 'owned offline decoder wait timeout; no retry'}
 [IO.File]::WriteAllText((Join-Path $root 'decoder.stdout.json'),$stdout.Result,[Text.UTF8Encoding]::new($false));[IO.File]::WriteAllText((Join-Path $root 'decoder.stderr.txt'),$stderr.Result,[Text.UTF8Encoding]::new($false))
 if($p.ExitCode-ne 0){throw 'offline decoder failed'}
 $np=Pin $out;$fresh=Digest $np;$meta=$stdout.Result|ConvertFrom-Json
 if($fresh-cne$old){throw 'saved CSV not byte-identical to fresh derivation'}
 if((Digest $ep)-cne$eh-or(Digest $xp)-cne$xh-or(Digest $sp)-cne$sh-or(Digest $cp)-cne$old){throw 'pinned input changed'}
 Save 'RESULT.json' @{utc=[DateTime]::UtcNow.ToString('o');scope='FRESH_FIXED_ETL_TO_SAVED_NUMERIC_COMPARISON';exit_code=$p.ExitCode;etl_sha256=$eh;decoder_sha256=$xh;source_sha256=$sh;numeric_sha256=$fresh;saved_numeric_byte_identical=$true;decoder_summary=$meta;read_locks_and_ancestor_pins_held=$true;retroactive_original_execution_binding_proven=$false;lifetime_semantics_changed=$false;uac=0;trace_starts=0;vm_starts=0;admission='BLOCKED'}
 Get-Content -LiteralPath (Join-Path $root 'RESULT.json')
}catch{Save 'FAILURE.json' @{utc=[DateTime]::UtcNow.ToString('o');error=$_.Exception.Message;scope='OFFLINE_FILE_ONLY';automatic_retry=$false;admission='BLOCKED'};throw}
finally{for($i=$held.Count-1;$i-ge 0;$i--){$held[$i].Dispose()}}
