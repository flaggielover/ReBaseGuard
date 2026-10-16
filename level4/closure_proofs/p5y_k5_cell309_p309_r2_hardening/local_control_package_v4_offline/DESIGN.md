# 已保存 ETL 的 QPC/中断归属分析（开发，不是准入）

真实 root 诊断完成后继续解决 I2 的 CPU 口径，不启动新的采集或 VM。保留已经批准和执行的 v3 字节。选择直接读取保存 ETL 的原始 QPC，避免将已转成 FILETIME 的 CSwitch 与 QPC 的 DPC/ISR 起点混用。另一方案是只比较 process CPU 与 VP 总量，但不能消除调度/中断混算；从头重新采集没有必要，现有数据已包含所需事件。

新 native reader 仅 OpenTrace/ProcessTrace/CloseTrace 文件 API，解析固定版本的有限前缀，拒绝未知所需格式。按 EVENT_HEADER_FLAG_PROCESSOR_INDEX 选择 CPU 标识。只输出本地 CSV（时间、CPU、PID/TID/不透明 process key/flags），不输出命令行、映像路径或 SID。QPC clock/frequency、loss、完整文件结束状态记录在摘要。不同 processor namespace 或不足 60 秒仍不能当完整覆盖。

分析使用实际 WHP 记录绑定 pid/creation/run_tid 与 process/thread 生命周期，以同一 QPC 窗口截取 CSwitch 间隔；按 CPU 合并重叠 DPC/ISR 区间后求交，避免嵌套中断重复扣除。单独保留 threaded DPC（它有自己的调度线程，不能当普通 IRQ 再扣除）。报告原始 scheduled、IRQ overlap、相减后时间与 VP/process delta，不设置任意误差阈值，不宣布口径等价。

无丢失只能证明这份文件的 loss 计数，不证明所有 provider/保护进程/其他 partition 都已覆盖。原 I1–I7、阈值、正式权限、exactly-once 均不变。新单元测试只核对解析边界与区间算法；实质证据来自已经批准的保存 ETL 重放。后续真实能力/安装权限仍需完整包的新批准。

依据：已保存并固定的 Microsoft PerfView KernelTraceEventParser.cs（65026df998f224dbb30be9a211e82c0ae18225c7，SHA2245ccc62b0d933190068a18344bc64749a2893bd9740a79706ba7fe5e86c778）；Microsoft EVENT_TRACE_LOGFILEW RAW_TIMESTAMP、TRACE_LOGFILE_HEADER ReservedFlags/PerfFreq、MS-DTYP EVENT_HEADER ProcessorIndex 文档。只证明所读字段，不外推完整事件 schema。
