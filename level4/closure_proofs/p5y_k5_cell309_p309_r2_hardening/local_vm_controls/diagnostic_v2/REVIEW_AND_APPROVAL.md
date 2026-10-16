# 单次本机 VM 诊断 V2：待批准，准入 BLOCKED

用户此前批准的平台包 V1 已实际执行到第一项 deadline 探针。本机重启已核验，WHP 已启用，QEMU 子进程存活至五秒；Job 的 ActiveProcesses=2 不符合原期望 1，因此整批失败，guard-exit 未运行。自有子进程的绑定句柄已确认退出，Job 清理记录为 active=0；这不证明全部 hypervisor 内核资源释放。原始失败永远保留，不改写成 PASS。

## 原因尚未确定

旧日志没有成员列表和有效限制读回，无法判断第二个计数代表何种对象。微软文档说明，限制触发的关联失败可能临时增加活动计数，直到被终止进程退出且引用释放后才递减。这是可能机制，不是本机原因的证明；也不猜测它是 vmmem 或豁免任何名字。

源码另外存在创建暂停进程后再加入 Job 的崩溃窗口。V2 改用 Windows 10 起支持的 PROC_THREAD_ATTRIBUTE_JOB_LIST，在创建时原子关联 Job；不存在回退到旧路径的代码。实际原生调用效果尚未验证。

## 本次具体执行包

仅请求 **一次 deadline 诊断运行**，不是重开 V1 批次，也不包含第二项 guard-exit：

- 保留现有已验签 QEMU 11.1.2、222 个文件和固定清单。不安装新软件，不修改 WHP 或其他 Windows 配置，无 UAC。
- 使用新构建的 `OwnedVmDiagnostic-v2c.exe` 和 `Run-ApprovedDiagnostic.ps1`。完整 SHA-256 在 `BINDINGS.json`；新批准记录必须绑定精确 guard、harness 和运行时清单。
- 普通用户运行，仍是 q35/WHPX、4 vCPU、128 MiB、暂停、无盘、无网络、无串口/显示/monitor；无 guest 操作系统和 P309 工作负载。禁 TCG 回退。
- 仍设置 active limit=1、process/job commit 各 768 MiB、无 breakaway、KILL_ON_JOB_CLOSE。读回实际配置，不一致即拒绝。
- Job 创建后、QEMU 暂停创建后、五秒和停止后记录 bounded Job-local 快照：accounting、最多 16 个成员的 PID、FILETIME、Job 归属、等待状态、可读时的 image path，以及 query 错误和原始 PID buffer。访问成员只有 query-limited/synchronize 权限；不能读取或终止任意指定进程。无法确认的成员明确 UNKNOWN。
- 创建后先启动独立线程看门狗，再采集暂停进程状态并恢复到 QEMU `-S` 暂停态。五秒计数异常时记录受限快照后立即请求 Stop；15 秒看门狗在观察和文件操作期间继续独立工作。普通 Windows 调度线程不是硬实时保证，记录实际 stop tick，不伪称严格时限达成。
- 外部脚本持有 QEMU 的 PID+creation FILETIME 绑定句柄。停止只通过新建私有 Job；绝不按名字或猜测 PID 清理。guard 终止时依赖 Job 最后句柄关闭保护。无其他进程清理。
- 每份批准固定唯一证据目录，已存在则拒绝；不自动重试、不启动第二项探针、不进入后续安装或正式阶段。

## 结果判据与保留项

本次用于解释 V1 异常，**不会自动输出平台准入 PASS**。记录是否仍满足原“唯一成员”期望、是否存在未知身份、有效限制、实际停止时间及 Job/精确进程句柄退出。旧运行仍 FAIL。即使新计数恰为 1，也不能独自说明旧的第二个计数来源。

完整性至少需要四个预期阶段快照、两次有效限制读回、外部绑定与退出观察；记录不全、身份未知或清理未知必须保留。不把重试后的偶然通过当作修复证据。若异常稳定存在，再据实际对象/生命周期调查契约兼容性；不把上限放宽为 2。

当前 20 项新纯函数/ABI 检查与 4 项 PowerShell 入口拒绝检查均通过；未创建 native Job/VM，不能替代原生验证。没有重复历史 Cloud 或 D2 套件。此文为协调者自审，不是独立安全审阅或正式 8b 判定。

I1–I7 及 AF-2、本机路线接受、真实 guest、独立身份/公钥、采集覆盖、完整运行时来源、broker、持久化和恢复等仍全部未关闭。未新增账户、服务、密钥、发行版、端点、ETW 或生产 unit。

## 所需权限与回滚

当前普通用户本机执行、D: records 写入已足够；不需要管理员或修改策略。仅在取得新批准后，将 `APPROVAL_BLUEPRINT_NOT_AUTHORIZATION.json` 中授权布尔值改为 true、填写本聊天真实批准引用；保留其余精确绑定和唯一证据路径，在新文件中保存。

停止/失败时不启动下一项，保存原始日志与退出证据；若清理 UNKNOWN，不写 STOPPED、不重新启动、不清理无关进程。没有新增系统配置需要撤销；诊断源码、二进制和日志封存。V1 已启用 WHP 的条件回滚仍只按原 `../ROLLBACK.md` 执行，不自动禁用，也不自动重启。

重新确认的原因来自用户总任务第 3 条以及 V1 的精确源码/两项固定探针批准边界：V1 已失败并停止，新的原生诊断执行不在旧源码绑定内。源码开发、构建和纯检查已经完成，无需用户为这些工作重复批准。

## 厂商来源

- [微软：创建时关联 Job，避免创建后关联的崩溃窗口](https://devblogs.microsoft.com/oldnewthing/20230209-00/?p=107812)
- [微软：UpdateProcThreadAttribute / JOB_LIST](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute)
- [微软：基本计数及临时增加语义](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_accounting_information)
- [微软：Job PID 列表](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_process_id_list)
- [微软：查询 Job 信息](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-queryinformationjobobject)

SDK 宏与常数来源保存于准备 records 的 microsoft-WinBase.h 和 sdk-provenance.json；正式审阅仍须检查所有实际 API 返回与生命周期。
