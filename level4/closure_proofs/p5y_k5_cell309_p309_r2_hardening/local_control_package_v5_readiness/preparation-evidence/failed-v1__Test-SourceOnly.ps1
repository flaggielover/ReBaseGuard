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
if([Runtime.InteropServices.Marshal]::SizeOf($oa) -ne 48){throw 'LSA_OBJECT_ATTRIBUTES ABI differs'}
if([Runtime.InteropServices.Marshal]::SizeOf($us) -ne 16){throw 'LSA_UNICODE_STRING ABI differs'}
$imports=@([P309InstallationRead].GetMethods([Reflection.BindingFlags]'NonPublic,Static')|Where-Object {$_.GetCustomAttributes([Runtime.InteropServices.DllImportAttribute],$false).Count -ne 0}|ForEach-Object {$_.Name}|Sort-Object)
$expected=@('EventAccessQuery','LsaClose','LsaEnumerateAccountRights','LsaFreeMemory','LsaNtStatusToWinError','LsaOpenPolicy')
if(($imports -join ',') -cne ($expected -join ',')){throw 'native import allowlist differs'}
[ordered]@{scope='SOURCE_ONLY_COMPILE_ABI_IMPORTS';winps=$PSVersionTable.PSVersion.ToString();source_sha256=(Get-FileHash -LiteralPath $Source).Hash.ToLowerInvariant();parse_errors=0;oa_size=48;us_size=16;imports=$imports;native_query_calls=0;harness_executions=0;uac=0;admission='BLOCKED'}|ConvertTo-Json -Depth 5
