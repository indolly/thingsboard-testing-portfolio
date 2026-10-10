# ThingsBoard Python 接口自动化

这个目录把已经在 Postman 中验证过的接口用例逐步迁移到 `pytest + requests`。

## 这一步是干嘛的

- `requests`：发送 HTTP 请求，相当于代码里的 Postman。
- `pytest`：发现并执行用例、判断断言、汇总通过和失败结果。
- Postman `local.json`：默认复用已经填写好的本机地址和账号密码。
- `.env`：可选的覆盖配置；需要切换环境时使用。
- `clients/`：集中封装接口调用，避免每条用例重复拼接 URL 和请求头。
- `tests/`：只描述测试场景、操作和预期结果。

当前已经迁移认证模块 `AUTH-001～AUTH-004`、设备模块
`DEVICE-001～DEVICE-004`、遥测模块 `TELEMETRY-001～TELEMETRY-002`
和告警模块 `ALARM-001～ALARM-004`。下一步迁移资产关系和客户权限模块。

## 第一次运行

在 PowerShell 中执行：

```powershell
cd D:\study\softtest\ThingsBoard\thingsboard\test-project\api-automation-python

# 虚拟环境会创建在当前 D 盘项目内，不会安装到 C 盘全局目录。
python -m venv .venv

# 使用虚拟环境里的 Python 安装依赖，不需要激活 PowerShell 脚本。
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

```

Python 默认读取已有的文件：

```text
..\postman\ThingsBoard_Local.postman_environment.local.json
```

需要确认其中至少存在并启用了以下变量：

```text
baseUrl
tenantUsername
tenantPassword
```

然后运行：

```powershell
.\run-auth-tests.cmd
```

也可以直接执行：

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_auth.py -v
```

## 通过标准

终端末尾应显示 `4 passed`。四条用例分别验证：

1. 有效账号登录返回 `200` 和非空 JWT。
2. 错误密码返回 `401`，响应中没有 JWT。
3. 有效 JWT 能查询当前租户管理员。
4. 伪造 JWT 返回 `401`，响应中没有用户信息。

## 运行设备模块

```powershell
.\run-device-tests.cmd
```

设备模块预期显示 `4 passed`，分别验证：

1. 按名称搜索并找到目标设备。
2. 复用查询得到的 `deviceId` 获取设备详情。
3. 不存在的设备 ID 返回 `404`。
4. 不携带 JWT 查询设备返回 `401`。

## 运行遥测模块

```powershell
.\run-telemetry-tests.cmd
```

遥测模块预期显示 `2 passed`，分别验证：

1. 使用设备访问令牌上报 `temperature=20`，返回 `200` 和空响应体。
2. 使用租户 JWT 查询最新遥测，得到 `temperature=20`，并得到规则链转换的 `temperatureF=68`。

这里有两套不同的认证方式：设备上报使用 URL 中的 `deviceToken`；平台管理接口查询使用请求头中的租户 JWT。不要混用。

## 运行告警模块

```powershell
.\run-alarm-tests.cmd
```

告警模块预期显示 `5 passed`，分别验证：

1. 查询设备告警列表并找到 `High Temperature`。
2. 使用查询得到的 `alarmId` 获取告警详情。
3. 不存在的告警 ID 返回 `404`。
4. 不携带 JWT 查询告警返回 `401`。
5. 自动发送高温触发告警，并在 `finally` 中发送恢复温度清除告警；
   默认最多轮询 30 秒，自动清除失败时手工清理环境但仍报告测试失败。

告警查询使用 `searchStatus=ANY`，因此激活和已清除的告警都可以作为测试基线。

## 运行资产实体模块

```powershell
.\run-asset-tests.cmd
```

资产实体模块预期显示 `4 passed`，分别验证：

1. 按名称搜索并找到 `QA_FACTORY_001`。
2. 使用查询得到的 `assetId` 获取资产详情。
3. 不存在的资产 ID 返回 `404`。
4. 不携带 JWT 查询资产返回 `401`。

资产表示工厂、楼宇、车间等非设备实体。下一组关系测试会验证
`QA_FACTORY_001 --Contains--> QA_TEMP_DEVICE_001`。

## 运行资产关系模块

```powershell
.\run-relation-tests.cmd
```

关系模块预期显示 `5 passed`，分别验证：

1. 精确查询资产到设备的 `Contains` 关系。
2. 从资产向外查询时包含目标设备。
3. 从设备反向查询时包含目标资产。
4. 不存在的资产查询关系返回 `404`，不是空数组。
5. 不携带 JWT 查询关系返回 `401`。

## 运行客户与权限模块

```powershell
.\run-customer-tests.cmd
```

客户模块预期显示 `10 passed`，覆盖：客户查询和详情、已分配资产、
已分配设备、仪表板分页、未认证访问、客户用户登录、身份信息、
访问已分配设备，以及客户用户不能查看全部客户的 `403` 权限边界。

## 运行完整回归并生成 Allure 报告

第一次增加 Allure 功能后，需要更新一次 Python 依赖：

```powershell
.\.venv\Scripts\python.exe -m pip install `
  --index-url https://pypi.org/simple `
  --no-cache-dir `
  -r .\requirements.txt
```

之后执行：

```powershell
.\run-regression.cmd
```

完整回归入口会同时生成 Allure 和 JUnit 结果：

```text
allure-results\             Allure原始结果
allure-report\              Allure网页报告
reports\pytest-results.xml
```

- Allure 报告供测试人员和面试展示查看。
- JUnit XML 供 Jenkins、GitHub Actions 等 CI 系统读取。
- 查看报告使用 `allure open .\allure-report`，不要直接双击 index.html。
- 报告目录已被 Git 忽略，避免提交每次运行产生的临时证据。

## 自动测试数据准备

测试数据采用按需、幂等策略：

- 设备、资产、客户按 `QA_*` 名称查找，不存在才创建。
- 设备会使用 `QA_TEMPERATURE_PROFILE` 创建；已有设备会校验 profile，
  但不会自动修改现有配置。
- 设备访问令牌从目标设备凭据实时读取，不依赖手工复制。
- `Contains` 关系不存在时自动创建。
- 客户缺少资产或设备分配时自动补齐。
- 不自动删除已有实体，避免误删共享测试环境数据。

客户用户账号仍需要预先存在，因为用户激活和密码设置属于身份生命周期，
不应由普通回归测试随意重置。

设备配置档案和规则链属于测试基础设施，也不会由普通回归测试自动重建；
缺失时会给出明确失败信息。

## Allure 失败证据与脱敏

所有客户端统一记录 HTTP 交互，但只有用例失败时才附加到 Allure。
密码、JWT、设备访问令牌、Cookie 和敏感响应字段会替换为
`***REDACTED***`，超长响应会截断。

## 安全规则

- `ThingsBoard_Local.postman_environment.local.json` 是实际执行环境，不要提交。
- `ThingsBoard_Local.postman_environment.example.json` 是空值模板，不用于执行。
- `.env` 已被 `.gitignore` 忽略，不要把真实密码或 JWT 写入其他文件。
- `.env.example` 只保留变量名和安全示例值，可以提交。
- 测试失败时只输出必要的响应片段，不打印密码或 JWT。

