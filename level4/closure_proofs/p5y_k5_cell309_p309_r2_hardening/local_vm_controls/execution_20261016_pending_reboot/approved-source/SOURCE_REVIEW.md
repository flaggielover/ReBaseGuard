# 新增平台包的协调者自审

这是实现者的源码自查，**不是独立审阅，不关闭任何正式 finding**。未启动 `/review-bugbot` 或声称外部 reviewer 已批准。现有 review 技能的显式命令入口不在本轮调用范围；不能把工具可用性替代 reviewer 权限。

审查范围：本目录新增 C#/Python/PowerShell 文件及 LOCAL_ROUTE/ROLLBACK。原 WSL/D2 与正式 r2 文件没有修改。

已在交付源码中修正：

- Windows Job 常量：进程内存位使用 `0x100`、Job 内存位 `0x200`，不误用 `0x400`；旧构建保留，交付绑定 v4。
- 子进程环境：去掉继承任意环境/插件路径，固定 runtime bin/System32、QEMU data/module 路径；禁用户配置、网络、磁盘、监控接口与 TCG。
- 来源核验：哈希清单本身绑定批准摘要并持有只读句柄，整个 runtime 文件集逐项锁定，拒绝额外文件及 reparse。安装不运行 archive hooks；归档先签名核验，再固定选取文件摘要。
- 停止竞态：不在 watchdog 可能继续访问 native handle 时关闭并复用该 handle；不能完成线程收尾时退出自有 guard，保留 kill-on-close。未绑定 Job 的暂停子进程只通过创建返回的句柄清理。
- 进程代次：外部观察者只打开记录的自有 child，核验创建 FILETIME，持有同步/有限查询句柄，不通过 PID 发终止。
- Windows 功能范围：不使用 `-All` 扩展父功能，不自动下载组件、重启或调整策略。父功能/servicing 问题应返回调查。
- 归档解析：固定 exact 和受限数值版本比较，不猜虚拟提供者；真实输入暴露了 TCG 插件和 `winspool.drv`，已排除 TCG 插件并正确识别 Windows DRV import；增加相应解析回归。

保留限制：

1. Native Job/WHP 行为尚未实测；纯函数测试和编译不能证明 Windows 清理成功。需先取得真实平台验证许可。
2. 两个暂停无盘 VM 探针只验证后端启动存活和自有进程停止，不能证明 guest 执行、隔离、完整 partition 回收或长期工作窗口。
3. Windows Job commit 上限并未被证明涵盖 WHPX 内核分配；不得据此宣称正式资源隔离已达标。
4. 当前普通 Windows owner 是可信操作身份；未创建隔离服务身份、公钥 pin 或生产 ACL。该 probe 不对同一 owner/admin 的并发恶意文件/目录改写提供生产级保证。
5. 静态 DLL closure 不证明动态装载完整；真实缺失 DLL/模块或后端错误必须保留失败，不扩大 DLL 搜索路径，不换版本/模拟器。
6. approval JSON 只记录人类确认与精确包摘要，不是独立签名授权、准入、freeze 或 grant；不能由程序生成 true 来替代用户批准。
7. 即便平台探针通过，I1–I7 和 AF-2、正式身份/采集/anchor/broker 的实现与独立审阅仍未完成。后续不从该 probe API 启动 P309。
