# v6：集中修复只读安装基线读取

本包是新增的开发候选；不是人员批准、生产安装或正式准入。旧v5源码、构建、实际失败/UNKNOWN记录和批准字节全部保留。单次v5批准已使用，禁止据此执行本包。

## 来源和修正

实际v5查询见 `../local_control_package_v5_readiness/execution_20261016_v1`，原件及精确副本保留在D records。

- EventAccessQuery文档的缓冲区不足响应是234。新核心分别记录probe/fetch阶段，仅一次probe和一次fetch；尺寸改变、调用/描述符解析失败保留UNKNOWN，不循环重试。专属registry值缺失时API可能返回默认描述符，不能说有效权限为空。[Microsoft](https://learn.microsoft.com/en-us/windows/win32/api/evntcons/nf-evntcons-eventaccessquery)
- 精确OpenService读取三个固定名字，仅1060为ABSENT；拒绝或其他失败为UNKNOWN。原Get-Service枚举不足以排除驱动或不可见服务。[OpenServiceW](https://learn.microsoft.com/en-us/windows/win32/api/winsvc/nf-winsvc-openservicew)、[Get-Service限制](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-service?view=powershell-5.1)
- LSA逐阶段保存attempted、原始NTSTATUS和可空转换码，仅成功获取后才取得清理所有权。query=2单列未取得直接权利列表，不推导账户存在、组继承或实际服务令牌有效权限。[Microsoft](https://learn.microsoft.com/en-us/windows/win32/api/ntsecapi/nf-ntsecapi-lsaenumerateaccountrights)
- powercfg不依赖LASTEXITCODE；仅固定绝对路径和只读参数，由显式Process对象并发限量收集两条输出流。退出、流完成、截断和超时分别记录。不能把取得输出解释为永不睡眠。
- 28个固定对象分属原10组，每对象独立保存，单项异常不抹去已取得的值。固定预期集合不随成功项目变化；总结列unknown、not-attempted及cleanup errors。证据写入失败则整个收集不完整；不继续运行或生成准入。

## 拟执行的具体只读范围

仅在新的明确人员批准后，一次普通owner调用、一次UAC，使用固定NativeEntry和inbox Windows PowerShell5.1，读取同一组事实：两GUID的ETW权限、三个拟用服务SID的已有LSA直接权利、四个固定ETW registry值、三个固定服务名、四个父目录ACL、C/D空间与D文件系统、三个拟用目录冲突、当前睡眠方案、四个选定更新/重启键、DeviceGuard选定字段及两个固定任务路径的元数据。

候选普通构建目录 `C:\Users\Lenovo\P309-FactsRepair-build-20261016-v1`。新证据目录 `C:\ProgramData\ReBaseGuardP309-FactsRepair-v1`，创建时admin所有、admin/SYSTEM写、当前owner只读。旧目录完全不采纳/覆盖。新批准文件将为 `D:\ReBaseGuard-309\records\p309-facts-repair-v1-human-approval.json`，只有实际回复到达才能创建。

查询不赋予任何LSA权利、不改ETW ACL或registry，不创建账户/服务/key/endpoint/unit，不安装软件、不改电源/更新策略，不触发重启，不启动ETW、host sampling、VM/QEMU或P309。只新增构建、单次attempt及证据。

powercfg20秒总预算；超时/异常时仅对持有句柄的本次powercfg请求终止，再等最多2秒。每流保存最多128KiB原字节及64Ki字符，保留base64/摘要与明确编码、严格解码和截断状态；无BOM时选用进程标准流初始decoder不是命令格式证明。单份证据上限2MiB，无法完整保存则收集不完整。不是任意PID终止，也不声称清除了后代。不能确认退出则UNKNOWN并保留身份/现场。Native等待240秒、外层260秒；OS调用不可硬抢占，不能承诺硬完成期限。无自动重试。

## 完整绑定、验证及回滚

Build-Private仅普通构建、纯注入单元测试及文件只读preflight，不执行native入口或真实host queries。生产适配器从测试注入入口明确分开；fake API测试不证明实际ETW、SCM或服务令牌行为。历史157项及其他未变suite不重跑；新增通过数仅记录本包实际运行输出。

所有源输入绑定不可变提交，编译工具/命令/输出、core/harness/template/native/launcher/caller SHA分别记录。elevated TrustedEntry校验core、harness、批准字节，在同一内存字节上执行；不从mutable路径Add-Type或dot-source。caller先核验批准scope/count/bindings并持久化attempt，才触发UAC。实际运行只能用最终bound caller，不能直接调用template或自建批准。

成功是取得并保留可解释的有限基线，不是installation_ready。逐对象检查native返回与cleanup；单纯exit0或文件数不能证明可用。复制前核验保护原件清单，D归档逐字节比较；Git仅追加最小化结果和原件hash，ACL/registry原字节及本机对象身份只留本地。

没有系统配置修改需要逆转。拒绝、异常、超时、未确认退出、清单/副本不符均停止推进，保存现场，不重试、不清除CBS标志、不删除旧数据。封存本包新增构建和证据，不执行猜测的ACL/registry回滚。

## 不变的后续依赖

D盘完整祖先custody、CBS维护/重启窗口、实际服务最小权限与公钥注册、guest完整runtime、broker/限制、独立stop和持久恢复仍需实现及真实验证。此前0.4392592秒未知CPU归属不豁免。原阈值、契约、freeze/grant/qualification/target和exactly-once不变。

**I1–I7 OPEN；正式准入BLOCKED；整体任务未完成。**
