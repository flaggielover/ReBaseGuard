# 单次管理员只读安装事实预检：修复后的 v3 构建目录

准备状态：源码已修复，私有目录已逐字节放置、解析和只读绑定预检。**尚未批准或执行管理员查询。I1–I7 OPEN；准入 BLOCKED。**

当前入口仅为 `Invoke-Once-v3.ps1`。旧 `Invoke-Once.ps1`、`Build-Private.ps1` 及旧绑定/构建记录作为历史保留；旧 source pins 与当前修复源码不相符，不能用作本包入口。

## 固定来源与已完成检查

运行源码提交：`28fd11c9c8398f5fbd85d4836970918a6ad5c711`。完整执行包的后续提交包含新的复制辅助脚本、一次调用器、绑定和本说明。

- 私有目录：`C:\Users\Lenovo\P309-InstallationFacts-build-20261016-v3`，普通 owner 构建目录，创建时保护 DACL，仅 owner、Administrators、SYSTEM 可写。
- 原生入口 SHA-256：`469efadffe76e5a66bd6997cb215042f74f0030c3ced819e1c1e4c2eccc65816`。
- 查询源码 SHA-256：`4ea4e224a876f6a1c0d42144f8f5edf819172992329a7231bf2d6fca8e561054`。
- 填充启动器 SHA-256：`9b89849c5e5636b219b29ad633f4dda43a6268bdd3a8858b4b0fc73ae9119d09`。
- 全部来源、模板、复制脚本与调用器摘要：`FINAL_BINDINGS_V3.json`。

原生入口由已有 MSVC 在 C 暂存目录普通构建，完整命令、工具摘要和源摘要保留。`Bind-Private-v3.ps1` 仅从 D 本地归档复制已核验的相同字节，没有重新编译、安装服务或执行入口。最终启动器的祖先 GENERIC_READ 修正在构建后独立生成，摘要单独保留；不得将旧启动器记录当成最终启动器的执行验证。

四项源码修复已另行独立复核：服务名完整且不区分大小写、路径 ABSENT/UNKNOWN、原生失败句柄所有权、祖先访问与 metadata 表述。已有13项纯判断/ABI检查和19个 ownership 合成案例保留，没有重跑。当前实际私有目录上的启动器与新调用器只读预检均成功；两者均未触发 UAC 或执行原生入口。

## 待人员批准的完整范围

一次普通 owner 调用，一次 UAC，使用上述固定原生入口及 inbox Windows PowerShell 5.1。创建全新的 `C:\ProgramData\ReBaseGuardP309-InstallationFacts-v1`：管理员所有，仅 Administrators/SYSTEM 写入，当前 owner 只读。写入每项结果、实际批准字节及最终摘要。

固定读取：两个 GUID 的 ETW 权限与对应注册表值存在性；三个拟用服务 SID 的已有 LSA 权利；三个固定服务名冲突；选定父目录 ACL、C/D 空间和拟用目录冲突；当前睡眠方案；选定更新/待重启键；DeviceGuard 选定字段；更新任务的名称、状态、enabled/wake flags。

只创建这次证据及进程内编译临时文件。没有 ETW session、host sampling、VM、QEMU、P309 计算、服务/账户/密钥、权限授予、策略或计划任务修改。`-ExecutionPolicy Bypass` 仅用于该普通进程，不更改系统执行策略。

普通 EventAccessQuery 先前返回错误5，不能据此推断现有 ACL 或准确回滚。此集中读取取得缺少的基线后，才能继续准备生产服务/权限安装、真实验证及回滚的具体包；本包不批准那些操作。

## 成功标准、失败与回滚

批准前检查 source/native/launcher/caller 摘要；C/D 各至少512 MiB；证据目录、私有 attempt 目录与批准文件必须匹配本次新批准。调用器先持久化单次记录，所有代码使用已核验字节。

成功必须逐项解释 API 返回、错误和路径状态；查询返回不代表全部可用。仅明确 file/path-not-found 可判 ABSENT，其他访问错误是 UNKNOWN；选定更新键不存在不代表不会维护/重启。保存受保护原件，并逐字节复制到 D records；Git只追加最小化摘要，ACL对象/卷文件身份明细留本地。

原生入口等待240秒，外层等待260秒；系统读取可能阻塞，这不是硬完成期限。超时、查询错误或证据不完整均保留 UNKNOWN，保留现场，不自动重试，不终止无关进程。结果不关闭任何 I 项、不授予正式运行权限。

没有系统配置变更需要撤销。回滚为停止后续推进、保留并封存本次新证据和私有构建目录；必要时核验复制到 D。不得删除旧证据、备份或原 Ubuntu，不执行猜测的 ACL/注册表逆向操作。

原9ae3完整审阅与后续C暂存修复复核均保留；本包仍需对新不可变提交完成绑定复审，再请求本次单次 UAC 的人员确认。之前 root-scheduler 诊断批准已经使用。
