# 暂存修复的独立工程复核

审阅者：`/root/staged_readiness_fix_review`。范围为指定 C 暂存源码、绑定和已有构建/测试记录；仅静态审阅，未执行候选、测试或主机查询。它不替代原 `9ae3c02b` 全范围扫描的封存结果。

结论：服务名比较、路径 UNKNOWN 分类、失败句柄所有权、祖先句柄访问及其限定表述这四项修复，在指定候选源码中均正确；本次限定复核未发现新增必须修正项。审阅者核对的五个指定文件 SHA-256 均一致。

- `Read-InstallationFacts.ps1`：`4ea4e224a876f6a1c0d42144f8f5edf819172992329a7231bf2d6fca8e561054`。服务名使用 OrdinalIgnoreCase 的完整比较；只有 HRESULT `0x80070002/03` 记 ABSENT，其余错误保留 UNKNOWN、HRESULT、异常类型和消息。
- `NativeEntry.c`：`427198611682bc9aee89eace595dbb93cb1913ab8da24d9c547432879bfe28ae`。token、algorithm、hash 的拥有标记只在对应 API 成功后设置；失败的非空输出不被采用或释放。
- 源启动器：`bb230018e00b07925ae8b4dc30439321eacd61a332ef1cd1894ead6be64c1c5d`。祖先使用 GENERIC_READ/FILE_SHARE_READ，并准确承认属性写仍可能成功。
- 最终填充启动器：`9b89849c5e5636b219b29ad633f4dda43a6268bdd3a8858b4b0fc73ae9119d09`。
- 原生暂存构建产物：`469efadffe76e5a66bd6997cb215042f74f0030c3ced819e1c1e4c2eccc65816`。

已有测试只支持其限定结论：13 项纯分类与 ABI/import/解析检查，19 个实际静态函数的合成 API 返回案例、1,186 个断言。它们不证明真实 Win32 故障输出、生产隔离或完整主机覆盖。

原构建记录填充的是较早 access=0 版本的启动器；GENERIC_READ 版本是随后单独生成并复核的候选，不能把旧构建记录当作其执行验证。审阅完成后另做了一次暂存路径覆盖的文件绑定预检，日志在 `validation/final-launcher-filecheck.*`；它未执行原生入口，也不证明尚未创建的私有目录。

已知待完成事项：D 盘应用与修复提交、私有目录复制、调用器精确重绑、私有路径预检、完整追加记录与普通推送，以及新的管理员预检批准。审阅没有批准执行该包。I1–I7 全 OPEN，准入 BLOCKED。
