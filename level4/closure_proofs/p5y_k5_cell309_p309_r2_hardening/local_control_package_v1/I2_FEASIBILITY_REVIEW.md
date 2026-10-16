# I2 本机采集能力：一次真实核验的具体包

状态：准备及审阅中，未获执行批准。此文件不是授权。正式准入 BLOCKED，I1–I7 全保留。

## 依赖关系和范围

V4 证明两项特定小型暂停 VM 探针的记录符合其限定判据；不能证明新执行平台的完整安全性。独立 AI 源码审阅也没有签发正式准入。Windows 的实际 ETW 字段、丢失情况、Hyper-V counter 可读性尚未知。存在性能类元数据不能替代这些事实。在此关键依赖没有实测前，生产 observer/签名和 CPU 归属规则不能诚实地宣布完成。此批次为接下来的完整控制层提供实际输入，不安装生产服务、账户、密钥或 guest，也不关闭 I2。

用户已授权普通开发、构建、单元测试、只读主机事实，但要求真实跟踪/验证前给出具体包再确认。V4 的批准只覆盖原两项暂停 VM，因此不能沿用到本批次。

## 具体操作及权限

- 一次提升的 Windows PowerShell 入口。需要 UAC/admin 来创建当前批次的受保护目录及控制 system logger。仅在 capture 自己的进程 token 内启用已存在的 `SeSystemProfilePrivilege`，退出前恢复；未被分配则拒绝，不修改 LSA/组成员/服务/全局 provider ACL 或任何策略。
- 原子创建两个新目录，存在即拒绝：`C:\ProgramData\ReBaseGuardP309-I2-Feasibility-v1`、`D:\ReBaseGuard-309\records\p309-i2-native-capture-v1`。owner 为 Administrators；受保护 DACL 仅 SYSTEM、Administrators 可写，当前 Windows owner 有只读/执行权限。不会修改现有父目录 ACL。
- 将精确摘要绑定的 `EtwCapture-i2-final.exe` 复制到新受保护目录并再次验哈希，记录批准文件和 ACL。二进制由已存在 .NET Framework C# 编译器构建，不下载或安装软件。
- 先证明固定会话名称不存在。启动一个独立 watchdog 进程，ready 记录用临时文件完整落盘后原子改名。确认它仍活着且创建时间匹配、年龄不超过 5 秒后，才允许一次 capture 调用。
- 新建唯一名称 `ReBaseGuard-P309-I2-Feasibility-v1` 的 system logger，会话 GUID 固定为 `b65ec272-436b-45e5-a4e3-87fddbc73a80`。启动冲突拒绝，不采用现存会话。只启用 PROCESS、THREAD、IMAGE_LOAD、CSWITCH、DPC、INTERRUPT；不启用网络/文件内容、堆栈或 sampled profile。
- 采集一个 60 秒窗口，原始 ETL 顺序文件上限 256 MiB；64 KiB buffer、64–256 buffers，实际值仍以 API 回读为准。读取 logical/root VP/VP 的三个运行时间原始 counter，每秒一组，保留原始时间戳和频率，证据预算 16 MiB；任何读取失败都不能用零补齐。
- 在窗口第 3、6、9 秒，各启动一个同一已验哈希二进制的固定子模式，忙循环约 200 毫秒后退出。共三个自有短命 CPU 夹具，预计总 CPU 约 0.6 秒；只有这三个，不能接收命令、路径或目标输入。父进程保留各自的 Process 原生句柄，记录创建/退出 FILETIME、CPU 时间和返回码；超时仅终止该自有句柄所指进程并判失败。这不是 P309、qualification、target 或正式 worker-tier 演练。
- 控制器正常结束先调用原生 StopTrace，后写停止记录。丢失、错误、超时先停止当前会话。独立进程在其启动后 75 秒检查并请求停止仍存在的精确 GUID 会话；触发兜底即为失败。Windows 调度/API 卡死不是硬实时保证：无法确认会话消失或仍有在途 helper 时，结果只能 UNKNOWN，不能宣传保证清理。
- harness 最后查询会话已不存在且所有自有 helper 已退出，保留 SHA-256 与原始证据到 D:。必要的同会话停止是安全清理，不是重跑采集。不会自动开始第二次 capture。

## 判据、分析及结论限制

执行完成只标记 `CAPTURE_COMPLETED_REQUIRES_OFFLINE_ANALYSIS`，并固定 `coverage_complete=false`。native start/query/stop 返回码、最终 loss counters、counter 类型/读数、夹具 PID+FILETIME、会话消失、helper 退出必须全部可解释，任何缺失保持失败/未知。

在已保存 ETL 上用系统原有 `tracerpt.exe` 离线解码；解析器只读取记录，不启动新跟踪。核验三项夹具的生命周期与调度字段、rundown、CPU 标识、时间域、原始 loss 及运行时间 counter。记录不支持的 schema/字段，不推测完整性。原始 ETL 可能包含本机进程命令行和模块路径，仅在本地受保护证据目录保留；普通推送只发布摘要、源绑定、经过筛选的结论。

这批次不证明 PPL 全覆盖、所有短命活动完整性、跨 partition 到具体 VM 的身份归属、QEMU/guest/host CPU 去重、实际签名服务最小权限或未来长时无丢失。它也不证明非管理员服务能采集，因为本次是提升身份的能力核验。上述限制必须留在 I2/I3，实际结果不能冒充生产 observer 的 green observation。

## 回滚和故障处理

先停止已创建的精确会话并确认无在途 capture，保留 watchdog/控制和所有原始记录直到清理得到证明；不按进程名或任意 PID 清理。若身份冲突、API 卡住或 helper 未退出，记录 UNKNOWN 并保留现场，不停止其他 logger、不扩大权限、不自动 retry。

本批次不改服务、账户、key、发行版、Windows power/update/provider 策略或原 Ubuntu，所以没有这些对象的回滚操作。进程 token 的临时 privilege 随原进程退出消失；新二进制和两个目录封存保留，不删除证据。不重跑 V4、D2 或既有 53/24/19/157 测试。

## 实现来源

Microsoft 原始 API 文档（2026-10-16 核对）：
- https://learn.microsoft.com/en-us/windows/win32/etw/configuring-and-starting-a-systemtraceprovider-session
- https://learn.microsoft.com/en-us/windows/win32/api/evntrace/ns-evntrace-event_trace_properties
- https://learn.microsoft.com/en-us/windows/win32/etw/logging-mode-constants

结构布局/纯配置检查只调用内存分配和结构封送，不调用 StartTrace、ControlTrace、PerformanceCounter、token privilege、fixture 或目录创建。PowerShell 入口仅作语法解析与嵌入 C# 编译，不执行。
