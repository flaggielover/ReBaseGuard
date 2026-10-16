# V4：分离控制台后的固定两项平台验证包

当前任务未完成；I1–I7 仍开放，正式准入 BLOCKED。这不是正式演练、guest 安装、P309 grant 或运行授权。

## V3 真实结果与证据边界

本机已在批准范围实际运行一次 V3。两次限制读回均为 active limit=1、768 MiB 进程/Job commit、kill-on-close 且无 breakaway。五秒快照识别了两个活成员：固定 QEMU 与 `C:\Windows\System32\conhost.exe`，各有 Job 归属、PID+creation FILETIME、未退出状态和 image path。不能按系统进程名称豁免，原单成员要求未满足。

异常后在 5031 ms 请求停止，5078 ms 观察到 Job active=0；外部持有的精确 QEMU 句柄确认退出。V3 未运行 guard-exit。完整原始日志保留于 diagnostic_v3_result_20261016，旧失败不改为 PASS。

V3 运行后复核：222 个运行时文件摘要仍一致、无额外文件；五个缓存位于 child-scratch/program-data。缓存原文留在本机，只发布其摘要。旧 candidate-v1、旧缓存及所有历史记录不动。

已验证的 QEMU 源归档中，对 32,290 个小于 4 MB 的 C/C++/头文件搜索 AllocConsole/AttachConsole 未命中；已安装 QEMU PE 子系统为 console。此静态搜索不能排除依赖 DLL 调用，也不等于动态调用归因。微软区分隐藏控制台窗口的 CREATE_NO_WINDOW 与不附加控制台的 DETACHED_PROCESS；目前证据支持用后者作为待验证修正，不能在真实运行前宣布 conhost 问题已关闭。

## 已完成的源码改动

- QEMU 创建标志改为 `0x0008040c`：DETACHED_PROCESS、CREATE_SUSPENDED、CREATE_UNICODE_ENVIRONMENT、EXTENDED_STARTUPINFO_PRESENT；不含 CREATE_NO_WINDOW、CREATE_NEW_CONSOLE 或 BREAKAWAY。仍原子绑定同一私有 Job，句柄不继承。不改变 Windows 全局控制台策略。
- 保持固定参数：q35/WHPX、4 vCPU、128 MiB、`-S` 暂停、无盘/网络/显示/串口/monitor；无 TCG 回退。继续使用已安装的 candidate-v3，全部 222 文件/清单完整预检，运行时不重新安装。
- 保持 active limit=1，绝不豁免 conhost 或接受额外成员；有效限制、原始 PID buffer、解码成员、Job 归属和代次须一致。
- 独立看门狗目标在 14.5 秒请求停止，给原 15 秒上限预留调度余量；不是放宽上限。deadline 判定要求实际请求和记录的清理观察均在 15 秒内。Windows 调度不是硬实时保证；超时则本次失败，绝不自行降低标准。
- 恢复固定 guard-exit 检查：五秒单成员状态下 `ExitProcess(86)`，由操作系统关闭 Job 最后句柄。外部脚本以持有的精确 QEMU 句柄观察退出。没有一般 PID/命令或终止任意进程的入口。
- 两项共用一次不可覆盖的证据根目录；每项开始前重核启动代次、内存和完整运行时。第一项严格通过后才允许第二项；任何失败立即结束整批，无自动重试。

## 已完成的验证

31 项 C# 纯环境/ABI/创建标志检查、14 项 PowerShell 纯证据判定回归、4 项批准入口拒绝检查通过；另有语法检查、原始源码/二进制摘要。新判定器明确拒绝实际 V3 双成员记录以及合成的过时限、外来镜像、PID 复用、原始 buffer 不一致、限制放宽、缺失/重复记录、查询失败和错误退出状态。

这些是限定单元检查，不是新的真实 VM 结果，也不证明停止/I1–I7 闭合。此前的 27/7/4、20/4 及更早 D2/Cloud 记录按其原有含义保留；未通过重复旧套件制造整体进展。

## 本次集中请求的动作

以 BINDINGS.json 的精确 guard/harness/preflight/verdict 摘要，在普通非提升用户下执行以下固定顺序，**最多两次**：

1. `deadline`：固定暂停 VM，五秒确认只有绑定 QEMU、有效限制无变；在 14.5 秒目标请求独立停止，按实际日志确认 15 秒内清理、Job 空、外部句柄退出。所有阶段与原始成员数据必须一致。
2. 只有第 1 项通过才执行 `guard-exit`：相同参数的新自有代次，五秒确认唯一成员及有效限制，guard 退出码 86；外部确认绑定 QEMU 退出。此证据不等于整个 hypervisor 内核/partition 回收证明。

使用固定新证据根 `D:\ReBaseGuard-309\records\p309-local-vm-detached-v4-run-20261016-01`。不新增软件副本、不下载、不提权、不创建账户/服务/生产密钥/发行版/端点，不改 Windows 政策，不启动 ETW、安全采样、guest OS、正式演练或 P309。此批准不扩展到以后任意修订或任意次数运行。

## 验收、回滚与后续

每项结果只写 scoped_probe_pass 与实际时间；formal_admission 永远 BLOCKED。原源码绑定、unique member、原始缓冲区、内存上限等任何一项不成立，拒绝第二项或后续。原始失败记录永久保留。

停止只作用于新建私有 Job；不按名字、猜测 PID、全局 WSL shutdown 清理。异常/未知时保存文件与控制状态，不宣布清理成功，不再运行实例。无系统配置变更需要回滚；源码、二进制和 scratch 文件封存，candidate-v1/v3、历史备份均保留。WHP 的原条件回滚不会自动触发。

通过后仍需继续完整控制层实现、具体生产变更包、真实 guest/身份/采集/来源/broker/持久化与恢复验证、独立审阅及原正式授权链；不把这两项平台探针作为任务完成。这份文件是协调者自审，不是独立准入审阅。

新的确认依据：用户总任务第 3 条，以及上次 V3 仅许可一次固定诊断的范围。此次改变启动源码并重新安排两项固定真实验证；源码/构建/判定器/回滚已准备完成后才请求确认。

厂商来源：

- [Microsoft：Process Creation Flags](https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags)
- [Microsoft：Creation of a Console](https://learn.microsoft.com/en-us/windows/console/creation-of-a-console)
- [Microsoft Terminal 控制台接入说明](https://github.com/microsoft/terminal/blob/main/doc/specs/%23492%20-%20Default%20Terminal/spec.md)

这些来源支持 API 语义，不能代替本机 V4 实测。
