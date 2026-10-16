$ErrorActionPreference='Stop'
$source='D:\ReBaseGuard-309\workspace\p309-local-vm-diagnostic-dev-20261016\level4\closure_proofs\p5y_k5_cell309_p309_r2_hardening\local_control_package_v2\NativeEntry.c'
$out='D:\ReBaseGuard-309\records\p309-local-control-package-preparation-20261016-01\i2-native-entry-v3-b4'
if(Test-Path -LiteralPath $out) {throw 'output collision'}
New-Item -ItemType Directory -Path $out | Out-Null
$tool='C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64'
$sdk='C:\Program Files (x86)\Windows Kits\10'
$cl=Join-Path $tool 'cl.exe';$link=Join-Path $tool 'link.exe'
$argsCompile=@('/nologo','/c','/GS-','/O1','/Oi-','/Zl','/D_WIN32_WINNT=0x0602',('/I'+'C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.44.35207\include'),('/I'+$sdk+'\Include\10.0.26100.0\ucrt'),('/I'+$sdk+'\Include\10.0.26100.0\um'),('/I'+$sdk+'\Include\10.0.26100.0\shared'),('/Fo'+$out+'\NativeEntry.obj'),$source)
& $cl @argsCompile 2>&1 | Tee-Object -FilePath (Join-Path $out 'compile.txt')
if($LASTEXITCODE -ne 0){throw 'native compile failed'}
$argsLink=@('/NOLOGO','/NODEFAULTLIB','/ENTRY:Entry','/SUBSYSTEM:WINDOWS','/DYNAMICBASE','/NXCOMPAT','/MANIFEST:EMBED',"/MANIFESTUAC:level='requireAdministrator' uiAccess='false'",('/OUT:'+$out+'\NativeEntry.exe'),($out+'\NativeEntry.obj'),($sdk+'\Lib\10.0.26100.0\um\x64\kernel32.lib'))
& $link @argsLink 2>&1 | Tee-Object -FilePath (Join-Path $out 'link.txt')
if($LASTEXITCODE -ne 0){throw 'native link failed'}
& (Join-Path $tool 'dumpbin.exe') /imports /headers (Join-Path $out 'NativeEntry.exe') | Tee-Object -FilePath (Join-Path $out 'pe-inspection.txt')
if($LASTEXITCODE -ne 0){throw 'PE inspection failed'}
[ordered]@{source_sha256=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant();binary_sha256=(Get-FileHash -LiteralPath (Join-Path $out 'NativeEntry.exe') -Algorithm SHA256).Hash.ToLowerInvariant();compiler=$cl;compiler_sha256=(Get-FileHash -LiteralPath $cl -Algorithm SHA256).Hash.ToLowerInvariant();compiler_args=$argsCompile;linker=$link;linker_sha256=(Get-FileHash -LiteralPath $link -Algorithm SHA256).Hash.ToLowerInvariant();linker_args=$argsLink;build_exit=0;native_executions=0;uac_requests=0;admission='BLOCKED'} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $out 'BINDINGS.json') -Encoding UTF8
