# 已执行：单次管理员只读安装基线（不完整）

实际人员批准到达后，于2026-10-16 04:47:09–04:47:20 UTC执行一次固定2fbb包；原生入口38168退出0。10组查询与13份JSON已保存，原manifest列出的12项全部摘要匹配，保护原件逐字节复制到D记录。没有自动重试。

程序结束不等于基线完整。必须保留以下结论：

- ETW两GUID大小探测返回234，分别需要184/292字节；v5只接受122，未进行第二次实际读取。原final_rc复制probe值，不是fetch失败。权限描述符均UNKNOWN。
- 注册表保存的SystemTraceProvider binary为184字节、SHA256 `a79948ddef24f0bb0ff391e2bfdeb914fa16b02d52df5bf5ba77c294cbe8875c`。它可离线解析为4个ACE，但长度相同不证明等于API有效描述符；私有GUID没有专属值也不证明有效ACL为空。
- 三个拟用SID均LSA open=0、query=2、rights=null；没有获得直接权利列表，更未获得实际服务令牌权限。默认free_rc=0不是成功释放证据。
- 三个服务未在原枚举中匹配，但枚举可漏驱动和不可见服务，不能宣称名字ABSENT；需精确OpenService读取。
- 三个拟用路径均明确file-not-found而ABSENT。C/D可用分别5,722,697,728与130,174,083,072字节、D为NTFS。这不是正式资源预算通过。
- 睡眠项只有LASTEXITCODE未设置异常，输出与退出状态未保存，结论UNKNOWN。不能称powercfg返回非0，也不能称不会睡眠。
- CBS RebootPending键存在；另一个重启键及所选更新Policy键不存在不能抵消它。没有清除标志或触发重启。14个所选维护任务12个enabled；不代表完整未来维护时间表。
- D根和既有记录父目录含普通Authenticated Users写/创建及对象DELETE权限，后者owner为普通用户。不能把其下保护叶目录自动当作生产可信根。该mask不含DELETE_CHILD，也未证明每个D直属受保护目录均可替换；本机路线尚不能判不可行。

原件与未脱敏ACL/registry在本地记录目录。Git只追加有限摘要及原件hash。原Ubuntu、Python、历史、备份和分支保留；没有账户/服务/密钥/策略修改，没有采集、VM或P309计算。

## 集中后续工作

新代码一次修正ETW probe/fetch、LSA每阶段与清理记录、精确SCM查询及可靠powercfg双流结果；固定对象独立保存，失败不抹掉已取得结果。只进行普通构建与针对实际缺陷的单元验证及独立复审。旧批准已使用，不能运行新查询。

生产安装包还需完整身份、最小权限、可信目录、镜像/runtime来源、broker/transport、持久anchor及独立stop/recovery；权限基线不完整处不能填猜测值。现有0.4392592秒未知CPU归属及I1–I7均保留。实际部署与真实验证仍须具体包批准；正式freeze/grant/qualification/target另依原授权和exactly-once规则。

**I1–I7 OPEN；正式准入BLOCKED；本次不是整体任务完成。**
