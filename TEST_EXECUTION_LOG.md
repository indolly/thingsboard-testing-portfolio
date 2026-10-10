# ThingsBoard 测试执行记录

> 文档状态：持续更新  
> 凭据规则：Token、密码、JWT和Cookie不写入本文档。

## 执行汇总

| 指标 | 当前数量 |
|---|---:|
| 已执行用例 | 30 |
| 通过 | 30 |
| 失败 | 0 |
| 阻塞 | 0 |
| 当前通过率 | 100% |

## TC-HTTP-TEL-001：合法Token上报正常遥测

| 项目 | 内容 |
|---|---|
| 用例编号 | TC-HTTP-TEL-001 |
| 所属模块 | 设备接入 / HTTP遥测 |
| 用例标题 | 使用合法Token上报正常遥测数据 |
| 优先级 | P0 |
| 前置条件 | ThingsBoard运行正常；`QA_TEMP_DEVICE_001`创建成功；WSL访问9091端口成功；已安全读取32字符设备Token |
| 测试数据 | POST `http://localhost:9091/api/v1/<DEVICE_TOKEN>/telemetry`；请求头`Content-Type: application/json`；请求体`{"temperature":25,"humidity":60}` |
| 测试步骤 | 1. 在Ubuntu中加载平台地址和设备Token；2. 使用curl发送POST请求；3. 记录HTTP状态码和耗时；4. 打开设备列表检查状态；5. 打开最新遥测数据检查键值 |
| 预期结果 | 1. HTTP状态码为200；2. 设备状态变为活动；3. 最新遥测显示temperature=25、humidity=60；4. 两个键的更新时间与本次上报一致 |
| 实际结果 | HTTP 200，总耗时0.610105秒；设备状态由非活动变为活动；最新遥测显示temperature=25、humidity=60，两个键更新时间一致 |
| 测试结果 | 通过 |

## TC-DASH-001：创建温度监控仪表板

| 项目 | 内容 |
|---|---|
| 用例编号 | TC-DASH-001 |
| 所属模块 | 仪表板管理 |
| 用例标题 | 租户管理员创建温度监控仪表板 |
| 优先级 | P0 |
| 前置条件 | ThingsBoard运行正常；租户管理员已登录；进入仪表板列表 |
| 测试数据 | 标题`QA_TEMPERATURE_DASHBOARD`；说明`温度监控测试仪表板：用于验证最新遥测、历史趋势和高温告警展示`；客户留空；移动端隐藏关闭；图片不设置 |
| 测试步骤 | 1. 点击新增并选择“创建仪表板”；2. 填写标题和说明；3. 保持客户及移动端非核心配置为默认；4. 点击“添加”；5. 返回列表搜索或检查新仪表板 |
| 预期结果 | 仪表板创建成功；列表中出现`QA_TEMPERATURE_DASHBOARD`；未被分配给客户 |
| 实际结果 | 仪表板创建成功，列表中出现`QA_TEMPERATURE_DASHBOARD` |
| 测试结果 | 通过 |

### 证据索引

- `evidence/private/2026-09-27_device-active-raw.png`
- `evidence/private/2026-09-27_latest-telemetry-raw.png`
- 原图包含登录邮箱，只能保存在本地；公开前生成脱敏副本。

官方接口依据：[ThingsBoard Telemetry HTTP API](https://thingsboard.io/docs/reference/http-api/telemetry/)

## TC-ALARM-001：温度低于阈值时不产生告警

| 项目 | 内容 |
|---|---|
| 用例编号 | TC-ALARM-001 |
| 所属模块 | 遥测数据 / 告警 |
| 用例标题 | 温度为49.9时不产生高温告警 |
| 优先级 | P0 |
| 前置条件 | ThingsBoard运行正常；`QA_TEMP_DEVICE_001`已绑定`QA_TEMPERATURE_PROFILE`；告警创建条件为`temperature > 50`；本地`.env`已配置平台地址和设备Token |
| 测试数据 | POST `/api/v1/<DEVICE_TOKEN>/telemetry`；请求体`{"temperature":49.9}` |
| 测试步骤 | 1. 在Ubuntu中加载`.env`；2. 使用curl上报temperature=49.9；3. 检查HTTP状态码；4. 在设备最新遥测中检查temperature；5. 检查是否出现`High Temperature`告警 |
| 预期结果 | HTTP状态码为200；最新temperature为49.9；不产生`High Temperature`告警 |
| 实际结果 | HTTP状态码为200；最新temperature为49.9；未出现`High Temperature`告警 |
| 测试结果 | 通过 |

## TC-ALARM-002：温度等于阈值时不产生告警

| 项目 | 内容 |
|---|---|
| 用例编号 | TC-ALARM-002 |
| 所属模块 | 遥测数据 / 告警 |
| 用例标题 | 温度等于50时不产生高温告警 |
| 优先级 | P0 |
| 前置条件 | ThingsBoard运行正常；`QA_TEMP_DEVICE_001`已绑定`QA_TEMPERATURE_PROFILE`；告警创建条件为`temperature > 50`；本地`.env`已配置平台地址和设备Token |
| 测试数据 | POST `/api/v1/<DEVICE_TOKEN>/telemetry`；请求体`{"temperature":50}` |
| 测试步骤 | 1. 在Ubuntu中加载`.env`；2. 使用curl上报temperature=50；3. 检查HTTP状态码；4. 在设备最新遥测中检查temperature；5. 检查是否出现`High Temperature`告警 |
| 预期结果 | HTTP状态码为200；最新temperature为50；由于创建条件是`temperature > 50`，不产生`High Temperature`告警 |
| 实际结果 | HTTP状态码为200；最新temperature为50；未出现`High Temperature`告警 |
| 测试结果 | 通过 |

## TC-ALARM-003：温度超过阈值时产生告警

| 项目 | 内容 |
|---|---|
| 用例编号 | TC-ALARM-003 |
| 所属模块 | 遥测数据 / 告警 |
| 用例标题 | 温度为50.1时产生高温告警 |
| 优先级 | P0 |
| 前置条件 | ThingsBoard运行正常；`QA_TEMP_DEVICE_001`已绑定`QA_TEMPERATURE_PROFILE`；告警创建条件为`temperature > 50`；测试开始前不存在活动的`High Temperature`告警 |
| 测试数据 | POST `/api/v1/<DEVICE_TOKEN>/telemetry`；请求体`{"temperature":50.1}` |
| 测试步骤 | 1. 使用curl上报temperature=50.1；2. 检查HTTP状态码；3. 检查设备最新temperature；4. 打开设备告警详情，检查类型、严重程度和状态 |
| 预期结果 | HTTP状态码为200；最新temperature为50.1；产生`High Temperature`告警；严重程度为MAJOR（中文显示“重要”）；状态为活动未确认 |
| 实际结果 | HTTP状态码为200；最新temperature为50.1；产生`High Temperature`告警；严重程度显示“重要”；状态为“激活未确认” |
| 测试结果 | 通过 |

### 证据索引

- `evidence/screenshots/high-temperature-alarm-active.png`

## TC-ALARM-004：温度回落到阈值时自动清除告警

| 项目 | 内容 |
|---|---|
| 用例编号 | TC-ALARM-004 |
| 所属模块 | 遥测数据 / 告警 |
| 用例标题 | 温度从50.1回落到50时自动清除高温告警 |
| 优先级 | P0 |
| 前置条件 | `High Temperature`告警处于激活未确认状态；清除条件为`temperature <= 50`；未点击人工清除按钮 |
| 测试数据 | POST `/api/v1/<DEVICE_TOKEN>/telemetry`；请求体`{"temperature":50}` |
| 测试步骤 | 1. 保持告警为活动状态；2. 使用curl上报temperature=50；3. 检查HTTP状态码和最新遥测；4. 刷新活动告警列表；5. 检查告警清除通知 |
| 预期结果 | HTTP状态码为200；最新temperature为50；规则自动清除`High Temperature`告警；活动告警列表为空；产生告警已清除通知 |
| 实际结果 | HTTP状态码为200；最新temperature为50；未进行人工清除；活动告警列表显示“未发现告警”；通知显示`Alarm 'High Temperature' - cleared` |
| 测试结果 | 通过 |

### 证据索引

- `evidence/screenshots/high-temperature-alarm-cleared.png`

## TC-ALARM-005：应答活动告警

| 项目 | 内容 |
|---|---|
| 用例编号 | TC-ALARM-005 |
| 所属模块 | 告警管理 |
| 用例标题 | 对激活未确认的高温告警执行应答 |
| 优先级 | P0 |
| 前置条件 | 上报temperature=51返回HTTP 200；最新遥测为51；`High Temperature`告警处于激活未确认状态 |
| 测试数据 | 告警类型`High Temperature`；严重程度MAJOR（重要） |
| 测试步骤 | 1. 打开活动的`High Temperature`告警详情；2. 点击“应答”；3. 刷新并检查告警状态；4. 确认告警是否仍处于激活状态 |
| 预期结果 | 告警状态由“激活未确认”变为“激活已确认”；告警仍处于激活状态；应答操作不清除告警 |
| 实际结果 | 告警状态显示“激活已确认”；页面仍提供“清除”按钮，告警保持激活 |
| 测试结果 | 通过 |

### 证据索引

- `evidence/screenshots/high-temperature-alarm-acknowledged.png`

## TC-ALARM-006：已确认告警命中规则后自动清除

| 项目 | 内容 |
|---|---|
| 用例编号 | TC-ALARM-006 |
| 所属模块 | 遥测数据 / 告警管理 |
| 用例标题 | 已确认的活动高温告警在温度回落后自动转为清除已确认 |
| 优先级 | P0 |
| 前置条件 | `High Temperature`告警状态为“激活已确认”；清除条件为`temperature <= 50`；未点击人工清除按钮 |
| 测试数据 | POST `/api/v1/<DEVICE_TOKEN>/telemetry`；请求体`{"temperature":50}` |
| 测试步骤 | 1. 使用curl上报temperature=50；2. 检查HTTP状态码和最新遥测；3. 在告警筛选器中取消“激活”，选择“已清除”和“已确认”；4. 打开最新的`High Temperature`告警并检查状态 |
| 预期结果 | HTTP状态码为200；最新temperature为50；告警自动从“激活已确认”转为“清除已确认”；无需人工清除 |
| 实际结果 | HTTP状态码为200；最新temperature为50；未点击人工清除；通过“已清除+已确认”组合筛选找到告警，详情状态为“清除已确认” |
| 测试结果 | 通过 |

## TC-DASH-002：仪表板展示设备最新温度

| 项目 | 内容 |
|---|---|
| 用例编号 | TC-DASH-002 |
| 所属模块 | 仪表板 / 最新遥测 |
| 用例标题 | Value card绑定设备后展示最新temperature |
| 优先级 | P0 |
| 前置条件 | `QA_TEMPERATURE_DASHBOARD`已创建；`QA_TEMP_DEVICE_001`存在temperature遥测数据；租户管理员进入仪表板编辑模式 |
| 测试数据 | 数据源设备`QA_TEMP_DEVICE_001`；数据键`temperature`；标签`当前温度`；单位`°C` |
| 测试步骤 | 1. 添加Cards部件包中的Value card；2. 选择测试设备和temperature数据键；3. 设置标签和单位；4. 添加并保存仪表板；5. 退出编辑模式检查卡片值 |
| 预期结果 | 仪表板成功保存；Value card显示“当前温度”；显示设备最新temperature及单位°C |
| 实际结果 | 仪表板保存成功；卡片显示“当前温度”和最新值50°C，并显示最后更新时间 |
| 测试结果 | 通过 |

### 证据索引

- `evidence/screenshots/dashboard-latest-temperature.png`

## TC-DASH-003：仪表板展示温度历史趋势

| 项目 | 内容 |
|---|---|
| 用例编号 | TC-DASH-003 |
| 所属模块 | 仪表板 / 历史遥测 |
| 用例标题 | Line chart查询并展示最近7天temperature历史数据 |
| 优先级 | P0 |
| 前置条件 | `QA_TEMPERATURE_DASHBOARD`已创建；测试设备已累计上报多条temperature时序数据 |
| 测试数据 | 设备`QA_TEMP_DEVICE_001`；数据键`temperature`；部件时间窗口“实时－最后7天”；单位°C |
| 测试步骤 | 1. 添加Charts部件包中的Line chart；2. 绑定测试设备及temperature；3. 设置部件时间窗口为最后7天；4. 设置标题、单位和图例；5. 保存并退出编辑模式 |
| 预期结果 | 折线图显示最后7天内多条temperature历史数据；横轴为时间，纵轴为温度；卡片和图表数据来源一致 |
| 实际结果 | 折线图成功展示25°C至51°C再回落至50°C的多条历史数据；时间窗口显示最后7天；图例显示平均值39.4°C |
| 测试结果 | 通过 |

### 证据索引

- `evidence/screenshots/dashboard-temperature-history.png`

## TC-DASH-004：新遥测驱动仪表板实时更新

| 项目 | 内容 |
|---|---|
| 用例编号 | TC-DASH-004 |
| 所属模块 | 仪表板 / 遥测数据 |
| 用例标题 | 上报新温度后最新值卡片与历史折线图同步更新 |
| 优先级 | P0 |
| 前置条件 | 仪表板已配置temperature最新值卡片和最近7天历史折线图；上报前最新温度为50°C |
| 测试数据 | POST `/api/v1/<DEVICE_TOKEN>/telemetry`；请求体`{"temperature":42}` |
| 测试步骤 | 1. 使用curl上报temperature=42；2. 检查HTTP状态码；3. 等待部件刷新；4. 检查最新值卡片；5. 检查折线图最右侧数据点 |
| 预期结果 | HTTP状态码为200；卡片更新为42°C；历史图新增42°C数据点；两个部件数据一致 |
| 实际结果 | HTTP状态码为200；卡片显示42°C和最新更新时间；折线图最右侧新增42°C数据点 |
| 测试结果 | 通过 |

### 证据索引

- `evidence/screenshots/dashboard-realtime-update.png`

## TC-DASH-005：仪表板展示设备历史告警

| 项目 | 内容 |
|---|---|
| 用例编号 | TC-DASH-005 |
| 所属模块 | 仪表板 / 告警 |
| 用例标题 | Alarms table展示测试设备最近7天高温告警 |
| 优先级 | P0 |
| 前置条件 | 测试设备存在`High Temperature`历史告警；仪表板处于编辑模式 |
| 测试数据 | 告警源`QA_TEMP_DEVICE_001`；时间窗口最近7天；严重程度“重要”；类型`High Temperature`；受托人“所有” |
| 测试步骤 | 1. 添加Alarm widgets中的Alarms table；2. 绑定测试设备；3. 配置时间窗口和告警筛选；4. 保留创建时间、发起者、类型、严重程度、状态、受托人列；5. 保存仪表板并检查记录 |
| 预期结果 | 表格仅展示目标设备的高温告警；正确显示类型、严重程度和状态；能够区分已确认与未确认记录 |
| 实际结果 | 表格展示2条`High Temperature`告警；设备均为`QA_TEMP_DEVICE_001`；严重程度均为“重要”；状态分别为“清除已确认”和“清除未确认” |
| 测试结果 | 通过 |

### 证据索引

- `evidence/screenshots/dashboard-alarm-table.png`

## TC-ASSET-001：创建温度监控测试资产

| 项目 | 内容 |
|---|---|
| 用例编号 | TC-ASSET-001 |
| 所属模块 | 资产管理 |
| 用例标题 | 租户管理员创建测试工厂资产 |
| 优先级 | P0 |
| 前置条件 | ThingsBoard运行正常；租户管理员已登录；进入实体－资产列表 |
| 测试数据 | 名称`QA_FACTORY_001`；标签`测试工厂-001`；资产配置`default`；客户留空；说明`温度监控测试资产，用于验证资产与设备关联` |
| 测试步骤 | 1. 点击新增资产；2. 填写名称、标签和说明；3. 保持默认资产配置且不分配客户；4. 点击添加；5. 检查资产列表 |
| 预期结果 | 资产创建成功；列表中出现`QA_FACTORY_001`；资产未分配客户 |
| 实际结果 | 资产创建成功，列表中出现`QA_FACTORY_001` |
| 测试结果 | 通过 |

## TC-ASSET-002：建立资产包含设备关系

| 项目 | 内容 |
|---|---|
| 用例编号 | TC-ASSET-002 |
| 所属模块 | 资产管理 / 实体关系 |
| 用例标题 | 建立测试工厂Contains温度设备的向外关系 |
| 优先级 | P0 |
| 前置条件 | `QA_FACTORY_001`资产与`QA_TEMP_DEVICE_001`设备均已存在；租户管理员打开资产关联页签 |
| 测试数据 | 起点资产`QA_FACTORY_001`；方向From（从）；类型`Contains`；目标实体类型“设备”；目标`QA_TEMP_DEVICE_001` |
| 测试步骤 | 1. 在资产关联页点击新增；2. 设置方向From和类型Contains；3. 选择目标设备；4. 保存；5. 查看资产的向外关联列表 |
| 预期结果 | 关系保存成功；资产向外关联列表显示`Contains`、设备、`QA_TEMP_DEVICE_001` |
| 实际结果 | 关系保存成功；资产“向外的关联”显示类型`Contains`、目标实体类型“设备”和目标名称`QA_TEMP_DEVICE_001` |
| 测试结果 | 通过 |

### 证据索引

- `evidence/screenshots/asset-contains-device-relation.png`

## TC-ASSET-003：从设备侧反向查询所属资产

| 项目 | 内容 |
|---|---|
| 用例编号 | TC-ASSET-003 |
| 所属模块 | 资产管理 / 实体关系 |
| 用例标题 | 设备向内关联能够查询到Contains关系的来源资产 |
| 优先级 | P0 |
| 前置条件 | 已建立`QA_FACTORY_001 --Contains--> QA_TEMP_DEVICE_001`关系 |
| 测试数据 | 当前实体`QA_TEMP_DEVICE_001`；查询方向To（到） |
| 测试步骤 | 1. 打开测试设备详情；2. 进入关联页签；3. 将方向切换为To；4. 检查关系类型、来源实体类型和来源实体名称 |
| 预期结果 | 设备向内关联显示类型`Contains`；来源实体类型为资产；来源实体名称为`QA_FACTORY_001` |
| 实际结果 | 设备“向内的关联”显示`Contains`；来源实体类型为“资产”；来源实体名称为`QA_FACTORY_001` |
| 测试结果 | 通过 |

### 证据索引

- `evidence/screenshots/device-inbound-asset-relation.png`

## TC-ASSET-004：删除资产与设备关系

| 项目 | 内容 |
|---|---|
| 用例编号 | TC-ASSET-004 |
| 所属模块 | 资产管理 / 实体关系 |
| 用例标题 | 删除Contains关系后两端同步消失且实体保留 |
| 优先级 | P0 |
| 前置条件 | `QA_FACTORY_001 --Contains--> QA_TEMP_DEVICE_001`关系存在；资产和设备均正常 |
| 测试数据 | 关系类型`Contains`；仅删除关系，不删除实体 |
| 测试步骤 | 1. 在设备向内关联列表删除该关系；2. 刷新设备侧关联列表；3. 打开资产向外关联列表；4. 检查资产与设备实体是否仍存在 |
| 预期结果 | 设备侧和资产侧的同一关系均消失；`QA_FACTORY_001`和`QA_TEMP_DEVICE_001`仍然存在 |
| 实际结果 | 两端关系均已消失；资产和设备实体仍然存在，未发生级联删除 |
| 测试结果 | 通过 |

## TC-PERM-001：创建权限隔离测试客户

| 项目 | 内容 |
|---|---|
| 用例编号 | TC-PERM-001 |
| 所属模块 | 客户与用户权限 |
| 用例标题 | 租户管理员创建未分配资源的测试客户 |
| 优先级 | P0 |
| 前置条件 | ThingsBoard运行正常；租户管理员已登录；进入客户列表 |
| 测试数据 | 客户名称`QA_CUSTOMER_001`；说明`权限隔离测试客户，用于验证设备、资产和仪表板授权`；其他地址信息留空 |
| 测试步骤 | 1. 点击新增客户；2. 填写客户名称和说明；3. 不分配任何设备、资产或仪表板；4. 保存；5. 检查客户列表 |
| 预期结果 | 客户创建成功；客户列表出现`QA_CUSTOMER_001`；客户初始未获得租户资源 |
| 实际结果 | 客户创建成功，客户列表中出现`QA_CUSTOMER_001` |
| 测试结果 | 通过 |

## TC-PERM-002：在测试客户下创建客户用户

| 项目 | 内容 |
|---|---|
| 用例编号 | TC-PERM-002 |
| 所属模块 | 客户与用户权限 |
| 用例标题 | 租户管理员为测试客户创建待激活用户 |
| 优先级 | P0 |
| 前置条件 | `QA_CUSTOMER_001`已创建且尚未分配设备、资产和仪表板；租户管理员已登录 |
| 测试数据 | 邮箱`qa.customer.001@example.com`；名字`QA`；姓氏`CustomerUser`；激活方式“显示激活链接” |
| 测试步骤 | 1. 打开测试客户的用户页签；2. 新增客户用户；3. 填写测试邮箱和姓名；4. 选择显示激活链接；5. 保存并检查结果 |
| 预期结果 | 客户用户创建成功；用户归属`QA_CUSTOMER_001`；系统生成一次性激活链接 |
| 实际结果 | 客户用户创建成功，系统显示激活链接；链接未截图、未写入项目文档 |
| 测试结果 | 通过 |

## TC-PERM-003：激活并登录客户用户

| 项目 | 内容 |
|---|---|
| 用例编号 | TC-PERM-003 |
| 所属模块 | 客户与用户权限 / 用户认证 |
| 用例标题 | 使用一次性激活链接设置密码并首次登录客户用户 |
| 优先级 | P0 |
| 前置条件 | `qa.customer.001@example.com`已创建且处于待激活状态；系统已生成激活链接 |
| 测试数据 | 客户用户邮箱`qa.customer.001@example.com`；随机测试密码保存在本地`.env`，不记录明文 |
| 测试步骤 | 1. 在无痕窗口打开一次性激活链接；2. 设置并确认随机密码；3. 提交激活；4. 检查是否自动进入ThingsBoard |
| 预期结果 | 用户激活成功；能够以客户用户身份进入ThingsBoard；租户管理员原会话保持独立 |
| 实际结果 | 激活成功，提交后自动进入ThingsBoard，客户用户登录成功 |
| 测试结果 | 通过 |

## TC-PERM-004：未授权客户用户默认不可见租户资源

| 项目 | 内容 |
|---|---|
| 用例编号 | TC-PERM-004 |
| 所属模块 | 客户与用户权限 / 权限隔离 |
| 用例标题 | 客户未分配资源时用户不能访问租户设备、资产、仪表板和管理菜单 |
| 优先级 | P0 |
| 前置条件 | 客户用户已激活并登录；`QA_CUSTOMER_001`尚未分配测试设备、资产和仪表板 |
| 测试数据 | 设备`QA_TEMP_DEVICE_001`；资产`QA_FACTORY_001`；仪表板`QA_TEMPERATURE_DASHBOARD` |
| 测试步骤 | 1. 登录客户用户；2. 检查设备列表；3. 检查资产列表；4. 检查仪表板列表；5. 检查客户管理和规则链菜单 |
| 预期结果 | 三个测试资源均不可见；客户管理和规则链等租户级菜单不可见或不可用 |
| 实际结果 | 测试设备、资产和仪表板均不可见；客户管理和规则链菜单均不可见 |
| 测试结果 | 通过 |

## TC-PERM-005：仅分配资产时资源权限独立生效

| 项目 | 内容 |
|---|---|
| 用例编号 | TC-PERM-005 |
| 所属模块 | 客户与用户权限 / 资源授权 |
| 用例标题 | 仅向客户分配资产时设备和仪表板仍不可见 |
| 优先级 | P0 |
| 前置条件 | 客户用户已登录；三个测试资源初始均未分配；资产与设备存在Contains关系 |
| 测试数据 | 向`QA_CUSTOMER_001`仅分配`QA_FACTORY_001` |
| 测试步骤 | 1. 租户管理员将测试资产分配给客户；2. 不分配设备和仪表板；3. 客户用户刷新；4. 分别检查资产、设备和仪表板列表 |
| 预期结果 | 测试资产可见；测试设备和仪表板不可见；实体关系不应导致资源被自动授权 |
| 实际结果 | `QA_FACTORY_001`可见；`QA_TEMP_DEVICE_001`不可见；`QA_TEMPERATURE_DASHBOARD`不可见 |
| 测试结果 | 通过 |

## TC-PERM-006：实体关系不能绕过未授权设备权限

| 项目 | 内容 |
|---|---|
| 用例编号 | TC-PERM-006 |
| 所属模块 | 客户与用户权限 / 关系权限隔离 |
| 用例标题 | 客户用户不能通过已授权资产的关联页发现未授权设备 |
| 优先级 | P0 |
| 前置条件 | `QA_FACTORY_001`已分配给客户；`QA_TEMP_DEVICE_001`未分配；两者存在Contains关系；客户用户已登录 |
| 测试数据 | 在资产关联页查询方向From（从） |
| 测试步骤 | 1. 客户用户打开已授权资产；2. 进入关联页；3. 选择方向From；4. 查找`QA_TEMP_DEVICE_001` |
| 预期结果 | 未授权设备不出现在资产关联页；客户用户不能通过实体关系绕过资源授权 |
| 实际结果 | 资产关联页未显示`QA_TEMP_DEVICE_001`，无法通过关系进入设备详情 |
| 测试结果 | 通过 |

## TC-PERM-007：分配设备后设备与实体关系同步可见

| 项目 | 内容 |
|---|---|
| 用例编号 | TC-PERM-007 |
| 所属模块 | 客户与用户权限 / 资源授权 |
| 用例标题 | 向客户分配设备后设备及其与已授权资产的关系可见 |
| 优先级 | P0 |
| 前置条件 | 测试资产已分配给客户；测试设备和仪表板尚未分配；资产与设备存在Contains关系 |
| 测试数据 | 向`QA_CUSTOMER_001`分配`QA_TEMP_DEVICE_001` |
| 测试步骤 | 1. 租户管理员分配测试设备；2. 客户用户刷新；3. 检查资产、设备和仪表板；4. 检查资产From关联；5. 检查设备To关联 |
| 预期结果 | 资产和设备均可见；仪表板仍不可见；资产侧显示目标设备，设备侧显示来源资产 |
| 实际结果 | 资产和设备可见，仪表板不可见；资产From关联显示`QA_TEMP_DEVICE_001`，设备To关联显示`QA_FACTORY_001` |
| 测试结果 | 通过 |

## TC-PERM-008：分配仪表板后客户用户可查看授权数据

| 项目 | 内容 |
|---|---|
| 用例编号 | TC-PERM-008 |
| 所属模块 | 客户与用户权限 / 仪表板授权 |
| 用例标题 | 向客户分配仪表板后客户用户可查看已授权设备数据和告警 |
| 优先级 | P0 |
| 前置条件 | 测试资产和设备已分配给客户；测试仪表板尚未分配；客户用户已登录 |
| 测试数据 | 向`QA_CUSTOMER_001`分配`QA_TEMPERATURE_DASHBOARD` |
| 测试步骤 | 1. 租户管理员分配测试仪表板；2. 客户用户刷新；3. 打开仪表板；4. 检查当前温度、历史趋势和告警记录 |
| 预期结果 | 仪表板可见；三个部件均能读取已授权设备的数据 |
| 实际结果 | 仪表板可见；当前温度、历史趋势和高温告警记录均正常显示 |
| 测试结果 | 通过 |

## TC-PERM-009：客户用户只能查看仪表板且无租户管理菜单

| 项目 | 内容 |
|---|---|
| 用例编号 | TC-PERM-009 |
| 所属模块 | 客户与用户权限 / 垂直权限 |
| 用例标题 | 客户用户不能编辑已授权仪表板且不能访问租户级管理菜单 |
| 优先级 | P0 |
| 前置条件 | 客户用户已登录并打开已授权仪表板 |
| 测试数据 | 客户用户`qa.customer.001@example.com`；角色“客户” |
| 测试步骤 | 1. 检查仪表板页面编辑入口；2. 检查铅笔、添加部件和保存按钮；3. 检查左侧客户管理和规则链菜单 |
| 预期结果 | 仪表板只有查看权限；不显示编辑、添加或保存入口；不显示客户管理和规则链菜单 |
| 实际结果 | 仪表板数据可查看，但不存在编辑入口；客户管理和规则链菜单仍不可见 |
| 测试结果 | 通过 |

### 证据索引

- `evidence/screenshots/customer-user-dashboard-readonly.png`

## TC-PERM-010：撤销仪表板授权后访问立即失效

| 项目 | 内容 |
|---|---|
| 用例编号 | TC-PERM-010 |
| 所属模块 | 客户与用户权限 / 权限撤销 |
| 用例标题 | 取消客户仪表板分配后列表和原页面URL均不可访问 |
| 优先级 | P0 |
| 前置条件 | 客户用户能够正常访问已分配仪表板；资产和设备仍分配给客户 |
| 测试数据 | 从`QA_CUSTOMER_001`撤销`QA_TEMPERATURE_DASHBOARD`分配 |
| 测试步骤 | 1. 保持客户用户仪表板页面打开；2. 租户管理员取消仪表板分配；3. 客户用户刷新原页面；4. 检查仪表板列表；5. 检查资产和设备 |
| 预期结果 | 原页面不能继续访问；仪表板从列表消失；资产和设备仍可见，其他资源权限不受影响 |
| 实际结果 | 刷新原页面显示“未找到仪表板”；仪表板列表不再显示；资产和设备仍可见 |
| 测试结果 | 通过 |

## TC-RULE-001：创建温度转换规则链并建立处理流程

| 项目 | 内容 |
|---|---|
| 用例编号 | TC-RULE-001 |
| 所属模块 | 规则链 / 流程配置 |
| 用例标题 | 创建非根规则链并连接脚本转换与时序保存节点 |
| 优先级 | P0 |
| 前置条件 | 租户管理员已登录；测试设备和`QA_TEMPERATURE_PROFILE`存在 |
| 测试数据 | 规则链`QA_TEMPERATURE_RULE_CHAIN`；TBEL脚本将`temperature`转换为`temperatureF` |
| 测试步骤 | 1. 创建非根规则链；2. 添加script节点；3. 添加save time series节点；4. 建立`Input → script → save time series`连接；5. 保存规则链 |
| 预期结果 | 规则链保存成功；消息能够依次进入转换节点和时序保存节点 |
| 实际结果 | 规则链创建并保存成功；画布显示完整处理路径，script到save time series的关系为Success |
| 测试结果 | 通过 |

## TC-RULE-002：正常温度转换并持久化华氏度

| 项目 | 内容 |
|---|---|
| 用例编号 | TC-RULE-002 |
| 所属模块 | 规则链 / 数据转换 |
| 用例标题 | 上报摄氏温度后自动计算并保存华氏温度 |
| 优先级 | P0 |
| 前置条件 | `QA_TEMPERATURE_PROFILE`临时绑定`QA_TEMPERATURE_RULE_CHAIN`；设备Token有效 |
| 测试数据 | `{"temperature":20}`；换算公式`temperature × 9 ÷ 5 + 32` |
| 测试步骤 | 1. 通过HTTP上报temperature=20；2. 检查HTTP状态码；3. 查看设备最新遥测；4. 核对temperatureF |
| 预期结果 | HTTP返回200；保留temperature=20；新增并保存temperatureF=68 |
| 实际结果 | HTTP返回200；最新遥测同时显示temperature=20和temperatureF=68.0，两个字段更新时间一致 |
| 测试结果 | 通过 |

## TC-RULE-003：缺少温度字段时安全跳过转换

| 项目 | 内容 |
|---|---|
| 用例编号 | TC-RULE-003 |
| 所属模块 | 规则链 / 异常输入 |
| 用例标题 | 遥测消息缺少temperature时不生成错误的temperatureF |
| 优先级 | P0 |
| 前置条件 | 转换规则链处于启用状态；设备已有temperatureF=68.0及其更新时间 |
| 测试数据 | `{"humidity":66}` |
| 测试步骤 | 1. 记录temperatureF值和更新时间；2. 上报仅含humidity的遥测；3. 检查HTTP状态码；4. 刷新最新遥测并比较各字段时间 |
| 预期结果 | HTTP返回200；humidity更新为66；temperature和temperatureF不更新；规则链不中断 |
| 实际结果 | HTTP返回200；humidity在2026-10-08更新为66；temperature和temperatureF仍保持2026-10-01的20和68.0，更新时间均未变化 |
| 测试结果 | 通过 |

## TC-RULE-004：恢复根规则链后告警功能回归正常

| 项目 | 内容 |
|---|---|
| 用例编号 | TC-RULE-004 |
| 所属模块 | 规则链 / 配置恢复与回归 |
| 用例标题 | 恢复Root Rule Chain后高温告警仍可创建并自动清除 |
| 优先级 | P0 |
| 前置条件 | 温度转换规则链测试完成；`QA_TEMPERATURE_PROFILE`原默认规则链为`Root Rule Chain` |
| 测试数据 | 先上报`{"temperature":51}`，再上报`{"temperature":50}` |
| 测试步骤 | 1. 将设备配置默认规则链恢复为Root Rule Chain；2. 上报51；3. 检查High Temperature告警；4. 上报50；5. 检查清除通知 |
| 预期结果 | 51触发MAJOR高温告警；50自动清除该告警；原告警流程未受规则链专项测试影响 |
| 实际结果 | 收到新的High Temperature重要告警，随后收到High Temperature cleared通知，创建和自动清除均正常 |
| 测试结果 | 通过 |

### 规则链证据索引

- `evidence/screenshots/temperature-rule-chain.png`
- `evidence/screenshots/rule-chain-missing-temperature.png`
- `evidence/screenshots/rule-chain-alarm-regression.png`
