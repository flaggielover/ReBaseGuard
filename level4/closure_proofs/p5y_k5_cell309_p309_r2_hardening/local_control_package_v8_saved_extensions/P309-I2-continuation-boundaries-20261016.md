# I2 继续调查的边界与停止条件

这是实际结果之后的工程记录，不是准入、路线修订或再次采集授权。I1–I7 全部保留 OPEN；正式准入 BLOCKED。用户批准的一次 v6 管理员只读修复预检已执行；本文不续用该授权。

## 已取得的实际结果

绑定源码 `1e3837bf7f1cdad3ce5b573d5fc9f6fba310b90a` 的 v7 离线审计已经完成，公开结果随提交 `ddb9667dcacd34e447f0074e7a6855ffca8dcfda` 普通推送。两遍各 4,191,774 行、3,829,610 次 CSwitch，绑定同一 CSV 摘要 `8d8a412465231f1bd8aca6caa28408c1c0730cc92ab3ee60e861030565bd3d8c`。60 秒、32 CPU 的窗口有 0.3413936 CPU 秒 UNKNOWN。

历史 0.4392592 CPU 秒仍保留。旧未知变成新已知 0.1247455 秒；与此同时，旧已知有 0.0268799 秒因原始跨度越过线程存在边界被新算法拒绝。不能把差值 0.0978656 秒都写成“已恢复”。完整性、受保护活动覆盖、partition 归属、host/guest 去重均未获证明。

## 已核对的官方接口语义

Windows client 的受支持 Hyper-V 配置是 root scheduler；不能为规避归属问题建议改成 classic/core，也不能把服务器专用资源控制当成本机已有能力。[Microsoft：Hypervisor scheduler types](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/manage/manage-hyper-v-scheduler-types)。这限制替代方案的选择，并不自行证明所有 Windows 采集路线都不可能。

现代 System Providers 可以通过 `EnableTraceEx2` 为 SYSTEM_LOGGER 会话启用，但官方明确输出事件本身没有因为启用机制而改变。因此，改用 SystemProcess/SystemScheduler Provider 并不自动修正生命周期端点或 CPU 归属。[Microsoft：System Providers](https://learn.microsoft.com/en-us/windows/win32/etw/system-providers)。

`EVENT_ENABLE_PROPERTY_PROCESS_START_KEY` 请求扩展项中的本次 boot 唯一进程序号；这是值得检查的额外身份来源，不等同于进程名或可复用 PID。[Microsoft：ENABLE_TRACE_PARAMETERS](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/ns-evntrace-enable_trace_parameters)。扩展项类型还明确要求相应 EnableProperty；应遍历原始 EVENT_RECORD 的 ExtendedData，不能从旧 CSV 缺列推断原始 ETL 也没有该字段。[Microsoft：EVENT_HEADER_EXTENDED_DATA_ITEM](https://learn.microsoft.com/en-us/windows/win32/api/evntcons/ns-evntcons-event_header_extended_data_item)。

在进程/线程 Start 上，header 的发出进程不自动等于 payload 中被创建的目标进程。即使发现 start key，也必须先确认其所属语义，不能直接给子进程或 CSwitch 的旧线程赋值。已有 v7 厂商语义审阅及原始反例继续有效，不通过 ThreadEnd 延长、窗口裁切后重绑、PID0 豁免或平均负载很低来消除 UNKNOWN。

## 现在可继续做的实际工作

新增 v8 只读离线扫描器将检查已经保存的 `capture.etl` 的扩展项结构。输入预期 SHA-256 为 `3faee3bd46a7fd33b046edce00da058f630296a0b73d1893c3281c250e1d6870`，308,346,880 字节。先完成源码、构建、内存检查及独立源码审阅，再执行固定的已有文件解码；不新建 trace、不提权、不启动 VM，也不生成新的主机样本。

输出仅为 provider/id/version/opcode 和 extType/length 的聚合、存在/缺失/重复/异常、时钟/loss/API/文件读取状态。无原始 PID、路径或 start-key 值。源文件、二进制、编译器、SDK 和调用入口必须绑定；输入保持句柄钉住并前后验摘要。部分输出、读取/关闭错误或未覆盖的格式都保留为失败/未知。

无论发现字段与否，v8 都不直接设置 coverage_complete。若原 ETL 没有可用身份字段，只能决定“此历史采集不能补出这些证据”；不能把它扩大成“整个 Windows 平台不可能”。若确有可用字段，先证明其归属及其与线程代次的关系，再修改解码器并保留旧结果。

## 后续真实采集的必要门槛

不因 v8 缺失就自动重跑采集。新的真实采集必须说明它增加哪个已核实的官方字段、解决哪个反例，以及仍无法解决什么；把必要的 provider 权限、精确源码/二进制、日志预算、固定夹具、停止与回滚同其他真实验证统一成包后请求批准。仅换启用接口、增大测试数或更换解析库，不构成重跑的充分理由。

若最终仍无法为硬要求提供可审阅的实际证据，应交付实际失败、官方语义边界和最小替代路线；不将 UNKNOWN 改成零，也不自授豁免。原 AWS/IMDS/维护与独立正式接受要求仍由 I7 保留。
