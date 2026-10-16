# v6修复包：已构建，等待独立绑定复核与新批准

固定运行输入：`e211d4946515d506696d56f03ff2651eece10400`。源码manifest12项与Git原始blob逐字节一致；当前private目录普通用户构建成功。

Windows PowerShell5.1实际执行：36个核心注入案例、191条断言通过；11个生产总结/部分结果helper案例通过。合计47个案例，仅验证读取包装与失败语义，没有真实ETW/SCM/LSA/powercfg调用，没有UAC或VM，不能关闭I1–I7。未重跑历史suite。

原生入口为x64、仅静态kernel32 imports、干净环境启动固定WinPS。core、harness、template、native、launcher、caller分别绑定见FINAL_BINDINGS.json。私有目录内仅进行了文件/祖先pin只读预检。

最终调用器：`Invoke-Once.bound.ps1`，SHA256 `5b547021ef7cc97a95bb10b1a1579fa52568d9d8df79abae0a172bf6bc6f2a70`。只有实际人员新批准后才可执行；不能调用template或沿用v5授权。旧v5实际采集和UNKNOWN全部保留。

具体固定查询、逐项判据、进程预算/自身powercfg停止、无硬抢占保证、失败无重试及封存回滚见SCOPE_AND_CRITERIA.md。此时尚未收到v6人员执行批准。

完整本地构建归档：`D:\ReBaseGuard-309\records\p309-facts-repair-preparation-20261016-v2`；原ACL及二进制只留本地，Git最小化记录未包含PRIVATE原件或exe/obj。

**I1–I7 OPEN；正式准入BLOCKED；整体任务未完成。**
