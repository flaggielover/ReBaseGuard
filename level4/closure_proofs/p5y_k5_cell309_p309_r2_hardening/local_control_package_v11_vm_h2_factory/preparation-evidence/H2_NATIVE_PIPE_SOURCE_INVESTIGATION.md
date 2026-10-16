# H2 独立VM传输：源码调查及待接入的具体边界

本记录是统一安装/真实验收包的工程输入，不是部署、路线接受或正式运行授权。原Windows/WSL启动元组没有被自动移植，旧D2、r2和历史记录不改。I1–I7 OPEN，BLOCKED。

QEMU上游v11.1.2的[Windows pipe后端](https://github.com/qemu/qemu/blob/v11.1.2/chardev/char-pipe.c#L39)创建的是一个双向Windows named pipe，单实例，使用默认安全属性；不是Unix分支的两个.in/.out文件。它等待连接完成，没有本控制包的可信对端检查、明确DACL或remote-client拒绝。这里是对上游版本源码的观察，不是已证明签名candidate二进制与该源码可复现对应，也不是现有候选已经运行过H2。现有暂停VM探针没有验证这个传输。

不能为让Relay直连而给QEMU整个token的DefaultDACL泛加Relay权限。默认DACL影响其他新对象，不只这个pipe；VM执行身份也不能直接拥有Controller防回滚anchor的写权限。仅把QEMU放入Job不建立这层写隔离。

具体候选连接是Controller中介：受限的独立VM执行身份运行QEMU；Controller只连接从其成功启动事务得到、持有进程句柄和创建时间绑定的QEMU pipe。连接后以GetNamedPipeServerProcessId与仍存活的held-process身份核验，不按进程名认领。Relay只接Controller自己创建的固定、有界、本地认证端点，拿不到QEMU进程、Job或磁盘控制句柄。Controller转发固定代次的协议字节，不接受command、path、PID、UID、任意签名输入或控制动作。停止通道不得等待转发I/O。

Controller端点需要明确每种对象的实际access mask、FIRST_PIPE_INSTANCE和PIPE_REJECT_REMOTE_CLIENTS，精确服务身份校验与每次G绑定。上游QEMU pipe本身没有remote拒绝flag，不能宣称它已有该保证；后续实现若通过Controller核验后的owned pipe handle设置拒绝Network SID等精确ACL，必须记录before/after、验证实际效果，并证明只改本次QEMU创建的对象。握手完成前不释放guest gate；抢占连接、身份不符、连接超时均停止本次owned VM并保持UNKNOWN，不重连到任意同名实例。

独立VM执行身份仍须实现和审阅：选择受限token/独立虚拟账户服务等具体方式后，列出精确TokenUser、enabled/restricted SIDs、owner/defaultDACL、代码RX、VM数据最小写权限及所需CreateProcess权限。不能把Controller同一未受限制的写身份当作VM隔离；不能用SeDebug、LocalSystem或临时扩大权限后备。新增身份/服务的碰撞及有效token需要实际批准后的核验，不从v6只查三个服务名的记录推断第四个名字不存在。

guest固定virtio-serial端口候选名为rebaseguard.p309.relay-v1，仅guest relay可读写，runner/monitor无设备写权限。guest monitor的H3/H4仍分别按实际Unix peer和当前InvocationID认证；host观察事实仍只来自独立Observer自身构造及公钥登记。帧大小、顺序、challenge/sequence/G/runtime/policy绑定、异常后的不可逆停止须贯穿全链。没有host目录挂载、QMP/HMP或通用远程shell。

真实验收包必须覆盖：默认pipe实际权限、错误实例/其他客户端/remote拒绝、同名抢占、超大和断帧、阻塞转发时独立stop、Controller/Relay/QEMU任一退出、guest gate超时与迟到帧、持有Job/进程身份的停止及清理。源码支持的后端、选定二进制实际支持和真实隔离是三种不同证据；当前都不能合成成已通过H2。

这是一项尚须完成源码、构建和独立审阅的具体候选。实际创建端点、服务、账户或VM前，与其他控制组件合并成精确来源绑定、权限、验收和回滚包，再集中向用户请求确认。
