# C 暂存成果的追加传输记录

本目录保留先前 C 暂存目录的相对布局和原始时间语义。其中 pending、未写 D、未发布等字段描述当时的状态，不应改写为现在的事实；本文件与 v5 `FINAL_BINDINGS_V3.json` 追加记录后续进展。

当前运行源码提交 `28fd11c9c8398f5fbd85d4836970918a6ad5c711` 已应用四项修复。私有 v3 目录及新调用器只读文件绑定检查完成；尚未执行管理员查询或取得新批准。实际预检包入口是上层 `Invoke-Once-v3.ps1`，不是历史 `package/Build-Private.ps1` 或 `package/Invoke-Once.ps1`。

C 新记录完整逐字节归档到 `D:\ReBaseGuard-309\records\p309-post-root-continuation-20261016-v1`，初始 FULL_ARCHIVE_MANIFEST 含211项、469,491,929字节，后续复制/绑定记录另行追加。没有覆盖原始 capture、迁移记录、备份、旧构建或已有分支。

Git采用逐文件选择。原始 ETL、CSV、PRIVATE 身份列表、exe/obj/pdb及缓存只在本地。三份含实际 ACL/卷文件对象身份的原件留 D，公开另命名派生摘要保留原件摘要和删去字段说明。源码中必要的固定本机路径和既有 custody pin 保持原字节，以便核对实际构建。SHA清单列到本地原件不代表授权将它们加入Git。

ownership 测试相对布局 `tests/../package/NativeEntry.c` 保持，证明历史测试的实际输入。terminal 诊断源码与 `p309-offline-input-integrity-staging-v1` 保持兄弟关系。这里的脚本和命令是实际历史源码，不应当作可以自动重跑的正式准入步骤。

保存 ETL 的重新派生及输入绑定审计均完成：数字CSV SHA `8d8a412465231f1bd8aca6caa28408c1c0730cc92ab3ee60e861030565bd3d8c`，实际两遍各4,191,774行、3,829,610条CSwitch，同一已核验句柄。新证据不倒证旧执行稳定。

线程退出诊断精确复现1,328个未知区间/0.4392592秒。668个相关ThreadEnd代次最后观测切出为状态4，170代次曾在End后再次切入，最大33.8504毫秒。PID0仅DCEnd组另有297区间/0.0375085秒。没有延长归属、豁免PID0或关闭I2；原完整覆盖、保护进程、其他partition和运行时来源仍未获证明。

I1–I7全OPEN；formal admission BLOCKED。未freeze、grant、qualification或target。
