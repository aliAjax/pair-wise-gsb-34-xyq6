# 消防设施巡检维保平台

面向园区和物业公司的消防设备巡检、隐患整改、维保计划和合规台账系统。
支持巡检员按楼栋领取任务逐项提交、异常自动生成隐患单、维保整改、主管复验关闭，
并在流转过程中自动重算消防设备状态与合规总览。

## 快速启动

```bash
cp .env.example .env && docker compose up -d
```

- 前端：<http://localhost:20103>
- 后端健康检查：<http://localhost:21103/health>

演示账号（用户名与密码相同）：

| 账号 | 角色 | 可执行动作 |
|---|---|---|
| `inspector_a` / `inspector_b` | 巡检员 | 按楼栋领取巡检任务、逐项提交检查结果、提交复核 |
| `maintainer_a` | 维保人员 | 查看派给自己的隐患单、提交整改结果 |
| `supervisor_a` | 物业主管 | 排期、派单、升级清单版本、复验关闭任务与隐患单 |
| `auditor_a` | 审计员 | 只读查看报表与全部操作审计日志 |

## 巡检处置流程（端到端）

1. **排期（主管）**：选择楼栋和设备类型，系统按该楼栋此类设备自动生成标准检查清单（每台设备 3 项）。
2. **领取（巡检员）**：待领取任务通过条件更新领取，两名巡检员同时领取只有一人成功（`409 TASK_NOT_CLAIMABLE`）。
3. **逐项提交（巡检员）**：每项携带打开清单时的 `checklist_version`：
   - 正常项直接保存；
   - **异常项自动生成隐患单**（OPEN），设备状态立即重算为“整改中”；
   - 两名巡检员同时提交同一检查项，数据库唯一约束 + 归属校验保证**只落一份结果和一张隐患单**；
   - 清单版本过期的旧项返回 `409 CHECKLIST_VERSION_CONFLICT`，消息说明“v{submitted} 已过期，当前 v{current}”，**旧项拒绝、未过期项照常保存**（批量接口按单项隔离，`saved`/`conflicts` 分别返回）。
4. **提交复核（巡检员）**：全部检查项提交后任务变为“待复验”；缺项返回 `409 TASK_INCOMPLETE`。
5. **派单（主管）**：调整隐患级别、指派维保人员和整改期限。
6. **整改（维保人员）**：只有被指派的维保人员能提交整改结果。
7. **复验关闭（主管）**：通过则隐患单关闭，**消防设备状态与总览重新计算**；不通过退回“待整改”。
8. **审计（审计员）**：所有写操作同事务落审计日志，可在“合规报表 → 操作审计日志”查看。

## 本地开发方式

- 前端：`cd frontend && npm install && npm run dev`（开发服务器代理 `/api` 到 `http://localhost:21103`）
- 后端：`cd backend && pip install -r requirements.txt && PYTHONPATH=. uvicorn src.main:app --reload --port 21103`
  - 未设置 `DB_HOST` 时默认使用本地 SQLite（自动建表、写种子、启用 WAL）；
  - 容器内通过 `DB_HOST=db` 使用 PostgreSQL。
- 后端测试：`cd backend && PYTHONPATH=. python3 tests/test_workflow.py`（58 项端到端断言）
  与 `python3 tests/test_concurrent_submit.py`（并发领取/并发提交只落一份）。

## 主要接口

| 方法 | 路径 | 角色 | 说明 |
|---|---|---|---|
| POST | `/api/auth/login` | 公开 | JWT 登录 |
| GET | `/api/building` `/api/fire-device` | 登录用户 | 楼栋/设备台账 |
| POST | `/api/inspection-task` | 主管 | 按楼栋排期并生成清单 |
| POST | `/api/inspection-task/{id}/claim` | 巡检员 | 领取任务（条件更新防并发） |
| POST | `/api/inspection-result/task/{id}/submit` | 巡检员 | 逐项批量提交（版本冲突/并发单项隔离） |
| POST | `/api/inspection-task/{id}/submit` | 巡检员 | 全部完成后提交复核 |
| POST | `/api/inspection-task/{id}/review` | 主管 | 复验关闭任务 |
| POST | `/api/inspection-task/{id}/checklist-version` | 主管 | 升级清单版本 |
| POST | `/api/hazard-ticket/{id}/assign` | 主管 | 派单 |
| POST | `/api/hazard-ticket/{id}/rectify` | 维保人员 | 整改 |
| POST | `/api/hazard-ticket/{id}/close` | 主管 | 复验关闭/退回 |
| GET | `/api/stats/dashboard` `/api/stats/monthly-report` | 登录用户 | 实时重算的总览与月报 |
| GET | `/api/auth/audit-logs` | 主管/审计员 | 操作审计日志 |

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | React 18 + TypeScript + Vite + Zustand |
| 后端 | FastAPI + Python 3.11 + SQLAlchemy 2.0 |
| 数据库 | PostgreSQL 15（本地开发可用 SQLite + WAL） |
| 认证 | JWT + RBAC |
| 部署 | Docker Compose |

## 项目目录结构

```text
frontend/src/
├── api/            # 按实体分文件 + client.ts（JWT/错误统一封装）
├── stores/         # zustand：Auth/实体/统计 store
├── types/          # 接口与枚举类型
├── constants/      # 枚举、错误码、错误消息、日志模板、状态文案
├── constructors/   # 默认对象/表单/响应构造器
├── components/      # AppShell + common 共享组件（StatusBadge 等）
├── hooks/          # useChecklistProgress / useHazardFlow / usePagination
├── pages/          # 登录、总览、台账、任务、隐患、报表
├── router/         # 路由与角色元数据
├── utils/          # 日期/状态/百分比等格式化
└── mocks/          # 种子数据说明（数据全部来自后端）
backend/src/
├── routes/ controllers/ services/ repositories/ models/
├── database/       # SQLAlchemy engine/session（SQLite WAL / PostgreSQL）
├── middlewares/    # auth / rbac / 限流 / 审计访问日志 / 错误兜底
├── constants/      # 枚举、错误码、错误消息、日志模板
├── constructors/   # ORM 实体 -> 响应 DTO 构造器
├── types/          # 请求体 Pydantic 模型
├── config/         # settings（.env -> compose -> config 多处同步）
├── seed.py         # 幂等种子（账号、楼栋、设备、任务、隐患、审计样例）
└── tests/          # 端到端与并发专项测试
```

## 环境变量说明

- `COMPOSE_PROJECT_NAME`: Compose 项目名，默认 `fire-inspect`
- `FRONTEND_PORT`: 前端端口，默认 `20103`
- `BACKEND_PORT`: 后端端口，默认 `21103`
- `DB_PORT`: 数据库宿主机端口
- `DB_USER/DB_PASSWORD/DB_NAME/DB_HOST`: 数据库连接信息
- `JWT_SECRET`: JWT 签名密钥
- `RATE_LIMIT_PER_MINUTE` / `LOGIN_RATE_LIMIT_PER_MINUTE`: 接口与登录限流

## Docker 部署说明

- 根 Compose 文件不写 `version`，顶层 `name: fire-inspect`。
- 容器名均使用 `${COMPOSE_PROJECT_NAME:-fire-inspect}` 前缀。
- 数据库使用命名卷 `db_data`，避免绑定中文路径。
- 常见问题：端口占用时修改 `.env` 中端口后重启；需要重置数据时执行 `docker compose down -v`。

## 枚举/常量出现位置清单

- **DeviceType** `EXTINGUISHER/HYDRANT/SMOKE_DETECTOR/SPRINKLER/EXIT_LIGHT`
  - 前端：`types/DeviceType.ts`、`constants/DeviceType.ts`、`constants/statusText.ts`、`utils/formatters.ts`、设备台账筛选器、`DeviceLocationCell`、任务排期下拉
  - 后端：`constants/device_type.py`（含标准检查项 `DEVICE_CHECKLIST`）、排期 service、种子数据、`init.sql`
- **DeviceStatus** `NORMAL/FAULT/MAINTAINING/SCRAPPED`
  - 前端：`types/DeviceStatus.ts`、`constants/DeviceStatus.ts`、总览分布、设备列表徽章
  - 后端：`constants/device_status.py`、`FireDeviceService.recalculate_status`、种子数据
- **InspectionStatus** `PLANNED/IN_PROGRESS/SUBMITTED/REVIEWED/OVERDUE`
  - 前端：`types/InspectionStatus.ts`、`constants/InspectionStatus.ts`、任务筛选/徽章、任务页动作按钮
  - 后端：`constants/inspection_status.py`、任务 service 状态机、错误消息、审计模板
- **ResultStatus** `NORMAL/ABNORMAL`：前后端 constants/types、提交载荷、隐患自动生成判定
- **RectifyStatus** `OPEN/ASSIGNED/RECTIFIED/CLOSED`：隐患流转按钮、`useHazardFlow`、设备状态重算
- **HazardSeverity** `LOW/MEDIUM/HIGH/CRITICAL`：提交异常项级别选择、派单分级、`HazardSeverityTag`、总览高危统计
- **UserRole** `INSPECTOR/MAINTAINER/SUPERVISOR/AUDITOR`：JWT claims、`rbac_middleware`、路由守卫、前端菜单/按钮显隐

## 为什么会牵一发动全身

实体字段、枚举、日志模板、错误消息、构造器、筛选器和展示组件被刻意拆散到多个目录；
一次巡检提交流转会同时触达 `types`（载荷）→ `routes/controllers`（RBAC）→
`services`（版本/并发/状态机）→ `repositories/models`（唯一约束）→
`constants`（错误码/日志模板）→ 构造器（DTO）→ 前端 store/页面/组件，
修改一个状态值通常需要同步类型、构造器、服务、控制器、store、页面、README 与数据库种子。

## License

MIT
