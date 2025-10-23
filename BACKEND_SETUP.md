# Reader QAQ 后端服务搭建指南

## 📂 项目结构

```
Reader_QAQ/
├── web/              # 前端代码 (React + TypeScript + Vite)
├── src/              # 后端代码 (FastAPI + Python)
├── docker/           # Docker 配置（PostgreSQL, Redis, MinIO）
├── API_SPEC.md       # API 接口设计文档
└── DB_SCHEMA.md      # 数据库设计文档
```

## ⚡ 快速启动

### 步骤 1：启动 Docker 服务

```bash
cd docker
docker-compose up -d
```

等待所有服务健康检查通过：
```bash
docker-compose ps
```

### 步骤 2：启动后端 API

```bash
cd ../src
./run.sh
```

或手动启动：
```bash
cd src
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

后端服务：http://localhost:8000

- API 文档：http://localhost:8000/api/docs
- ReDoc：http://localhost:8000/api/redoc

### 步骤 3：启动前端（可选）

```bash
cd web
pnpm install
pnpm dev
```

前端：http://localhost:5173

## 🔌 服务端口

| 服务 | 端口 | 说明 |
|---|---|---|
| 前端 (Vite) | 5173 | React 开发服务器 |
| 后端 (FastAPI) | 8000 | API 服务 |
| PostgreSQL | 5433 | 数据库 |
| Redis | 6380 | 缓存 |
| MinIO API | 8999 | 对象存储 API |
| MinIO Console | 9002 | MinIO 管理控制台 |

## ✅ 实现状态

### 已完成
- ✅ Docker 环境配置
- ✅ 项目目录结构（分层架构）
- ✅ 用户认证模块（登录/注册/JWT）
- ✅ 笔记管理模块（完整 CRUD + 润色）
- ✅ 收藏管理模块（完整 CRUD + 切换）
- ✅ 错误处理与统一响应格式
- ✅ API 文档自动生成（Swagger/ReDoc）

### 待实现（已标记 TODO）

#### 知识库核心功能
- [ ] 知识库 CRUD 操作
- [ ] 文档上传至 MinIO
- [ ] 文档解析（PDF, DOCX, Markdown 等）
- [ ] 向量化与存储（需集成 pgvector 或 Milvus）
- [ ] RAG 问答（需集成 LLM API）
- [ ] 文档状态追踪与处理队列

#### 知识广场
- [ ] Hub 模型与 CRUD
- [ ] 帖子管理
- [ ] 订阅关系
- [ ] 搜索与推荐

#### 其他功能
- [ ] 文件夹管理完善
- [ ] 速率限制中间件
- [ ] 审计日志
- [ ] 用户头像上传
- [ ] 刷新令牌机制

## 🎯 符合的软件工程规范

- ✅ **模块化设计**（高内聚低耦合）
- ✅ **职责单一原则**（每个类/函数只做一件事）
- ✅ **依赖倒置**（依赖抽象不依赖实现）
- ✅ **开闭原则**（易扩展不修改）
- ✅ **代码注释完整**（docstring）
- ✅ **类型提示完整**
- ✅ **错误处理规范**
- ✅ **配置与代码分离**
- ✅ **环境隔离**（虚拟环境）
- ✅ **异步编程**（全异步 I/O）

## 📖 API 接口文档

所有接口定义详见项目根目录的 `API_SPEC.md`。

## 🗄️ 数据库设计

数据库表结构详见项目根目录的 `DB_SCHEMA.md`。

## ⚙️ 环境变量

复制并修改配置：
```bash
cd src
cp .env.example .env  # 然后编辑 .env 文件
```

主要配置项见 `src/config/settings.py`。

## 🐛 故障排除

### PostgreSQL 连接失败
```bash
docker-compose ps  # 检查服务状态
docker-compose logs postgres  # 查看日志
```

### Redis 连接失败
```bash
docker exec -it reader_redis redis-cli -a reader_dev_password ping
```

### MinIO 访问失败
访问 http://localhost:9002 查看控制台

## 📈 生产部署建议

1. 使用 Gunicorn + Uvicorn workers
2. 配置 Nginx 反向代理
3. 启用 HTTPS
4. 使用托管数据库服务
5. 配置日志聚合（Sentry, ELK 等）
6. 启用监控（Prometheus + Grafana）
7. 实施备份策略

## 📄 License

MIT

