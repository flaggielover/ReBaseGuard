# V3 修正包：保留旧运行时、完整预检、单次诊断

任务未完成，正式准入 BLOCKED；I1–I7 均保留。

## 已发生的事实

V1 的真实 deadline 探针在五秒时记录 Job active=2，违反期望 1；Job 后续 active=0、精确子进程句柄退出。批次 FAIL，guard-exit 未运行。

V2 获批准后，在 LockRuntime 检查中因额外文件而拒绝。拒绝发生在 CreateJobObject/CreateProcess 之前；没有创建 V2 QEMU/VM。源码及 stderr 支持这个结论。harness 的 UNKNOWN 表示没有取得子进程观察，不应误读为已知有 VM 遗留。没有自动重试。

只读复核确认：原 222 个绑定文件均未变；五个额外缓存 .db 创建于 V1 的 00:20:10 UTC，位于字面量 `%SystemDrive%/ProgramData/...` 下。旧环境缺少 SystemDrive 且工作目录为运行时 bin，这与路径展开异常相符，仍非写入者归因证明，也不能解释 Job 的第二个计数。缓存文件没有删除、移动或加入可信代码清单。

协调者在 V2 准备时漏做运行时额外文件检查。这次明确修复该准备缺陷，不以反复运行消耗真实探针次数。

## 已完成的修正和验证

- `RuntimePreflight.ps1` 是只读模块：核验清单摘要、全部条目 SHA-256、路径边界/重复项、reparse、缺失与额外文件。默认任何额外文件拒绝。唯一的 `AllowSourceExtras` 仅用于从旧目录读取明确选择的 222 个源文件，不能用于启动新运行时。
- 新 guard 固定 `candidate-v3`；运行时文件集仍为原来的 222 个，清单摘要不变。保留 V2 原子 Job 关联、限制读回、成员诊断和独立停止逻辑。
- 明确设置 SystemDrive、SystemRoot/windir。把 CWD、TEMP/TMP、USERPROFILE、APPDATA、LOCALAPPDATA、ProgramData 指向本次证据目录内的 child-scratch 子目录；Windows 系统目录保持真实值。环境变量设置不能保证所有 Windows 组件绝不访问自己的系统缓存，也不是安全隔离证据。不修改系统环境变量、注册表或系统配置。
- 启动脚本在创建一次性证据目录、启动 guard 之前，对新运行时做完整只读预检；guard 内仍再次核验并持有文件句柄。
- 实际通过：27 项 C# 纯环境/ABI/解析检查，7 项合成文件预检回归（额外缓存、摘要、重复、越界、缺失等），4 项授权拒绝检查；5 个 PowerShell 文件语法检查。均未创建 VM/Job，不等于原生验证。
- 实际只读计划确认旧目录可选的 222 文件共 459,552,711 字节，额外 5 文件保留；严格启动预检确实拒绝该旧目录。新 candidate-v3 尚不存在，D: 当前空间足够。完整计划保存于 actual-source-copy-plan.json。

## 本次集中请求的精确变更

1. 用 `Stage-ApprovedRuntime.ps1` 将已逐一核验的 222 个文件复制到全新的 `D:\ReBaseGuard-309\local-vm-feasibility\candidate-v3`，建立相同相对路径清单 `candidate-v3.sha256`。约 459.6 MB。仅复制固定清单内文件；不下载、不执行安装器/hooks，不复制额外缓存。旧 candidate-v1、缓存及全部历史证据完全保留。目标已存在则拒绝，不覆盖或清理。
2. 安装后完整核验新目录，使用 `OwnedVmDiagnostic-v3.exe` 与新 harness **只执行一次 deadline 诊断**。仍是普通非提升用户、暂停 q35/WHPX、4 vCPU、128 MiB、无磁盘/网络/显示/串口/monitor，不启动 guest OS/P309。不运行 guard-exit。
3. Job 限制仍为 1 个 active process、768 MiB 进程/Job commit、无 breakaway、KILL_ON_JOB_CLOSE。创建时原子关联；记录有效限制和四个阶段的有界成员快照。计数异常取证后立即请求停止；独立线程保留 15 秒停止期限，记录实际 tick，不宣称 Windows 硬实时保证。
4. 仅通过新建私有 Job 和已绑定进程句柄停止/观察，不按名称结束进程。单次证据目录固定为 `D:\ReBaseGuard-309\records\p309-local-vm-diagnostic-v3-run-20261016-01`，存在则拒绝。任何失败保留日志，不自动重试、不改上限、不进入第二项或生产阶段。

源文件、编译器、guard/harness/staging/preflight SHA-256 在 BINDINGS.json；新批准蓝图默认全部未授权，必须填写本聊天真实批准引用。运行时清单仍为 `48abd49ab20d074a4dea88306418a6c6c3e4374b81e7e1eb21a10929d2159238`。

## 验收与回滚

诊断应留下完整限制读回、Job 计数与成员信息、停止时间、精确子进程退出及清理结果。未知/不全保留为未知；计数 2 仍不满足原验收，不能自动视为系统进程豁免。即使新运行记录为 1，也不能独自证明旧计数来源。本次不产出正式准入 PASS。

失败时立即停止后续步骤，保留新目录、临时目录与全部日志；不删除任何旧目录，不回滚旧文件，不重新覆盖部分安装。当前没有新增账户、服务、密钥、端点、WHP/电源/更新/安全策略变更，不需要 UAC 或重启。新运行时可封存为未准入候选；WHP 仅按 V1 既有条件回滚，不自动禁用。清理 UNKNOWN 时不得声称 STOPPED 或启动另一实例。

这是协调者自审，未获得独立安全审阅。实际 guest、完整采集、生产身份、公钥注册、完整运行时、broker、持久化/恢复及 AF-2 等工作仍待平台问题明确后推进，不能拿本次单元结果关闭 I1–I7。

## 为什么需要新的确认

用户总任务第 3 条要求安装和实际验证先确认。此次新增运行时目录并改变 guard/harness 源码绑定；V2 许可不应被悄悄扩展成任意代码或无限次重试。所需源码修正、构建、回归、只读复制计划均已完成后才请求此次确认。

厂商 API 依据及原子 Job 设计参见保留的 diagnostic_v2/REVIEW_AND_APPROVAL.md；本修订不扩大这些来源支持的边界。
