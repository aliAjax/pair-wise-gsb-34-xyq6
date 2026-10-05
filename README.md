# 消防设施巡检维保平台（fire-inspect）

面向园区和物业公司的消防设备巡检、隐患整改、维保计划和合规台账系统。支持巡检员按楼栋领取任务逐项提交、异常自动开隐患单、维保整改、主管复验关闭，设备状态与合规总览随处置流程实时重算。

## 快速启动

```bash
cp .env.example .env && docker compose up -d
```

启动后：

- 前端：<http://localhost:20103>
- 后端健康检查：<http://localhost:21103/health>
- API 文档（Swagger）：<http://localhost:21103/docs>

### 演示账号（用户名与密码相同）

| 用户名 | 角色 | 可执行动作 |
|---|---|---|
| `inspector` / `inspector2` | 巡检员 | 按楼栋领取巡检任务、逐项提交合格/异常结果 |
| `maintainer` | 维保人员 | 对派发给自己的隐患单提交整改说明 |
| `supervisor` | 物业主管 | 排期任务、发布清单新版本、隐患派单/复验关闭、任务复核 |
| `auditor` | 审计员 | 只读浏览全部台账与审计日志 |

## 巡检处置流程

```text
主管排期任务(PLANNED)
  └─ 巡检员领取(IN_PROGRESS，先到先得，他人不可重复领取/提交)
       └─ 逐项提交结果（持清单版本号）
            ├─ 合格 NORMAL：仅落结果
            └─ 异常 ABNORMAL：每个异常结果自动生成一张隐患单(OPEN)，设备立即变 FAULT
                 └─ 主管派单(ASSIGNED，指定维保人/级别/期限) → 设备 MAINTAINING
                      └─ 维保人提交整改(RECTIFIED)
                           ├─ 主管复验不通过 → REJECTED，退回维保重新整改
                           └─ 主管复验通过 → CLOSED，设备状态按剩余隐患重算（无隐患恢复 NORMAL）
```

关键一致性规则：

1. **并发提交只落一份**：领取是第一道串行化（原子 UPDATE 抢占）；提交时对任务行加 `FOR UPDATE` 行锁，提交完成任务进入 `SUBMITTED` 终态后后续提交一律 409 拒绝；数据库层还有 `UNIQUE(task_id, item_code)` 兜底。
2. **清单版本冲突**：提交携带巡检员拉取清单时的 `checklist_version`。服务端比对当前版本：
   - 已被新版本移除的旧项 → 拒绝并返回 `CHECKLIST_STALE` 冲突说明；
   - 不属于清单的编号 → `CHECKLIST_ITEM_UNKNOWN`；
   - 新版本中仍存在/新增但本次未提交的项 → 返回补检提示，任务保持 `IN_PROGRESS`；
   - 未过期项照常保存，允许巡检员逐项补录而不是整批作废。
3. **设备状态重算**：异常即 `FAULT`；派单/退回整改中为 `MAINTAINING`；全部隐患 `CLOSED` 后恢复 `NORMAL`。总览页统计与设备台账使用同一套状态口径。
4. **RBAC**：后端 JWT + 角色依赖（`require_roles`）在每个写接口上强制；前端路由守卫、侧边导航与操作按钮同步显隐。审计页仅主管/审计员可进入。
5. **审计日志**：领取、逐项提交、版本过期拒绝、开单、派单、整改、复验关闭等所有写操作落 `audit_log` 表并在「合规报表/审计」页展示。

## 本地开发方式

- 前端：`cd frontend && npm install && npm run dev`（Vite 已配置 `/api` 代理到 `http://localhost:21103`）
- 后端：`cd backend && pip install -r requirements.txt && uvicorn src.main:app --reload --port 21103`
  - 不设置 `DB_HOST` 时自动回退到本地 SQLite（`fire_inspect.db`），启动自动建表并播种演示数据；容器内使用 PostgreSQL 15。
- 后端测试：`cd backend && PYTHONPATH=. pytest tests`（15 个用例覆盖主流程、并发/版本冲突、RBAC 矩阵）

## 访问地址

| 用途 | 地址 |
|---|---|
| 前端 | http://localhost:20103 |
| 后端健康检查 | http://localhost:21103/health |
| Swagger 文档 | http://localhost:21103/docs |

主要 API：`/api/auth/login`、`/api/inspection-task`（领取 `/{id}/claim`、清单 `/{id}/checklist`、发布 `/checklist/publish`、复核 `/{id}/review`）、`/api/inspection-result/task/{id}/submit`、`/api/hazard-ticket/{id}/assign|rectify|review`、`/api/dashboard/overview`、`/api/dashboard/monthly-report`、`/api/audit-log`。

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | React 18 + TypeScript + Vite + Material UI（依赖内置）+ Zustand |
| 后端 | FastAPI + Python 3.11 + SQLAlchemy 2.0 + Pydantic v2 |
| 数据库 | PostgreSQL 15（开发态可回退 SQLite） |
| 认证 | JWT（HS256）+ RBAC |
| 部署 | Docker Compose / Nginx |

## 项目目录结构

```text
frontend/src/
├── api/                  # 按实体分文件 + client 统一请求封装（注入 JWT、错误码映射）
├── stores/               # Zustand：Auth/Building/FireDevice/InspectionTask/InspectionResult/HazardTicket
├── types/                # 共享类型定义（Auth/Dashboard/AuditLog 等）
├── constants/            # 枚举、角色、错误码、错误消息、日志模板、状态文案
├── constructors/         # 按实体的默认对象/表单/响应构造器
├── components/common/    # StatusBadge / HazardSeverityTag / ChecklistPanel / DeviceLocationCell / TimelineList / StatCard / Modal / AlertBanner ...
├── components/layout/    # AppShell（侧边导航 + 路由守卫）
├── hooks/                # useChecklistProgress / useHazardFlow / usePagination
├── pages/                # Login / Dashboard / Devices / Tasks / Hazards / Reports
├── router/               # 路由表（含每路由角色元数据）
├── utils/                # formatters（日期/百分比/各枚举中文文案）
└── mocks/                # 早期演示种子（已不再作为数据源）
backend/src/
├── routes/               # 按实体分文件
├── controllers/          # 入参解析 + require_roles 角色拦截
├── services/             # 业务编排（领取/提交/版本冲突/整改/复验/状态重算/总览报表/审计）
├── models/               # SQLAlchemy 模型（含 checklist 快照/模板、唯一约束）
├── repositories/         # 数据访问层（行锁、唯一约束冲突转换）
├── middlewares/          # auth / rbac / rate_limit / audit_log / error_handler
├── constants/            # 枚举/角色/错误码/错误消息/日志模板
├── constructors/         # ORM -> Pydantic 响应 DTO 工厂
├── db/                   # engine / SessionLocal
├── types/                # Pydantic 请求/响应模型
├── utils/                # JWT/口令、格式化
└── seed.py               # 演示账号/楼栋/设备/任务/v1 清单播种
database/init.sql         # PostgreSQL 初始结构（与模型一致）
backend/tests/            # pytest：主流程 + 并发冲突 + RBAC
```

## 环境变量说明

| 变量 | 默认值 | 说明 |
|---|---|---|
| `COMPOSE_PROJECT_NAME` | `fire-inspect` | Compose 项目名与容器名前缀 |
| `FRONTEND_PORT` | `20103` | 前端宿主端口 |
| `BACKEND_PORT` | `21103` | 后端宿主端口（容器内 8000） |
| `DB_PORT` | `54320` | PostgreSQL 宿主端口 |
| `DB_NAME/DB_USER/DB_PASSWORD` | `app_db/app_user/app_password` | 数据库凭据 |
| `JWT_SECRET` | `local-dev-secret` | JWT 签名密钥（生产请覆盖） |
| `JWT_EXPIRE_MINUTES` | `720` | 令牌有效期（分钟） |
| `RATE_LIMIT_PER_MINUTE` | `120` | 单 IP 滑动窗口限流阈值 |

## Docker 部署说明

- 根 Compose 文件不使用 `version:` 字段，顶层 `name: fire-inspect`，容器名均带 `${COMPOSE_PROJECT_NAME:-fire-inspect}` 前缀。
- 数据库使用命名卷 `db_data`，不绑定挂载（避免中文路径权限问题），并配置 `pg_isready` healthcheck；后端 `depends_on: condition: service_healthy`，前端再以后端 `/health` 为健康条件。
- Nginx 将 `/api/` 反向代理到 `http://backend:8000/api/`，前端只发相对路径请求，无硬编码 localhost。
- 常见问题：端口被占用时改 `.env` 中端口后 `docker compose up -d`；重置数据执行 `docker compose down -v`。

## 枚举/常量出现位置清单

- **DeviceType**（EXTINGUISHER/HYDRANT/SMOKE_DETECTOR/SPRINKLER/EXIT_LIGHT）
  - 前端：`constants/DeviceType.ts`、`types/DeviceType.ts`、`constants/deviceLabels.ts`、`utils/formatters.ts(formatDeviceType)`、任务排期/发布弹窗筛选、`DevicesPage` 类型筛选、`TasksPage`、构造器默认值。
  - 后端：`constants/device_type.py`、`services/inspection_task_service.py(INITIAL_CHECKLISTS)`、清单模板、创建任务校验、`types/fire_device_payload.py`。
- **InspectionStatus**（PLANNED/IN_PROGRESS/SUBMITTED/REVIEWED/OVERDUE）
  - 前端：`constants/InspectionStatus.ts`、`types/InspectionStatus.ts`、`utils/formatters.ts(formatInspectionStatus)`、`StatusBadge` 色调、任务列表筛选与按钮显隐。
  - 后端：`constants/inspection_status.py`（含 `CLOSED_TASK_STATUSES`）、领取/提交/复核服务、总览完成率、日志模板、错误消息（`TASK_CLOSED` 等）。
- **HazardSeverity**（LOW/MEDIUM/HIGH/CRITICAL）
  - 前端：`constants/HazardSeverity.ts`、`types/HazardSeverity.ts`、`HazardSeverityTag`、派单弹窗选项、`utils/formatters.ts(formatRisk)`。
  - 后端：`constants/hazard_severity.py`（含默认级别）、派单校验、开单、总览严重隐患统计。
- 关联新增枚举：`DeviceStatus`（NORMAL/FAULT/MAINTAINING/SCRAPPED）、`ResultStatus`（NORMAL/ABNORMAL）、`RectifyStatus`（OPEN/ASSIGNED/RECTIFIED/CLOSED/REJECTED）、四个 RBAC 角色常量，前后端同名同义。

## 为什么会牵一发动全身

- 修改一个状态值需要同时动：后端枚举常量、服务流转分支、错误码/错误消息、日志模板、Pydantic 模型、前端常量与中文文案、`StatusBadge` 色调、页面按钮显隐、构造器默认值。
- 巡检提交横跨 `InspectionResultService → InspectionTaskService → HazardTicketRepository → FireDevice → DeviceStatusRecalculator → audit_log` 与多个工厂 DTO；清单版本升级还会改 `checklist_template` 与每个进行中任务的 `checklist_item` 快照。
- 总览/报表直接消费设备、任务、结果、隐患四张表的状态，任何一处处置动作都会改变统计口径。

## License

MIT
