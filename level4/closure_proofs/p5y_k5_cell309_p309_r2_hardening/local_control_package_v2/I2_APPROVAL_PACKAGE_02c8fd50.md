# P309 本机 I2 一次性采集核验：具体批准包

源码候选：`02c8fd500e643bfffd553ac0aa78c54670e2099f`，分支 `codex/p309-local-control-package-dev-20261016`。此文件是执行前说明，不是授权；独立复审已完成，0 项新漏洞，完整结果见追加记录。P309 全任务尚未完成，I1–I7 OPEN，准入 BLOCKED。

## 为什么现在需要这一步

原生 Windows 采集器能否实际取得必须的调度、生命周期和 Hyper-V 计数器，是余下实现的关键输入。已存在的类别名称、模拟数据、编译成功或小型暂停 VM 结果都不能回答这个问题。此次只取得这项真实输入，随后继续完成生产控制实现、完整部署包、真实验证和正式审阅，不把本核验当作 P309 运行完成。

## 请求批准的整批范围

1. 以普通用户运行精确摘要绑定的外层启动器，短时持有本包二进制及其祖先目录句柄以防替换；请求一次 UAC 启动本机构建的未签名原生入口。入口用固定系统 DLL 和显式白名单环境启动 Windows PowerShell 5.1。不会设置全局环境或策略。
2. 新建 `C:\ProgramData\ReBaseGuardP309-I2-Feasibility-v2`，已有即拒绝；仅 SYSTEM、Administrators 可写，当前用户只读/执行。只在这个目录写管理员证据。不安装服务、账户、密钥、任务或 guest；不改现有父 ACL、Windows power/update/LSA/provider 策略或原 Ubuntu。
3. 只创建一次 ETW 会话，采集一个 60 秒窗口；只收集进程、线程、模块、上下文切换、DPC、interrupt 和原始 Hyper-V 运行时间计数器。ETL 上限 256 MiB，计数器日志上限 16 MiB。不采网络/文件内容、堆栈或 sampled profile。
4. 窗口内只启动三个固定 200 ms CPU 子进程，均为本包二进制、原子加入各自私有 Job，限制一个成员和 256 MiB，并记录退出/空 Job。它们不是 P309、qualification、target 或正式 worker 演练。
5. 唯一创建者持有真实会话 handle；独立于采样器的 75 秒计时线程请求停止。错误后不重试采集，不按同名会话或任意 PID 清理。仅临时启用创建者进程 token 已分配的 profile privilege；未分配即拒绝，不更改权限策略。
6. 核验会话消失、所有 helper 退出、三个 Job 为空、最终无丢失。完成后由普通用户把证据复制到新 `D:\ReBaseGuard-309\records\p309-i2-native-capture-v2` 并核验摘要。只在已有 ETL 上使用系统 tracerpt 离线解码；原始 ETL 留在本地受保护目录，普通推送只发布筛选后的结论和源绑定。

## 判据与回滚

只有全部清理和原生返回码可解释、无最终 loss，才标记“采集完成，仍待离线分析”。它不关闭 I2，不证明 PPL 全覆盖、VM CPU 归属/去重、生产服务权限、签名与完整停止恢复。

若 API 卡住、guard 自身突然丢失、证据不可写或不能证明清理，只能 FAILED/UNKNOWN；保留现场，不扩大权限、不终止无关进程、不自动再跑。正常结束停止自有会话、清空自有 Job；临时 token privilege 随进程退出消失。新目录和文件封存，不删除证据。没有全局配置、服务或账户需要回滚。

## 精确来源

| 对象 | SHA-256 |
|---|---|
| 普通用户 `Launch-Approved.ps1` | `2da80a3b3b4b666b9e40c145bad82106084b22025e03f6ea20203ff2eed47563` |
| 原生 `NativeEntry.exe` | `23cfc53c4b501f91f647b4c73b75ff99e53c305c1cb37bd2fc7ec32a2187881e` |
| PowerShell 模板 | `a8dcefd041116b248fefae96917895a70729a0a28df41c7bbcb4d40b64967a43` |
| 采集 harness | `9c5702c030200afbb63e8d5dfde42637f222e6b2b370e6bf9dda59ff060cd86c` |
| `EtwCapture-v2.exe` | `f3641470ee82d201063910480c9ecad67d78c45f2b4c65907c6331e65c0e8ca4` |

源目录：`D:\ReBaseGuard-309\workspace\p309-local-vm-diagnostic-dev-20261016\level4\closure_proofs\p5y_k5_cell309_p309_r2_hardening\local_control_package_v2`。

完整权限、失败语义和来源在该目录 `REPAIR_AND_APPROVAL_SCOPE.md`、`FINAL_BINDINGS.json`。所有旧版本、失败构建、审阅发现、原 Ubuntu、私有 Python、迁移记录和备份保留。新包的实际 ETW/UAC/fixture 次数均为 0。

## 已做准备与证据边界

- V4 已批准的两个小型暂停 VM 验证已完成并单独保留；未重跑。
- 独立审阅发现的可写提升入口、会话误认、fixture 清理和失败记录问题已落实源码修复并完成独立技术复审；源码审阅不是部署或正式准入授权。
- 新 guest CPython 3.11.15 staging build 完成，记录源码、编译命令、文件和 ELF/动态库摘要。首轮遇到 Ubuntu 原有 unattended-upgrade 导致系统 Python 变动，弃用于部署且保留证据；第二轮前后清单稳定。未将 staging 安装到 guest，未改系统 Python 链接或安装目标。
- 已核验 Ubuntu 镜像签名和 19 个离线库包；包文件已下载，尚未安装。manifest 推导的依赖计划不等于实际 guest dpkg 状态。
- 7 项 guest 原语单元检查、10 项 native 编码/摘要检查以及真实 WinPS 5.1 语法检查，仅支持对应代码性质；不计为主机准入或真实采集证据。

此次需要确认的原因来自用户接管请求第 3 条：真实跟踪/验证前须先准备具体包并集中确认。先前 V4 的批准只覆盖两项暂停 VM，不包含 ETW 或这三个短时子进程。

实际执行来源为新建的私有目录 C:\Users\Lenovo\P309-I2-build-20261016-v4。构建时固定输入摘要，持续持有只读共享源文件和对象句柄；新目录仅本机所有者、SYSTEM、Administrators 可写。D: 上同名产物仅作归档，不能替代私有入口。既有目录 ACL 未修改。该修正的独立复审编号为 7db198e0-7ca1-43da-b2e1-dea6a6074497，已封存：覆盖全部 41 个变更文件，构建替换问题在本修订技术修复有效；0 项新漏洞。此结论不授予执行或正式准入。
