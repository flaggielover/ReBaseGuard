# 单次 I2 root scheduler 诊断包：批准前材料

状态：已构建，待独立源码复审及新的单次人工批准。**没有执行本包的 UAC、trace、fixture 或 VM。I1–I7 OPEN，admission BLOCKED。**

## 为什么需要这一批

已批准的上一批确实启动一次，但 256 MiB ETL 用尽，约 50 秒内丢失 12,027 个事件；48 条 Hyper-V 计数器 rows 全空。该失败原样保留，禁止自动重试。扩大日志预算只能处理容量问题，不能解决 CPU 归属。

本包在一个新窗口内，同时检验日志容量和一个由自身持有 partition handle 的 WHP 实例。它能提供 VP 计数器与 Windows 原生线程调度的实际对照；不能外推为 QEMU、其他 VM、PPL、虚拟账户权限或 I2 全部通过。两条事实若仍不能关联，就保留缺口，不调低原标准。

## 精确绑定及构建

代码输入提交 `5eb6cbb6532d852dcf6c7f0e2686023ced64ef0a`，最终执行字节及普通调用器摘要见 FINAL_BINDINGS.json。准备、调用器及本材料由本文件所在提交一并固定；批准问题将给出该不可变提交。

唯一执行来源是 `C:\Users\Lenovo\P309-I2-root-build-20261016-v1` 内的新私有构建，不从 D: 存档运行可执行文件。现有 v4 build、candidate-v1/v3、原 Ubuntu、私有 3.11.15、系统 Python、备份及旧采集均保持不变。

普通用户使用已安装 .NET Framework C# compiler、MSVC 14.44.35207、SDK 10.0.26100.0 构建。源文件和中间对象在后续构建期间持有禁止写入的句柄；目录在创建时仅允许 owner/SYSTEM/admin 写入。完整参数、工具摘要、ACL、两项纯 ABI 检查、17 项 fixture 判定测试、调用器测试和 WinPS 5.1 解析记录见 preparation-evidence。没有以这些测试替代本机采集证明。

## 请求的单次范围

1. 普通调用器先确认 C: 至少 2 GiB（1 GiB log + 1 GiB reserve），D: 至少 12 GiB（存档/离线展开预算），新证据/attempt 路径不存在，固定 launcher/native 字节及父目录 pin 正确。失败则不 UAC、不继续。
2. **一次 UAC**，native pre-CLR 入口加载固定摘要 template，以 clean process environment 启动 Windows PowerShell 5.1。只在自身 token 中临时启用 SeSystemProfilePrivilege；不改变账户、服务或系统权限策略。
3. 新建 `C:\ProgramData\ReBaseGuardP309-I2-RootDiagnostic-v3`，创建时 DACL 限制 admin/SYSTEM 写、当前 owner 只读。放置两个已固定摘要的本批 exe 和批准记录；不安装服务。
4. 创建 **一个** 新 GUID 绑定的 system-logger ETW 会话，采集 process/thread/image、CSwitch、DPC/interrupt。无 stack、sampled profile、文件/网络内容采集。sequential 上限 **1 GiB**，原 60 秒窗口、75 秒停止请求线程不变；不是实时保证，逾期/丢失均失败。
5. 同一窗口内运行三个固定、各 200 ms 循环的原生 fixture，以及 **一个 WHP fixture**。四个子进程都原子进入各自私有、单成员、kill-on-close、256 MiB process/Job 的 Job，句柄不继承。固定三原生 fixture 最多各等 3 秒；WHP fixture 最多等 8 秒，超时只终止该自有 Job，再等 3 秒并记失败/UNKNOWN。
6. WHP fixture 也继承本批提升 token：这是本次诊断权限上界，绝不是生产最小权限验收。仅 1 vCPU、2 MiB GPA 映射、固定 `EB FE` 循环，约 1 秒后由本进程另一线程请求取消；不加载 guest OS、磁盘、网络或设备，不运行 QEMU、Ubuntu 或 P309。Job 内存限制不被宣称能限制所有 hypervisor 内核开销。记录自身 VP counters、PID/创建时间、执行线程 ID、QPC/时间锚点和 process CPU。
7. 任何失败结束整批，没有第二个 partition、第二次 trace 或自动重试。终态保留所有输出及准确 native exit code；普通 owner 之后复制并逐文件验摘要，离线解析原始 ETL。原始系统 payload 只留本地，仓库只发布必要摘要和自身 fixture 信息。

## 验证标准与尚未接受的语义

- 技术采集记录必须有成功创建和同 GUID 成功停止凭据、完整至少 60 秒窗口、查询与 ETL header 零 lost、decoder 零未知 CSwitch 格式、helper 全退出。仅最终会话名不存在不算成功停止。
- 三个原生 fixture 各有精确创建/退出身份、唯一 Job 成员、退出 0 和 active=0；WHP 另有相同外层证明、成功 WHP 调用/取消/清理、有效返回长度及非倒退的计数器。错误/超时/读不到输出不能填零或转为 PASS。
- 离线检查每个 fixture 的 process/thread lifetime，关联其 CSwitch；WHP 输出还须与该自有 PID、创建时间和运行 TID 相符，报告 VP delta、宿主 interval 和 process CPU 的原始比较。没有预设“误差可忽略”的比例，更不通过调整比例闭合正式 CPU 去重。
- Hyper-V 空实例明确记为 UNAVAILABLE。为调查 root scheduler，此诊断可继续记录 ETW；**此行为不允许正式 observer 在缺少计量时继续运行**。coverage_complete 始终 false，正式 admission 始终 BLOCKED。
- 任一技术条件失败保留 FAILED/UNKNOWN；即使全部技术条件成立，也仅得到可继续实现/审阅的事实。PPL、所有短进程、其他 partition/VM 归属、采集最小权限、QEMU 的实际 VP 对应及去重仍须证明。I1–I7 没有自动关闭入口。

## 回滚及后续

由 creator 使用成功 StartTrace handle 和 GUID 核对后停止本会话；不按名字停止，不采纳同名新会话。WHP 只取消/删除自己创建的 VP/partition；外层仅使用已持有的自有 Job/Process handle。无法证明清理则 UNKNOWN 并保留现场，不猜 PID、不杀无关进程、不执行 WSL shutdown、不更改 WHP 安装状态。

不修改电源、更新、BCD/scheduler、全局策略、账户、服务、密钥、发行版。没有这些配置需要回滚；本批文件与日志封存，不删除历史或备份。随后继续完整 I1–I7 实现与真实验收包、独立正式路线审阅和授权链；禁止 freeze/grant/qualification/target。

此处再次确认的依据是用户接管请求第 3 条：新的真实跟踪/隔离试验需先准备完整包再批准；上一批准明确只允许一次不含 VM 的采集，且失败不自动重试。本包增加固定 WHP 实例并改变源码/日志预算，旧批准不覆盖。

## 厂商依据

- [root scheduler](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/manage/manage-hyper-v-scheduler-types)：客户端 root 由 NT 调度；不建议切到不支持的 scheduler。
- [VP counter API](https://learn.microsoft.com/en-us/virtualization/api/hypervisor-platform/funcs/whvgetvirtualprocessorcounters)：需要自身持有 partition handle。网页示例函数声明省略 CounterSet，但参数说明及本机 SDK WinHvPlatform.h 均包含它；代码按已固定摘要的 SDK 头构建。
- [Run VP](https://learn.microsoft.com/en-us/virtualization/api/hypervisor-platform/funcs/whvrunvirtualprocessor) 与 [Cancel VP](https://learn.microsoft.com/en-us/virtualization/api/hypervisor-platform/funcs/whvcancelrunvirtualprocessor)：取消由另一线程发起；不假定取消先于 Run 时能被保留，退出不明依靠外层自有 Job 限时并记 UNKNOWN。

厂商接口文档、编译和 ABI 检查不能代替本机实际行为。
