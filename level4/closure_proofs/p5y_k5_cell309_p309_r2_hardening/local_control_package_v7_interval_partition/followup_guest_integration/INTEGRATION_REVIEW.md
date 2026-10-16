# Guest broker 接通核对（仅源码准备，2026-10-16）

当前有可复用的 Linux 停止原语，没有已经接通的 guest broker / guardian / systemd 安装包。可实施的下一个完整交付物应包含固定 idle 事务、真实认证通道、独立停止及安装回滚；不能把 D2 fixture 或内存对象接到执行器后称为生产实现。本记录未执行任何 guest、VM、服务、主机查询或测试。原文件未修改，来源摘要见 SOURCE_BINDINGS.json。I1–I7 OPEN，admission BLOCKED。

## 现有代码的准确能力

| 已读入口 | 已实现的真实 API / 逻辑 | 尚不具备的事实 |
|---|---|---|
| v1 guest/owned_instance.py:48,81,142 | 固定 systemctl show；逐祖先 openat/O_NOFOLLOW；本地 boot_id、/proc/PID/stat 和 cgroup 核对；pidfd_open；持有 cgroup 目录及 cgroup.kill FD，绑定前后检查 InvocationID/PID/start_ticks | 没有 StartUnit/StartTransientUnit、启动许可、job 回执或生成这些权威字段的事务。StartedIdentity 是 caller 构造的 dataclass，不是 OS 认证类型 |
| owned_instance.py:191 | 先 latch，再向已经持有的 killfd 写 1；不等日志、manager、存储 | stop 请求不等于完成；构造失败不会取得所有权，也不能按名字补杀 |
| owned_instance.py:210 | pidfd 退出、cgroup populated/frozen、固定 manager invocation/state/job 的保守组合；未知不报 stopped | 没有 guardian reap/FD 完成证据；没有持久化 fence/外部 anchor；没有事务层证明无迟到 start。pidfd readable 本身不证明子进程已被回收 |
| v1 guest/stop_guard.c | 原生独立进程；验证 FIFO/cgroup2/固定 kill 路径；poll、CLOCK_BOOTTIME、PDEATHSIG；EOF/异常/3 秒 lease/120 秒 idle 总期限触发持有 FD 的 kill | 没有 READY 回执，只有两个输入 FD；没有安装/实际运行证据。SIGKILL、同 cgroup 整体清除、guest/kernel 停顿不由它自己解决 |
| D2 control_wire | 16384 字节上限、严格 JSON、拒绝重复/额外字段；仅 status/stop 与精确 G | 不是 socket server、peer credential、权限或 start API |
| D2 broker/session/chain/memory_dispatch | 不可逆 latch、stale-G 先于 dedup、有限预算、纯内存状态和假时间/签名验证测试模型 | SyntheticPeer、FixtureFacts、_fixture_prepare/_fixture_event/_SyntheticCleanup、_fixture_session、MemoryDispatch 均不是生产 authority。Session 明确只接 P309_D2_SYNTHETIC_OBSERVER_FACTS/1，不能改 diagnostic 布尔值升级 |
| accepted r2 p309_launch.py | 非 root unit user、自身 UID 一致、durability/exclusion/isolation、无已有 p309-r2-*、固定 mode，单次 systemd-run --no-block，无 retry | 与 root broker 的固定 idle unit 不等价；它记录的是提交状态，不是本新 broker 的 generation/guardian 证明 |
| accepted r2 p309_driver.py:1230,1236,1525 | _assert_execute_context 后 CAS 创建 marker ref；pending ref 保存内存产生的证据；marker 前正式 gate/control，之后只执行一次 | broker 许可不是 grant；broker 不得代建/删除 marker/pending、绕过 guard、重新启动已消费的正式 run |

## 新模块与固定接口

建议新增独立 guest_control_v1 包，旧 v1/D2/r2 都保留历史字节。原生 broker 使用 libsystemd sd-bus，不把 manager 操作包成任意 shell。若选择 Python 控制层，也必须另行绑定完整 3.11.15 runtime 与 native adapter；不能用未审 ctypes 声明替代 ABI 核验。

1. activation_peer.c：sd_listen_fds_with_names + fstat/getsockopt/getsockname 检查唯一预期 listener；accept4(SOCK_CLOEXEC|SOCK_NONBLOCK) 后 SO_PEERCRED。固定 UID + 本地 peer PID/start/boot + 当前 monitor InvocationID 验证；重新确认后才构造内部 PeerBinding。H3/H4 拒绝 SCM_RIGHTS、MSG_CTRUNC/MSG_TRUNC、超大/多帧、未知字段；协议可用固定长度前缀 stream，边界需独立定稿。客户端不假设 socket activation listener 的 SO_PEERCRED 是最终 monitor UID。
2. broker_wire.c：实现现有 control_wire 同等 status/stop schema 和 conformance vectors；任何 start/arm/reset/command/path/UID/PID/property/environment 字段拒绝。不能用网络来的对象构造 StartedIdentity。真实 monitor heartbeat/loss 为内部独立通道，不把 H4 status 当续租。
3. lifecycle_store.c：持有 serial lifecycle lock，内部类型分别为 UnusedPermit、ConsumedStartIntent、OwnedInvocation、TerminalReceipt；没有把 model snapshot 转为 OwnedInvocation 的入口。启动前先持久化消费许可及 start-intent；临时文件 O_EXCL/O_NOFOLLOW、fsync 文件、原子发布、fsync 目录。root-only state 下保存版本/序列/G/boot/epoch/code/runtime/policy/permit/job/monitor 身份及哈希链。状态存储失败禁止 start；stop latch 的即时停止先于任何持久化等待。
4. manager_start.c：仅固定 p309-dev-owned-check.service；sd_bus 的 Manager.Subscribe 与 JobRemoved match 先于 StartTransientUnit(name,"fail",固定属性,无 aux)，保存 reply job path/ID；核验 JobRemoved 的 job/unit/result，再读 Unit+Service properties。同名 load/运行/queued job 均拒绝，不 adopt/replace；失去 reply 不是重试理由。STARTING 后任何 stop 永久禁止 gate release。完成晚到只进入 cleanup/UNKNOWN，不回 RUNNING。调用 GetUnit/GetAll/RefUnit 可保持 manager 引用，但引用不防止 cgroup 清除，也不保证 InvocationID 字段终态留存；实际版本必须验收，缺失仍 UNKNOWN。
5. fixed_gate.c：unit ExecStart 是固定原生 gate，启动后不运行 payload，带短的本地 BOOTTIME 等待期限。通过 root-owned /run/rebaseguard-p309/launch-gate.sock 与 broker 完成 challenge；broker用内核peer PID和成功启动事务的 MainPID/InvocationID/cgroup相互验证。只读固定 READY/RELEASE/CANCEL frame；不是允许 runner提交command的端点。只有 guardian 已READY、当前G未stop、state/外部anchor已提交才发送 RELEASE。gate直接 execve 固定 idle binary，不fork，保持 PID/start identity。超时/EOF/坏frame自行退出，绝不重连复活。
6. owned_instance_native.c：保留现有逐祖先/内核对象/pidfd思路，新增 cgroup.type=domain、fstatfs cgroup2、固定 unit policy readback。只从成功 start 事务创建 binding；固定路径不等于已经拥有。stop 只写 retained killfd；不在停止热点做 manager RPC、日志或 fd 路径重开。不能将 native/Python 两份可变状态当成两份权威。
7. stop_guard_v2.c：现有 guardian 增加可信启动私有 READY 状态管道（额外FD），所有对象/计时器/parent-death设置成功后才回 READY；失败必须明确，Popen/exec成功不能替代READY。内部 channel 可传 FD，H3/H4绝不能。broker关多余写端，确认worker/relay均未继承。heartbeat只由已经验证当前G安全状态的循环产生；单独无条件定时发送线程会掩盖 monitor/验证阻塞，禁止。guardian pidfd/退出码写入cleanup证据。
8. monitor_runtime.py：用固定私有 runtime 的隔离入口装载固定模块；新生产 Enrollment/Observation 类型及版本化 schema，真实随机 challenge、真实 BOOTTIME、被独立登记的公钥/host/guest/runtime/policy绑定。D2仅作为行为参考和负测试 oracle。验证可阻塞的线程不能拥有唯一停止期限；真实 timer/guardian续租与完成时间再次检查独立，保留60秒/5秒suspend/45秒gap原规则，不把模型105秒常量当任意生产宽限。
9. install_guest.py / rollback_guest.py / verify_guest.py：manifest限定对象与允许动作，apply、verify、rollback分离；verify不会隐式启动固定idle。输出区分未尝试、错误、未知和已证实，失败不自动重试。

## 必须先解决的启动与停止连接边界

- 固定 gate 的存在使未建立 guardian 的窗口只能等待，不能开始 worker；它自己的超时是启动丢回执时的退路，不是正常独立控制链。
- guardian 必须在 worker cgroup 外。若与 broker 同属一个会被 systemd KillMode=control-group 一起终止的 cgroup，broker unit 被强杀时它也会消失；不能声称覆盖该故障。实现可把新 guardian 作为单独、root-only 单元：由独立 root 控制服务经私有、认证且固定用途的 FD 交付通道提供已有 killfd 和 heartbeat endpoint，取得 READY；不得重新按名字打开 kill path。该新内部接口不扩展 H4。其父进程/服务关系一变，原 PDEATHSIG 语义也须相应重写和实测。
- 即使分离 guest unit，整个 guest 被挂起或 guardian 被SIGKILL仍需 Windows controller持有原VM Job/进程句柄的独立停止通路；此处仅定义依赖，不重复I2计量设计。
- 现有 stop_guard 写出 kill即退出，不是cleanup ACK。收尾需 manager已处理本次Exec退出（ExecMainCode/Status/ExitTimestamp等固定属性）、pidfd退出、原cgroup populated=0/frozen=0、无本事务未决job、gate关闭、guardian退出/回收与私有FD关闭。systemd是worker父进程，broker不能用对非子pidfd的waitid声称自己reap；需要manager完成证据。systemd GC或字段丢失不降级为STOPPED。
- 取消 job 只作用于本次保存的job，并不单独证明进程未启动；仍需 late completion/owned binding/empty结果。丢失所有权不可按名字杀替换unit，也不可删除旧状态再初始化UNARMED。
- root store无法抵抗guest磁盘快照整体回滚。Windows受保护的独立epoch/permit消费anchor必须先提交并收到确切ACK；无ACK不启动。guest重启、外部anchor倒退/不一致都RECOVERY_UNKNOWN，不恢复许可。trusted root/Windows owner/admin在既定信任根内，不增加无限同owner对抗。

## 固定路径和单位属性清单（候选新安装对象，不是已安装事实）

| 对象 | 固定路径/身份 | 明确属性与例外 |
|---|---|---|
| 代码 | /usr/local/libexec/rebaseguard-p309/；root:root0755目录，root只写版本化文件 | broker、guardian、gate、idle、relay；所有祖先验证；无runner可写加载源或环境。可执行文件0555，config0644/敏感state0600 |
| runtime | /opt/rebaseguard-p309/cpython-3.11.15 | 固定完整树/ELF/动态库清单；私有runtime不是系统python替换；新guest ABI尚未证明 |
| configuration | /etc/rebaseguard-p309/{manifest.json,enrollment.json,policy.json} | root:root0755父目录，文件0644；public pin只读，禁止client更新；UID及版本为安装时本地解析并封存，重用UID需重新登记 |
| state | /var/lib/rebaseguard-p309-control/ | root:root0700；permit/fences/journal/terminal独占新增；配额、空间与最长窗口预算写进manifest；日志不是唯一stop path |
| H3 | /run/rebaseguard-p309/monitor-ingress.sock | ingress.socket，Accept=no，SocketUser=root，SocketGroup=p309-relay，SocketMode=0660，DirectoryMode=0755，FileDescriptorName=ingress，Service=rebaseguard-p309-monitor.service |
| H4 | /run/rebaseguard-p309/control.sock | control.socket，同上但group=p309-monitor、descriptor=control、Service=rebaseguard-p309-control.service |
| gate | /run/rebaseguard-p309/launch-gate.sock | root监听；仅p309-runner连接，父root:root0755；必须核对本次gate PID/InvocationID，组权限本身不授权release |
| R/M/U | p309-relay / p309-monitor / p309-runner | locked系统账户，无交叉supplementary groups，无sudo/polkit manager grant；不使用可能重用的DynamicUser身份替代已登记UID |
| broker | rebaseguard-p309-control.service，User=root | 固定ExecStart、Restart=no、UMask=0077、NoNewPrivileges=yes、ProtectSystem=strict、只允许自身state写入、限制AF_UNIX；需要访问manager和固定cgroup.kill，不能盲设ProtectControlGroups=yes使其停止权限失效；不授M/R/U此例外 |
| monitor | rebaseguard-p309-monitor.service，User/Group=p309-monitor | Restart=no、NNP、CapabilityBoundingSet=空、ProtectSystem=strict、ProtectControlGroups=yes、PrivateTmp=yes、RestrictAddressFamilies=AF_UNIX；只自身诊断dir可写；无需worker写路径、manager权限或root |
| idle | p309-dev-owned-check.service，User/Group=p309-runner | Type=exec，ExecStart固定gate，Restart=no，KillMode=control-group，KillSignal=SIGKILL，SendSIGKILL=yes，TimeoutStopSec=10s，RuntimeMaxSec=120s，RuntimeRandomizedExtraSec=0，Delegate=no，NNP，空capability，ProtectSystem=strict，ProtectControlGroups=yes，PrivateDevices=yes，PrivateTmp=yes，RestrictAddressFamilies=AF_UNIX；不配置自动开机start或重启 |
| guardian | rebaseguard-p309-guardian.service，root专用 | 单独cgroup、固定binary、Restart=no；READY前不释放gate。具体FD交付原生接口与unit关系要作为实现部分审阅，不能把现有fork helper虚称已实现该unit |

MemoryMax/TasksMax/CPUWeight/IOWeight/MemorySwapMax/日志字节上限应固定成数值并在manifest/readback中核对；这里不捏造可用headroom或拿idle限额替代正式4CPU、8 decimal GB、每根40 decimal GB条件。正式unit仍须接受r2原资源属性与foreign-root隔离要求。禁止因为一个hardening选项妨碍所需API就删掉全部hardening；按每个实际调用的最小例外重新审阅。systemd properties兼容性以新guest实际版本为准，不能从构建主机推定。

H2需要单独的新VM transport合同：原wsl.exe启动元组对独立QEMU/WHPX guest不成立。可选一个固定virtio-serial端口名rebaseguard.p309.relay-v1、guest仅relay可读写设备、host侧仅controller/relay允许访问的受保护本地pipe；无guest host-directory挂载、QMP/HMP或通用command端点。具体QEMU构建是否支持该Windows后端、设备权限和端到端身份绑定还需源码/真实验收，尚不视为已选已可用实现。不能临时换成开放SSH/端口转发而称原H2已满足。

## 安装、真实验收和回滚必须交付的记录

安装器在批准范围内才运行：先检查image/runtime/source摘要、空间、kernel cgroup2/domain/cgroup.kill/pidfd/close_range、systemd版本、用户/组/全部unit与drop-in/alias/socket/路径碰撞。任何已存在的非本次对象拒绝，不覆盖或adopt。精确记录pre-state，root创建新父目录和账户，校验签名依赖包离线安装输入；写入固定文件后对owner/mode/hash/祖先再次核对，再daemon-reload，并readback实际生效properties。不要仅依据systemd-analyze verify成功认定安全属性已生效。安装成功只到UNARMED，没有start许可。

真实验收是一份另需批准的有限矩阵：R/U不能H4，伪M同UID不同instance拒绝；H4起动/任意参数拒绝；socket替换/错误listener/额外FD拒绝；固定idle单次permit；stop-before-dispatch与late-start；monitor退出/挂起、broker存储阻塞/退出、guardian退出、host relay丢失与VM暂停；descendant被同一retained cgroup.kill终止；退出/empty/manager job/guardian reap证据完整；超时/丢ACK/磁盘满/重启/旧G/旧permit重放均UNKNOWN或拒绝，不能retry。测试计划列明实际范围，不用synthetic PASS关闭I1/I3/I5/I6。

回滚顺序：撤销未来start及外部permit→不可逆stop latch→通过仍存活的owned-instance/guardian停止本次work→核对退出/empty/no-inflight/guardian完成→封存终态→停M/R与socket→停B/guardian→停止host控制/观察（其间保留最后独立stop路径）→只撤销本次安装且当前摘要/pre-state仍匹配的对象。未知时保留控制、state和失败证据并隔离guest；不删除marker/permit history、reset-failed后自动重试、猜PID、卸载现有Ubuntu、删除磁盘或自动unregister。单独保留原值与安装清单供未来受审人工恢复。

## 正式入口不可省略的衔接

开发idle permit只允许本固定idle。将来正式adapter必须同时消费有效外部授权并保留accepted r2自身的host gates、模式、unit user、冻结源与exactly-once marker。broker的OS-attempt fence发生在任何OS-start前，r2 marker仍在其accepted位置；两者不是可互换或彼此补偿的事务。任何启动不确定/正式marker已消费均不自动重试。root broker不得替runner运行资格/target代码，不得把原p309_launch的launcher_not_unit_user检查删掉以适应root。具体替代launcher/AF-2/VM transport和授权绑定仍是I7的明确修订，必须外部正式接受。AI工程复核不签发这个接受。

## 官方接口参考与证据局限

[systemd v255 Manager API](https://raw.githubusercontent.com/systemd/systemd/v255/man/org.freedesktop.systemd1.xml)定义StartTransientUnit/JobRemoved/Unit properties；提交成功与job完成分开记录。[service](https://raw.githubusercontent.com/systemd/systemd/v255/man/systemd.service.xml)、[exec](https://raw.githubusercontent.com/systemd/systemd/v255/man/systemd.exec.xml)、[socket](https://raw.githubusercontent.com/systemd/systemd/v255/man/systemd.socket.xml)用于核对上述属性语义；v255文档不是新guest版本证明。Type=notify允许扩展RuntimeMaxSec，因此idle候选采用Type=exec并不开放扩展消息。

[Linux cgroup v2](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)说明cgroup.kill覆盖后代且处理并发fork/migration；populated=0只说明没有live processes，不能单独证明zombie已reap；threaded cgroup的kill可能EOPNOTSUPP。这些是API依据，不是本机已经成功运行或配置的证据。
