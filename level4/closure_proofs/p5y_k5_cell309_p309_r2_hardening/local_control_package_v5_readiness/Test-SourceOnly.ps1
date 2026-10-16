param([Parameter(Mandatory=$true)][string]$Source)
$ErrorActionPreference='Stop';Set-StrictMode -Version Latest
if($PSVersionTable.PSVersion.ToString() -notlike '5.1.*'){throw 'Windows PowerShell 5.1 required'}
$tokens=$null;$errors=$null
$ast=[Management.Automation.Language.Parser]::ParseFile($Source,[ref]$tokens,[ref]$errors)
if($errors.Count){throw 'source parse failed'}
$assignment=@($ast.FindAll({param($n)$n -is [Management.Automation.Language.AssignmentStatementAst] -and $n.Left.Extent.Text -ceq '$native'},$true))
if($assignment.Count -ne 1){throw 'unique embedded native source required'}
$literal=@($assignment[0].Right.FindAll({param($n)$n -is [Management.Automation.Language.StringConstantExpressionAst]},$true))
if($literal.Count -ne 1){throw 'native source literal required'}
# Compile the literal only. Never invoke the harness or any native query method.
Add-Type -TypeDefinition $literal[0].Value
$oa=[P309InstallationRead].GetNestedType('OA',[Reflection.BindingFlags]::NonPublic)
$us=[P309InstallationRead].GetNestedType('US',[Reflection.BindingFlags]::NonPublic)
if(([Runtime.InteropServices.Marshal].GetMethod('SizeOf',[type[]]@([type]))).Invoke($null,@($oa)) -ne 48){throw 'LSA_OBJECT_ATTRIBUTES ABI differs'}
if(([Runtime.InteropServices.Marshal].GetMethod('SizeOf',[type[]]@([type]))).Invoke($null,@($us)) -ne 16){throw 'LSA_UNICODE_STRING ABI differs'}
$imports=@([P309InstallationRead].GetMethods([Reflection.BindingFlags]'NonPublic,Static')|Where-Object {$_.GetCustomAttributes([Runtime.InteropServices.DllImportAttribute],$false).Count -ne 0}|ForEach-Object {$_.Name}|Sort-Object)
$expected=@('EventAccessQuery','LsaClose','LsaEnumerateAccountRights','LsaFreeMemory','LsaNtStatusToWinError','LsaOpenPolicy')
if(($imports -join ',') -cne ($expected -join ',')){throw 'native import allowlist differs'}
$pureChecks=0
foreach($pair in @(@('ReBaseGuardP309Observer','rebaseguardp309observer'),@('ReBaseGuardP309Controller','REBASEGUARDP309CONTROLLER'),@('ReBaseGuardP309Relay','ReBaseGuardP309Relay'))){if(-not [P309InstallationRead]::SameServiceName($pair[0],$pair[1])){throw 'case-insensitive service identity mismatch'};$pureChecks++}
foreach($pair in @(@('ReBaseGuardP309Relay','ReBaseGuardP309RelayExtra'),@('ReBaseGuardP309Observer','ReBaseGuardP309Controller'),@('ReBaseGuardP309Relay',' ReBaseGuardP309Relay'))){if([P309InstallationRead]::SameServiceName($pair[0],$pair[1])){throw 'nonidentical service name adopted'};$pureChecks++}
foreach($hr in @(-2147024894,-2147024893)){if([P309InstallationRead]::PathErrorState($hr) -cne 'ABSENT'){throw 'explicit not-found not classified'};$pureChecks++}
foreach($hr in @(-2147024891,-2147024864,-2147024887,0,-1)){if([P309InstallationRead]::PathErrorState($hr) -cne 'UNKNOWN'){throw 'unavailable path falsely absent'};$pureChecks++}
[ordered]@{scope='SOURCE_ONLY_COMPILE_ABI_IMPORTS';winps=$PSVersionTable.PSVersion.ToString();source_sha256=(Get-FileHash -LiteralPath $Source).Hash.ToLowerInvariant();parse_errors=0;oa_size=48;us_size=16;imports=$imports;new_pure_classification_checks=$pureChecks;native_query_calls=0;harness_executions=0;uac=0;admission='BLOCKED'}|ConvertTo-Json -Depth 5
