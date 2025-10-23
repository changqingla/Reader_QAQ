# Reader QAQ - 项目总览

> 一个面向 AI 时代的智能阅读与知识管理平台

## 📋 项目简介

Reader QAQ 是一个现代化的知识管理系统，集成了文档上传、笔记管理、收藏系统和 AI 问答功能。项目采用前后端分离架构，前端使用 React + TypeScript，后端使用 Python FastAPI。

## 🏗️ 技术架构

### 前端
- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **路由**: React Router v7
- **样式**: CSS Modules + Tailwind CSS
- **图标**: Lucide React

### 后端
- **框架**: FastAPI (Python)
- **数据库**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.0 (异步)
- **缓存**: Redis 7
- **对象存储**: MinIO (S3 兼容)
- **认证**: JWT

## 📁 项目结构

```
Reader_QAQ/
├── web/                    # 前端代码
│   ├── pages/             # 页面组件
│   ├── components/        # 通用组件
│   ├── hooks/             # 自定义 Hooks
│   └── lib/               # 工具函数
├── src/                    # 后端代码
│   ├── config/            # 配置模块
│   ├── models/            # 数据模型
│   ├── repositories/      # 数据访问层
│   ├── services/          # 业务逻辑层
│   ├── controllers/       # API 控制器
│   ├── middlewares/       # 中间件
│   ├── utils/             # 工具函数
│   └── types/             # 类型定义
├── docker/                 # Docker 配置
├── public/                 # 静态资源
├── API_SPEC.md            # API 接口文档
├── DB_SCHEMA.md           # 数据库设计
└── BACKEND_SETUP.md       # 后端搭建指南
```

## ✨ 主要功能

### 1. 用户系统
- ✅ 用户注册/登录
- ✅ JWT 认证
- ✅ 用户资料管理

### 2. 笔记管理
- ✅ Markdown 笔记编辑
- ✅ 文件夹分类
- ✅ 标签管理
- ✅ 全文搜索
- ✅ AI 润色功能

### 3. 收藏系统
- ✅ 收藏论文/知识库
- ✅ 标签分类
- ✅ 搜索与筛选
- ✅ 网格/列表视图

### 4. 知识库 (TODO)
- 🚧 文档上传与管理
- 🚧 RAG 问答系统
- 🚧 知识图谱
- 🚧 智能推荐

### 5. 知识广场 (TODO)
- 🚧 公开知识库浏览
- 🚧 订阅与分享
- 🚧 社区互动

## 🚀 快速开始

### 前提条件
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose

### 1. 启动后端服务

```bash
# 启动 Docker 服务
cd docker
docker-compose up -d

# 启动 Python API
cd ../src
./run.sh
```

### 2. 启动前端开发服务器

```bash
cd web
pnpm install
pnpm dev
```

### 3. 访问应用

- **前端**: http://localhost:5173
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/api/docs

## 📚 文档索引

| 文档 | 说明 |
|---|---|
| [API_SPEC.md](./API_SPEC.md) | 后端 API 接口设计规范 |
| [DB_SCHEMA.md](./DB_SCHEMA.md) | PostgreSQL 数据库设计 |
| [BACKEND_SETUP.md](./BACKEND_SETUP.md) | 后端服务搭建指南 |
| [src/README.md](./src/README.md) | 后端开发文档 |
| [docker/README.md](./docker/README.md) | Docker 服务说明 |

## 🎯 开发规范

### 前端
- 使用 TypeScript 严格模式
- 组件采用 CSS Modules
- 遵循 React Hooks 最佳实践
- 代码格式化：ESLint + Prettier

### 后端
- 严格的分层架构（Controller → Service → Repository → Model）
- 完整的类型提示
- Docstring 注释
- 代码格式化：Black + Flake8

## 📊 实现进度

### 前端
- ✅ 页面布局与导航
- ✅ 用户认证界面
- ✅ 笔记管理界面
- ✅ 收藏管理界面
- ✅ 知识库界面（基础）
- ✅ 响应式设计

### 后端
- ✅ 认证系统（100%）
- ✅ 笔记管理（100%）
- ✅ 收藏管理（100%）
- 🚧 知识库（0% - 已标记 TODO）
- 🚧 知识广场（0% - 已标记 TODO）

## 🔐 安全性

- JWT Token 认证
- 密码 bcrypt 哈希
- SQL 注入防护（ORM）
- CORS 配置
- 速率限制（TODO）

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交代码
4. 推送到分支
5. 创建 Pull Request

## 📄 License

MIT

## 👥 作者

Reader QAQ Team

---

**注意**: 所有知识库相关功能（文档上传、RAG问答等）已在代码中用 `TODO` 标记，后续可按需实现。

