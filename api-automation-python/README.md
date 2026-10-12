# Python接口自动化

该目录使用`pytest + requests`实现ThingsBoard核心REST API回归。

## 目录职责

```text
clients/      封装认证、设备、遥测、告警、资产、关系和客户接口
config/       读取环境配置
tests/        描述测试场景和断言
conftest.py   公共fixture、认证和幂等测试数据准备
pytest.ini    Pytest与Allure分类配置
```

## 覆盖范围

| 模块 | 用例数 | 主要覆盖 |
|---|---:|---|
| 认证 | 4 | 正确登录、错误密码、有效JWT、无效JWT |
| 设备 | 4 | 搜索、详情、不存在、未认证 |
| 遥测 | 2 | 设备上报、摄氏转华氏并保存 |
| 告警 | 5 | 查询、详情、异常认证、自动触发与恢复 |
| 资产 | 4 | 搜索、详情、不存在、未认证 |
| 关系 | 5 | 精确关系、正向、反向、异常资源、未认证 |
| 客户与权限 | 10 | 客户资源、客户用户身份和权限边界 |
| 接口安全 | 8 | JWT篡改、敏感信息、设备凭据和对象级越权 |
| **合计** | **42** | 核心REST API回归与基础安全检查 |

## 首次运行

```powershell
cd thingsboard-testing-portfolio\api-automation-python
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

本机实际配置可以放入被Git忽略的`.env`或Postman `*.local.json`环境文件。仓库中的`.env.example`和`*.example.json`只提供变量模板。

## 执行方式

完整回归：

```powershell
.\run-regression.cmd
```

按模块运行：

```powershell
.\run-auth-tests.cmd
.\run-device-tests.cmd
.\run-telemetry-tests.cmd
.\run-alarm-tests.cmd
.\run-asset-tests.cmd
.\run-relation-tests.cmd
.\run-customer-tests.cmd
```

只运行基础安全测试：

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_security.py -v
```

也可以直接执行：

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

## 报告

回归会生成：

```text
allure-results/             Allure原始结果
allure-report/              Allure网页报告
reports/pytest-results.xml  Jenkins读取的JUnit结果
```

查看本地Allure报告：

```powershell
allure open .\allure-report
```

这些运行产物已被Git忽略，由Jenkins作为构建结果保存。

## 数据与安全

- 测试资源使用`QA_`前缀；
- 设备、资产、关系和客户资源采用幂等检查或创建；
- 已存在资源会校验，不随意修改或删除；
- 测试失败时才向Allure附加HTTP交互；
- 密码、JWT、Cookie和设备访问令牌会被脱敏；
- 安全测试会临时创建设备验证对象级权限，并在测试结束时自动删除；
- 真实`.env`和Postman本地环境不得提交。

