# 单次 I2 续行：真实失败及离线分析

本次授权已消费一次，结果 **FAILED / I2 OPEN / admission BLOCKED**。不是 60 秒采集通过，不是全部任务完成，也没有自动续期或重试。I1–I7、正式运行阈值和 exactly-once 规则均保留。

## 来源与实际执行

- 提升入口及采集源码：`02c8fd500e643bfffd553ac0aa78c54670e2099f`。
- 普通调用器：`b76d69b7fa0f99a7d9ab51fa0777c5f59ff9e7af`。
- 人工批准：`request_user_input_async/call_b6e7db4ba10b499bb4f804f10ab8cebb/item0`，原文“已释放空间，批准单次续行及离线分析”。批准字节摘要见 evidence；先前批准和失败记录未覆盖。
- 外层调用 UTC 2026-10-16 02:11:35.1664276 至 02:12:36.8857235；native PID 46672、退出码 1。创建且只创建一个会话 `de145de9-9282-491d-be8a-7ea94b1839ea`。
- 调用前 C: 可用 7,794,196,480 字节，超过原 1 GiB 前置门槛；此次失败不是先前的空间拒绝。
- 原始受保护记录在 `C:\ProgramData\ReBaseGuardP309-I2-Feasibility-v2`；逐文件核验复制到 `D:\ReBaseGuard-309\records\p309-i2-renewed-attempt-v3\capture`。原始 RESULT.json 保持 `FAILED_OR_UNKNOWN`。

## 实际发现

ETL 恰为 268,435,456 字节，SHA-256 `35993a2dab730812043e167d4f4c9bb4cdc1d6fb9d1ce5d316e13d6e6027e113`。系统 tracerpt 离线读取 4,005,205 个事件，报告 **12,027 个丢失事件、4096 buffers、50 秒**。首末事件间隔为 49.7801394 秒，不能代替要求的完整 60 秒窗口。

这是 sequential system logger，256 MiB 是该开发包的上限。[Microsoft 的日志模式说明](https://learn.microsoft.com/en-us/windows/win32/etw/logging-mode-constants)规定 sequential 模式到达上限即停止。精确达到上限和最终会话消失支持容量终止解释；并未逐一证明所有丢失事件的原因。不得改用循环覆盖掩盖丢失。

48 条已写入采样记录的 ETW loss 字段均为零，但 **每条 Hyper-V counter rows 都为空**。下一条失败前代码先抛错、未保留触发查询的统计值；因此不能宣称最终零丢失。实际 sampler 报 `loss or sampler deadline`，guard 的所有权查询报 4201（会话不存在），没有 creator successful-stop receipt。

最终只读查询证实会话名不存在，全部 helper 已退出。三个固定自有子进程分别 PID 13680、46552、39844，均有保留的创建时间、exit=0、Job active=0/total=1。原 harness 的 fixture 布尔值受缺失 guard-clean.json 门控，故记录为 false；这不撤销三个独立 Job 事实，也不能反过来把 creator-stop 失败改成成功。

只读既有 Hyper-V 事件记录 scheduler=0x4；三个相关 counter category 均返回零实例。[Microsoft scheduler 文档](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/manage/manage-hyper-v-scheduler-types)把 0x4 解释为 root，并说明 Windows 客户端只支持 root，由 NT scheduler 管理调度。当前证据不支持原 Hyper-V counter 计量方案；它也没有证明所有 NT scheduler 方案均不可行。未修改 scheduler/BCD/策略，不能靠改用不支持的模式修补。

## 离线工具、关联结果和边界

系统 tracerpt 成功，但没有解码 CSwitch version 5 的字段，只给出 DataSize=28。新建并普通用户构建的 OfflineCswitch.cpp 仅用 OpenTrace/ProcessTrace/CloseTrace 读取已保存文件；没有启动/控制会话 API。它只解析经版本和长度检查的前两个线程 ID。依据的 Microsoft TraceEvent 源码现已固定到 commit `65026df998f224dbb30be9a211e82c0ae18225c7`，下载摘要和 URL 在 REFERENCE_SOURCE.json；初次分析引用的是移动 main，现固定源已逐字段核对。

恢复 3,673,287 个 CSwitch 前缀，未知版本数量 0。三个子进程均关联到唯一 process lifetime key、6 对线程 start/end、70 条 image 事件，并有匹配的上下文切换区间。具体数据见 FIXTURE_CORRELATION.json。**这些区间总和不等于完整 CPU 用量**：没有完成 ISR/DPC 扣除、guest/hypervisor 去重和所有时间边界证明；已知丢失的 trace 不可变成准入数据。零 CPU 连续性错配也不能消除 ETL header 的 12,027 lost。

Python 分析使用既有 bundled Windows **3.12.14**，用途仅为离线解析；不是 P309 解释器，也没有替代私有 CPython 3.11.15。Ubuntu 和 docker-desktop 当时均停止，未为本次分析启动。首次 CSV 按 UTF-8 解析在字节 5148 因 0xbf 失败；保留该脚本，按只读 ACP=936 更正后成功。此为普通离线解析修复，不是再次真实采集。correlate_saved_fixtures.py 是这个固定记录的事后分析，其中 loss=12027 是取自 tracerpt 的明确常量；不是通用生产分析器。

完整 ETL、1.49 GB CSV、CSwitch CSV、原始系统事件样本与其他进程 payload 仅留本地；本目录只发布固定采集摘要、自有 fixture 数据、源代码及源/工具摘要。不把全机原始活动推到仓库。

## 已确认的修正及剩余路线

另建后续源码目录，保留所有已批准及实际执行字节。下一版需要：先持久化查询失败/丢失现场，再停止；明确空 category 是 UNAVAILABLE；分别记录 fixture 清理、会话不存在、creator stop 和 coverage；保持成功 StartTrace 及 GUID 检查的停止权，不以 4201 为理由采用别人的同名会话。扩大文件预算只能解决容量因素，不能作为 counter/归属修复。

WHP 的 [WHvGetVirtualProcessorCounters](https://learn.microsoft.com/en-us/virtualization/api/hypervisor-platform/funcs/whvgetvirtualprocessorcounters) 需要调用方持有 partition handle；这是可能的独立计量对照，不能假装现有外部采集器已持有 QEMU 的 handle。原生 root scheduler 计量和完整归属仍需实际对照、完整来源及独立审阅。任何新 trace/VM/隔离试验都须先形成新的完整批准包；本次授权已耗用。

没有新增 VM、账户、服务、密钥、Windows 策略，没有 drill、freeze、grant、qualification 或 P309。I1（隔离）、I3（注册）、I4（guest 实际来源）、I5（broker/unit）、I6（独立停止与恢复）、I7（正式路线及外部授权）仍按 DEPENDENCIES_AND_ORDER.md 继续，不能把本报告当作这些项的关闭。
