已保存 ETL 的线程退出时序诊断，2026-10-16

本次只普通构建并单次解码固定保存 ETL；未启动新跟踪、VM、UAC 或
P309 工作负载。原 ETL SHA-256 为
3faee3bd46a7fd33b046edce00da058f630296a0b73d1893c3281c250e1d6870。
新 native 解码器保留原始 Thread 头/负载两组 PID/TID、两种 CPU 字段
及其标志、CSwitch 的 New/Old TID 和 byte 0xe 的 OldThreadState。
CSwitch 仅接受 v2/24 字节、v5/28 字节；Thread 仅接受 v3 op1–4 的
有限身份前缀，不宣称完整事件 schema 已验证。依据为既有固定 PerfView
65026df998f224dbb30be9a211e82c0ae18225c7 / KernelTraceEventParser.cs。

实际一次解码 exit0，3,829,610 个 CSwitch 全为 v5/28 字节，21,694 个
Thread；未知前缀、ETW loss、ProcessTrace/CloseTrace 和输出错误均为0。
新 CSV 为319,246,453字节，SHA-256 为
e1846fe314c5ac9f49b4794cf92dad4cdef0ce9b6afdc300cd1974486027ed8c。
Thread 头/负载不一致按 op1–4 为614、0、0、0；本 trace 的 ThreadEnd
身份未见头/负载差异。614个 Start 差异仅按原始字段记录，未据此改规则。

离线分析以历史 PRIVATE 未归属清单选中的682个 TID 为范围，保持既有
lifetimes 函数及归属边界，核对新提取的每个选定线程事件三元组，并
精确复现每个 TID 的未知 ticks 和总1,328区间、4,392,592 ticks：

- PID0 且只有 DCEnd 的组：297区间、0.0375085秒，OldState 全为2。
  继续未归属；本诊断未凭 PID、名字或状态豁免该组。
- 其余1,031区间、0.4017507秒：668区间严格跨 ThreadEnd，363区间
  完全处于 ThreadEnd 之后。跨 End 区间中只有498个切出状态为4；
  End 后区间中170个为4，其余出现1、2、3、5、7。
- 关联的668个 ThreadEnd 代次，在下一次观测到的同 TID Start 之前，
  最后一个观测切出均为 OldState=4。170个代次在 End 到最后切出之间
  存在再次切入，共363次；最大 End 到最后切出间隔为33.8504毫秒。
- 这些未知区间中未见 End 至其切出之间插入新的同 TID Start。
  “最后切出”的搜索明确在下一 Start 之前截止，不能据此宣称已证明
  所有可能的 TID 重用、跨代或丢失事件场景都安全。

观测说明 ThreadEnd 记录可能先于后续退出清理调度，且不能把第一个
ThreadEnd 后的切出直接等同最终 Terminated 切出。该观测不自动授予
将线程所有权延伸至任何后续 CSwitch 的规则；状态4是实际记录的字节，
并非准入授权。后续若提出终止边界修订，仍需明确代次、PID/ProcessKey、
重入、全 CPU 覆盖、下一 Start、缺失/丢失和 fail-closed 规则并独立审阅。

范围限制：这是已保存、此前获批的诊断 trace 的重新提取和解释；并非
真实正式工作负载或所有进程类别的覆盖证据。历史原审计的执行时输入
绑定没有被追溯证明；旧 v4 schema/输出和历史记录均未修改。CPU 双字段
虽在新诊断 CSV 同时保留，CPU 拓扑、跨组/跨分区的完整归属仍未证明。
受保护进程及其他分区覆盖、I1–I7 均保留，coverage_complete=false，
admission=BLOCKED。无新合成测试总数。

发布时只选源码、构建命令/哈希、匿名摘要和本说明。PRIVATE*.csv/json
及原始身份列表仅留本地；原 D 仓库、记录、私有构建目录均未写入。
