# v6保存事实对生产安装 验证 回滚的约束

2026-10-16单次管理员只读执行的保存基线，可用于具体安装提案的before清单；它没有建立成功after。执行包 `e9af7e0b2a822e518164f8c547adb8d9311d7dfd`，输入源码 `e211d4946515d506696d56f03ff2651eece10400`，UTC 05:09:10至05:09:24，native PID4148退出0。该单次批准已使用，没有自动retry。

本轮读取D归档执行摘要RESULT.md和ACTUAL_RESULT.json，并与受保护保存JSON交叉核对。D ACTUAL_RESULT的summary与保存RESULT.json一致：28预期、28完成、19 OBSERVED、6 ABSENT、3 NOT_FOUND_DIRECT_RIGHTS_NOT_ENUMERATED；没有遗漏对象或cleanup错误。31份保存JSON含30项manifest；既有逐字节归档与所有者检查作为保存记录引用，本轮没有重新查询主机ACL。原始描述符、ACL、Base64、个人账户标识和批准字节不复制到本公开记录。

## 可确定的采集时点before

- 两ETW GUID均probe234、fetch0。SystemTraceProvider API descriptor为184字节，SHA256 `a79948ddef24f0bb0ff391e2bfdeb914fa16b02d52df5bf5ba77c294cbe8875c`，与本次保存的不带括号registry Binary逐字节相同。私有GUID API descriptor为292字节，SHA256 `4324e8e1501d0e094750397a65705338aa7cc71f09b446a09f0eed3c5b96de46`，但对应两种registry名称均不存在。这是有效默认描述符，不能作为原本存在的registry值备份。[EventAccessQuery](https://learn.microsoft.com/en-us/windows/win32/api/evntcons/nf-evntcons-eventaccessquery)
- 默认描述符中的register/join权限不能解释成start、query或consume。SystemTraceProvider已有的其他服务授权必须保留；本公开摘要不复制其原始ACL。
- ReBaseGuardP309Observer、ReBaseGuardP309Controller、ReBaseGuardP309Relay三个精确服务名均OpenService返回1060 ABSENT，SCM handle关闭成功。没有服务handle，相关close为未尝试，不是成功0。该查询不证明key、pipe或Job不存在。
- 三个拟用服务SID均LSA open成功，query原始NTSTATUS `0xc0000034`转换Win32 `2`，rights=null、DirectRightsEnumerated=false，close成功。free未尝试，因为没有成功query的owned buffer。此状态与有效token、组继承权利、未来登录账户权利不同，不能改写为成功空列表。[LsaEnumerateAccountRights](https://learn.microsoft.com/en-us/windows/win32/api/ntsecapi/nf-ntsecapi-lsaenumerateaccountrights)
- 三个拟部署目录当时ABSENT：`C:\Program Files\ReBaseGuardP309`、`C:\ProgramData\ReBaseGuardP309`、`D:\ReBaseGuardP309Private`。现有`D:\ReBaseGuard-309`由普通用户拥有且对Authenticated Users可写，不可用作生产可信祖先。D根的普通用户创建/对象DELETE权限不等于具有对所有子项的FILE_DELETE_CHILD权限；新具体child的owner、ACL、祖先与替换拒绝尚未验证。不能说D盘全部不可用，也不能说新child custody已通过。
- 空间时点值为C 5,624,152,064字节、D 130,155,388,928字节，D为NTFS。C不足一个40 decimal GB根；D剩余量不是根数量、overlay、日志、快照、最长窗口及保留预算通过。
- power子进程PID47412退出0，用时113ms，未超时、未请求kill；两流完整，无raw/text截断。stdout原始1449字节，SHA256 `860b5807846f8b6a330b6083141ab317f14383d37f5966bdaa31d4b5fbb02413`，CP936严格解码与保存文本一致。这个解码结果不建立通用CLI编码保证。
- 当前方案的STANDBYIDLE AC/DC为0/600秒；HIBERNATEIDLE为0/10800秒；混合睡眠为0/0；wake timer为1/0。STANDBYIDLE的0表示不因idle自动睡眠；**HIBERNATEIDLE的0不能说成never**，官方文档说明adaptive hibernate threshold。没有完整盖子、电池临界、Modern Standby、当前供电及维护窗口保证。[Sleep idle](https://learn.microsoft.com/en-us/windows-hardware/customize/power-settings/sleep-settings-sleep-idle-timeout)、[Hibernate idle](https://learn.microsoft.com/en-us/windows-hardware/customize/power-settings/sleep-settings-hibernate-idle-timeout)
- CBS RebootPending存在。另三个所选更新键不存在，不能推出没有其他维护，也不能推出马上重启。不得自动清CBS、自动重启或宣称已取得不休眠不重启窗口。

## 完整安装包必须固定的对象

1. 三个独立OWN_PROCESS服务的StartName、账户SID与服务SID、ServiceSidType、RequiredPrivileges和服务DACL。实际token必须验证enabled/restricted SID与权限；不能承诺给服务SID授予某LSA right就必然进入未来token。Observer需要的profile权限单独证明，Controller和Relay不继承。不采用LocalSystem、SeDebug或宽泛组成员资格后备。RequiredPrivileges只裁剪已有token权限，不授予缺失权利。[Service required privileges](https://learn.microsoft.com/en-us/windows/win32/api/winsvc/ns-winsvc-service_required_privileges_infow)
2. ETW生产mode和明确API操作。provider enable候选mask为0x80；仅文件session QUERY加CREATE_ONDISK候选为0x41；实时QUERY加CREATE_REALTIME加ACCESS_REALTIME候选为0x421。它们只是待验证的最小操作需求，不是已证实充分或已批准的mask，尤其实际token的停止权限与覆盖须实证。只增加指定主体所需权限，保留无关授权，不全局替换DACL。[EventAccessControl](https://learn.microsoft.com/en-us/windows/win32/api/evntcons/nf-evntcons-eventaccesscontrol)
3. 受保护代码和配置树。管理员/SYSTEM维护，服务仅必要读执行；完整绑定文件、解释器与库、配置、cwd和环境。部署碰撞、reparse、可写祖先和路径替换必须拒绝，不能从可写checkout直接作为生产输入。日志和temp分离。
4. 分开的Observer checkpoint/anchor、Controller生命周期状态、Relay临时数据。角色只写自己的数据，不得改owner或DACL；Relay不得写观察状态或签名输入。持久化、外部anchor、序号和重启拒绝规则须实现；D历史归档副本不是生产防回滚anchor。
5. 固定CNG provider、算法、位数、key名称、存储范围、签名用途、export policy和key权限。碰撞拒绝、不覆盖，验证provider实际行为；不直接改provider内部key文件。Observer只签自身构造并验证的固定事实，不提供任意签名接口。pipe按真实API mask区分server/client，排除client创建实例、改owner/ACL及远程访问；固定endpoint与token校验。
6. 新D盘VM目录的具体custody、签名base image、overlay、seed、data及全部QEMU/WHPX和guest运行时文件。固定资源预算、命令和网络面；不挂载host目录、不暴露QMP/HMP。Controller持有本VM Job控制句柄；独立停止通道仅必要QUERY、TERMINATE、SYNCHRONIZE，Relay没有Job/进程控制权。guest root broker、pidfd/cgroup绑定、guardian和Windows兜底必须接成完整链。
7. 默认不修改电源和更新策略。如确需修改，列出精确scheme、setting GUID、AC/DC原值、拟值、范围和并发检查后恢复条件，不能用清标志代替维护解决。4 CPU、8 decimal GB、每根40 decimal GB及原时间/CPU阈值保持不变。

## 真实验证必须覆盖的结果

真实验证必须另绑有限、target-free、无自动retry的包和批准。以实际生产服务身份验证：正常收集/签名/控制成功，Relay和普通客户端无法写代码、状态、key、创建服务端或取得VM控制；碰撞、伪造endpoint/request、错误代次和旧pin被拒绝。保存精确服务配置、token与实际对象权限after，而不是拿本次管理员读取成功代替。

对I2验证实际ETW启动、消费、停止、loss、时钟与CPU命名空间、process/thread代次、PPL及其他partition可见性，完成guest vCPU、QEMU开销、root和其他partition去重。counter metadata存在、总量接近、无观察到loss或某工具可显示进程均不足以独自宣称coverage_complete。

验证Controller和guest broker的生命周期状态、一次启动许可、创建与停止竞争、独立停止、heartbeat失联、挂起或gap、恢复拒绝及持久anchor。UNKNOWN必须阻止继续，不当STOPPED；仍保留原5秒suspend、45秒gap和exactly-once语义。新VM transport必须精确保护并独立审阅，不能把历史WSL元组换成任意SSH。

绑定实际guest镜像和全树运行时、ELF/共享库及保护祖先；容量和内存必须按完整预算验证。镜像已下载校验、小VM探针、构建通过和本次空间快照都不能替代生产运行时after。

## 回滚清单

1. 先撤销一次启动许可和新请求入口，保持Observer、Controller和独立停止通道可用；按持有的精确实例身份停止本包VM、guest、trace，记录退出、cgroup空和handle清理。UNKNOWN时保留控制，不猜PID、不删除现场。
2. 保存失败证据、checkpoint、key身份、anchor和已用许可。不得重置序号、复用旧pin或借恢复配置获得retry。
3. LSA仅撤销本次确实新增的明确权利，并检查并发变化；禁止AllRights=true。移除全部权利会删除LSA账户对象，不能把direct-notfound当成已知空账户来盲目恢复。[LsaRemoveAccountRights](https://learn.microsoft.com/en-us/windows/win32/api/ntsecapi/nf-ntsecapi-lsaremoveaccountrights)
4. SystemTraceProvider仅撤销本次增量并保存其他授权。私有GUID原registry为不存在：只有本包确实新建、当前值仍等于预期postimage且无并发变更时，才移除新条目恢复默认语义。**不得把API默认292字节写回成伪原值。**[EventAccessRemove](https://learn.microsoft.com/en-us/windows/win32/api/evntcons/nf-evntcons-eventaccessremove)
5. 只恢复该installer实际改变且当前仍等于其预期after的设置。冲突停止并保留记录，不能覆盖第三方变化、替换整个D根ACL或删无关授权。
6. 确认停止、无owned进程或未决handle且封存完成后，才移除本包新服务和访问入口。VM磁盘、key和状态先隔离保留，不自动递归删除、unregister或销毁历史；数据销毁需另列具体范围。原Ubuntu、私有运行时、历史records与备份保持。

## 尚不能填写为成功after

服务真实token与授权充分性，key/pipe/Job碰撞及最终权限，具体D盘child custody，生产签名与broker整链，外部anchor与重启恢复，完整guest运行时和资源预算，维护窗口，以及ETW/counter跨partition和受保护活动的完整覆盖均未由本次事实建立。

原0.4392592秒未知CPU归属量保持不变。I1至I7全部OPEN，正式准入BLOCKED；本记录不创建新的安装、授予权限或真实验收授权。
