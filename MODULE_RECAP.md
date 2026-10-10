# ThingsBoard测试板块回顾

> 用途：每完成一个测试板块，记录“为什么做、具体怎么做、用了什么命令或代码、产生了什么文件、如何验证、发现了什么问题”，用于复盘和面试回忆。

## 板块一：Docker环境与HTTP设备接入

### 1. 板块目标

- 确认ThingsBoard单节点环境能够稳定运行和重启。
- 创建独立的温度测试设备。
- 从Linux客户端使用设备Token发送HTTP遥测。
- 验证设备状态、数据存储和UI展示的完整链路。
- 建立凭据脱敏和GitHub发布规则。

### 2. 环境怎么验证

使用Docker Compose和Docker命令检查：

```text
docker compose ps
docker compose images
docker inspect
docker stats --no-stream
docker logs
```

实际确认：

- ThingsBoard版本：4.2.1.1。
- 容器：`thingsboard-thingsboard-1`。
- Web端口：宿主机9091映射到容器9090。
- MQTT端口：1883。
- 数据目录和日志目录均进行了宿主机持久化。
- 容器状态为running，Exit=0，OOM=false。
- 首页返回HTTP 200。
- 手工重启后46.02秒恢复HTTP 200，应用自身启动耗时27.892秒。

对应文档：`ENVIRONMENT_BASELINE.md`。

### 3. 测试设备怎么创建

在租户管理员页面使用“添加设备”向导创建：

| 字段 | 实际值 |
|---|---|
| 名称 | `QA_TEMP_DEVICE_001` |
| 标签 | `温度传感器-001` |
| 设备配置 | `default` |
| 是否网关 | 否 |
| 分配给客户 | 暂不分配 |
| 说明 | `ThingsBoard测试项目-温度遥测设备` |
| 凭据类型 | Access Token |

测试数据使用`QA_`前缀，避免与环境原有设备混淆。

### 4. Token怎么处理

凭据页面会显示设备Token。第一次截图包含Token，因此没有保存到项目证据目录，也禁止上传GitHub。

使用PowerShell生成新的32字符随机Token：

```powershell
$newToken = [guid]::NewGuid().ToString("N")
Set-Clipboard -Value $newToken
```

在Ubuntu中使用静默输入读取Token，避免显示在终端：

```bash
read -r -s -p "请输入设备Access Token: " TB_DEVICE_TOKEN
echo
```

随后将平台地址和Token保存到本地`.env`。真实`.env`被`.gitignore`排除，仓库只保留`.env.example`。

### 5. 为什么先检查网络

发送带Token的业务请求前，先从WSL Ubuntu访问平台首页：

```bash
curl --silent --show-error \
  --output /dev/null \
  --write-out 'HTTP=%{http_code} CONNECT=%{time_connect}s TOTAL=%{time_total}s\n' \
  http://localhost:9091/
```

结果：HTTP 200，连接耗时0.000343秒，总耗时0.012148秒。

这样先排除Linux到ThingsBoard之间的网络和端口问题。如果业务请求失败，可以集中检查Token、API路径和JSON数据。

### 6. 遥测是怎么上报的

使用ThingsBoard设备HTTP遥测接口：

```text
POST http://localhost:9091/api/v1/<DEVICE_TOKEN>/telemetry
```

实际执行的脱敏命令：

```bash
curl --silent --show-error \
  --output /dev/null \
  --write-out 'HTTP=%{http_code} TOTAL=%{time_total}s\n' \
  --request POST \
  --url "${TB_BASE_URL}/api/v1/${TB_DEVICE_TOKEN}/telemetry" \
  --header 'Content-Type: application/json' \
  --data '{"temperature":25,"humidity":60}'
```

请求数据：

```json
{
  "temperature": 25,
  "humidity": 60
}
```

执行结果：HTTP 200，总耗时0.610105秒。

### 7. 如何验证结果

接口返回成功后，在ThingsBoard设备列表和设备详情中继续验证：

- `QA_TEMP_DEVICE_001`从非活动变为活动。
- 最新遥测出现`temperature=25`。
- 最新遥测出现`humidity=60`。
- 两个键的更新时间一致。

这证明链路已经覆盖：

```text
Linux curl模拟设备
  → Access Token认证
  → HTTP遥测接口接收JSON
  → ThingsBoard保存时序数据
  → 更新设备活动状态
  → Web页面查询并展示最新值
```

正式用例记录：`TEST_EXECUTION_LOG.md`中的`TC-HTTP-TEL-001`。

### 8. 为什么设备后来又变成非活动

设备状态不是永久有效。当前Compose没有覆盖活动超时配置，因此使用默认规则：连续600秒（10分钟）没有收到设备消息，平台会将设备标记为非活动；状态检查默认每60秒执行一次。

本项目通过HTTP发送的是一次性请求，不会保持长连接。因此上报时设备变为活动，停止上报一段时间后变为非活动是符合预期的。已经保存的`temperature`和`humidity`不会因此过期或删除。

### 9. 本板块发现的问题与风险

- 设备接入向导生成的示例地址使用`localhost:8080`，实际Docker宿主机端口为9091，原命令不能直接用于当前环境。
- 镜像使用`latest`标签，重新拉取后可能发生版本漂移。
- Gateway扩展仓库因网络原因同步失败，但不影响本板块核心功能。
- 截图和自动化报告可能泄露Token、登录邮箱和实体ID，必须按发布清单脱敏。

### 10. 产生的项目文件

- `ENVIRONMENT_BASELINE.md`：环境基线和故障排查。
- `REQUIREMENTS_AND_SCOPE.md`：需求、业务规则和范围。
- `TEST_EXECUTION_LOG.md`：标准测试用例及执行结果。
- `.env`：本地真实配置，禁止上传。
- `.env.example`：公开配置模板，可以上传。
- `.gitignore`：阻止敏感文件进入仓库。
- `GITHUB_PUBLISHING_GUIDE.md`：GitHub脱敏与发布规则。

### 11. 面试回忆要点

- 为什么先验证网络再发送业务请求：减少排查变量，体现分层定位思路。
- 为什么使用环境变量保存Token：避免把凭据写死在命令、代码和Git仓库中。
- 为什么接口200后还要检查UI：HTTP成功只证明请求被接受，还要验证存储、状态更新和展示链路。
- 为什么设备会从活动变成非活动：设备状态由最近活动时间和超时规则动态维护，不代表遥测数据丢失。

## 板块二：高温告警边界与自动清除

### 1. 板块目标

- 为温度设备创建独立配置，避免修改默认配置影响其他设备。
- 验证高温告警在阈值下方、等于阈值和阈值上方的行为。
- 验证温度回落后由规则自动清除告警，而不是人工清除。
- 保存能够公开到GitHub的告警创建和清除证据。

### 2. 设备配置怎么建立

创建专用设备配置`QA_TEMPERATURE_PROFILE`，并将`QA_TEMP_DEVICE_001`从`default`切换到该配置。传输方式保持“默认”，继续兼容现有HTTP Access Token接入方式。

告警规则配置如下：

| 配置项 | 实际值 |
|---|---|
| 告警类型 | `High Temperature` |
| 严重程度 | MAJOR（页面显示“重要”） |
| 创建条件 | `temperature > 50` |
| 清除条件 | `temperature <= 50` |
| 传播告警 | 关闭 |
| 启用规则 | 始终启用 |

配置过程中曾把`temperature > 50`和`temperature <= 50`同时放进创建条件，并使用AND连接。审查后发现该条件不可能成立，因此删除错误条件，将`<= 50`单独配置为清除条件。这体现了测试前对业务规则逻辑进行评审的重要性。

### 3. 边界值怎么设计

围绕阈值50使用边界值分析法选取三组数据：

| 测试值 | 与阈值关系 | 预期行为 | 实际结果 |
|---:|---|---|---|
| 49.9 | 刚好低于阈值 | 不产生告警 | HTTP 200，未产生告警 |
| 50 | 等于阈值 | 不产生告警 | HTTP 200，未产生告警 |
| 50.1 | 刚好高于阈值 | 产生MAJOR告警 | HTTP 200，产生激活未确认告警 |

这样不仅验证正常值，还验证了运算符是严格大于`>`，而不是大于等于`>=`。

### 4. 遥测怎么发送

每组数据都通过Linux中的curl调用同一个设备遥测接口，只替换JSON中的温度值。以触发告警的50.1为例：

```bash
curl --silent --show-error \
  --output /dev/null \
  --write-out 'HTTP=%{http_code} TOTAL=%{time_total}s\n' \
  --request POST \
  --url "${TB_BASE_URL}/api/v1/${TB_DEVICE_TOKEN}/telemetry" \
  --header 'Content-Type: application/json' \
  --data '{"temperature":50.1}'
```

真实平台地址和设备Token来自本地`.env`，没有写入测试记录、截图或Git仓库。

### 5. 告警怎么验证

发送50.1后，接口返回HTTP 200，最新遥测显示`temperature=50.1`。设备告警详情显示：

- 类型为`High Temperature`。
- 严重程度为“重要”（MAJOR）。
- 状态为“激活未确认”。
- 发起者为温度测试设备。

关键证据：`evidence/screenshots/high-temperature-alarm-active.png`。

### 6. 自动清除怎么验证

保持告警处于活动状态，不点击页面的人工“清除”按钮，再通过同一接口上报：

```json
{"temperature": 50}
```

实际结果：HTTP 200，最新遥测为50；活动告警列表变为空，通知中心显示`Alarm 'High Temperature' - cleared`。这证明命中的是`temperature <= 50`自动清除条件，而不是人工修改状态。

关键证据：`evidence/screenshots/high-temperature-alarm-cleared.png`。

### 7. 为什么49.9后来不在最新遥测中

“最新遥测数据”对每一个键只显示最后一次上报值。后续发送50和50.1时，页面中的`temperature`会更新为最新值；49.9仍属于历史时序数据，并非被删除。后续将在仪表板或历史遥测接口中验证完整趋势。

### 8. 本板块形成的闭环

```text
设备绑定专用配置
  → HTTP上报温度边界值
  → 规则判断temperature > 50
  → 生成High Temperature告警
  → 温度回落到50
  → 命中temperature <= 50
  → 自动清除告警
```

正式用例：`TC-ALARM-001`至`TC-ALARM-004`，加上前一板块HTTP遥测用例，目前累计执行5条，全部通过。

### 9. 面试回忆要点

- 为什么建立独立设备配置：隔离测试范围，避免修改默认配置影响环境中的其他设备。
- 为什么测试49.9、50和50.1：覆盖阈值下方、阈值本身和阈值上方，验证比较运算符边界。
- 为什么不点击人工清除：需要证明业务规则能够根据遥测值自动完成状态转换。
- 为什么HTTP 200后仍检查告警：200只表示遥测请求被平台接收，还要验证规则处理和告警状态结果。

### 10. 告警应答怎么验证

再次上报`temperature=51`产生告警，接口返回HTTP 200，最新遥测为51。打开告警详情并点击“应答”后，状态从“激活未确认”变为“激活已确认”，告警仍保持激活，页面仍提供“清除”按钮。

这说明“应答”表示人员已经看到并处理告警，但不会改变告警触发条件，也不会代替清除操作。

关键证据：`evidence/screenshots/high-temperature-alarm-acknowledged.png`。

### 11. 已确认告警的最终状态怎么验证

在告警处于“激活已确认”时，不点击人工清除按钮，通过HTTP上报`temperature=50`。接口返回HTTP 200，最新遥测为50。

由于当前版本的告警筛选器没有单独的“全部”选项，因此使用组合条件查询历史状态：取消“激活”，同时选择“已清除”和“已确认”。筛选后找到最新的`High Temperature`告警，详情状态为“清除已确认”（内部状态可表示为`CLEARED_ACK`）。

最终生命周期得到验证：

```text
temperature=51
  → 激活未确认
点击应答
  → 激活已确认
temperature=50
  → 清除已确认
```

截至本步骤，累计执行7条用例，全部通过；告警模块已经覆盖阈值边界、创建、应答、自动清除以及状态组合筛选。

## 板块三：温度监控仪表板

### 1. 板块目标

- 创建独立的测试仪表板。
- 展示设备最新温度。
- 查询并展示历史温度趋势。
- 验证新遥测能够驱动多个部件同步更新。
- 在同一页面展示高温告警历史和状态。

### 2. 仪表板与部件怎么配置

创建`QA_TEMPERATURE_DASHBOARD`，暂不分配客户，避免在功能验证阶段混入权限变量。仪表板包含三个核心部件：

| 部件 | 数据源与配置 | 验证目标 |
|---|---|---|
| Value card | `QA_TEMP_DEVICE_001`的`temperature`最新值，单位°C | 当前温度展示 |
| Line chart | 同一设备的`temperature`，部件时间窗口最近7天 | 历史时序查询和趋势展示 |
| Alarms table | 同一设备、最近7天、`High Temperature`、严重程度重要 | 告警记录和状态展示 |

### 3. 最新温度怎么验证

Value card保存后显示“当前温度”和50°C，并显示最近更新时间，证明仪表板能够读取设备最新遥测。

证据：`evidence/screenshots/dashboard-latest-temperature.png`。

### 4. 历史趋势怎么验证

Line chart使用独立的“实时－最后7天”部件时间窗口，成功展示此前通过HTTP上报的多个温度点，包括25、49.9、50、50.1和51°C，并显示平均值。部件时间窗口不受页面顶部全局“最后1分”影响，证明局部时间配置生效。

证据：`evidence/screenshots/dashboard-temperature-history.png`。

### 5. 实时更新怎么验证

通过Linux curl再次调用设备遥测接口：

```bash
curl --silent --show-error \
  --output /dev/null \
  --write-out 'HTTP=%{http_code} TOTAL=%{time_total}s\n' \
  --request POST \
  --url "${TB_BASE_URL}/api/v1/${TB_DEVICE_TOKEN}/telemetry" \
  --header 'Content-Type: application/json' \
  --data '{"temperature":42}'
```

接口返回HTTP 200后，最新值卡片更新为42°C，历史图最右侧同步增加42°C数据点，验证了“一次上报、多部件一致更新”。

证据：`evidence/screenshots/dashboard-realtime-update.png`。

### 6. 告警表格怎么验证

Alarms table按设备、最近7天、类型`High Temperature`和严重程度“重要”过滤，显示2条历史告警。两条记录的状态分别为“清除已确认”和“清除未确认”，与前一板块执行的告警生命周期一致。

证据：`evidence/screenshots/dashboard-alarm-table.png`。

### 7. 本板块形成的链路

```text
HTTP上报temperature
  → ThingsBoard保存最新值与历史时序
  → Value card显示当前温度
  → Line chart展示7天趋势
  → 告警规则产生/清除High Temperature
  → Alarms table展示告警历史和状态
```

### 8. 面试回忆要点

- 为什么分别使用最新值卡片和折线图：一个验证当前状态，一个验证时序数据查询，两者覆盖不同数据接口和展示逻辑。
- 为什么使用部件时间窗口：确保历史图和告警表格能够独立展示7天数据，不被仪表板全局时间范围限制。
- 为什么上报42°C做实时验证：它与旧值不同且低于告警阈值，能验证展示更新，同时避免产生新的高温告警干扰。
- 为什么告警表格关闭确认和清除操作：当前目标是只读监控，降低误操作改变测试数据状态的风险。

本板块对应`TC-DASH-001`至`TC-DASH-005`。截至完成时，项目累计执行12条标准用例，全部通过。

## 板块四：资产与设备实体关系

### 1. 板块目标

- 创建独立的工厂测试资产。
- 建立资产包含设备的定向关系。
- 从资产和设备两端验证同一关系。
- 验证删除关系不会级联删除实体。
- 恢复关系作为后续权限与规则链测试基线。

### 2. 测试数据

| 实体 | 名称 | 说明 |
|---|---|---|
| 资产 | `QA_FACTORY_001` | 使用default资产配置，暂不分配客户 |
| 设备 | `QA_TEMP_DEVICE_001` | 前序板块创建的温度设备 |
| 关系 | `Contains` | `QA_FACTORY_001 → QA_TEMP_DEVICE_001` |

### 3. 关系创建与双向查询怎么验证

从资产关联页建立方向From、类型`Contains`、目标为温度设备的关系。资产侧“向外的关联”显示目标设备；随后在设备侧选择方向To，“向内的关联”显示来源资产`QA_FACTORY_001`。

```text
QA_FACTORY_001（资产）
  --Contains-->
QA_TEMP_DEVICE_001（设备）
```

证据：

- `evidence/screenshots/asset-contains-device-relation.png`
- `evidence/screenshots/device-inbound-asset-relation.png`

### 4. 关系删除怎么验证

从设备侧删除该关系后：

- 设备向内关联记录消失。
- 资产向外关联记录同步消失。
- 资产和设备实体仍然存在。

这证明删除的是独立关系记录，没有错误级联删除两端实体。验证后重新建立相同关系，保证后续测试数据完整。

### 5. 本板块形成的覆盖

```text
创建资产
  → 建立资产到设备的Contains关系
  → 资产侧正向查询
  → 设备侧反向查询
  → 删除关系并验证两端同步
  → 验证实体不被级联删除
  → 恢复关系
```

### 6. 面试回忆要点

- 实体关系有方向性，`资产 → 设备`与`设备 → 资产`语义不同，配置时必须明确From和To。
- 双向页面展示的是同一条关系的两个观察方向，不是两条独立关系。
- 删除关系后要同时检查两端和实体本身，避免只看到列表为空就忽略级联删除风险。

本板块对应`TC-ASSET-001`至`TC-ASSET-004`。截至完成时，项目累计执行16条标准用例，全部通过。

## 板块五：客户用户与资源权限隔离

### 1. 板块目标

- 创建独立测试客户和客户用户。
- 验证客户用户未授权时默认不可见租户资源。
- 将资产、设备、仪表板逐项授权，验证权限增量。
- 验证实体关系不能泄露未授权设备。
- 验证客户用户只能查看仪表板，不能编辑或访问租户级菜单。
- 验证撤销授权后列表和直接URL立即失效。

### 2. 测试账号与凭据处理

创建客户`QA_CUSTOMER_001`及客户用户`qa.customer.001@example.com`。由于Docker环境未配置SMTP，选择“显示激活链接”，在无痕窗口打开一次性链接并设置随机密码。

激活链接和真实密码均未截图、未写入文档；账号和密码仅保存在被`.gitignore`排除的本地`.env`中。

### 3. 零资源权限怎么验证

客户初始未分配任何资源。用户激活并登录后：

- 看不到`QA_FACTORY_001`。
- 看不到`QA_TEMP_DEVICE_001`。
- 看不到`QA_TEMPERATURE_DASHBOARD`。
- 看不到客户管理和规则链菜单。

这验证了新客户采用默认最小权限，而不是继承租户全部资源。

### 4. 逐项授权怎么验证

按资产、设备、仪表板顺序逐项分配：

| 授权阶段 | 资产 | 设备 | 仪表板 |
|---|---|---|---|
| 初始未授权 | 不可见 | 不可见 | 不可见 |
| 仅分配资产 | 可见 | 不可见 | 不可见 |
| 再分配设备 | 可见 | 可见 | 不可见 |
| 再分配仪表板 | 可见 | 可见 | 可见 |

仅分配资产时，客户用户在资产关联页也看不到未授权设备；设备分配后，资产From关联和设备To关联同时可见。这证明实体关系查询同样受目标实体权限控制。

### 5. 垂直权限怎么验证

仪表板授权后，客户用户能够查看当前温度、历史趋势和告警记录，但页面没有编辑、添加部件或保存入口，同时客户管理和规则链菜单仍不可见。

证据：`evidence/screenshots/customer-user-dashboard-readonly.png`。

### 6. 撤权和直接URL怎么验证

保持客户用户仪表板页面打开，由租户管理员撤销仪表板分配。客户用户刷新原页面后显示“未找到仪表板”，仪表板列表同步移除，而资产和设备仍然可见。

这说明：

- 撤权能够立即生效。
- 直接使用原页面URL不能绕过授权。
- 撤销单个资源不会错误影响其他资源权限。

验证结束后重新分配仪表板，恢复最终演示基线。

### 7. 本板块形成的覆盖

```text
创建客户
  → 创建并激活客户用户
  → 验证零资源默认隔离
  → 逐项分配资产、设备、仪表板
  → 验证关系不能绕过授权
  → 验证仪表板只读和租户菜单隔离
  → 撤销仪表板并验证直接URL失效
  → 恢复最终授权基线
```

角色矩阵：`ROLE_PERMISSION_MATRIX.md`。

本板块对应`TC-PERM-001`至`TC-PERM-010`。截至完成时，项目累计执行26条标准用例，全部通过。

## 板块六：规则链数据转换与回归

### 1. 板块目标

- 理解规则链作为设备消息处理流水线的作用。
- 使用TBEL脚本将摄氏温度转换为华氏温度。
- 将转换后的数据保存为设备时序遥测。
- 验证缺少温度字段时脚本能够安全跳过转换。
- 测试后恢复根规则链，并回归验证原高温告警流程。

### 2. 规则链配置

创建非根规则链`QA_TEMPERATURE_RULE_CHAIN`，建立以下处理路径：

```text
Input
  → Calculate Fahrenheit（script）
  → Save Temperature Timeseries（save time series）
```

TBEL脚本：

```javascript
if (msg.temperature != null) {
    msg.temperatureF = msg.temperature * 9 / 5 + 32;
}
return {
    msg: msg,
    metadata: metadata,
    msgType: msgType
};
```

`if`判断保证只有消息存在`temperature`时才执行换算；返回值保留原消息、元数据和消息类型，使后续保存节点可以继续处理同一条消息。

### 3. 正常转换怎么验证

将`QA_TEMPERATURE_PROFILE`的默认规则链临时调整为`QA_TEMPERATURE_RULE_CHAIN`，通过HTTP上报：

```json
{"temperature": 20}
```

接口返回HTTP 200，设备最新遥测同时显示`temperature=20`和`temperatureF=68.0`，且更新时间一致，验证了消息接收、脚本转换和时序保存的完整链路。

### 4. 缺少字段怎么验证

仅上报：

```json
{"humidity": 66}
```

接口仍返回HTTP 200；`humidity`更新为66，而`temperature=20`和`temperatureF=68.0`的值与更新时间均保持不变。这证明脚本在缺少温度字段时不会错误计算，也不会阻断其他遥测字段的保存。

### 5. 为什么要恢复根规则链

专项规则链只包含转换和保存节点，不承担原根规则链中的完整设备配置及告警处理职责。测试结束后，将`QA_TEMPERATURE_PROFILE`恢复为`Root Rule Chain`，再依次上报51和50：

- 51°C成功产生`High Temperature`重要告警。
- 50°C成功自动清除告警。

这证明测试配置已恢复，规则链专项没有破坏原高温告警业务。

### 6. 证据与面试回忆要点

- `evidence/screenshots/temperature-rule-chain.png`
- `evidence/screenshots/rule-chain-missing-temperature.png`
- `evidence/screenshots/rule-chain-alarm-regression.png`

面试时可以说明：规则链是消息处理流水线，节点负责过滤、转换、保存或转发；本项目不仅验证正常转换，还覆盖缺少字段的异常输入、配置恢复和告警回归，避免只验证“能算出68”而遗漏业务影响。

本板块对应`TC-RULE-001`至`TC-RULE-004`。截至完成时，项目累计执行30条标准用例，全部通过。

