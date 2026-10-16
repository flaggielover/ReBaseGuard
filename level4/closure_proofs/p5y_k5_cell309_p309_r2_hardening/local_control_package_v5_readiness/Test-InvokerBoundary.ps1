param([Parameter(Mandatory=$true)][string]$Invoker,[Parameter(Mandatory=$true)][string]$PreviousInvoker)
$ErrorActionPreference='Stop';Set-StrictMode -Version Latest
. $Invoker -LibraryOnly
$pass=0
foreach($fn in @('Assert-FactsEvidenceSpace','Assert-ArchiveSpace')){
 & $fn 536870912;$pass++
 foreach($value in @(536870911,-1)){$refused=$false;try{& $fn $value}catch{$refused=$true};if(-not $refused){throw 'insufficient space accepted'};$pass++}
}
function FunctionText([string]$Path,[string]$Name){
 $tokens=$null;$errors=$null;$ast=[Management.Automation.Language.Parser]::ParseFile($Path,[ref]$tokens,[ref]$errors)
 if($errors.Count){throw 'parse'}
 $nodes=@($ast.FindAll({param($n)$n -is [Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -ceq $Name},$true))
 if($nodes.Count -ne 1){throw 'unique function required'}
 $nodes[0].Body.Extent.Text
}
if((FunctionText $Invoker 'Invoke-FactsRecordedOperation') -cne (FunctionText $PreviousInvoker 'Invoke-RootRecordedOperation')){throw 'cannot reuse changed operation recorder checks'}
@{scope='PURE_BOUNDARY_AND_EXACT_FUNCTION_REUSE';new_boundary_checks=$pass;operation_body_identical=$true;unchanged_operation_checks_not_repeated=4;native_query_calls=0;uac=0;admission='BLOCKED';winps=$PSVersionTable.PSVersion.ToString()}|ConvertTo-Json
