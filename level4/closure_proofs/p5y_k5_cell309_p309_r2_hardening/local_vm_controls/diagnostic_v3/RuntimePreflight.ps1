# Dot-source only. This module does not create directories, query the host, or launch processes.
function Assert-NoReparse([string]$Path){
 $p=[IO.Path]::GetFullPath($Path)
 while($p){
  $item=Get-Item -LiteralPath $p -Force -ErrorAction Stop
  if($item.Attributes -band [IO.FileAttributes]::ReparsePoint){throw "Reparse point: $p"}
  $p=[IO.Path]::GetDirectoryName($p)
 }
}
function Get-BoundRuntime {
 param([Parameter(Mandatory)][string]$Root,[Parameter(Mandatory)][string]$HashList,
       [Parameter(Mandatory)][string]$ExpectedListHash,[switch]$AllowSourceExtras)
 $ErrorActionPreference='Stop'
 Assert-NoReparse $Root;Assert-NoReparse $HashList
 if((Get-FileHash -LiteralPath $HashList).Hash.ToLowerInvariant() -cne $ExpectedListHash){throw 'Hash-list digest mismatch'}
 $full=[IO.Path]::GetFullPath($Root).TrimEnd('\');$prefix=$full+'\'
 $names=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
 $selected=[Collections.Generic.List[object]]::new()
 foreach($line in Get-Content -LiteralPath $HashList){
  if($line -cnotmatch '^([0-9a-f]{64})  (.+)$'){throw 'Invalid hash row'}
  $hash=$Matches[1];$relative=$Matches[2]
  if([IO.Path]::IsPathRooted($relative) -or $relative.Contains(':')){throw 'Invalid relative path'}
  $path=[IO.Path]::GetFullPath((Join-Path $full $relative))
  if(-not $path.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase) -or -not $names.Add($path)){throw 'Path escape or duplicate'}
  Assert-NoReparse $path
  if((Get-FileHash -LiteralPath $path).Hash.ToLowerInvariant() -cne $hash){throw "Runtime digest mismatch: $relative"}
  $selected.Add([pscustomobject]@{relative=$relative;sha256=$hash;bytes=(Get-Item -LiteralPath $path).Length})
 }
 # Enumerate explicitly so a reparse directory is rejected before descending into it.
 $stack=[Collections.Generic.Stack[string]]::new();$stack.Push($full)
 $extras=[Collections.Generic.List[string]]::new()
 while($stack.Count){
  foreach($entry in Get-ChildItem -LiteralPath $stack.Pop() -Force){
   if($entry.Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Runtime reparse entry'}
   if($entry.PSIsContainer){$stack.Push($entry.FullName)}elseif(-not $names.Contains($entry.FullName)){$extras.Add([IO.Path]::GetRelativePath($full,$entry.FullName))}
  }
 }
 if($extras.Count -and -not $AllowSourceExtras){throw 'Unlisted runtime file(s); no launch reservation consumed'}
 [pscustomobject]@{root=$full;file_count=$selected.Count;total_bytes=($selected|Measure-Object -Property bytes -Sum).Sum;selected_files=@($selected);extra_files=@($extras)}
}
