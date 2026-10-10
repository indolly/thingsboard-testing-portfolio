# ThingsBoard 测试环境基线与运维记录

> 文档编号：D02  
> 版本：V1.0  
> 检查日期：2026-09-21  
> 当前结论：环境准入验证通过。

## 1. 环境清单

| 检查项 | 实际结果 |
|---|---|
| 宿主环境 | Windows + Docker Desktop/WSL2 |
| Docker Client | 29.7.2 |
| Docker Server | 29.7.2 |
| Docker Compose | v5.5.0 |
| ThingsBoard | CE 4.2.1.1 |
| Java | 17.0.17 |
| 部署方式 | Docker Compose 单节点、ThingsBoard与PostgreSQL单容器 |
| Compose服务名 | `thingsboard` |
| 容器名 | `thingsboard-thingsboard-1` |
| 镜像 | `thingsboard/tb-postgres:latest` |
| 镜像ID | `08decb7b3671` |
| 镜像大小 | 1.47 GB |
| 重启策略 | `always` |
| 数据目录 | `D:\study\softtest\ThingsBoard\thingsboard\data` → `/data`，可读写 |
| 日志目录 | `D:\study\softtest\ThingsBoard\thingsboard\logs` → `/var/log/thingsboard`，可读写 |
| Web地址 | `http://localhost:9091` |

## 2. 端口基线

| 用途 | 宿主机 | 容器 | 协议 | 状态 |
|---|---:|---:|---|---|
| Web UI / REST API | 9091 | 9090 | TCP | 已验证HTTP 200 |
| MQTT | 1883 | 1883 | TCP | 已映射，业务连接待后续验证 |
| CoAP | 5683 | 5683 | UDP | 已映射，当前项目不重点覆盖 |
| CoAP over DTLS | 5684 | 5684 | UDP | 已映射，当前项目不重点覆盖 |
| LwM2M相关端口 | 5685～5688 | 5685～5688 | UDP | 已映射，当前项目不重点覆盖 |

说明：当前部署没有映射官方新版本示例中常见的8080、7070和8883端口，本项目必须以实际Compose配置为准。

## 3. 实际验证记录

| 编号 | 验证项 | 实际结果 | 结论 |
|---|---|---|---|
| ENV-001 | Docker Engine可访问 | Client/Server均为29.7.2 | 通过 |
| ENV-002 | 容器运行状态 | `running`，Exit=0 | 通过 |
| ENV-003 | 异常重启/OOM | RestartCount=0，OOM=false | 通过 |
| ENV-004 | Web端口连通性 | localhost:9091 TCP连接成功 | 通过 |
| ENV-005 | 首页HTTP响应 | HTTP 200，探测耗时约0.296秒，响应3776字节 | 通过 |
| ENV-006 | 应用启动日志 | `Started ThingsboardServerApplication` | 通过 |
| ENV-007 | 应用启动耗时 | 首次观测27.515秒；重启后27.892秒 | 通过 |
| ENV-008 | 手工重启恢复 | 发起重启至HTTP 200共46.02秒 | 通过 |
| ENV-009 | 重启后容器状态 | running、Exit=0、OOM=false | 通过 |
| ENV-010 | 数据持久化挂载 | `/data`和日志目录均为宿主机bind挂载且可写 | 通过 |
| ENV-011 | 资源快照 | CPU 8.43%，内存1.461 GiB/13.5 GiB，PIDs 271 | 记录值，不作为性能结论 |
| ENV-012 | 浏览器登录 | 租户管理员登录成功 | 通过 |
| ENV-013 | 2026-09-26续测准备检查 | 容器因`restart: always`已自动运行约6小时，首页HTTP 200、响应约0.839秒 | 通过 |
| ENV-014 | Linux客户端环境 | 已安装Ubuntu，运行于WSL2；Docker Desktop同样运行于WSL2 | 通过，Ubuntu按需启动 |
| ENV-015 | WSL到ThingsBoard网络访问 | 从Ubuntu访问`http://localhost:9091/`返回HTTP 200；连接耗时0.000343秒，总耗时0.012148秒 | 通过 |
| ENV-016 | 设备活动超时 | Compose未设置自定义`DEFAULT_INACTIVITY_TIMEOUT`，使用平台默认600秒；状态检查默认间隔60秒 | 已确认，设备停止上报后变为非活动属于预期行为 |

## 4. 启停与日志命令

以下命令均在 `D:\study\softtest\ThingsBoard\thingsboard` 目录执行。

查看状态：

```powershell
docker compose ps
```

启动：

```powershell
docker compose up -d
```

停止但保留容器和数据：

```powershell
docker compose stop thingsboard
```

重新启动已停止的服务：

```powershell
docker compose start thingsboard
```

重启：

```powershell
docker compose restart thingsboard
```

查看最近200行日志：

```powershell
docker compose logs --tail 200 thingsboard
```

持续查看日志：

```powershell
docker compose logs -f --tail 200 thingsboard
```

筛选常见严重错误：

```powershell
docker compose logs --since 30m thingsboard | Select-String -Pattern 'ERROR|Exception|OutOfMemory|PSQLException|Connection refused|Killed'
```

查看一次资源快照：

```powershell
docker stats --no-stream thingsboard-thingsboard-1
```

验证首页：

```powershell
curl.exe --noproxy "*" --output NUL --write-out "HTTP=%{http_code} TOTAL=%{time_total}s`n" http://127.0.0.1:9091/
```

## 5. 常见故障排查

### 5.1 端口冲突

典型现象：容器无法启动，日志或命令行出现 `port is already allocated`、`address already in use`。

检查9091和1883端口：

```powershell
Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
Where-Object { $_.LocalPort -in @(9091,1883) } |
Select-Object LocalAddress,LocalPort,OwningProcess
```

根据进程ID确认程序：

```powershell
Get-Process -Id 需要替换的进程ID
```

处理原则：先确认占用程序，不直接结束未知进程；需要换端口时只修改Compose映射左侧的宿主机端口，例如将 `9091:9090` 改为 `9092:9090`。

### 5.2 数据库连接或启动异常

当前PostgreSQL位于同一个 `tb-postgres` 容器中，没有独立数据库容器。优先从日志判断：

```powershell
docker compose logs --since 30m thingsboard |
Select-String -Pattern 'PSQLException|password authentication failed|Connection refused|database system|PostgreSQL'
```

检查容器进程：

```powershell
docker top thingsboard-thingsboard-1
```

检查持久化目录是否存在：

```powershell
Test-Path .\data
Test-Path .\data\db
```

处理原则：先保存日志和确认磁盘/挂载，不删除 `data` 目录，不使用 `docker compose down -v`。

### 5.3 容器崩溃或反复重启

查看退出码、OOM和重启次数：

```powershell
docker inspect --format 'Status={{.State.Status}} Exit={{.State.ExitCode}} Restarts={{.RestartCount}} OOM={{.State.OOMKilled}} Error={{.State.Error}}' thingsboard-thingsboard-1
```

查看崩溃前日志：

```powershell
docker logs --tail 300 --timestamps thingsboard-thingsboard-1
```

查看资源：

```powershell
docker stats --no-stream thingsboard-thingsboard-1
```

判断参考：

- `OOM=true`：优先检查Docker Desktop内存限制和Java内存配置。
- `Exit=137`且`OOM=true`：通常表示进程因内存不足被终止。
- 持续出现`PSQLException`：优先检查内置PostgreSQL、数据目录和磁盘空间。
- RestartCount持续增加：保存首次异常堆栈，不要只看日志最后一行。

## 6. 已发现风险与告警

### ENV-R01：镜像使用latest标签

- 级别：中
- 现象：Compose配置为 `thingsboard/tb-postgres`，实际解析为 `latest`。
- 风险：重新拉取镜像后版本可能变化，导致测试环境不可复现。
- 处理：完成备份和镜像信息确认后，将镜像固定为与当前运行版本匹配的明确标签；修改前不执行pull。

### ENV-R02：Compose version字段已过时

- 级别：低
- 现象：Docker Compose v5.5.0提示顶层 `version` 属性已过时并被忽略。
- 影响：当前不影响启动，但会产生警告并可能让配置含义不清晰。
- 处理：后续先备份Compose文件，再删除顶层version字段并执行 `docker compose config` 验证。

### ENV-R03：Gateway扩展仓库同步失败

- 级别：低，当前判断不阻塞核心测试
- 现象：启动后访问GitHub仓库时出现 `Connection refused github.com`。
- 当前影响：首页仍返回HTTP 200，核心服务启动成功；可能影响gateway管理扩展内容同步。
- 处理：记录为环境网络问题。当前测试范围不依赖该扩展；若后续测试gateway相关功能，再专项处理网络访问。

## 7. 环境准入结论

当前已经满足以下条件：

- Docker Engine和Compose可用。
- ThingsBoard容器正常运行。
- Web首页返回HTTP 200。
- 数据和日志具备持久化挂载。
- 服务能够完成重启并恢复访问。
- 没有OOM和异常重启记录。
- Docker Desktop重启策略可使ThingsBoard服务自动恢复运行；续测前仍需用`docker compose ps`和HTTP检查确认实时状态。

后续优化项：

- 在需求分析阶段核对租户管理员实际菜单。
- 决定并实施镜像版本固定策略；该项不阻塞当前测试。

环境已准入，可以进入需求分析和功能测试阶段。
