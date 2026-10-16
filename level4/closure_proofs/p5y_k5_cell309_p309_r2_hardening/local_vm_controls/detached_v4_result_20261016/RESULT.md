# V4 实际平台验证结果

精确源码 `57fac3a72783861b5cd72e84665ba68fafc1cc96`；用户批准 V4 两项验证后仅执行这一批，无重试。

两项 scoped probe 均通过。deadline 在 14500 ms 请求停止，14547 ms 确认清理，未超过原 15000 ms 上限；唯一 QEMU PID 38408 / creation FILETIME 134365850570917456。Job active=0、进程退出码 777、两个进程等待均成功。随后才执行 guard-exit：唯一 QEMU PID 36928 / FILETIME 134365850799303259；guard ExitProcess(86)，外部持有的精确 QEMU 句柄确认退出。

两项在暂停创建及 5 秒观察时均只有 1 个 Job 成员。原子 Job 绑定、无句柄继承和限制回读成立。DETACHED_PROCESS 下本批未再观察到 V3 的额外 conhost 成员；不将两次观察推广为全场景证明。运行后 222 个 runtime 文件、459552711 字节全部匹配，无额外文件。

5 个 Windows scratch cache 文件保留在本机原证据目录，只发布路径/大小/摘要清单，不发布缓存内容。全部 V1/V2/V3 历史及其失败保留。证据中 preparation 的未授权/未执行标志是当时快照，由本记录追加更新事实，不重写旧记录。

这证明指定小型、暂停、无盘无网络配置下的 deadline 和 guard 退出清理。没有证明 Linux guest 启动、完整 WHPX partition 资源回收、生产隔离身份、采集覆盖、服务/密钥、持久化和恢复。无新安装、提权、策略修改、ETW、正式演练、qualification、target 或 grant。

I1–I7 全部 OPEN_RETAINED；正式准入 BLOCKED；P309 整体未完成。后续继续同一任务准备完整控制层、真实验证与回滚包，按已要求的权限边界集中确认。
