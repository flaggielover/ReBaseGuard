# 本机路线的连续推进与当前批准边界

**整个 P309 任务未完成。正式准入 BLOCKED；I1–I7 全部 OPEN_RETAINED。**

用户已选择继续本机，确认其同时代表 P309 owner、Windows 管理员、Cell-308 操作者，并声明本机没有 Cell-308 或其他需保留计算窗口的工作负载。该声明仅限本机，不是远端状态，也不是安装、正式演练或计算授权。此前 AWS 入口建议保留为历史，不再作为当前路线的输入要求。

## 为什么先跨越真实平台验证边界

现有 WSL 设计的隔离问题没有通过源码修复消失。新候选使用 **Windows 上独立的 QEMU/WHPX VM**，原 Ubuntu 只承担已授权的开发工作。Windows Home 不具备完整 Hyper-V 主机角色，因此不走强装 Hyper-V 角色的路径。QEMU 11.1.2 文档明确支持 WHPX，但要求安装 Windows Hypervisor Platform；本机功能元数据为 Disabled，而只读 WHvGetCapability 返回 HypervisorPresent=true。**这个差异必须用实际平台配置/启动验证解决，不能由 API 名称、合成测试或推测代替。**

原用户要求在实际安装、提权和隔离演练前集中批准。因此当前制作完整、可审核的**平台可行性变更包**，并在这一必要边界请求许可。此包的准备完成不代表全套生产控制层安装包已经实现：身份、ETW、guest broker、anchor 等仍未实现，不能在未知后端上把占位服务伪装成可部署成果。批准并取得真实平台结果后，继续同一任务完成这些工程、审阅和下一次确实必要的生产变更批准，不要求用户来回搬运子任务。

## 当前具体变更包

| 项目 | 精确内容 | 权限与验证 |
|---|---|---|
| WHP | 仅在 Disabled 时启用 `HypervisorPlatform`，`-NoRestart -LimitAccess`；已 Enabled 则不改 | 需要一次 UAC；不使用 `-All` 自动扩展父功能，不下载 payload，不自动重启；pending/失败停止 |
| QEMU | MSYS2 UCRT QEMU **11.1.2-1**，159 个锁定归档签名已验；从中选取 222 个文件，459,552,711 字节 | 只放到新目录 `D:\ReBaseGuard-309\local-vm-feasibility\candidate-v1`；不运行 pacman/hooks，不改 PATH，目录碰撞停止 |
| 短时真实探针 | 两次固定 q35/WHPX VM，4 vCPU、128 MiB、暂停态、无磁盘/网络/串口/显示/监控接口；每次 15 秒 deadline | 普通用户运行，禁止提权；不启动 Ubuntu guest、不运行任何 P309 workload |
| 独立停止 | 子进程暂停创建，先加入 unnamed Job，再恢复；Job 禁 breakaway，1 进程上限、768 MiB 进程和 Job commit 上限、KILL_ON_JOB_CLOSE | 一次 deadline；一次 guard `ExitProcess(86)` 故障注入；外部 harness 以 PID+creation FILETIME 绑定句柄，观察精确子进程退出 |
| 证据/回滚 | 仅追加新目录；先停止并确认，再退役；必要时恢复本次启用的 WHP | 无后台服务或端点；软件和日志封存，不删除；WHP 恢复条件见 ROLLBACK.md |

128 MiB 是平台探针的尺寸，**不是降低正式 8 GB 可用内存要求**。768 MiB Job commit 限制也不是已证明覆盖全部 WHPX 内核内存。探针 PASS 最多证明指定二进制在固定参数下存活及自有进程停止；不证明 Linux 启动、全部 partition 资源回收、host CPU 归属、正式容量或 I1/I6 关闭。

候选二进制来自 MSYS2，不能标成“QEMU 上游直接发布的 Windows 二进制”。签名公钥从 MSYS2 官方 keyring 包取得，keyring 包 SHA-256 与官网一致，验证使用官方列出的 developer 主指纹；未生成/注册生产密钥。全部包、签名、失败下载记录和选取文件摘要保存在 records，未安装这些包。

## 源码和真实验证标准

`OwnedVmProbe.cs` 只提供上述固定平台探针，不接受调用者传入 PID、命令、QEMU switches、磁盘、网络或 Job 名称。批准清单哈希和整个 runtime 文件集在启动前核验，保持只读文件句柄，拒绝 reparse/逃逸/额外文件；最小环境固定 DLL/data/module 搜索。guard 的停止线程先调用原生 Job 终止，再进行任何日志操作；外部 harness 无终止任意进程接口。

必须同时满足：官方包及全部依赖绑定一致；非提升身份启动；没有 TCG fallback；5 秒时唯一自有进程仍在 Job；deadline 用句柄确认退出并查询 Job active=0；guard 退出用绑定的外部句柄确认 child 退出。错误、提权需求、资源不足或身份 UNKNOWN 都停止，无自动换后端、自动扩大权限或重复真实探针。真实加载的模块及动态依赖仍需后续记录；静态 import 清单并不是完整运行时证明。

## I1–I7 后续统一实施顺序（提案，未获接受）

1. **平台结果 → I1/I7 路线审阅**：独立 VM 硬件后端通过后，提交安全边界/威胁模型、Windows Home/WHPX 支持来源及实际现象。runner 不取得 Windows 管理身份，不挂主机目录，不转发通用 QMP/命令。有限拒绝用例不能证明不存在逃逸。若固定后端不成立，记录决定性失败及受支持替代，不追加模拟 PASS。
2. **I4**：独立 Linux image 的签名/摘要、全新 guest root-owned CPython **3.11.15** 构建、编译依赖、完整 prefix+ELF依赖+系统包/镜像清单、实际 glibc/二进制、所有父目录权限。现有 UID1000 runtime 仅用于开发，不能复制旧摘要冒充新部署 pin。系统 Python 不改。
3. **I3/I5**：确定新 Windows 服务身份和客体 UID 后生成逐 SID/UID ACL、最小权限和独立公钥登记包；控制接口只允许已接受的固定 status/stop，明确 guest/host/boot/runtime/代次绑定。固定 broker 不接受任意 unit、命令或属性。未来 start 只能由另行批准的固定管理入口单次分配，不能扩充当前 D2 API。账户、服务、密钥、unit 尚未创建，也没有以这些提案索取无限部署许可。
4. **I2**：实际最小权限的 Windows 生命周期/调度事件采集，短命/受保护活动、丢失计数、跨边界归属及 guest/host 去重。任何丢失、无法解释 CPU 或不能读取的受保护活动都阻断；不能按 vmmem/QEMU 名字豁免，不能自动转 LocalSystem/debug/driver。当前未启动 ETW 或安全采样，CIM 快照不是完整覆盖证明。
5. **I6**：collector/signature/transport/log 故障时独立停止；guest cgroup 清空+退出回收、Windows 自有 VM 退出/资源释放；外部保护 anchor、不可回滚代次、日志容量和落盘失败。断电/休眠/重启是 continuity failure，恢复只能 RECOVERY_UNKNOWN/STOPPED，不自动重启计算；未宣称 Windows 普通线程具备实时停止保证。
6. **I7/AF-2 修订**：原 Linux systemd/x86_64/非容器检查在新 VM 实际执行；IMDS 缺失不能伪造 AWS 响应。提出经过独立审阅的本机托管身份、非 Spot/非 burstable 和维护窗口替代证据，需 owner 接受。Windows host 活动与 guest 活动的计量去重规则须独立确认。用户“本机没有其他计算窗口”只作为操作者声明，不能删掉 foreign-process gates 或虚构 ForeignRoots。
7. **正式流程**：在独立正式 checkout 上保持原字节/保护绑定，经真实证据和独立审阅、完整 8a/8b、owner/operator 具体许可后才进 worker-tier drill；再按 R2/R2b、O1–O10、OD-R2-0(D)、qualification、grant、target 顺序。OD-R2-0(D) 不是 grant。禁止自授、自动 retry/resume 或把本平台探针算成正式演练。

原阈值仍是 4 affinity CPU、8 decimal GB、每根 40 decimal GB、60 秒采样、0.05/0.5/1.0 core、5 秒 suspend、45 秒 gap。12 GiB guest/14 GiB host cap 等未来资源数值都还只是候选；当前约 9.94 GB 可用 RAM 不足以预先承诺完整 VM 容量，不终止无关进程来腾空间。

## 当前验证边界

新增 archive parser 单元测试只验证依赖解析与 PE 输入拒绝；Windows guard 的纯函数检查只验证参数编码/固定参数。既有 157 Cloud、18 数学签名、12 Session/Chain 样本和 2048 位额外时间反例仍按历史边界保留。没有重跑它们，没有用这些检查关闭 I1–I7。

厂商原始来源：

- https://raw.githubusercontent.com/qemu/qemu/v11.1.2/docs/system/whpx.rst
- https://raw.githubusercontent.com/qemu/qemu/v11.1.2/docs/system/security.rst
- https://learn.microsoft.com/en-us/virtualization/api/hypervisor-platform/funcs/whvgetcapability
- https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects
- https://packages.msys2.org/packages/mingw-w64-ucrt-x86_64-qemu
- https://www.msys2.org/dev/keyring/
