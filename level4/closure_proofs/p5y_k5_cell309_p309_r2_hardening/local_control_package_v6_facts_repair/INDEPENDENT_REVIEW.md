# 独立静态复核与包装绑定复核

执行包 `e9af7e0b2a822e518164f8c547adb8d9311d7dfd`，运行输入 `e211d4946515d506696d56f03ff2651eece10400`。两项独立复核完成后，未发现请求本包一次固定范围只读UAC批准前必须修复的明确阻断。此结论不是人员执行批准，不构成正式准入。

## 核心与入口的独立源码复核

由 security_preflight 完整阅读Core、测试、修复后wrapper、TrustedEntry、NativeEntry、launcher、invoker及构建绑定；该代理未编写本次Core或包装源码。

- ETW正确处理234 probe，最多一次fetch；阶段码可空；尺寸变化及解析失败UNKNOWN。
- LSA保留原NTSTATUS，成功取得后才拥有清理责任，失败输出不释放；未取得直接权利不推导有效权限。
- SCM精确打开固定服务名，仅服务打开的1060为ABSENT；其他失败UNKNOWN，关闭只针对owned句柄。
- Power双流并发原字节限量保存与摘要，记录decoder来源、严格解码、截断、超时；仅停止自有Process，未确认退出不报成功。
- 上轮部分管道结果丢失问题已修复，生产helper逐条保存及完成标志；固定28项和缺项统计独立。
- 12项源输入、6项私有payload及5项填充转换均逐字节吻合。

复核读取了保存的36个核心案例/191条断言及11个总结案例成功记录，没有重跑测试，没有调用生产API、UAC或新的security scan。

## 包装和绑定的独立复核

由 staged_readiness_fix_review 对root制作的包装/绑定单独复核；该代理是Core作者，因此未自评Core，Core结论以上述独立审阅为准。

核对12份源输入及20份包装提交文件的原始Git字节，6份payload在私有目录/D归档/FINAL_BINDINGS一致；21项私有清单和23项完整归档一致。模板填充、scope/count1、source/core/harness/native binding、先持久化attempt再UAC均相符。保存的只读文件preflight为exit0，native/UAC执行为0。28对象覆盖原10组，失败封存及无自动重试表述准确；包内没有实际批准或禁发二进制/PRIVATE原件。

## 保留限制

Power生产runner未被fake测试实际执行；OS预算不是硬期限。无BOM的decoder选择不证明CLI输出格式；超时且流仍活动时，原字节快照和计数不保证同一时刻，只能作为不完整前缀解释。持续存活的Process引用只在当前查询进程生命周期内保留，不能称为生产独立停止或持久化控制。

LSA missing-direct-rights结果仍不证明服务令牌权限。CBS标志、D盘祖先custody和此前0.4392592秒未知CPU归属等事实没有消失。47个本包案例不是主机准入证据；历史测试未重跑。

**可以提出新的单次只读UAC批准请求；尚未收到该批准。I1–I7 OPEN，admission BLOCKED，整体任务未完成。**
