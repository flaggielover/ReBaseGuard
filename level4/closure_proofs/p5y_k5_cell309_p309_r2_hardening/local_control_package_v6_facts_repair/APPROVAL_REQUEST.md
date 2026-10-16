# 待确认：集中修复后的单次管理员只读基线

这是一份具体执行范围，不是实际人员批准。独立源码和包装绑定复核均已通过；执行前仍须取得新的明确回复。

执行包：`e9af7e0b2a822e518164f8c547adb8d9311d7dfd`。
运行源码：`e211d4946515d506696d56f03ff2651eece10400`。
最终调用器 `Invoke-Once.bound.ps1` SHA-256：`5b547021ef7cc97a95bb10b1a1579fa52568d9d8df79abae0a172bf6bc6f2a70`。
Native SHA-256：`44565e9f0d6fcfd8eeff0c3ccaa881ef9726b7eccf26384aee60138c1093078c`。
Core SHA-256：`1ea61f4b3f905c5644ddec1c2fa852eb281aed9a3c5e9130ccc73587e0c47484`。
Harness SHA-256：`9ff4db26b765469269c78567200d39d65b5a984163d3d3db91bf47445e0b211d`。
其余绑定见包内 `FINAL_BINDINGS.json`。

## 前次实际结果和本次修正

前次单次UAC已实际执行，13份保护原件及D副本已保留。程序退出0，但ETW读取代码只接受了错误的长度返回码，睡眠项没有保存可靠的退出码/输出，服务枚举也不能证明名字不存在。LSA直接权利未取得；Windows还报告CBS待重启标志。这些均未包装成通过，未自动重试。

本包集中修正上述读取问题和逐阶段结果/清理记录。Windows PowerShell5.1实际验证36个注入核心案例（191条断言）及11个总结/部分结果案例通过。它们只证明包装代码的有限行为，没有调用真实ETW/SCM/LSA/powercfg，也不代替主机或正式准入证据。

## 批准范围

一次普通owner调用，一次UAC；使用已构建的私有入口和固定Windows PowerShell5.1，对原10组事实的28个固定对象逐项只读查询：ETW权限、拟用SID的已有LSA直接权利、ETW registry值、三个精确服务名字、父目录ACL、C/D空间和三个拟用目录冲突、当前睡眠方案、选定更新/重启键、DeviceGuard字段及两个固定任务路径的元数据。

新建 `C:\ProgramData\ReBaseGuardP309-FactsRepair-v1`，admin所有且仅admin/SYSTEM写入，owner只读；保存实际批准字节和逐项证据。随后逐字节归档到D records、离线解释并普通推送最小化记录。保留v5全部原件、原Ubuntu、Python、历史与备份。

不安装软件，不创建账户、服务、密钥、endpoint或unit，不授予权限，不改既有ACL/registry/电源/更新策略，不触发重启，不启动ETW、host sampling、VM、QEMU、隔离演练或P309。

powercfg使用固定只读参数，总预算20秒；超时/异常时，仅对持有句柄的本次powercfg请求终止，再等最多2秒。每流最多128KiB原字节及64Ki字符，保留编码、摘要和截断状态；超时且流仍活动时，快照/计数只是不完整前缀。未确认退出为UNKNOWN，不能声称已清理后代。Native等待240秒，外层260秒；系统调用无法硬抢占，不能承诺硬完成期限。

单次执行，固定只读项逐项保存；失败/未知不补跑，保留现场，不进入后续安装或运行。回滚为封存本次新增构建与证据；没有既有系统配置变更需要逆转，不删除旧数据或猜测性恢复ACL/registry。

## 为什么仍需确认

根据你的接管要求第3条，实际提权前必须批准具体包。前次授权明确限单次，已使用；本包改变源码、入口摘要和证据目录，并增加明确的自身powercfg超时清理，因此需要新的具体批准。管理员权限本身不能代替这次范围确认。

新的批准scope为 `P309_SINGLE_ELEVATED_READONLY_FACTS_REPAIR_V1`，count=1。只有实际回复到达后才创建 `D:\ReBaseGuard-309\records\p309-facts-repair-v1-human-approval.json`。

**I1–I7仍OPEN；正式准入BLOCKED。此次批准不授予生产部署、freeze、grant、qualification或target权限。**
