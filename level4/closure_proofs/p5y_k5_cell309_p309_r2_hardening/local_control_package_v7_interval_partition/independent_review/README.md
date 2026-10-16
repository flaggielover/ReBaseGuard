# P309 v6事实与v7代次绑定独立审阅

2026-10-16。此目录是新建的additive公开审阅记录，不修改v1至v6历史文件、v7暂存源码、原始证据、批准记录或接受标准。

v6单次管理员只读执行取得28对象的完整保存基线，但没有建立生产安装、最小权限充分性或正式覆盖。v7 v2修复了两层逐片重新归属问题，可进入限定saved CSV适配层集成；该适配层和driver仍须另行独立审阅。ThreadEnd后的身份尾段继续UNKNOWN。历史未知CPU归属量 **0.4392592秒保持不变**，不得预扣thread-only前段小计0.1247455秒。

- [v6事实对安装 验证 回滚的约束](V6_FACTS_INSTALL_VALIDATE_ROLLBACK.md)：保存结果交叉核对、具体对象清单和不可填写为成功after的部分。
- [ETW公开契约与vendor实现调查](VENDOR_LIFECYCLE_REVIEW.md)：Microsoft字段保证、固定PerfView源码行为及决定性缺口。
- [v7 v2独立源码复审](V7_V2_INDEPENDENT_REVIEW.md)：被拒绝v1的两项问题、v2修复、saved CSV适配层边界。
- [来源与哈希](SOURCE_BINDINGS.json)：审阅对象、执行包和输入提交、保存记录哈希、官方及固定vendor URLs。

本审阅者曾编写v6 FactsReadCore.cs；这里对v6做的是已保存事实的交叉核对与部署约束解读，不冒充该core的独立安全复审。v6 core独立复审由security_preflight负责。v7 core由其他agent编写，本审阅者未参与其实现。

本轮仅读取本地保存文件和公开primary资料，并写入此新目录；未运行测试、numeric audit、decoder、生产adapter、host query或UAC，没有创建服务、账户、key、VM、权限或策略。公开记录仅保留必要摘要和哈希；原始安全描述符、ACL、Base64、个人账户标识和批准字节不复制到此目录。

I1至I7全部OPEN；正式准入BLOCKED；整体任务未完成。新真实变更和验收必须绑定具体完整包及其批准，本目录不携带新的运行授权，也不恢复已消耗的单次批准。
