param([string]$Source)
$ErrorActionPreference='Stop';Set-StrictMode -Version Latest
$tokens=$null;$errors=$null
$ast=[Management.Automation.Language.Parser]::ParseFile($Source,[ref]$tokens,[ref]$errors)
if($errors.Count){throw 'parse failed'}
$fn=@($ast.FindAll({param($x)$x -is [Management.Automation.Language.FunctionDefinitionAst] -and $x.Name -ceq 'Can-HashStableCapture'},$true))
if($fn.Count -ne 1){throw 'unique gate required'}
. ([ScriptBlock]::Create($fn[0].Extent.Text))
$cases=@(
 @($true,$true,$true,$true,$true),
 @($false,$true,$true,$true,$false),
 @($true,$false,$true,$true,$false),
 @($true,$true,$false,$true,$false),
 @($true,$true,$true,$false,$false),
 @($false,$false,$false,$false,$false)
)
foreach($c in $cases){$v=Can-HashStableCapture $c[0] $c[1] $c[2] $c[3];if($v -ne $c[4]){throw 'unsafe stable manifest gate'}}
@{scope='PURE_QUIESCENCE_GATE_NO_FILES_HASHED_OR_TRACE_APIS';passed=$cases.Count;winps=$PSVersionTable.PSVersion.ToString();admission='BLOCKED'}|ConvertTo-Json
