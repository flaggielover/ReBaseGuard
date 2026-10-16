# 本机完整控制包：开发中的明确边界

状态：DEVELOPMENT_IN_PROGRESS_NOT_DEPLOYABLE。I1–I7 OPEN_RETAINED；正式准入 BLOCKED。
当前分支由 4070e3d346a4530f6d01fecb9b86d80a2cddec02 派生；V4 两项小型暂停 VM 探针通过，不推导生产安全性。

## 已选工程方向与未获接受的语义

原 Ubuntu-24.04 只做普通用户构建。执行环境候选为签名 Ubuntu Minimal 24.04 20261008 独立 QEMU/WHPX guest，不挂载主机目录、不暴露 QMP/HMP，不允许 runner 取得 Windows owner 身份。可信 Windows owner/admin 和 guest root/kernel 仍是原威胁模型的信任根。不得把普通用户 QEMU 进程的同用户文件权限说成进程沙箱。

未来 Windows 侧将控制角色分开：受保护代码和配置、独立观察与签名身份、独立持有 VM Job 的控制身份、只转发有限协议字节的 relay。不采用 LocalSystem/SeDebugPrivilege 的自动后备。生产账户、服务、key/pipe、ETW 会话与策略均须在完整绑定、回滚和真实验收包获批准后创建。当前未创建。

客体保留原 R/M/B/U 权限分工与 H3/H4 固定 status/stop 协议。H2 的 WSL 启动元组在独立 VM 上不适用，需要新 transport 的精确保护方案和独立审阅；不是把 wsl.exe 字符串替换为任意 SSH 命令。D2 源码、历史证明和公共 API 不改，模型不是 OS executor。

## 独立停止实施

guest/owned_instance.py 是实际 OS 接口原语，尚未连接到服务。它只接收未来 root broker 自己的一次启动事务得到的 generation/InvocationID/PID/start-ticks/boot-id；禁止从 H1–H4 反序列化这些“权威”值，禁止仅按 unit 名称认领。打开 cgroup 及各祖先拒绝 symlink 和非 root/可写目录，固定 p309-dev-owned-check.service；前后核对 manager 和 /proc 身份，持有 pidfd 和 cgroup.kill FD。stop 先锁定内存状态，仅写已持有的 FD，不等待 manager、日志或存储；cleanup 另行要求 exact invocation、pidfd 退出、populated=0、unit 终止且无 manager job。UNKNOWN 不作为 STOPPED。

guest/stop_guard.c 为独立本机可执行 guardian 源码，编译但未运行。未来由可信 root broker 显式传入专用 heartbeat pipe 和已绑定 kill FD，验证 FIFO/cgroup2/固定内核对象后持有；EOF、错误、超过 3 秒无新 heartbeat、父进程退出或 120 秒 development idle 总期限触发固定停止写入。期限是开发 idle 场景提案，不覆盖正式运行、不中和原 5 秒 suspend/45 秒 gap 判据，也不是实时保证。guardian SIGKILL/内核挂起仍需独立 Windows VM 控制通路兜底；C 源码不证明这个整链已实现。

尚需完整 broker 状态序列化、一次启动许可、创建与停止竞争处理、guardian 生命周期绑定、manager 事务、guest/host 心跳、受保护持久化与外部 anchor。不能拿当前两个原语直接接正式 launcher。

## 主机采集与计量

新只读 metadata 发现 12 个 Hyper-V 性能类和 27 个相关 counter sets，包括 logical/root/guest VP；没有采样计数器，也没有启动 ETW。metadata 存在不证明读取权限或 partition 到固定 QEMU 的归属。

拟用独立 system-logger ETW 会话采集 process/thread lifetime、CSwitch 和 loss，同时使用 hypervisor accounting 校核跨 partition CPU。仅 process snapshot 或 PID 名称不满足 I2。非管理员系统 trace 需要 profile privilege 及 session/provider ACL 的明确授权，先查询原值，精确添加本服务 SID 权限，回滚仅撤销本次添加且原值未被并发改动的项。不能全局替换提供者 DACL。

CPU 去重须在真实负载对照中确定：guest vCPU 时间、QEMU 模拟开销、Windows root 活动和其他 partition 各计一次。不可把 qemu/vmmem 名称排除，不可把无法关联的 partition 或 PPL 活动算作零。未测、丢失、身份歧义、时间倒退或证据落后均 BLOCKED。当前没有受支持的“完整覆盖”生产签名实现。

## 运行时与供给

Ubuntu 镜像仅下载并校验，未 boot/mount/install。Canonical UEC 公钥指纹从官方说明独立核对；SHA256SUMS detached signature 和镜像摘要匹配。原 CPython 官方 3.11.15 tar.xz 重新核验；新配置前缀 /opt/rebaseguard-p309/cpython-3.11.15，以 DESTDIR 在原 Ubuntu 非 root ext4 工作目录构建归档。此归档是新的候选，不把历史二进制摘要冒充新部署摘要。未来需要只读绑定复制、全树清单及 guest 实际 ELF/glibc/父目录保护证据；二进制 ABI 不兼容则停止，不替换 Python 版本。构建不覆盖系统 Python；实际自动更新的漂移见下一段。

首次新构建期间，原 Ubuntu 的既有 unattended-upgrade 将系统 Python 3.12.3-1ubuntu0.13 更新到 0.17，保留摘要校验失败，首次产物不入部署包。第二次独立目录构建前后 dpkg 清单和系统 Python 摘要一致；没有修改更新策略。旧私有解释器的二进制摘要仍为 b21d680e…cf194，但共享系统库发生过更新，不能声称整个旧运行时依赖均未变。

新增 Windows ETW/counter 能力入口已构建并做纯 ABI 检查，尚未执行；具体有限批次、必要权限、验收和回滚见 I2_FEASIBILITY_REVIEW.md。它没有生产签名功能，也不会把 raw capture 自动变成 coverage_complete。完成此依赖的真实调查后继续完整控制包，全部未解决项和顺序见 DEPENDENCIES_AND_ORDER.md。

## 完整生产部署包才可请求的内容

1. 固定并审阅上述来源、剩余控制层实现、SID/UID/ACL/API 掩码与部署期碰撞拒绝。
2. 给出新 VM、镜像/数据/seed 路径和容量，资源前置条件、完整命令/网络面、保护路径及剩余硬盘/内存预算。不承诺 128 MiB 探针证明 8 GB 正式可用内存。
3. 给出账户/服务/key/ETW/权限/单位安装清单和逐项原值快照、一次启动许可/记录、故障时撤销许可→精确停止→证明清理→封存的回滚脚本。未知时保留控制，不猜 PID、不销毁 VM/历史。
4. 固定一批覆盖 I1–I6 的 target-free 真实验收及每项通过/失败/未知标准；有限测试与厂商边界说明结合，不扩大结论；无自动 retry。
5. 提交本机 AF-2/launcher/计量替代的精确修订供独立审阅及 owner 接受。原 r2 不变；没有 IMDS 不得伪造 AWS。完整 8a/8b、8c、worker-tier、pre-freeze、O1–O10 和后续正式授权仍各自生效。

4 CPU、8 decimal GB、每根 40 decimal GB、60 秒、0.05/0.5/1.0 core、5 秒 suspend、45 秒 gap 及 exactly-once/禁止 retry 全部保留。

来源：QEMU 11.1.2 security.rst/whpx.rst；Microsoft System Providers、Configuring and Starting a SystemTraceProvider Session、WHvGetVirtualProcessorCounters；Canonical Verify an image checksum。来源 URL 与下载摘要随准备记录保存。
