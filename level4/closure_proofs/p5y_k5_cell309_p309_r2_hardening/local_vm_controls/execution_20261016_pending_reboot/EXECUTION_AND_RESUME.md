# P309 本机平台包执行记录：等待人工重启

本次仅执行用户批准的 P309_LOCAL_VM_FEASIBILITY_V1。整个 P309 任务尚未完成；正式准入 BLOCKED，I1–I7 全部保留。

## 实际执行结果

- 批准原文：“批准上述平台包，重启由我人工完成”。引用及精确范围见 APPROVAL.json。
- 批准源码提交：8a941ac0b37867795b38ce1fcbe8adbe7e4422f0；准备记录基线：acef678a1750a525fa39ad14645db80cef3355cc。12 个源码文件绑定全部一致。
- 再次验证 159 个 MSYS2 归档签名。固定 QEMU 11.1.2 / MSYS2 11.1.2-1 运行时已放置到 D:\ReBaseGuard-309\local-vm-feasibility\candidate-v1；独立重哈希 222 个文件、459,552,711 字节，无不匹配。未运行 QEMU。
- 经已批准的 UAC 执行 Enable-WindowsOptionalFeature -Online -FeatureName HypervisorPlatform -NoRestart -LimitAccess。返回成功且 RestartNeeded=true，未自动下载组件，未自动重启。原始前后状态及 PowerShell transcript 均保留。
- 启用前启动时刻：2026-10-09T06:18:21.6613670Z。尚未完成要求的人工重启，因此两项 VM 探针均未启动，不能报告探针通过或 WHPX 已可实际使用。
- 启用后的单次容量记录：可用 RAM 9,828,253,696 字节，D: 可用 127,437,672,448 字节，C: 可用 2,140,491,776 字节。此为点时事实，不能替代重启后的检查或正式安全采样。
- 未创建服务、账户、生产密钥、端点或 guest；未启动 ETW、正式演练或 P309 工作负载。未改电源/更新策略；原 Ubuntu、系统 Python、历史记录及备份未作为此次操作对象。

## 当前需要用户完成的操作

保存其他工作后，使用 Windows 的“重启”人工重启本机；完成后在本聊天回复“已重启，继续”。这是已批准流程中的人工操作，不需要再次批准同一平台包。

## 重启后续跑检查与固定动作

1. 恢复本检查点和原 APPROVAL.json；核验新启动时刻不同于上述 boot_before，WHP 已启用且不再处于等待重启状态。不要重跑安装或启用步骤。
2. 核验批准源码、guard、运行时清单及全部文件摘要，确认普通非提升身份、可用 RAM 至少 8,805,306,368 字节。若前置条件不满足，保留真实失败事实，不降低标准、不关闭无关应用。
3. 用 PowerShell 7 执行下方已批准脚本，EvidenceDirectory 必须是尚不存在的 D: records 子目录。脚本固定运行 deadline 与 guard-exit 两项暂停、无盘、无网络探针；任何失败立即停止，不自动重试。只观察/停止已绑定的自有进程，绝不按进程名清理。

```powershell
& 'D:\ReBaseGuard-309\records\p309-local-vm-execution-20261016-231849\approved-source\Run-ApprovedVmProbes.ps1' `
  -ApprovalRecord 'D:\ReBaseGuard-309\records\p309-local-vm-execution-20261016-231849\APPROVAL.json' `
  -EvidenceDirectory ('D:\ReBaseGuard-309\records\p309-local-vm-probes-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
```

4. 保存实际进程代次、句柄退出、Job 清理、guard 退出码及原始日志，追加发布。即使通过，也只证明限定平台探针；不证明 guest 启动、完整内存隔离、生产控制、I1/I6 关闭或正式准入。继续剩余工程和独立审阅，后续生产变更仍需完整方案与相应批准。

## 回滚及证据

精确回滚规则见 approved-source/ROLLBACK.md。当前不回滚、不删除：保留已放置文件；只有确认本包无 VM 存活、owner 确认没有新增 WHP 依赖且状态明确时，才可依原批准范围恢复本次启用的 HypervisorPlatform，并保留前后状态。不得禁用 WSL/VirtualMachinePlatform，任何所需重启仍由用户人工完成。

本次权威证据目录：D:\ReBaseGuard-309\records\p309-local-vm-execution-20261016-231849。
原始证据使用 SHA256SUMS.json 绑定；清单不自包含。Git 镜像设置 -text 保留原始字节，既有记录不覆盖。发布提交及远端核验在另附的 publication 文件中记录，避免自引用提交哈希。
