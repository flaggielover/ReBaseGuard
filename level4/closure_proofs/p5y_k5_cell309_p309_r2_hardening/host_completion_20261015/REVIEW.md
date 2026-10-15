# P309 接管调查与执行路线判定

状态：**未完成最终运行；正式准入 BLOCKED，I1–I7 全部 OPEN_RETAINED。**

本记录以 `47118d4837ab2dd5a4ff03e66263c82754769c36` 为起点。它是本地协调者的来源与可行性调查，不是独立准入审阅、8b 正式判定、部署批准或运行授权。本轮没有创建账户、发行版、服务、端点、密钥或 unit，没有修改策略、启动跟踪、主机安全采样、演练、资格验证或目标计算，也没有终止任何无关进程。

## 结论与证据强度

现有“同一 Windows 用户拥有新的 WSL 发行版，关闭 interop/automount，隔离 Linux 角色”的候选方案，不具备可据以关闭 I1 的受支持 Windows 隔离边界。因此**不建议将当前候选设计直接实现并安装为正式主机控制层**。在安全边界未成立之前，服务、签名和持久化代码的增加不能改变这个结论。

微软 WSL 官方安全说明明确区分功能分离与安全边界：同一用户的发行版可能共享 utility VM；发行版不是该 Windows 用户资源的安全边界；interop、automount 等配置也不是沙箱保证。该说明已固定到微软仓库提交 `4d091f77295a37d3321ef8a896965dd743474b8e`，原文 SHA-256 为 `d5f7a484facca9062787efdfdd8a63a9b42e02d8444cba4ca9c3c8dfd829270e`。[微软原始来源](https://github.com/microsoft/WSL/blob/4d091f77295a37d3321ef8a896965dd743474b8e/doc/docs/technical-documentation/security.md)

这是对**当前设计不能提供所需保证**的架构证据，**不是本机逃逸复现，也不是“任何重新设计的 Windows/WSL 架构都不可能”的证明**。Linux UID/DAC 的具体限制仍需实测；即使有限负面用例通过，也不能扩张为厂商未承诺的 Windows 边界。原设计已经排除可信 Windows owner/admin、guest root/kernel 被攻破的情形；此处没有偷偷扩大攻击者能力。

另外，本机 `systemd-detect-virt --container` 实际返回 `wsl`、退出码 0。原 r2 `501f48cb` 的 R-OS-2/B-04 明确拒绝容器。这是**原契约对当前环境的不兼容证据**。本轮不是完整 8a，不能冒称已产生正式 HOST_REJECTED 8b 记录。IMDS 没有新探测；AWS 替代语义、容器规则及 launcher 改写均无已接受修订，AF-2 仍需要 owner 决定与独立审阅，不能自行把这些条件改成 PASS。

## 已完成的实际工作

- origin 核验为 `https://github.com/flaggielover/ReBaseGuard.git`；远端 `codex/p309-d2-rereview-record-20261015` 与精确起点一致。
- 创建独立工作树 `D:\ReBaseGuard-309\workspace\p309-host-completion-20261015`，新分支 `codex/p309-host-completion-20261015`。
- 核验 141 个既有当前文件、2 份新增复审记录、20 个受保护文件以及 624 条历史源绑定；均匹配。Git 原始 LF 字节与 Windows CRLF 工作树散列分开记录。
- 读取原正式主机契约、8a/8b/8c/8d、owner 返回条件，以及 D2、隔离修订和 I1–I7。正式 r2 远端仍为 `501f48cb31fd3f80d5c6dd33f1eef6b8f01b2853`；此次指定前缀查询未返回保护 ref。这不是整个历史的 exactly-once 清白证明。
- 恢复 Windows/Ubuntu 只读元数据核验；没有启动真实安全采样或 ETW。
- 对现有私有 Python 前缀生成 8,398 条目录、链接和文件记录，无读取错误；清单摘要 `e386908060fb442cc6c23544b4826f3a0c4e0addfa5c6785e5d9cd1d79a8a62c`。它不是原子安全快照，不含全部外部系统依赖，也不是未来新安装的 pin。
- 从精确 Git 字节导出并校验 27 份原生主机入口文件，包括审计代码、正式契约和审阅/回滚/授权条件。没有执行其中代码。

历史 157 项仍只是 Cloud 测试结果；18 个数学验签样本、12 个 Session/Chain 样本，以及仅 2048 位额外时间反例的边界保持不变。本轮新增单元测试数为 0，不用重复合成测试充当主机进展。F1–F4/V1 的既有源码层结论不扩张为运行保障。

## 新鲜主机事实

采集时间约为 2026-10-15 15:42–15:45 UTC；各原始 JSON 有自己的时间戳，数值不是预留资源。

| 项目 | 实际观察 | 含义/限制 |
|---|---|---|
| Windows | Windows 11 家庭中文版，10.0.26200；32 逻辑 CPU | 不能据此宣称 32 个独占物理核 |
| 内存 | Windows 总计 34,158,272,512 B，可用 11,505,553,408 B；WSL 可用约 15,927,558,144 B | 两侧瞬时均超过 8 decimal GB；未预留独占窗口 |
| 存储 | 原 Ubuntu VHDX 注册且存在于 NTFS D:；D: 空闲 129,510,592,512 B；C: 2,280,804,352 B | C: 空间紧张；未清理任何文件。未来受保护日志容量未证明 |
| Linux 文件系统 | 现有 `/home/suzhe/p309` 位于 ext4，空闲约 1,021,452,840,960 B | 虚拟容量不得代替 D: 实际空间 |
| 预设路径 | `/home/suzhe/p309/workspace`、`scratch` 不存在 | 首次查询的 UNKNOWN 原样保留；改查现有父路径没有创建这些目录 |
| systemd/cgroup | PID1 systemd 255；运行中；查询进程 affinity 32，`cpu.max=max 100000`；根控制器含 cpu/io/memory | 不是未来执行 unit 的限制、资源隔离或独立停止证据 |
| Python | CPython 3.11.15；glibc 2.39；现有二进制 SHA-256 `b21d680e5061c20ee39c75f0c6edf8db4220f327de45e52ab2040e15ca0cf194` | 路径及父目录仍为 UID1000 所有；系统 Python 未变；新部署需重建并重新固定完整来源 |
| 时钟 | 正确使用多个 `-p` 的补查：NTP=yes、NTPSynchronized=no | 不能沿用历史“已同步”；早期逗号属性查询空输出不是成功证明 |
| 更新/重启 | Ubuntu unattended-upgrades、apt-daily timers 活跃；Windows PendingFileRenameOperations 存在 | 不等于已确定重启时间；无连续窗口或升级暂停保证 |
| 电源 | AC 自动睡眠 0；DC 自动睡眠 600 秒；S3 可用，休眠未启用 | AC 配置不能保证手动睡眠、断电、更新或重启不会发生 |
| 隔离 | 原 Ubuntu 的 interop 启用；无按名发现的 P309 Linux 独立账户；候选 Windows 服务/目录/发行版未发现 | 没有探测密钥；无正式 enrollment |
| 备份 | F: 不在场 | 历史备份未修改；不宣称当前可用、重验或恢复成功 |

## I1–I7 的统一缺口与验收顺序

以下均是未来验收要求，不是本轮已完成项。原始 blocker 文本完整保留在 `STATUS.json`。

| 顺序 | 项目 | 必须取得的真实证据 |
|---|---|---|
| 1 | I1 路线及隔离边界 | 先选有受支持边界的执行架构；随后证明 runner 不能取得 Windows owner/root 权限、读取其他工作区、绕过端点或继承控制句柄。有限测试不替代边界论证 |
| 2 | I4 镜像与运行时 | 镜像发布者/摘要、源包官方签名或校验、构建命令/依赖、整个安装树和系统依赖来源、实际二进制/glibc、所有父目录所有权；实际新主机新构建不能复用旧 pin |
| 3 | I3 注册与权限 | 独立取得的 operator/service 身份、公钥 pin、host/boot/guest/runtime 绑定、ACL/API 掩码、双向端点认证、拒绝未注册对端及描述符泄漏；不得使用合成 signer 作为生产 signer |
| 4 | I5 broker 与 unit | 固定操作及参数、最小权限、当前有效 unit/cgroup 属性、不可任意 start/rearm、UID/代次/PID 启动标识绑定、资源及 ForeignRoots 隔离。只限制 unit 名称的 polkit 规则不足以证明参数/UID/命令约束，须单独核验 |
| 5 | I2 采集 | 生命周期/短命及受保护活动覆盖，损失/未知必阻断，实际最小权限，host/guest 归属和 CPU 去重；不得按 vmmemWSL 名字豁免、不自动升级 LocalSystem/debug/驱动 |
| 6 | I6 停止/恢复 | 采集、验签、日志阻塞时独立停止；真实 unit 退出/cgroup 空/回收完成；持久化及外部 anchor 防回滚；崩溃/WSL 挂起/重启/监督者死亡；最长期窗口日志预算及低空间策略。先撤销并停止，清理确认后才拆控制层 |
| 7 | I7 正式准入 | 接受的架构/语义及源码审阅→当前完整 8a/8b→精确 OD-R2-4 及操作者许可→真实验收→worker-tier drill→独立 pre-freeze 审阅→O1–O10→独立后续授权 |

如果转原生 Linux，Windows 特定 I 项不能被我自动删除或置为 PASS。须由独立审阅将其映射到所选架构并接受适用性；保留原 WSL 分支全部未解决项。

## 最小替代路线及实际变更边界

推荐优先使用原 owner 已指定的 AWS ReBaseGuard Linux worker，取得**独立 P309 访问路径**后做原字节 8a。这样避免新建 Windows 信任链、WSL 边界及无 IMDS 适配。此推荐不表示该 worker 当前可用、合格或已获安装/运行授权。若原 worker 不可用，再由 owner 指定非 burstable、非 Spot、x86_64、systemd、至少 4 affinity CPU/8 GB 可用 RAM/各根 40 GB 可用盘的原生 AWS 主机；推荐余量另行按实际工作负载确定，未购买任何资源。

本次可交付的原生入口已完整固定在 `reviewed-native-entry/EXPORT_BINDINGS.json`。其中 `native-audit/p309_host.py` 的精确 SHA-256 为 `ec9c8416159cf9e2e7372f97ce179a290def987007dc144591833615ca251f65`。入口只允许按 `HOST_READ_ONLY_AUDIT_8A.md` 走 audit，不从当前开发 checkout 运行 official/drill，也不以 wrapper 改写原字节。8a 的 5 秒进程观察需要对应主机与 operator 同意；当前 Windows 元数据授权不能代替远端指定主机授权。

实际安装包目前**未就绪**：尚无目标原生主机事实，不能编造账户碰撞、依赖缺失、更新文件、UID、外来目录、MemoryMax 或执行窗口。不能以一个含占位值的脚本索取无限制安装许可。取得目标主机及 8a 后，我将一次准备这些可审核项目，再集中请求实际变更许可：

| 变更 | 权限/验证 | 回滚及保留 |
|---|---|---|
| 新 P309 账户和独立 clone/scratch | 管理员创建；固定非 root 账号、无附加组；仅自己的新目录；独立 object store；碰撞即停止 | 不删除已有账户或目录；停用新增入口并封存数据；证据导出后才另行决定删除 |
| 私有 CPython 3.11.15 及缺失构建依赖 | 先列精确缺失包；限定新前缀与构建并发；源码验证、全部安装树/外部依赖和新散列 | 系统 Python 不变；新前缀封存；不自动移除其他软件依赖的包 |
| 特定 broker/启动权限及 unit | root 创建经过源码审阅的最小权限配置；不能把通用命令权限隐藏在 unit 名称规则中；实际负面验收 | 先撤销启动许可并停止唯一所拥有代次；确认退出和回收后禁用新增接口；控制未知则保留 supervisor 并隔离，不猜 PID |
| 确需的时钟、更新 hold、控制器/重启项 | 8a 触发的精确项目；owner 以及受影响操作者同意；逐文件/服务保存前后状态 | 按批准窗口恢复原字节和原运行状态，不一律启动服务；重启事件不可撤销，需事前安排 |
| 窗口、8d 及后续正式阶段 | 原阈值 4 CPU、8 GB、40 GB、60 秒、0.05/0.5/1.0 core、5 秒 suspend、45 秒 gap 不变 | 无自动 retry/resume；失败保留证据并按契约返回 owner；不把测试失败后的重开算作同一次 |

也可以选择独立管理的非 WSL VM，但这仍需要新的宿主覆盖与无 IMDS 语义修订；当前信息下它不是最少契约变更路线。没有把“在当前 Windows 新建另一个普通 WSL 发行版”列作已经足够的替代方案。

## 后续一直到最终结果的授权链

统一顺序为：确认指定主机/访问/操作者 → 原字节 8a 与全部 8b 行 → 精确安装配置回滚包及集中批准 → 实际实施、故障修复、真实验证和独立审阅 → owner 同意的 worker-tier drill → 按结果决定后续，绝不静默重试 → R2/R2b 授权的追加归档与独立 pre-freeze 审阅 → O1–O10 满足后再请求 OD-R2-0(D) 及主机确认 → 单次正式 qualification 及其独立审阅 → 目标执行主机和规定 QC10 检查 → 有效正式 grant → exactly-once 目标执行、持续监视及结果验证/归档。

**这不是将所有阶段一次预授权。** OD-R2-0(D) 不等于 grant；owner、独立 reviewer、Cell-308 operator 的角色不能由协调者自授。freeze、grant、qualification、target 的每个约束和禁止 retry 规则继续按原契约执行。任何结果只按真实产物判定，不依据退出码或先前合成结果猜测。

## 现在一次需要的外部输入

1. 确认你所代表的 owner/主机管理员/Cell-308 operator 角色；说明本机及拟选 worker 的共同使用者。此前异步问题仍待答复。
2. 提供原指定 AWS worker 的独立 P309 连接方式（或明确指定替代原生主机）、非 root 审计身份、已核验主机指纹及 P309 专用凭据的安全使用位置。**不要在聊天里粘贴私钥或 token**。不能借用 Cell-308 会话或凭据。
3. 提供该主机 Cell-308 表 Part A 的真实目录/重任务识别及允许 5 秒只读观察的时间；若确无 Cell-308/共租户，由有权操作者明确声明，再按正式契约处理，不能伪造 foreign_roots/UID 通过门槛。

当前卡点是**执行主机/访问路径与外部角色事实缺失，以及当前 WSL 候选安全边界不成立**，不是需要你替我拆工程子任务。尚不请求实际安装/提权/服务/密钥/策略/演练许可，也不把本报告当整个任务完成。任务目标保持未完成；收到上述必要输入后应在同一任务继续。
