# 本机 VM 可行性包的回滚

范围仅为 `P309_LOCAL_VM_FEASIBILITY_V1`。它不是未来生产服务/guest 的回滚许可。

1. 不再启动下一项探针；先保留 guard 的私有 Job。正常探针到 15 秒请求停止；guard 非正常退出时依赖 Job 的 KILL_ON_JOB_CLOSE。未取得精确进程句柄退出与 Job 为空的证据，不写 STOPPED，不重新启动探针。
2. 若 harness 报 UNKNOWN，保存日志并调查自有 guard/Job；不要按名称、猜测 PID 或用 `taskkill /IM`。不得结束其他 QEMU/WSL 进程，不得 `wsl --shutdown`。当前包没有安装后台服务、启动项或长期端点。
3. 两项探针结束后，`candidate-v1`、源归档、所有日志留在 D: 封存；没有 PATH/注册表/安装器 hooks 需要撤销。**不删除、不覆盖、不自动重试安装**。可在外部证据目录追加 `RETIRED.json`；这不是安全锁，后续流程仍需显式授权。
4. 如果 WHP 在本次之前为 Disabled，确由本包启用，并且新鲜核验确认无仍在运行的本包 VM、owner 确认期间没有其他应用开始依赖 WHP，则在已批准的回滚范围内，用提升的 Windows PowerShell 执行：

   ```powershell
   Disable-WindowsOptionalFeature -Online -FeatureName HypervisorPlatform -NoRestart
   ```

   完整保存返回值和前后 `Get-WindowsOptionalFeature -Online -FeatureName HypervisorPlatform`。若本来 Enabled，不禁用。若出现 Pending/Unknown 或有其他消费者，不猜测恢复状态，暂停回滚操作并保留证据。服务化正式部署开始后，此初始包不再适用。
5. 只恢复 `HypervisorPlatform`；不禁用 `VirtualMachinePlatform`、WSL，不改 Ubuntu、系统 Python、Windows 电源、更新、Defender 或网络策略。需要重启时先由用户保存其他工作并人工重启；不自动重启。

Windows 组件启用/禁用与重启不能被宣称是文件级原子事务。失败可能留下 servicing pending 状态；只能记录真实状态，不能把“命令退出”当恢复成功。原 Ubuntu 和此前迁移备份不参与此包。
