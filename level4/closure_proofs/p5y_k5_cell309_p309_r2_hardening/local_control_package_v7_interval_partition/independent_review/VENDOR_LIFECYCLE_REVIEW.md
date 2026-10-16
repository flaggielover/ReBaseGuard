# Windows ETW线程代次与终止尾段公开契约调查

公开primary资料支持CSwitch运行片段和生命周期事件字段的解释，尚不足以把ThreadEnd到某次后续切出之间的尾段无歧义归回旧线程代次。此调查不批准延伸ThreadEnd，不改变I2或接受标准。

## Microsoft公开保证

CSwitch描述NewThreadId、OldThreadId、priority、wait及OldThreadState；4表示Terminated。该payload没有ThreadGeneration、ProcessKey或旧进程的boot唯一标识。文档没有规定ThreadEnd与最终切出的身份延续关系，也没有给出终止尾时长上限。连续CPU span只能支持调度片段的几何关系，不能单独证明复用后的数值TID仍是旧代。[CSwitch](https://learn.microsoft.com/en-us/windows/win32/etw/cswitch)

TraceProcessor的CpuTimeSlices说明一段运行由switch-in和switch-out界定；ICpuTimeSlice的Process、Thread及切换信息仍可能不可用。此公开接口没有承诺修复缺失生命周期或证明End后尾段所属代次。[CpuTimeSlices](https://learn.microsoft.com/en-us/dotnet/api/microsoft.windows.eventtracing.cpu.icpuschedulingdatasource.cputimeslices?view=trace-processor-dotnet-1.0)、[ICpuTimeSlice](https://learn.microsoft.com/en-us/dotnet/api/microsoft.windows.eventtracing.cpu.icputimeslice?view=trace-processor-dotnet-1.0)

DCStart和DCEnd分别枚举session开始、结束时存在的线程，不能当作真实出生和死亡。Thread Start可能在parent上下文记录，事件header的PID/TID可能不同于payload目标；必须保留两者，不能用header替代目标身份。[Thread](https://learn.microsoft.com/en-us/windows/win32/etw/thread)、[Thread生命周期字段](https://learn.microsoft.com/en-us/windows/win32/etw/thread-typegroup1)

ProcessTrace只尝试按timestamp交付。不同CPU产生同timestamp事件时，交付顺序不可预测；decoder的event_sequence是交付序号，不是跨CPU因果序。相同QPC的Start、End、CSwitch不能通过排序opcode或交付顺序消除歧义。[ProcessTrace](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/nf-evntrace-processtrace)

旧Process payload的UniqueProcessKey是内核process object地址，不等同于boot唯一sequence。EVENT_HEADER_EXT_TYPE_PROCESS_START_KEY是64位、boot内唯一标识，需采集时请求并实际存在；其语义是logging process，不能无契约套给payload中的另一目标。已有ETL若没有该扩展字段，不能事后制造。[Process字段](https://learn.microsoft.com/en-us/windows/win32/etw/process-typegroup1)、[扩展字段](https://learn.microsoft.com/en-us/windows/win32/api/evntcons/ns-evntcons-event_header_extended_data_item)、[启用属性](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/ns-evntrace-enable_trace_parameters)

## 固定PerfView源码的分析器策略

固定公开commit为 `65026df998f224dbb30be9a211e82c0ae18225c7`。

TraceLog.cs 1387至1445将DCStart起点设为session start、DCEnd终点设为session end；5988至6090的GetThread/GetOrCreateThread使用最近start不晚于查询时刻的历史记录，并存在缺失事件时假设死亡或新建线程的修补路径。该查找不以end作严格存在检查。ThreadIndex是工具log内唯一索引，不是OS提供的不可复用线程标识。[TraceLog](https://github.com/microsoft/perfview/blob/65026df998f224dbb30be9a211e82c0ae18225c7/src/TraceEvent/TraceLog.cs#L5988)、[HistoryDictionary](https://github.com/microsoft/perfview/blob/65026df998f224dbb30be9a211e82c0ae18225c7/src/TraceEvent/TraceUtilities/HistoryDictionary.cs#L78)

ThreadTimeComputer.cs 737至748在ThreadStop标记dead；865至899明确忽略记录线程死亡后的清理时间。该文件不使用OldThreadState延长身份，并在处理CSwitch时跳过TID0。这些是性能分析器的选择，不能拿来证明P309完整覆盖、允许丢弃尾段或给idle豁免。[ThreadTimeComputer](https://github.com/microsoft/perfview/blob/65026df998f224dbb30be9a211e82c0ae18225c7/src/TraceEvent/Computers/ThreadTimeComputer.cs#L737)

KernelTraceEventParser.cs的ThreadTraceData.FixupData会调整header呈现，并保留或交换parent字段；CSwitch的OldProcessID是依据历史映射推导的属性。分析器显示出的ProcessID不能自动当作额外raw证据。[KernelTraceEventParser](https://github.com/microsoft/perfview/blob/65026df998f224dbb30be9a211e82c0ae18225c7/src/TraceEvent/Parsers/KernelTraceEventParser.cs#L4072)

这些源码可以说明工具如何解释数据，不能升级为Windows内核的完整身份、事件顺序或无丢失契约。

## PID0与DCEnd-only历史还可补读什么

已有ETL可以在另行审阅的有限离线decoder中补读：原始Start/DCStart/End/DCEnd的QPC和opcode、完整Thread_V3 payload、原始header PID/TID、CPU命名空间判别、版本、长度、flags以及实际存在的extended items。Thread payload中的stack范围、Affinity、Win32StartAddr、TEB、SubProcessTag及priorities可用于检查schema和关联一致性。

但这些字段不提供不可复用ThreadGeneration。公开ThreadFlags说明为Not used，本调查没有找到可将其某一bit当idle身份凭据的Microsoft契约。PID0或DCEnd-only最多证明枚举时点的目标身份；不能倒推出session开始就存在，也不能仅凭名称、地址或affinity创建idle例外。[Thread_TypeGroup1](https://learn.microsoft.com/en-us/windows/win32/etw/thread-typegroup1)

当前OfflineQpc.cpp只保留thread的PID/TID前缀；SavedThreadTerminal.cpp又保留了header和payload双身份、OldThreadState等，但并未保留完整Thread_V3或extended items。本轮只静态阅读这些源码，没有执行新的ETL解码；不能承诺补读后必然消除未知。

## 生产observer必须保留的边界

生产身份至少应使用受绑定的trace与boot命名空间、不可变ProcessGeneration、ThreadGeneration及其原始证据引用。保留真实Start、rundown存在锚点、真实End或DCEnd边界类型，以及每CPU switch-in当时绑定的代次。部分字段缺失不能从后来的同PID/TID记录倒填。

遇到丢失、复用、同QPC歧义或End后的无受支持身份链接，保留UNKNOWN并守恒计量。若希望提出新的终止尾延续规则，决定性缺口是ThreadEnd事件、最终运行、ID回收和后续CSwitch之间的官方身份与顺序契约，或同等强度的可审核身份依据。本轮primary资料尚未补足它。

33.8504毫秒经验量、首个End后切出、事后选择最后一次切出、PerfView可显示某进程、OldState4或连续CPU span，都不能单独作为证明。即使未来解决该尾段，PPL、其他partition、IRQ口径及guest与host去重仍各需独立证据。

原0.4392592秒未知CPU归属量未变。I2 OPEN；I1至I7 OPEN；正式准入BLOCKED。
