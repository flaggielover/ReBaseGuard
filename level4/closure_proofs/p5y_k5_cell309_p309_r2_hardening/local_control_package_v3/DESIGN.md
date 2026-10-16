# I2 root scheduler 诊断修正版（提案，尚未执行）

目标是解决真实失败暴露的关键依赖，而不是累加模拟 PASS。已执行 v2、所有 raw records、历史 source bindings 不变。正式 I1–I7 全开，准入 BLOCKED。

比较过三种做法：仅增大旧 ETL 预算不能解决 counter rows 为空；修改客户端 hypervisor scheduler 不在支持/授权范围；采用已存在 WHP 的固定小型 VM 与 NT 调度记录做对照，能调查关键计量缺口且不需安装 guest OS。选择第三种作为下一批候选诊断。这个选择尚不是正式运行路线修订。

实现范围：新名字和新受保护目录，sequential ETL 上限 1 GiB（开发预算提案，原 60 秒要求不变），75 秒原停止线程保留；所有 query 的 rc/GUID/loss 在判断前持久化；counter 逐 category 明确 AVAILABLE/UNAVAILABLE/ERROR，不把空 rows 当零负载。诊断可以记录 unavailable 并继续 ETW，但永远不产生 coverage_complete 或正式成功。

同一批次保留三次固定 200 ms 原生 CPU fixture，并增加一次独立 WHP 对照 fixture：1 vCPU、2 MiB 映射内存、无磁盘/网络/设备/guest OS，仅固定 EB FE 两字节循环；由内部线程在约 1 秒请求 WHvCancelRunVirtualProcessor。外层保留单成员私有 Job、256 MiB 进程/Job 限制、最多 8 秒等待后终止自有 Job，并要求清理证据；WHP 内核开销不冒充已受 Job 内存上限约束。这个 fixture 只证明本实例的运行与计量接口，不能证明生产 QEMU 来源或其他 partition 归属。

WHP fixture 的 partition handle 由自己创建和持有，采集 VP RuntimeCounters、当前执行线程 ID、QPC 与 GetProcessTimes；为 NT CSwitch 对照提供独立计量字段。API/资源初始化失败或返回值/输出长度不符立即失败，不回退 QEMU/TCG、其他 hypervisor、其他 Python 或计量定义。已存在 QEMU 不改变、不启动。

下一批若获批准，collector 与固定 WHP fixture 都在同一次 UAC 批次内运行；这是诊断权限上界，不是生产最小权限已满足。虚拟账户权限与 PPL/短进程/跨 partition 覆盖仍是独立硬要求。未经新的人工批准不得运行任何 --guard/--sample/--fixture/--probe 入口。

构建使用既有 MSVC/SDK/.NET，在新的 owner/SYSTEM/admin 保护目录内锁定 source/object/executable。普通用户仅运行纯内存测试和 ABI 检查。提升链沿用 native pre-CLR、固定摘要、clean environment 的设计，用新路径及新摘要绑定；没有一般命令、PID、会话名或 binary 参数。

验收分开记录：完整无丢失窗口、三个普通 fixture、WHP fixture、会话 absence、creator stop receipt、helper exit。任何缺失都不得改写为 STOPPED/完整采集。采集技术完成也只进入离线分析，不授予正式准入。

回滚只停止本批新建且句柄/GUID 绑定的会话/Job/partition，保留新旧证据；不按名字收养会话，不碰其他进程、WSL、服务、策略、密钥或原 Ubuntu。UNKNOWN 保留现场、不自动重试。下一次实际动作必须在全部源码、构建、独立复审、精确批准文件准备后集中请求。

复审修正：partition 仅在创建精确返回 S_OK 且句柄非空后取得清理权；稳定摘要以 session/helper/native/WHP 四项静止为门槛。75 秒线程仅请求停止，不能抢占已占有停止状态并阻塞的 Query/ControlTrace；不作为实际清理硬期限或 I6 证明。当前构建与调用绑定见 FINAL_BINDINGS_V2.json。
