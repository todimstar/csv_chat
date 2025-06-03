# 后端技术设计文档（Backend Technical Design Document）
版本：1.0
日期：2025-05-28
作者：后端架构师 & 团队
状态：草稿

## 1. 文档修订记录
| 版本 | 日期       | 作者      | 描述         |
| ---- | ---------- | --------- | ------------ |
| 1.0  | 2025-05-28 | 后端架构师 | 初始创建     |

## 2. 架构概述
- **技术栈**：Python 3.8+、FastAPI、Uvicorn、PostgreSQL、Redis、Celery、Docker、Kubernetes
- **部署方式**：容器化部署，支持 Docker Compose 本地调试和 Kubernetes 集群生产环境
- **微服务划分**：
  - API 服务：负责接收前端请求并返回同步/异步结果
  - 异步任务服务：使用 Celery Worker 处理耗时分析及 AI 调用
  - 数据存储服务：PostgreSQL 存储任务和分析结果，Redis 用于队列和缓存
  - 对象存储（可选）：存储用户上传的大文件或中间结果

## 3. 系统组件
### 3.1 API 服务
- **框架**：FastAPI
- **主要模块**：
  - `routers/`：REST 接口路由定义
  - `services/`：业务逻辑实现
  - `models/`：Pydantic 数据模型和数据库 ORM 模型
  - `utils/`：通用工具（文件校验、错误处理、日志等）
  - `config.py`：配置管理，支持环境变量与配置文件
- **启动**：通过 Uvicorn 启动 `app:app`

### 3.2 异步任务服务
- **框架**：Celery
- **Broker**：Redis
- **任务**：
  - CSV 解析与统计任务
  - AI 分析任务（摘要、清理建议、文件夹问答）
- **重试机制**：任务失败后自动重试，最多 3 次，指数退避

### 3.3 数据存储
- **数据库**：PostgreSQL
- **重要表结构**：
  - `analysis_task`：存储分析任务元信息（id, file_path, status, created_at, updated_at）
  - `analysis_result`：存储统计摘要数据(JSONB格式)
  - `ai_responses`：存储 AI 生成的建议与问答结果
  - `folder_queries`：存储具体文件夹问答记录
- **缓存**：Redis 用于存储短期查询结果，加速频繁请求

### 3.4 对象存储
- 支持本地文件系统或 S3 兼容存储
- 上传的 CSV 文件和生成的中间文件存储于对象存储

### 3.5 日志与监控
- **日志框架**：Loguru 或 Python 标准 `logging`
- **监控**：Prometheus + Grafana 采集指标（API 请求、任务队列长度、错误率）
- **报警**：基于 Prometheus Alertmanager 配置

## 4. 模块设计
### 4.1 路由模块（routers）
- 按资源分文件：`upload.py`、`analysis.py`、`query.py`、`logs.py`
- 使用 FastAPI 路由和依赖注入（Dependency Injection）管理认证与配置

### 4.2 服务模块（services）
- 业务逻辑与数据库操作分离
- 每个主要功能对应一个 Service 类（`UploadService`、`AnalysisService`、`QueryService`）

### 4.3 数据模型（models）
- **Pydantic**：请求/响应模型定义（自动生成 OpenAPI 文档）
- **SQLAlchemy/ORM**：数据库表与模型映射

### 4.4 配置管理
- `config.py` 统一加载环境变量或 `.env` 文件
- 支持不同环境的配置文件（开发、测试、生产）

## 5. 数据库设计
### 5.1 ER 图简述
```text
[Upload] 1 ---- n [AnalysisTask] 1 ---- n [AIResponse]
```
### 5.2 示例表结构
```sql
CREATE TABLE analysis_task (
  id UUID PRIMARY KEY,
  file_path TEXT NOT NULL,
  status VARCHAR(20) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP
);

CREATE TABLE analysis_result (
  task_id UUID REFERENCES analysis_task(id),
  summary JSONB,
  PRIMARY KEY (task_id)
);

CREATE TABLE ai_responses (
  id SERIAL PRIMARY KEY,
  task_id UUID REFERENCES analysis_task(id),
  type VARCHAR(50) NOT NULL,
  content JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE folder_queries (
  id SERIAL PRIMARY KEY,
  task_id UUID REFERENCES analysis_task(id),
  folder_path TEXT NOT NULL,
  user_query TEXT,
  response JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## 6. 异步流程
1. 用户上传 CSV → API 服务入库 → 返回 `analysis_id`
2. Celery Worker 获取任务，解析 CSV，生成统计摘要并写入 `analysis_result`
3. Celery Worker 调用 AI 服务生成清理建议和问答结果，写入 `ai_responses`

## 7. 安全与权限
- **认证**：支持 JWT 或 API Key，使用 OAuth2 密码模式或 Header 传递
- **授权**：基于角色的访问控制（RBAC），运维用户和普通用户分离
- **输入校验**：严格校验文件和请求参数，防范注入攻击

## 8. CI/CD 与测试
- **代码分析**：使用 `flake8` + `black`
- **测试框架**：`pytest`，覆盖核心逻辑与接口测试
- **管道**：GitHub Actions 实现拉取请求自动测试、Lint、构建 Docker 镜像并推送
- **部署**：基于 Docker Compose（dev）和 Kubernetes（prod）

## 9. 可观测性
- **日志**：结构化日志输出到 ELK 或 Loki
- **指标**：Prometheus 指标暴露在 `/metrics` 接口
- **追踪**：支持 OpenTelemetry 分布式追踪 