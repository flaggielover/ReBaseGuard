# 待确认：单次管理员只读安装事实预检

源码、私有目录及单次调用器已完成准备和独立绑定复核。此文件是具体执行范围，**不是实际人员批准**。

执行包：`2fbb2b453611cf55790ba81f6557f791c7e23e0f`；源码输入：`28fd11c9c8398f5fbd85d4836970918a6ad5c711`。调用器为 `Invoke-Once-v3.ps1`，SHA-256 `cdab07b49f829dd9ca5c5462eedb7b7c35003cf182765fe2965cc827e5bb193f`。

原生入口 SHA-256 `469efadffe76e5a66bd6997cb215042f74f0030c3ced819e1c1e4c2eccc65816`；查询脚本 `4ea4e224a876f6a1c0d42144f8f5edf819172992329a7231bf2d6fca8e561054`；填充启动器 `9b89849c5e5636b219b29ad633f4dda43a6268bdd3a8858b4b0fc73ae9119d09`。全部绑定见 `FINAL_BINDINGS_V3.json`。

## 这次批准会执行什么

一次 UAC，以现有私有入口、固定 Windows PowerShell 5.1 读取以下事实：ETW权限、拟用服务SID的已有LSA权利、服务及目录冲突、目录ACL和空间，以及选定的睡眠、更新、DeviceGuard和维护任务元数据。

新建保护证据目录 `C:\ProgramData\ReBaseGuardP309-InstallationFacts-v1`，保存批准字节、逐项结果和摘要，随后核验复制到 `D:\ReBaseGuard-309\records` 并离线分析，普通推送最小化记录。

不创建服务、账户或密钥，不授予权限或修改策略，不启动ETW/采样/VM/QEMU或P309工作负载。只新增本次证据和进程内编译临时文件。现有 Ubuntu、系统Python、历史记录、备份及无关进程保留。

## 为什么需要管理员权限

普通用户的 EventAccessQuery 已返回错误5，未取得现有权限描述符。需要真实基线，才能准确准备后续生产服务/权限安装、验证和回滚。本次不包含生产安装。

根据用户接管要求第3条，实际提权前须批准完整具体包。上一次批准仅覆盖已执行完的一次 root-scheduler 诊断，不能转用于本次新的管理员事实查询。

## 判据和回滚

批准后只执行一次；运行前再核验所有固定摘要、C/D各512 MiB余量，以及证据/attempt目录未被使用。逐项保留 API 返回码和错误；UNKNOWN不得当作可用或空权限。结果不改变I1–I7或准入状态。

原生入口等待240秒、外层260秒；OS读调用可能阻塞，不能承诺硬完成期限。拒绝UAC、失败、超时或证据不全均不自动重试，保留现场。

没有系统配置修改需要逆转。回滚为停止推进并封存新证据/私有构建文件；保留全部旧数据，不执行猜测的ACL或注册表恢复。更详细范围和限制见 `READY_V3.md`。

批准范围名 `P309_SINGLE_ELEVATED_READONLY_INSTALLATION_FACTS_V1`、count=1。实际回复到达后才创建 `D:\ReBaseGuard-309\records\p309-installation-facts-v1-human-approval.json`。该批准不构成freeze、grant、qualification、target或正式准入。
