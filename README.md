# ThingsBoard 物联网平台测试项目

> 当前为持续完善中的测试作品集。已完成的成果与后续计划分开列出，避免把计划内容写成既有成果。

## 项目简介

本项目围绕 ThingsBoard 物联网平台的温度监控业务，验证从设备接入、遥测上报、规则处理、告警产生与恢复、仪表板展示，到客户用户授权与数据隔离的完整链路。

```text
设备接入 → 遥测上报 → 规则链处理 → 高温告警 → 仪表板展示 → 客户权限隔离
```

## 已完成成果

| 测试层级 | 已验证成果 |
|---|---|
| 功能与业务流程 | 30条执行记录，覆盖设备、遥测、告警边界、仪表板、资产关系、权限和规则链 |
| Postman接口测试 | 36个请求、117个断言，一次完整集合回归失败数为0 |
| Python接口自动化 | 34条`pytest + requests`用例，覆盖7个业务模块 |
| 测试数据 | 支持设备、资产、关系和客户资源的幂等检查或创建 |
| 报告与诊断 | 输出JUnit XML和Allure结果；失败时附加脱敏后的请求与响应 |
| 持续集成 | Jenkins Pipeline执行环境预检、接口回归、JUnit发布、Allure发布和产物归档 |
| 版本管理 | 使用Git管理测试代码，通过GitHub私有仓库保存当前成果 |

## 核心测试设计

- 使用`49.9 / 50 / 50.1`验证高温阈值边界，并验证告警自动清除。
- 验证租户管理员和客户用户的水平、垂直权限边界。
- 验证资产到设备的`Contains`关系及正向、反向查询。
- 验证摄氏温度经规则链转换为华氏温度并持久化。
- 同时覆盖有效认证、无效JWT、未认证访问、不存在资源和权限拒绝。
- 自动化执行前检查环境和测试数据，避免把环境问题误判为产品缺陷。

详细测试策略见[测试策略](docs/TEST_STRATEGY.md)，执行结果见[测试报告](docs/TEST_REPORT.md)。

## 技术栈

```text
ThingsBoard + Docker Compose
Postman / Postman CLI
Python + pytest + requests
Jenkins Pipeline
JUnit + Allure
Git + GitHub
```

## 仓库结构

```text
test-project/
├─ README.md
├─ Jenkinsfile
├─ docs/
│  ├─ TEST_STRATEGY.md
│  └─ TEST_REPORT.md
├─ postman/
│  ├─ ThingsBoard_REST_API_Tests.postman_collection.json
│  ├─ ThingsBoard_Local.postman_environment.example.json
│  └─ run-postman-regression.cmd
├─ api-automation-python/
│  ├─ clients/
│  ├─ config/
│  ├─ tests/
│  ├─ requirements.txt
│  ├─ pytest.ini
│  └─ run-regression.cmd
└─ evidence/screenshots/
```

## 快速运行

运行前需要启动 ThingsBoard，并准备仅保存在本机的环境变量和测试账号。

```powershell
cd api-automation-python
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\run-regression.cmd
```

运行 Postman 集合：

```powershell
cd postman
.\run-postman-regression.cmd
```

真实`.env`、Postman本地环境、密码、JWT和设备访问令牌不会提交到Git。

## 精选证据

- [设备创建与接入](evidence/screenshots/device-created-connectivity.png)
- [高温告警激活](evidence/screenshots/high-temperature-alarm-active.png)
- [高温告警清除](evidence/screenshots/high-temperature-alarm-cleared.png)
- [最新温度仪表板](evidence/screenshots/dashboard-latest-temperature.png)
- [温度历史趋势](evidence/screenshots/dashboard-temperature-history.png)
- [资产包含设备关系](evidence/screenshots/asset-contains-device-relation.png)
- [客户用户只读仪表板](evidence/screenshots/customer-user-dashboard-readonly.png)
- [温度转换规则链](evidence/screenshots/temperature-rule-chain.png)
- [Postman登录成功](evidence/screenshots/postman-login-success.png)
- [Postman未认证访问](evidence/screenshots/postman-device-without-jwt.png)

## 后续计划

- 配置GitHub提交触发Jenkins自动构建；
- 增加少量高价值的Playwright UI冒烟自动化；
- 增加性能基线和基础安全测试；
- 评估独立Jenkins Agent或容器化执行；
- 完成公开发布前的脱敏和材料复查。
