# Reader QAQ - Backend API

基于 FastAPI 的后端服务，为 Reader QAQ 前端提供 RESTful API 支持。

## 技术栈

- **Python 3.11+**
- **FastAPI** - 现代异步 Web 框架
- **SQLAlchemy 2.0** - 异步 ORM
- **PostgreSQL** - 主数据库
- **Redis** - 缓存与会话
- **MinIO** - 对象存储（S3 兼容）
- **Alembic** - 数据库迁移

## 项目结构

```
src/
├── config/          # 配置模块（数据库、Redis、设置）
├── models/          # SQLAlchemy 数据库模型
├── repositories/    # 数据访问层（Repository Pattern）
├── services/        # 业务逻辑层
├── controllers/     # API 路由控制器
├── middlewares/     # 中间件（认证、错误处理）
├── utils/           # 工具函数
├── types/           # Pydantic Schemas
└── main.py          # 应用入口
```

## 快速开始

### 1. 启动基础服务

```bash
cd docker
docker-compose up -d
```

这将启动：
- PostgreSQL (端口 5432)
- Redis (端口 6379)
- MinIO (端口 9000, 控制台 9001)

### 2. 安装依赖

```bash
cd src
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件（参考配置见 `config/settings.py`）

### 4. 初始化数据库

```bash
# 数据库表会在应用启动时自动创建
# 如需使用 Alembic 迁移：
# alembic init alembic
# alembic revision --autogenerate -m "Initial migration"
# alembic upgrade head
```

### 5. 启动开发服务器

```bash
python main.py
# 或
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API 文档：http://localhost:8000/api/docs

## API 规范

详细接口定义见项目根目录：
- `API_SPEC.md` - 接口设计文档
- `DB_SCHEMA.md` - 数据库设计文档

## 实现状态

### ✅ 已实现
- 用户认证（登录/注册）
- 笔记管理（CRUD、文件夹、标签）
- 收藏管理（添加/删除/列表）
- 基础中间件（JWT 认证、错误处理）

### 🚧 TODO（待实现）
- 知识库创建与管理
- 文档上传与处理
- RAG 问答功能
- 知识广场（Hub）管理
- RSS 订阅
- 文件上传至 MinIO
- 速率限制中间件
- 审计日志

## 开发规范

### 代码规范
- 使用 Black 格式化代码
- 使用 Flake8 进行 Lint
- 使用 MyPy 进行类型检查

```bash
black .
flake8 .
mypy .
```

### 分层架构
1. **Controller** - 处理 HTTP 请求/响应，调用 Service
2. **Service** - 业务逻辑，调用 Repository
3. **Repository** - 数据库操作，返回 Model
4. **Model** - 数据库模型定义

### 错误处理
统一使用 HTTPException 抛出错误，格式参考 `types/schemas.py` 中的 ErrorResponse。

### 异步编程
所有数据库和 IO 操作使用 async/await。

## 测试

```bash
pytest
pytest --cov=. --cov-report=html
```

## 部署

生产环境部署建议：
1. 使用 Gunicorn + Uvicorn workers
2. 配置 Nginx 反向代理
3. 使用环境变量管理敏感配置
4. 启用 HTTPS
5. 配置日志收集（如 Sentry）

## License

MIT

