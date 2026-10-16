# I2 原生能力核验 V2：执行前修复包

状态：未批准、未执行。仅源码、构建、结构布局和 PowerShell 语法检查。正式准入 BLOCKED，I1–I7 OPEN。本包不关闭原审阅结果；原包和全部证据保留。

## 本批修复和独立审阅范围

基线 `e72da101e036e4bd96c0bb230b89be91058c8857`。原独立 scan `2b0afe33-d593-4325-95db-5a2313e50159` 已封存。原脚本实际存在 AU Modify，提升后自校验不足；原固定 Name/GUID 清理可误认会话；controller 后代不在最终清理判据内。这些不是可以忽略的审阅备注。

1. 唯一 ETW 创建者改为独立 guard。只有 StartTrace 成功返回的非零 handle 可进入 Stop，使用每次新 GUID；不提供按名称停止或跨进程采用会话的入口。创建失败无 receipt、无 Stop。controller 改为只读 sampler，无法创建/停止会话。guard 内另有 75 秒计时线程，避免 sampler 消失或 guard 主线程日志阻塞取消停止。Stop 先于最终日志。若 guard 自身突然死亡、native API 卡住或创建/receipt 窗口中断，不能保证清理，只报 UNKNOWN，不接管同名会话。Windows 不是硬实时系统。
2. 三个固定 200 ms fixture 各以 `PROC_THREAD_ATTRIBUTE_JOB_LIST` 原子创建为 suspended + detached，无句柄继承。独占无名 Job 限一个成员、进程和 Job 各 256 MiB、KILL_ON_JOB_CLOSE；拒绝限制回读差异，入 Job 后再 resume。保留进程句柄与创建时间；退出必须为 0 且 Job active=0、total=1。超时只停止该 Job。guard 消失时 Job 句柄关闭；是否真的完成仍需外部/本次证据，不能仅从标志推断成功。harness 成功条件要求三个真实记录均满足，不再只数直接 helper。
3. 提升入口是可信工具调用中固定的 `-EncodedCommand` 字节，不是可写目录中的脚本路径。先读不可信脚本/批准文件字节并比对可信常量中的摘要，再执行内存中同一份 ScriptBlock。二进制摘要直接包含在已绑定脚本内，无可替换 adjacent pins。保存批准记录也用同一份已校验字节。
4. 提升进程不在 AU 可写的 D: 层级创建/写入任何目录。仅在 Windows 管理的固定 `C:\ProgramData` 下创建一个新目录；使用 .NET Framework 创建时安全描述符，随后严格核对 owner=Administrators、受保护 DACL 和无 reparse，再写文件。父路径依赖系统管理的不可替换边界；已有本机 ProgramData ACL 为 SYSTEM/Administrators full，Users read/create-directory，不允许普通用户改写既有其他所有者目录。若该前提发生变化必须拒绝，不扩展 ACL。执行完成后普通用户只读复制 C: 证据到 D:，校验全部摘要；D: 副本不是后续管理员执行的可信来源。
5. 新语法记录使用绝对 `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`，真实版本 5.1.26100.9444。旧 v1 的 `windows-powershell-51-parse.json` 实际写着 7.6.5；文件名错误，历史原文件不改。旧 V4 EXPORT_MANIFEST 的部分 canonical 文件不在 v1 Git 包内；完整来源仍为已封存 scan，修复包附完整副本。

## 待批准的具体动作

- 一次 UAC/admin Windows PowerShell 5.1 入口，`-NoProfile -NonInteractive -EncodedCommand`。启动前清空该新进程的环境，仅保留固定 Windows/system32、当前用户身份所需值，不继承 CLR profiler、PS module/user startup 变量；不改系统/用户全局环境。工具调用中的固定命令为信任起点，不从可写文件读取后直接提升执行。
- 创建且仅创建 `C:\ProgramData\ReBaseGuardP309-I2-Feasibility-v2`，存在即拒绝。SYSTEM、Administrators 可写，当前 owner SID 只读/执行；不改父目录 ACL。不创建服务/任务/账户/密钥，不安装软件、不改 Windows 策略或 Ubuntu。
- 二进制已由现有 Framework csc 构建。将已验证字节写入该受保护目录。正常 owner 在结束后将证据复制至新 `D:\ReBaseGuard-309\records\p309-i2-native-capture-v2`；保留原始 ETL 本地，不公开推送主机进程/路径。
- 固定名称 `ReBaseGuard-P309-I2-Feasibility-v2` 先只读查询，存在/未知则不启动。一次 StartTrace，无重试，GUID 每次新建。仅 PROCESS/THREAD/IMAGE_LOAD/CSWITCH/DPC/INTERRUPT，最多 256 MiB 顺序 ETL、64 KiB × 64–256 buffers；不采堆栈、网络/文件内容或 sampled profile。
- 60 秒原始 Hyper-V logical/root VP/VP counter 窗口，每秒一次。每类最多 256 实例，counter 日志最多 16 MiB。读取失败不填零。窗口第 3/6/9 秒的三个上述固定子进程合计约 0.6 CPU 秒；不是 P309 或正式演练。
- guard 临时启用自己 token 中已分配的 SeSystemProfilePrivilege 并恢复；无权限则拒绝，不更改 LSA/策略。75 秒停止请求限期，native 卡住/guard 崩溃只能 UNKNOWN；不自动查询并停止一个仅名称匹配的会话。sampler 超时只用保留句柄停止 sampler；不杀可能仍有 native 调用在途的 guard。
- 最终必须证明 ETW 名称已不存在、guard/sampler/query helper 均退出、三个 fixture Job 都空、无最终 loss。仍仅得出 `CAPTURE_COMPLETED_REQUIRES_OFFLINE_ANALYSIS`，coverage_complete=false。
- 允许在保存的 ETL 上用现有系统 tracerpt 离线解码；验证实际字段、三个短命进程 PID/创建时间/线程调度、时间域和 loss。离线解码不触发新采集。任何失败保存现场，不自动重试此真实批次。

## 回滚和仍未证明的事实

正常结束由创建者 Stop 已持有会话，Job 自有句柄终止/清空 fixture，token 随进程退出恢复。保留 C: 受保护证据与 D: 副本，不删证据；无全局配置需要恢复。若创建者突然丢失且没有成功停止证明，标 UNKNOWN 并集中报告必要人工恢复事项，不自行扩大范围、重启或停止其他 logger。

这一步不证明 PPL/所有瞬时线程覆盖、QEMU/guest/host CPU 去重或归属、独立安全服务身份、完整生产 broker/unit/密钥隔离、长期无丢失、恢复安全或正式路线接受。必须依据真实结果决定后续完整包；生产方案仍未完成，不能将本次原生能力实验称为全任务完成。

原阈值、freeze/grant/qualification/target、exactly-once 均不改。原 Ubuntu、系统 Python、备份、旧分支、历史记录和受保护源文件保留。
