# ThingsBoard 物联网平台测试项目

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
| Python接口自动化 | 42条`pytest + requests`用例，覆盖8个业务模块 |
| UI自动化 | 6条`pytest + Playwright`冒烟用例，覆盖登录、设备查询和客户权限 |
| JMeter性能测试 | 对只读设备详情接口执行10至800线程容量探索，全部0失败，定位400至800线程拐点区间 |
| 测试数据 | 支持设备、资产、关系和客户资源的幂等检查或创建 |
| 报告与诊断 | 输出JUnit XML和Allure结果；失败时附加脱敏后的请求与响应 |
| 持续集成 | Jenkins Pipeline一次构建执行42条接口测试和6条UI冒烟测试，48条全部通过，并发布JUnit、Allure和构建产物 |
| 版本管理 | 使用Git管理测试代码，通过GitHub私有仓库保存当前成果 |

## 核心测试设计

- 使用`49.9 / 50 / 50.1`验证高温阈值边界，并验证告警自动清除。
- 验证租户管理员和客户用户的水平、垂直权限边界。
- 验证资产到设备的`Contains`关系及正向、反向查询。
- 验证摄氏温度经规则链转换为华氏温度并持久化。
- 同时覆盖有效认证、无效JWT、未认证访问、不存在资源和权限拒绝。
- 验证JWT篡改、敏感凭据访问和已分配/未分配设备的对象级权限边界。
- 使用JMeter逐级提高并发，通过吞吐增幅、平均响应、P95和容器CPU共同判断容量拐点。
- 自动化执行前检查环境和测试数据，避免把环境问题误判为产品缺陷。

详细测试策略见[测试策略](docs/TEST_STRATEGY.md)，执行结果见[测试报告](docs/TEST_REPORT.md)。

## 性能测试结果

对`GET /api/device/{deviceId}`只读接口执行闭环并发容量探索。每个线程在请求完成后等待100 ms，以下数据使用每档最后10秒稳态窗口：

| 线程数 | 失败数 | 平均响应 | P95 | 稳态吞吐 |
|---:|---:|---:|---:|---:|
| 10 | 0 | 4.75 ms | 7 ms | 88.70/s |
| 25 | 0 | 4.40 ms | 6 ms | 221.70/s |
| 50 | 0 | 4.46 ms | 6 ms | 445.40/s |
| 100 | 0 | 5.07 ms | 8 ms | 875.70/s |
| 200 | 0 | 8.46 ms | 17 ms | 1677.00/s |
| 400 | 0 | 9.58 ms | 20 ms | 3274.30/s |
| 800 | 0 | 55.78 ms | 121 ms | 4219.60/s |

10至400线程时吞吐基本随并发增长；400至800线程时线程翻倍，但稳态吞吐只增长约28.9%，平均响应增长约5.8倍、P95增长约6.1倍。因此，本机单节点测试的明显拐点位于400至800线程之间，400线程档更接近低延迟稳定区上边界。

该结果来自JMeter与ThingsBoard Docker同机的短时单接口测试，只用于展示容量探索方法，不能直接外推生产容量或SLA。完整数据见[容量测试摘要](performance-testing/capacity-comparison.txt)。

## 技术栈

```text
ThingsBoard + Docker Compose
Postman / Postman CLI
Python + pytest + requests
Playwright
Apache JMeter
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
├─ ui-automation-python/
│  ├─ pages/
│  ├─ tests/
│  ├─ requirements.txt
│  └─ run-ui-smoke.cmd
├─ performance-testing/
│  ├─ thingsboard-device-read.jmx
│  ├─ run-performance.cmd
│  └─ capacity-comparison.txt
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

运行JMeter性能场景前，需要安装JMeter并设置`JMETER_HOME`或把`jmeter.bat`加入`PATH`：

```powershell
cd performance-testing
$env:PERF_THREADS='100'
$env:PERF_RAMP_SECONDS='15'
$env:PERF_DURATION_SECONDS='30'
$env:PERF_PACING_MS='100'
.\run-performance.cmd
```

JTL、HTML报告和日志只保存在本机，不提交到Git。

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
- [Jenkins流水线成功](evidence/screenshots/jenkins-build-success.png)
- [Jenkins阶段视图](evidence/screenshots/jenkins-pipeline-overview.png)
- [接口与UI自动化Allure总览](evidence/screenshots/allure-api-ui-regression-overview.png)
- [JMeter容量测试数据](performance-testing/capacity-comparison.txt)
