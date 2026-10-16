# 剩余工作统一顺序及开放项

用户要求持续到最终实际结果；本目录的代码、测试或归档都不是整体任务完成。原规则和阈值不变，没有 freeze、grant、qualification 或 target 授权。

1. **I2 关键依赖的真实能力核验**：先完成本批次的源绑定、构建、独立静态审阅和具体批准，再采集一次并离线分析。依事实决定 native collector 的实现、最小权限和不可满足点；未确认可采集的字段不能用虚构事实填充签名。完整 CPU 归属/去重规则仍需实现、审阅和实测。
2. **I4 运行环境**：签名的 Ubuntu 24.04 Minimal 镜像已经下载核验，尚未启动。CPython 3.11.15 已完成普通用户 staging build。首次构建遭遇既有 unattended-upgrade，明确不用于部署；第二次前后包清单及系统 Python 摘要稳定。18 项模块导入及 fork 检查、8,073 文件清单、78 个运行时 ELF、36 个动态库仅为构建主机事实。镜像缺少的运行库需补齐精确的签名来源、离线安装包及许可，不能把 build-host 的成功宣称为 guest 成功。原私有解释器字节不变。
3. **I1/I3/I5 完整部署包**：独立 VM/磁盘/网络面与资源预算；Windows observer/controller/relay 身份，公钥登记与保护目录；guest R/M/B/U、固定 root broker、monitor、socket activation 和限制 unit。H2 要改为明确的 VM 传输方案，须单独说明与原接受契约的差异。当前新停止原语与编译的 guardian 不能替代完整 broker，D2 synthetic API 也不能通过翻转一个标志变成生产授权。完成代码、安装器、逐项原值/碰撞拒绝和回滚后再集中请求该实际部署许可。
4. **I6 真实停止与恢复**：持有 cgroup/pidfd 身份、先锁定后停止、进程退出与空 cgroup/manager job 证据、broker/monitor/日志阻塞及退出、Windows VM 独立停止、外部保护 anchor、断电/重启的 UNKNOWN。当前 guardian 有单独进程和内核停止接口源码，尚未执行；V4 的退出观测不能排除 watchdog 因果混淆，不能作为完整 I6 关闭。持久化故障与 rollback 不能制造新代次/恢复运行权限。
5. **I7 正式路线修订和独立审阅**：完整来源与全部真实证据一并送审。独立 AI 审阅由本任务安排，不再要求用户搬运材料；它不冒充契约指定 owner/正式 reviewer 的有效接受。原 AWS/IMDS、systemd/非容器、维护窗口与 CPU 定义必须按原条件处理或获得明确接受的修订，不伪造 AWS，不默改原 r2。
6. **正式运行链**：只有实际 I1–I7 满足并获得有效外部正式授权后，才使用受保护原字节独立 checkout，按原 8a/8b/8c、R0/R1/R2/R2b、O1–O10、OD-R2-0(D)、freeze/grant/qualification/target 和 exactly-once 限制推进。D 不是 grant；结果未知不自动 retry/resume。

若实际 Windows 采集或 VM 边界无法满足硬要求，保存决定性失败和原始证据，给出最小替代主机方案；不累加 synthetic PASS 来声称解决。当前只有未验证点，不能提前宣布整条本机路线可行或不可行。
