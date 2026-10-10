# Python 接口自动化状态

## 已迁移范围

| 模块 | 用例数量 | 主要覆盖内容 |
|---|---:|---|
| Authentication | 4 | 正确登录、错误密码、有效 JWT、无效 JWT |
| Devices | 4 | 搜索、详情、不存在、未认证 |
| Telemetry | 2 | 设备上报、摄氏转华氏并保存 |
| Alarms | 5 | 告警列表、详情、不存在、未认证、自动触发与恢复 |
| Assets | 4 | 搜索、详情、不存在、未认证 |
| Relations | 5 | 精确关系、正向、反向、不存在、未认证 |
| Customers and Permissions | 10 | 客户资源及客户用户权限边界 |
| **合计** | **34** | 核心 REST API 回归链路 |

## 当前执行方式

单模块运行：

```powershell
.\run-auth-tests.cmd
.\run-device-tests.cmd
.\run-telemetry-tests.cmd
.\run-alarm-tests.cmd
.\run-asset-tests.cmd
.\run-relation-tests.cmd
.\run-customer-tests.cmd
```

全部回归并生成报告：

```powershell
.\run-regression.cmd
```

## 通过标准

- 全部 33 条测试通过。
- pytest 进程退出码为 `0`。
- Allure 报告没有失败用例，并按七个业务模块展示。
- JUnit XML 中 failures 和 errors 均为 `0`。
- 测试报告及终端输出不包含密码、JWT 或设备访问令牌。

## 后续增强

1. 将 `run-regression.cmd` 接入 CI。
2. 增加数据清理策略，减少对长期固定测试数据的依赖。
3. 根据风险补充参数边界、响应时间和并发场景。
4. 当接口版本发生变化时，对照本机 Swagger 更新客户端封装。

