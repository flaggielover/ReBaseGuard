# 已执行：修复包单次管理员只读预检

2026-10-16北京时间13:09:10–13:09:24，实际批准后执行固定e9af7e0b包一次。Native PID4148退出0；28/28对象保存，31份保护原件及D副本逐字节吻合，manifest30项全部匹配，原件叶所有者均为Administrators/SYSTEM，未发现cleanup错误。

## 已取得的基线

- 两个ETW GUID均234→0；SystemTraceProvider有效描述符184B、SHA256 `a79948ddef24f0bb0ff391e2bfdeb914fa16b02d52df5bf5ba77c294cbe8875c`，与本次保存的registry原值逐字节一致。私有GUID描述符292B、SHA256 `4324e8e1501d0e094750397a65705338aa7cc71f09b446a09f0eed3c5b96de46`，对应两种registry名称均不存在；API有效默认描述符不能冒充原本存在的registry值，未来回滚不得盲写该默认值。
- 三个固定服务名均精确OpenService返回1060，可判本次不存在；没有创建或启动服务。
- 三个拟用服务SID均LSA open成功、query raw `0xc0000034`→2、rights=null；free未调用而非成功0，policy close成功。它们是未获得直接权利列表的时点事实，不证明未来服务账户/组/实际token权限。Microsoft允许无account rights时返回missing类状态。[LsaEnumerateAccountRights](https://learn.microsoft.com/en-us/windows/win32/api/ntsecapi/nf-ntsecapi-lsaenumerateaccountrights)
- powercfg自身PID47412退出0，113ms，未请求kill；两流完整，无截断。stdout1449原字节、SHA256 `860b5807846f8b6a330b6083141ab317f14383d37f5966bdaa31d4b5fbb02413`；CP936严格解码与保存文本一致。
- 所选睡眠idle索引AC=0、DC=600秒；所选hibernate idle索引AC=0、DC=10800秒；混合睡眠AC/DC=0，wake timer AC=1/DC=0。只对睡眠idle的0可依文档解释为不因idle自动睡眠；hibernate的0不能直接说永不休眠。没有盖子/电池临界/完整维护或未来重启保证。[Sleep idle](https://learn.microsoft.com/en-us/windows-hardware/customize/power-settings/sleep-settings-sleep-idle-timeout)、[Hibernate idle](https://learn.microsoft.com/en-us/windows-hardware/customize/power-settings/sleep-settings-hibernate-idle-timeout)
- C/D可用空间5,624,152,064与130,155,388,928字节，D为NTFS；三个拟用目录仍ABSENT。空间时点值不是正式VM/日志/最长窗口预算通过。

## 保留的限制和后续依赖

CBS待重启标志仍存在，未清除、未重启。D根与现有记录父目录的普通用户写/对象DELETE权限问题未消失；D归档副本不是生产防回滚anchor。ETW默认DACL中的register/join权限不能当start/query/consume权限。新的最小权限必须由实际生产操作和服务token实证决定，不采用LocalSystem/SeDebug后备。

本次程序列出的unknown只有3项未取得直接权利列表；没有遗漏对象和cleanup错误。这不意味着可以部署、完整采样或发grant。此前0.4392592秒未知CPU归属、guest/partition去重、受保护活动覆盖、runtime来源、服务身份/公钥、broker限制、独立停止与持久恢复仍开放。

原始SDDL/registry字节、逐文件ACL及批准字节只留本地；Git发布有限摘要及原件hash。v5原件和失败记录不改写。本次未重跑测试，未安装软件或创建账户/服务/密钥，未修改既有ACL/策略，未启动跟踪、采样、VM、演练或P309；批准已使用，无自动重试。

继续完成保守的离线归属实现、生产部署/验证/回滚包及独立复核；真实变更或验收仍需具体包批准。

**I1–I7 OPEN；正式准入BLOCKED；整体任务未完成。**
