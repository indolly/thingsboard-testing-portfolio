# ThingsBoard Postman接口测试执行记录

> 文档状态：持续更新  
> 凭据规则：密码、JWT、Refresh Token和Cookie不写入本文档，不提交到GitHub。

## 执行汇总

| 指标 | 当前数量 |
|---|---:|
| 已执行接口用例 | 36 |
| 通过 | 36 |
| 失败 | 0 |
| 阻塞 | 0 |
| 当前通过率 | 100% |

## API-AUTH-001：有效租户管理员账号登录

| 项目 | 内容 |
|---|---|
| 用例编号 | API-AUTH-001 |
| 所属模块 | REST API / 登录鉴权 |
| 用例标题 | 使用有效租户管理员账号密码获取JWT |
| 优先级 | P0 |
| 前置条件 | ThingsBoard运行正常；Postman已选中`ThingsBoard Local`环境；账号密码变量已配置 |
| 测试数据 | `POST {{baseUrl}}/api/auth/login`；有效租户管理员账号密码 |
| 测试步骤 | 1. 使用JSON提交username和password；2. 发送POST请求；3. 检查状态码；4. 断言token存在且非空；5. 将token保存到环境变量jwt |
| 预期结果 | HTTP 200；返回非空JWT；两条断言通过；jwt环境变量保存成功 |
| 实际结果 | HTTP 200，响应耗时110ms；“HTTP状态码为200”和“响应包含非空JWT”两条断言均通过；jwt已保存 |
| 测试结果 | 通过 |

## API-AUTH-002：错误密码登录被拒绝

| 项目 | 内容 |
|---|---|
| 用例编号 | API-AUTH-002 |
| 所属模块 | REST API / 登录鉴权 |
| 用例标题 | 使用正确账号和错误密码登录时不签发JWT |
| 优先级 | P0 |
| 前置条件 | ThingsBoard运行正常；登录接口请求方法为POST；环境中的正确账号可用 |
| 测试数据 | `POST {{baseUrl}}/api/auth/login`；密码`QA_INVALID_PASSWORD_001` |
| 测试步骤 | 1. 保持正确username；2. 将password替换为错误密码；3. 发送POST请求；4. 检查状态码；5. 断言响应不包含token |
| 预期结果 | HTTP 401 Unauthorized；响应不包含JWT；已有jwt环境变量不被覆盖 |
| 实际结果 | HTTP 401，响应耗时95ms；“错误密码返回401”和“失败响应不包含JWT”两条断言均通过 |
| 测试结果 | 通过 |

## API-AUTH-003：有效JWT查询当前用户

| 项目 | 内容 |
|---|---|
| 用例编号 | API-AUTH-003 |
| 所属模块 | REST API / JWT认证 |
| 用例标题 | 使用有效JWT查询当前登录用户及角色 |
| 优先级 | P0 |
| 前置条件 | API-AUTH-001已通过；环境变量jwt已保存有效令牌 |
| 测试数据 | `GET {{baseUrl}}/api/auth/user`；Bearer Token=`{{jwt}}` |
| 测试步骤 | 1. 使用Bearer Token发送GET请求；2. 检查状态码；3. 核对authority；4. 核对email与环境账号一致 |
| 预期结果 | HTTP 200；authority为TENANT_ADMIN；email与登录账号一致；3条断言通过 |
| 实际结果 | HTTP 200；角色和邮箱均符合预期；3/3断言通过 |
| 测试结果 | 通过 |

## API-AUTH-004：伪造JWT访问受保护接口被拒绝

| 项目 | 内容 |
|---|---|
| 用例编号 | API-AUTH-004 |
| 所属模块 | REST API / JWT认证 |
| 用例标题 | 使用伪造JWT查询当前用户时拒绝访问 |
| 优先级 | P0 |
| 前置条件 | ThingsBoard运行正常；当前用户接口需要Bearer认证 |
| 测试数据 | `GET {{baseUrl}}/api/auth/user`；Bearer Token=`QA_INVALID_JWT_001` |
| 测试步骤 | 1. 将Authorization中的Token替换为伪造值；2. 发送GET请求；3. 检查状态码；4. 断言响应未返回用户角色和邮箱 |
| 预期结果 | HTTP 401 Unauthorized；不返回当前用户信息；2条断言通过 |
| 实际结果 | HTTP 401；未返回用户角色和邮箱；2/2断言通过 |
| 测试结果 | 通过 |

## API-DEVICE-001：按名称搜索租户设备

| 项目 | 内容 |
|---|---|
| 用例编号 | API-DEVICE-001 |
| 所属模块 | REST API / 设备查询 |
| 用例标题 | 使用有效JWT按名称搜索测试设备并保存设备ID |
| 优先级 | P0 |
| 前置条件 | 有效jwt已保存；`QA_TEMP_DEVICE_001`存在 |
| 测试数据 | `GET /api/tenant/devices`；pageSize=10、page=0、textSearch=`QA_TEMP_DEVICE_001`、按createdTime降序 |
| 测试步骤 | 1. 携带Bearer Token发送分页查询；2. 检查状态码；3. 检查data数组；4. 按名称定位目标设备；5. 验证并保存deviceId |
| 预期结果 | HTTP 200；返回分页数组；找到目标设备；设备ID非空并保存到环境变量 |
| 实际结果 | HTTP 200；4/4断言通过；找到目标设备并成功保存deviceId |
| 测试结果 | 通过 |

## API-DEVICE-002：根据设备ID查询详情

| 项目 | 内容 |
|---|---|
| 用例编号 | API-DEVICE-002 |
| 所属模块 | REST API / 设备查询 |
| 用例标题 | 使用环境变量中的设备ID查询设备详情 |
| 优先级 | P0 |
| 前置条件 | API-DEVICE-001已通过；环境变量deviceId已保存 |
| 测试数据 | `GET {{baseUrl}}/api/device/{{deviceId}}`；有效Bearer Token |
| 测试步骤 | 1. 使用deviceId发送详情查询；2. 检查状态码；3. 核对设备名称；4. 核对响应ID与环境变量；5. 检查设备配置ID |
| 预期结果 | HTTP 200；设备名称和ID正确；响应包含非空设备配置ID |
| 实际结果 | HTTP 200；设备名称、ID和设备配置ID均符合预期；4/4断言通过 |
| 测试结果 | 通过 |

## API-DEVICE-003：查询不存在的设备ID

| 项目 | 内容 |
|---|---|
| 用例编号 | API-DEVICE-003 |
| 所属模块 | REST API / 设备查询异常 |
| 用例标题 | 查询格式合法但不存在的设备ID时返回资源不存在 |
| 优先级 | P0 |
| 前置条件 | 有效jwt已保存；设备详情接口可用 |
| 测试数据 | `GET /api/device/00000000-0000-0000-0000-000000000000` |
| 测试步骤 | 1. 携带有效Bearer Token查询不存在的UUID；2. 检查状态码；3. 检查响应未包含设备实体；4. 检查错误提示 |
| 预期结果 | HTTP 404；不返回设备ID和名称；响应包含非空错误提示 |
| 实际结果 | HTTP 404；未返回设备实体；错误提示存在；3/3断言通过 |
| 测试结果 | 通过 |

## API-DEVICE-004：未认证访问设备详情

| 项目 | 内容 |
|---|---|
| 用例编号 | API-DEVICE-004 |
| 所属模块 | REST API / 设备接口认证 |
| 用例标题 | 不携带JWT查询真实设备详情时拒绝访问 |
| 优先级 | P0 |
| 前置条件 | 环境变量deviceId指向真实测试设备 |
| 测试数据 | `GET {{baseUrl}}/api/device/{{deviceId}}`；Authorization=`No Auth` |
| 测试步骤 | 1. 移除Authorization；2. 查询真实设备ID；3. 检查状态码；4. 检查未返回设备实体 |
| 预期结果 | HTTP 401 Unauthorized；不返回设备ID和名称 |
| 实际结果 | HTTP 401；未返回设备实体；2/2断言通过 |
| 测试结果 | 通过 |

## API-TELEMETRY-001：查询设备最新遥测

| 项目 | 内容 |
|---|---|
| 用例编号 | API-TELEMETRY-001 |
| 所属模块 | REST API / 最新遥测 |
| 用例标题 | 查询测试设备温度、华氏温度和湿度的最新值 |
| 优先级 | P0 |
| 前置条件 | 有效jwt和deviceId已保存；测试设备已有三个遥测键 |
| 测试数据 | `GET /api/plugins/telemetry/DEVICE/{deviceId}/values/timeseries`；keys=`temperature,temperatureF,humidity` |
| 测试步骤 | 1. 携带JWT查询三个键；2. 检查状态码；3. 检查字段数组；4. 检查ts/value结构；5. 核对最新值 |
| 预期结果 | HTTP 200；返回三个非空字段数组；数据点结构正确；最新值为50、68、66 |
| 实际结果 | HTTP 200；三个字段、数据结构和当前基线值均符合预期；4/4断言通过 |
| 测试结果 | 通过 |

## API-TELEMETRY-002：查询设备历史温度

| 项目 | 内容 |
|---|---|
| 用例编号 | API-TELEMETRY-002 |
| 所属模块 | REST API / 历史遥测 |
| 用例标题 | 查询最近30天原始温度时序数据并验证时间顺序 |
| 优先级 | P0 |
| 前置条件 | 测试设备存在多条历史温度；有效jwt和deviceId已保存 |
| 测试数据 | keys=`temperature`；动态startTs/endTs；limit=1000；agg=NONE；orderBy=ASC |
| 测试步骤 | 1. 前置脚本生成最近30天时间范围；2. 查询原始温度点；3. 检查状态码；4. 检查数据点结构；5. 验证升序和高温测试值 |
| 预期结果 | HTTP 200；返回多个温度点；每点包含ts/value；时间升序；包含50.1和51 |
| 实际结果 | HTTP 200；历史温度点、结构、顺序及高温测试值均符合预期；5/5断言通过 |
| 测试结果 | 通过 |

## API-ALARM-001：查询设备告警列表

| 项目 | 内容 |
|---|---|
| 用例编号 | API-ALARM-001 |
| 所属模块 | REST API / 告警查询 |
| 用例标题 | 查询测试设备告警列表并保存目标告警ID |
| 优先级 | P0 |
| 前置条件 | 有效jwt和deviceId已保存；测试设备存在`High Temperature`告警 |
| 测试数据 | `GET {{baseUrl}}/api/alarm/DEVICE/{{deviceId}}`；searchStatus=`ANY`；pageSize=50；page=0；按createdTime降序；fetchOriginator=true |
| 测试步骤 | 1. 携带JWT查询设备告警列表；2. 检查状态码和分页数据；3. 定位`High Temperature`且严重程度为`MAJOR`的告警；4. 保存其ID到环境变量alarmId |
| 预期结果 | HTTP 200；返回告警分页数据；找到目标高温告警；alarmId保存成功 |
| 实际结果 | HTTP 200；状态码和断言均正确；找到目标告警并成功保存alarmId |
| 测试结果 | 通过 |

## API-ALARM-002：根据告警ID查询详情

| 项目 | 内容 |
|---|---|
| 用例编号 | API-ALARM-002 |
| 所属模块 | REST API / 告警查询 |
| 用例标题 | 使用已保存的告警ID查询高温告警详情 |
| 优先级 | P0 |
| 前置条件 | API-ALARM-001已通过；环境变量alarmId和deviceId已保存 |
| 测试数据 | `GET {{baseUrl}}/api/alarm/{{alarmId}}`；有效Bearer Token |
| 测试步骤 | 1. 使用alarmId查询告警详情；2. 检查状态码；3. 核对告警ID；4. 核对类型和严重程度；5. 核对来源设备；6. 检查确认和清除状态字段 |
| 预期结果 | HTTP 200；告警ID与环境变量一致；类型为`High Temperature`；严重程度为`MAJOR`；来源为测试设备；包含acknowledged和cleared字段 |
| 实际结果 | HTTP 200；告警详情字段均符合预期；5/5断言通过 |
| 测试结果 | 通过 |

## API-ALARM-003：查询不存在的告警ID

| 项目 | 内容 |
|---|---|
| 用例编号 | API-ALARM-003 |
| 所属模块 | REST API / 告警查询异常 |
| 用例标题 | 查询格式合法但不存在的告警ID时返回资源不存在 |
| 优先级 | P0 |
| 前置条件 | 有效jwt已保存；告警详情接口可用 |
| 测试数据 | `GET {{baseUrl}}/api/alarm/00000000-0000-0000-0000-000000000000` |
| 测试步骤 | 1. 携带有效Bearer Token查询不存在的UUID；2. 检查状态码；3. 检查响应未包含告警实体；4. 检查错误提示 |
| 预期结果 | HTTP 404；不返回告警ID和类型；响应包含非空错误提示；3条断言通过 |
| 实际结果 | HTTP 404；未返回告警实体；错误提示存在；3/3断言通过 |
| 测试结果 | 通过 |

## API-ALARM-004：未认证访问告警详情

| 项目 | 内容 |
|---|---|
| 用例编号 | API-ALARM-004 |
| 所属模块 | REST API / 告警接口认证 |
| 用例标题 | 不携带JWT查询真实告警详情时拒绝访问 |
| 优先级 | P0 |
| 前置条件 | 环境变量alarmId指向真实告警；告警详情接口需要Bearer认证 |
| 测试数据 | `GET {{baseUrl}}/api/alarm/{{alarmId}}`；Authorization=`No Auth` |
| 测试步骤 | 1. 将请求方法设置为GET；2. 移除Authorization且不发送Body；3. 查询真实告警ID；4. 检查状态码；5. 检查未返回告警实体 |
| 预期结果 | HTTP 401 Unauthorized；不返回告警ID和类型；2条断言通过 |
| 实际结果 | 初次误用POST方法，发现后修正为GET并重跑；HTTP 401，未返回告警实体，2/2断言通过 |
| 测试结果 | 通过 |

## API-ALARM-005：上报高温遥测触发告警

| 项目 | 内容 |
|---|---|
| 用例编号 | API-ALARM-005 |
| 所属模块 | REST API / 告警状态流转 |
| 用例标题 | 设备上报51°C遥测触发新的高温活动告警 |
| 优先级 | P0 |
| 前置条件 | `QA_TEMP_DEVICE_001`设备令牌有效；设备配置的告警规则为temperature大于50°C时创建高温告警 |
| 测试数据 | `POST {{baseUrl}}/api/v1/{{deviceToken}}/telemetry`；`{"temperature":51}` |
| 测试步骤 | 1. 使用设备令牌向遥测接口提交51°C；2. 检查HTTP状态码；3. 检查成功响应正文为空 |
| 预期结果 | HTTP 200；响应正文为空；规则链异步创建`High Temperature`、`MAJOR`活动告警 |
| 实际结果 | HTTP 200；两条断言全部通过；高温遥测已成功提交 |
| 测试结果 | 通过 |

## API-ALARM-006：查找新产生的活动告警

| 项目 | 内容 |
|---|---|
| 用例编号 | API-ALARM-006 |
| 所属模块 | REST API / 告警状态流转 |
| 用例标题 | 查询设备活动告警并保存新告警ID |
| 优先级 | P0 |
| 前置条件 | API-ALARM-005已提交51°C；有效jwt和deviceId已保存 |
| 测试数据 | `GET {{baseUrl}}/api/alarm/DEVICE/{{deviceId}}`；searchStatus=`ACTIVE`；按createdTime降序 |
| 测试步骤 | 1. 查询设备活动告警；2. 检查状态码和data数组；3. 查找类型为High Temperature、严重程度为MAJOR且未清除的告警；4. 验证初始状态未确认且未清除；5. 保存新alarmId |
| 预期结果 | HTTP 200；找到新活动高温告警；acknowledged=false、cleared=false；alarmId更新成功 |
| 实际结果 | HTTP 200；4/4断言通过；找到新活动告警并更新alarmId |
| 测试结果 | 通过 |

## API-ALARM-007：确认活动告警

| 项目 | 内容 |
|---|---|
| 用例编号 | API-ALARM-007 |
| 所属模块 | REST API / 告警状态流转 |
| 用例标题 | 使用告警确认接口将新告警标记为已确认 |
| 优先级 | P0 |
| 前置条件 | API-ALARM-006已找到活动告警；环境变量alarmId指向该告警；有效jwt已保存 |
| 测试数据 | `POST {{baseUrl}}/api/alarm/{{alarmId}}/ack`；有效Bearer Token |
| 测试步骤 | 1. 使用alarmId调用确认接口；2. 不提交请求体；3. 检查HTTP状态码 |
| 预期结果 | HTTP 200；确认操作被服务器接受 |
| 实际结果 | HTTP 200；1/1断言通过 |
| 测试结果 | 通过 |

## API-ALARM-008：验证告警确认状态

| 项目 | 内容 |
|---|---|
| 用例编号 | API-ALARM-008 |
| 所属模块 | REST API / 告警状态流转 |
| 用例标题 | 重新查询告警并验证已确认但尚未清除 |
| 优先级 | P0 |
| 前置条件 | API-ALARM-007确认接口已返回200；alarmId仍指向目标活动告警 |
| 测试数据 | `GET {{baseUrl}}/api/alarm/{{alarmId}}`；有效Bearer Token |
| 测试步骤 | 1. 根据alarmId重新查询告警；2. 核对告警ID；3. 检查acknowledged；4. 检查cleared |
| 预期结果 | HTTP 200；告警ID正确；acknowledged=true；cleared=false |
| 实际结果 | HTTP 200；4/4断言通过；告警已确认且尚未清除 |
| 测试结果 | 通过 |

## API-ALARM-009：上报恢复温度触发自动清除

| 项目 | 内容 |
|---|---|
| 用例编号 | API-ALARM-009 |
| 所属模块 | REST API / 告警状态流转 |
| 用例标题 | 设备上报50°C使高温告警进入自动清除流程 |
| 优先级 | P0 |
| 前置条件 | 目标告警已确认但未清除；设备令牌有效；清除规则为temperature小于等于50°C |
| 测试数据 | `POST {{baseUrl}}/api/v1/{{deviceToken}}/telemetry`；`{"temperature":50}` |
| 测试步骤 | 1. 使用设备令牌向遥测接口提交50°C；2. 检查HTTP状态码；3. 检查成功响应正文为空 |
| 预期结果 | HTTP 200；响应正文为空；规则链异步清除目标高温告警 |
| 实际结果 | HTTP 200；2/2断言通过；恢复温度已成功提交 |
| 测试结果 | 通过 |

## API-ALARM-010：验证告警自动清除状态

| 项目 | 内容 |
|---|---|
| 用例编号 | API-ALARM-010 |
| 所属模块 | REST API / 告警状态流转 |
| 用例标题 | 重新查询同一告警并验证已确认、已清除及清除时间 |
| 优先级 | P0 |
| 前置条件 | API-ALARM-009已提交50°C；alarmId仍指向此前确认的目标告警 |
| 测试数据 | `GET {{baseUrl}}/api/alarm/{{alarmId}}`；有效Bearer Token |
| 测试步骤 | 1. 根据alarmId重新查询告警；2. 核对告警ID；3. 检查acknowledged；4. 检查cleared；5. 检查clearTs |
| 预期结果 | HTTP 200；告警ID正确；acknowledged=true；cleared=true；clearTs为大于0的时间戳 |
| 实际结果 | HTTP 200；5/5断言通过；告警保持已确认并已自动清除，清除时间有效 |
| 测试结果 | 通过 |

## API-ASSET-001：按名称查询资产

| 项目 | 内容 |
|---|---|
| 用例编号 | API-ASSET-001 |
| 所属模块 | REST API / 资产与实体关系 |
| 用例标题 | 使用有效JWT按名称搜索测试资产并保存资产ID |
| 优先级 | P0 |
| 前置条件 | 有效jwt已保存；`QA_FACTORY_001`存在 |
| 测试数据 | `GET {{baseUrl}}/api/tenant/assets`；pageSize=10、page=0、textSearch=`QA_FACTORY_001`、按createdTime降序 |
| 测试步骤 | 1. 携带Bearer Token查询资产列表；2. 检查状态码和data数组；3. 按名称定位目标资产；4. 验证并保存assetId |
| 预期结果 | HTTP 200；返回分页数组；找到目标资产；资产ID非空并保存到环境变量 |
| 实际结果 | HTTP 200；4/4断言通过；找到目标资产并成功保存assetId |
| 测试结果 | 通过 |

## API-ASSET-002：根据资产ID查询详情

| 项目 | 内容 |
|---|---|
| 用例编号 | API-ASSET-002 |
| 所属模块 | REST API / 资产与实体关系 |
| 用例标题 | 使用已保存的资产ID查询测试资产详情 |
| 优先级 | P0 |
| 前置条件 | API-ASSET-001已通过；环境变量assetId已保存 |
| 测试数据 | `GET {{baseUrl}}/api/asset/{{assetId}}`；有效Bearer Token |
| 测试步骤 | 1. 根据assetId查询详情；2. 检查状态码；3. 核对资产名称；4. 核对响应ID；5. 检查资产配置ID |
| 预期结果 | HTTP 200；名称为QA_FACTORY_001；响应ID与assetId一致；assetProfileId非空 |
| 实际结果 | HTTP 200；4/4断言通过；资产名称、ID和资产配置ID均符合预期 |
| 测试结果 | 通过 |

## API-ASSET-003：查询资产向外关系

| 项目 | 内容 |
|---|---|
| 用例编号 | API-ASSET-003 |
| 所属模块 | REST API / 资产与实体关系 |
| 用例标题 | 从测试资产查询指向温度设备的Contains关系 |
| 优先级 | P0 |
| 前置条件 | 有效jwt、assetId和deviceId已保存；资产与设备的Contains关系存在 |
| 测试数据 | `GET {{baseUrl}}/api/relations`；fromId=`{{assetId}}`、fromType=`ASSET`、relationTypeGroup=`COMMON` |
| 测试步骤 | 1. 从资产起点查询普通关系；2. 检查状态码和数组结构；3. 查找Contains关系；4. 核对from资产和to设备的类型与ID |
| 预期结果 | HTTP 200；返回关系数组；找到`ASSET --Contains--> DEVICE`；两端ID与环境变量一致 |
| 实际结果 | HTTP 200；4/4断言通过；关系类型和起止实体均符合预期 |
| 测试结果 | 通过 |

## API-ASSET-004：从设备反向查询来源资产

| 项目 | 内容 |
|---|---|
| 用例编号 | API-ASSET-004 |
| 所属模块 | REST API / 资产与实体关系 |
| 用例标题 | 从温度设备到端反向查询Contains关系的来源资产 |
| 优先级 | P0 |
| 前置条件 | 有效jwt、assetId和deviceId已保存；资产与设备的Contains关系存在 |
| 测试数据 | `GET {{baseUrl}}/api/relations`；toId=`{{deviceId}}`、toType=`DEVICE`、relationTypeGroup=`COMMON` |
| 测试步骤 | 1. 从设备终点查询普通关系；2. 检查状态码和数组结构；3. 查找来源为目标资产的Contains关系；4. 核对from资产和to设备的类型与ID |
| 预期结果 | HTTP 200；返回关系数组；找到`ASSET --Contains--> DEVICE`；两端ID与环境变量一致 |
| 实际结果 | HTTP 200；4/4断言通过；从设备侧反向查询到同一条Contains关系 |
| 测试结果 | 通过 |

## API-ASSET-005：查询不存在资产的关系

| 项目 | 内容 |
|---|---|
| 用例编号 | API-ASSET-005 |
| 所属模块 | REST API / 资产与实体关系异常 |
| 用例标题 | 使用格式合法但不存在的资产ID查询关系时返回资源不存在 |
| 优先级 | P0 |
| 前置条件 | 有效jwt已保存；关系查询接口可用 |
| 测试数据 | `GET {{baseUrl}}/api/relations`；fromId=`00000000-0000-0000-0000-000000000000`、fromType=`ASSET`、relationTypeGroup=`COMMON` |
| 测试步骤 | 1. 使用不存在的资产UUID查询向外关系；2. 检查状态码；3. 检查未返回关系数组；4. 检查错误提示 |
| 预期结果 | 当前部署版本应先校验资产存在性并返回HTTP 404；不返回关系数组；message包含not found |
| 实际结果 | 初始按通用列表语义预期200空数组，实测ThingsBoard 4.2.1.1先校验来源资产并返回404；据实际版本接口语义修正断言后3/3通过 |
| 测试结果 | 通过 |

## API-ASSET-006：未认证查询真实资产关系

| 项目 | 内容 |
|---|---|
| 用例编号 | API-ASSET-006 |
| 所属模块 | REST API / 资产与实体关系认证 |
| 用例标题 | 不携带JWT查询真实资产关系时拒绝访问 |
| 优先级 | P0 |
| 前置条件 | 环境变量assetId指向真实资产；关系查询接口需要Bearer认证 |
| 测试数据 | `GET {{baseUrl}}/api/relations`；fromId=`{{assetId}}`、fromType=`ASSET`、relationTypeGroup=`COMMON`；Authorization=`No Auth` |
| 测试步骤 | 1. 使用真实assetId配置关系查询；2. 移除Authorization；3. 发送请求；4. 检查状态码和响应结构 |
| 预期结果 | HTTP 401 Unauthorized；不返回实体关系数组 |
| 实际结果 | HTTP 401；未返回关系数组；2/2断言通过 |
| 测试结果 | 通过 |

## API-CUSTOMER-001：按名称查询客户

| 项目 | 内容 |
|---|---|
| 用例编号 | API-CUSTOMER-001 |
| 所属模块 | REST API / 客户资源授权 |
| 用例标题 | 使用有效JWT按名称搜索测试客户并保存客户ID |
| 优先级 | P0 |
| 前置条件 | 有效jwt已保存；`QA_CUSTOMER_001`存在 |
| 测试数据 | `GET {{baseUrl}}/api/customers`；pageSize=10、page=0、textSearch=`QA_CUSTOMER_001`、按createdTime降序 |
| 测试步骤 | 1. 携带Bearer Token查询客户列表；2. 检查状态码和data数组；3. 按title定位目标客户；4. 验证并保存customerId |
| 预期结果 | HTTP 200；返回分页数组；找到目标客户；客户ID非空并保存到环境变量 |
| 实际结果 | 初次误用客户保存请求导致缺少Body并返回500；修正为`GET /api/customers`且Body为none后，4/4断言通过并保存customerId |
| 测试结果 | 通过 |

## API-CUSTOMER-002：根据客户ID查询详情

| 项目 | 内容 |
|---|---|
| 用例编号 | API-CUSTOMER-002 |
| 所属模块 | REST API / 客户资源授权 |
| 用例标题 | 使用已保存的客户ID查询测试客户详情 |
| 优先级 | P0 |
| 前置条件 | API-CUSTOMER-001已通过；customerId已保存 |
| 测试数据 | `GET {{baseUrl}}/api/customer/{{customerId}}`；有效租户管理员JWT |
| 测试步骤 | 1. 根据customerId查询详情；2. 检查状态码；3. 核对客户title；4. 核对客户ID |
| 预期结果 | HTTP 200；title为QA_CUSTOMER_001；响应ID与customerId一致 |
| 实际结果 | HTTP 200；3/3断言通过；客户名称和ID正确 |
| 测试结果 | 通过 |

## API-CUSTOMER-003：查询客户已授权资产

| 项目 | 内容 |
|---|---|
| 用例编号 | API-CUSTOMER-003 |
| 所属模块 | REST API / 客户资源授权 |
| 用例标题 | 查询测试客户名下已分配的工厂资产 |
| 优先级 | P0 |
| 前置条件 | QA_FACTORY_001已分配给QA_CUSTOMER_001；customerId和assetId已保存 |
| 测试数据 | `GET {{baseUrl}}/api/customer/{{customerId}}/assets`；按名称搜索QA_FACTORY_001 |
| 测试步骤 | 1. 查询客户资产分页列表；2. 检查状态码和data数组；3. 按名称定位资产；4. 核对资产ID |
| 预期结果 | HTTP 200；列表包含QA_FACTORY_001；资产ID与assetId一致 |
| 实际结果 | HTTP 200；4/4断言通过；客户资产授权正确 |
| 测试结果 | 通过 |

## API-CUSTOMER-004：查询客户已授权设备

| 项目 | 内容 |
|---|---|
| 用例编号 | API-CUSTOMER-004 |
| 所属模块 | REST API / 客户资源授权 |
| 用例标题 | 查询测试客户名下已分配的温度设备 |
| 优先级 | P0 |
| 前置条件 | QA_TEMP_DEVICE_001已分配给QA_CUSTOMER_001；customerId和deviceId已保存 |
| 测试数据 | `GET {{baseUrl}}/api/customer/{{customerId}}/devices`；按名称搜索QA_TEMP_DEVICE_001 |
| 测试步骤 | 1. 查询客户设备分页列表；2. 检查状态码和data数组；3. 按名称定位设备；4. 核对设备ID |
| 预期结果 | HTTP 200；列表包含QA_TEMP_DEVICE_001；设备ID与deviceId一致 |
| 实际结果 | HTTP 200；4/4断言通过；客户设备授权正确 |
| 测试结果 | 通过 |

## API-CUSTOMER-005：查询客户已授权仪表板

| 项目 | 内容 |
|---|---|
| 用例编号 | API-CUSTOMER-005 |
| 所属模块 | REST API / 客户资源授权 |
| 用例标题 | 查询测试客户名下已分配的温度仪表板 |
| 优先级 | P0 |
| 前置条件 | QA_TEMPERATURE_DASHBOARD已恢复分配给QA_CUSTOMER_001；customerId已保存 |
| 测试数据 | `GET {{baseUrl}}/api/customer/{{customerId}}/dashboards`；按title搜索QA_TEMPERATURE_DASHBOARD |
| 测试步骤 | 1. 查询客户仪表板分页列表；2. 检查状态码和data数组；3. 按title定位仪表板；4. 检查仪表板ID非空 |
| 预期结果 | HTTP 200；列表包含QA_TEMPERATURE_DASHBOARD；仪表板ID非空 |
| 实际结果 | HTTP 200；4/4断言通过；客户仪表板授权正确 |
| 测试结果 | 通过 |

## API-CUSTOMER-006：未认证访问客户详情

| 项目 | 内容 |
|---|---|
| 用例编号 | API-CUSTOMER-006 |
| 所属模块 | REST API / 客户接口认证 |
| 用例标题 | 不携带JWT查询真实客户详情时拒绝访问 |
| 优先级 | P0 |
| 前置条件 | customerId指向真实客户；客户详情接口需要Bearer认证 |
| 测试数据 | `GET {{baseUrl}}/api/customer/{{customerId}}`；Authorization=`No Auth` |
| 测试步骤 | 1. 移除Authorization；2. 查询真实customerId；3. 检查状态码；4. 检查未返回客户实体 |
| 预期结果 | HTTP 401 Unauthorized；不返回客户ID和title |
| 实际结果 | HTTP 401；未返回客户实体；2/2断言通过 |
| 测试结果 | 通过 |

## API-CUSTOMER-007：客户用户登录

| 项目 | 内容 |
|---|---|
| 用例编号 | API-CUSTOMER-007 |
| 所属模块 | REST API / 客户用户认证 |
| 用例标题 | 使用有效客户用户账号密码登录并保存独立JWT |
| 优先级 | P0 |
| 前置条件 | 客户用户已重建、激活并设置新密码；Postman已配置Secret密码变量 |
| 测试数据 | `POST {{baseUrl}}/api/auth/login`；customerUsername和customerPassword |
| 测试步骤 | 1. 提交客户用户凭据；2. 检查状态码；3. 检查token非空；4. 保存到customerJwt |
| 预期结果 | HTTP 200；返回非空JWT；customerJwt保存成功 |
| 实际结果 | HTTP 200；2/2断言通过；customerJwt已保存 |
| 测试结果 | 通过 |

## API-CUSTOMER-008：验证客户用户身份与归属

| 项目 | 内容 |
|---|---|
| 用例编号 | API-CUSTOMER-008 |
| 所属模块 | REST API / 客户用户认证 |
| 用例标题 | 使用客户JWT查询当前用户角色、邮箱和所属客户 |
| 优先级 | P0 |
| 前置条件 | API-CUSTOMER-007已保存有效customerJwt；新customerId已刷新 |
| 测试数据 | `GET {{baseUrl}}/api/auth/user`；Bearer Token=`{{customerJwt}}` |
| 测试步骤 | 1. 使用客户JWT查询当前用户；2. 检查状态码；3. 核对CUSTOMER_USER角色；4. 核对邮箱；5. 核对customerId |
| 预期结果 | HTTP 200；authority为CUSTOMER_USER；邮箱和所属客户正确 |
| 实际结果 | HTTP 200；4/4断言通过；角色、邮箱和客户归属均正确 |
| 测试结果 | 通过 |

## API-CUSTOMER-009：客户用户访问已授权设备

| 项目 | 内容 |
|---|---|
| 用例编号 | API-CUSTOMER-009 |
| 所属模块 | REST API / 客户资源权限 |
| 用例标题 | 客户用户使用自身JWT读取已分配的温度设备 |
| 优先级 | P0 |
| 前置条件 | 测试设备已重新分配给测试客户；customerJwt和deviceId有效 |
| 测试数据 | `GET {{baseUrl}}/api/device/{{deviceId}}`；Bearer Token=`{{customerJwt}}` |
| 测试步骤 | 1. 使用客户JWT查询设备详情；2. 检查状态码；3. 核对设备名称；4. 核对设备ID |
| 预期结果 | HTTP 200；返回QA_TEMP_DEVICE_001；ID与deviceId一致 |
| 实际结果 | HTTP 200；3/3断言通过；客户用户能够读取已授权设备 |
| 测试结果 | 通过 |

## API-CUSTOMER-010：客户用户禁止查询租户客户列表

| 项目 | 内容 |
|---|---|
| 用例编号 | API-CUSTOMER-010 |
| 所属模块 | REST API / 垂直越权 |
| 用例标题 | 客户用户调用租户管理员客户列表接口时拒绝访问 |
| 优先级 | P0 |
| 前置条件 | customerJwt有效且所属角色为CUSTOMER_USER |
| 测试数据 | `GET {{baseUrl}}/api/customers`；Bearer Token=`{{customerJwt}}` |
| 测试步骤 | 1. 使用客户JWT调用客户列表接口；2. 检查状态码；3. 检查未返回客户分页数据 |
| 预期结果 | HTTP 403 Forbidden；身份有效但权限不足；不返回客户列表 |
| 实际结果 | HTTP 403；未返回客户列表；2/2断言通过 |
| 测试结果 | 通过 |

## 证据索引

- `evidence/screenshots/postman-login-success.png`
- `evidence/screenshots/postman-login-invalid-password.png`
- `evidence/screenshots/postman-device-without-jwt.png`

## 执行中识别的问题

- 执行客户用户密码恢复时误删除`QA_CUSTOMER_001`；确认设备、资产、仪表板及资产—设备Contains关系仍存在后，重建同名客户和客户用户，重新分配三类资源，清空旧customerId/customerJwt，并重新执行API-CUSTOMER-001至005全部通过。由于是既有用例的环境恢复回归，不重复计入用例数量。
- CUSTOMER-001初次请求被配置为客户保存接口，因缺少请求体返回500；检查后台错误指向`saveCustomer`后，修正为`GET /api/customers`并移除Body，查询恢复正常。
- 关系查询接口对不存在来源资产的行为与初始通用列表假设不同：ThingsBoard 4.2.1.1先校验资产存在性并返回404，而不是200空数组；已根据当前部署版本修正API-ASSET-005预期和断言。
- Postman获取JWT时曾出现`read ECONNRESET`，浏览器访问ThingsBoard正常且环境变量配置正确。排查确认Postman代理/`localhost`解析链路干扰本地请求；关闭Postman代理并将`baseUrl`由`http://localhost:9091`改为`http://127.0.0.1:9091`后恢复正常。
- 初次配置曾将`AUTH-002`请求方法错误设置为GET，虽然同样得到401，但不代表错误密码场景通过；已修正为POST后重新执行。
- 初次断言将`pm.expect`误写为`pm.except`，导致测试脚本报错；修正后两条断言均通过。
- 该过程说明接口用例不能只核对状态码，还必须核对请求方法、测试数据和断言执行结果，避免假通过。
