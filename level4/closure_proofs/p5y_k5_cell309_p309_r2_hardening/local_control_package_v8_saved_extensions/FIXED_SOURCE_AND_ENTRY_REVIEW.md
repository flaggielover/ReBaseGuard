# v8 固定已保存 ETL 扫描：独立源码及入口复审

状态：固定离线调用可继续；这不是采集完整性、主机或正式准入接受。I1–I7 OPEN，BLOCKED。此记录保存时尚未实际解码 ETL。已有只读调查及离线分析授权足以执行这里限定的保存文件读取；不请求或续用新的 UAC、跟踪或 VM 授权。

扫描器作者为独立子代理 `/root/staged_readiness_fix_review/anchor_primary_docs`；主代理逐项阅读并核验了全部 `SavedExtendedData.cpp`、`BuildToolRunner.cs`、`Build-Only.ps1`、源码及构建台账/设计/结果解释。输入路径、308,346,880 字节及 SHA-256 固定在源码，只有 `--self-test` 和 `--scan-saved <fresh-name>` 两个入口；后者没有任意输入、live logger、provider enable、PID 查找、服务、VM 或 workload 启动代码。

固定源码 SHA-256：`e493c3dc93ff99c948ac344bd8326129ef5b9648cdb11078398a96fb9e7c81cf`。
固定二进制 SHA-256：`a9a8f84d64051d11743f9c7d4a0cdbb56b21eb6b599026d50cd7ade91f3e903d`。
`SOURCE_BINDINGS.json` SHA-256：`ef1fc6d61c24dbc1db3752eebbf2b4d40b7d830ef89286e6967438dbde62277d`。
最终构建记录 SHA-256：`ddfad5408bf374e09b72cf373d39e22ef8fd9957ad0a10a1eb6334bb2d394890`。

输入叶文件禁止普通 Win32 数据写/删除共享，祖先保持禁止删除共享的句柄；同一持有叶对象核对大小、前后摘要和 FileID。OpenTrace 只读固定路径的重开依赖该路径钉住，不把旧解码器的未绑定来源追溯成已证明。管理员/kernel、已有映射和所有元数据攻击不在这项普通离线分享钉住保证之内。

回调遍历所有事件及其全部扩展项，按 provider/id/version/opcode 与 type/length 聚合，带预算和守恒检查。空/不可读数组、重复/空/非 8 字节/不可读 PSK、保留字段异常均不建立身份。PSK 值只做 8 字节可读性探测，不保留值或摘要，不绑定 payload 子进程。原始 payload/PID/TID/命令/路径不输出。loss、原始时钟、ProcessTrace/CloseTrace、输入 close 和输出 write/flush/close 分开记录；`scan_complete` 仅表示本次字段扫描完成，绝不等于 `coverage_complete` 或主机安全。

CreateNew 尝试目录及文件保留部分结果；输入/格式/API/预算/I/O 失败均非成功。必须同时有原生退出 0、原生 COMPLETE、完成回执、摘要/长度/状态匹配、外围调用退出 0，才解释为本次离线扫描完成。21 项历史内存检查没有重跑，也不充当实际 ETL 证据。

主代理编写外围入口，交由 `/root/staged_readiness_fix_review` 独立只读复审。初稿 `e3beca...` 的两项问题是旧 partial 目录可能被新错误记录污染，以及 post-Popen 异常清理/日志不完整。两项已同批修正；旧源码未执行实际扫描，逐字节保存在 D 盘 review history。最终入口 SHA-256：`27e7e9604f57f31b74330308bb5d05ef9ff3df63d5fa0854a1c50829bf58060d`。复审者明确回报两项闭合、无新增 must-fix，且没有执行扫描或测试。

入口将此前已复审 v7 pin helper 从固定摘要的字节编译，绑定六个输入及外围源码；启动前及退出后核验，实际编译的 caller 摘要须与钉住源码一致。仅一次持有的 Popen 对象可被终止；先记录 kill attempt，失败也尝试限时 wait，不按 PID 重开/清理。180 秒等待预算及 2 秒停止后等待是外围等待预算，不保证抢占 Windows 卡住的系统调用。所有 retained pin 关闭成功后才发布外围 COMPLETE。缺失完成、异常、退出不明保持 FAILED/UNKNOWN，无自动重跑。

针对新入口做了单独 7 项故障测试，使用 fake Popen 和本次自有临时文件，没有 ETL/native scanner/服务/VM 调用。首轮 6/7：旧 partial 用例的断言放在 `patch.dict` 还原整个 globals 之后，误读回测试自己预置的 True。保留失败源码及日志，修正测试断言位置后 7/7 通过；外围运行源码未因此变化。此 7 项与扫描器 21 项、host anchor 24 项各属不同调用，不相加冒充一次总测试。

这些审阅及测试不签发生产准入，不证明 Windows kernel 生命周期、受保护活动覆盖、独立停止、host/guest 去重、I4 完整运行时或持久化断电保证。实际扫描结果将另行追加，不修改本准备记录。
