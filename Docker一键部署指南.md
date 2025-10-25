# Docker 一键部署指南

## 🎯 方案说明

使用 Docker Compose 部署以下服务：
- ✅ PostgreSQL（数据库）
- ✅ Redis（缓存）
- ✅ MinIO（文件存储）
- ✅ Nginx（反向代理）

后端和前端在**宿主机**上单独启动。

## 📋 架构图

```
                   公网访问
                      ↓
          http://39.183.168.206:30003
                      ↓
            Docker: Nginx (3003:80)
                      ↓
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
   前端静态      后端 API        MinIO
    dist/    host:8000      Docker:9000
      ↑            ↑
      |            |
   宿主机        宿主机
```

## 🚀 快速开始

### 步骤 1：构建前端

```bash
cd /data/ht/workspace/Reader_QAQ/web
npm install
npm run build
```

### 步骤 2：启动 Docker 服务

```bash
cd /data/ht/workspace/Reader_QAQ/docker
docker-compose up -d
```

这会启动：
- PostgreSQL（端口 5433）
- Redis（端口 6380）
- MinIO（端口 8999, 9002）
- Nginx（端口 3003）

### 步骤 3：启动后端

```bash
cd /data/ht/workspace/Reader_QAQ/src
python main.py
```

### 步骤 4：访问应用

打开浏览器访问：**http://39.183.168.206:30003**

## 📝 详细说明

### Docker Compose 服务

#### 1. PostgreSQL
- 容器名：`reader_postgres`
- 端口映射：`5433:5432`
- 数据库：`reader_qaq`
- 用户：`reader`
- 密码：`reader_dev_password`

#### 2. Redis
- 容器名：`reader_redis`
- 端口映射：`6380:6379`
- 密码：`reader_dev_password`

#### 3. MinIO
- 容器名：`reader_minio`
- 端口映射：
  - API: `8999:9000`
  - Console: `9002:9001`
- 用户：`reader`
- 密码：`reader_dev_password`

#### 4. Nginx
- 容器名：`reader_nginx`
- 端口映射：`3003:80`
- 挂载：
  - 配置文件：`nginx/nginx-docker.conf`
  - 前端静态文件：`web/dist`
- 代理规则：
  - `/` → 前端静态文件
  - `/api/*` → 宿主机后端（localhost:8000）
  - `/minio/*` → Docker MinIO 服务

### 目录结构

```
Reader_QAQ/
├── docker/
│   ├── docker-compose.yml    # Docker Compose 配置
│   └── init-db/              # 数据库初始化脚本
├── nginx/
│   └── nginx-docker.conf     # Nginx 配置
├── web/
│   └── dist/                 # 前端构建产物（需先构建）
└── src/
    └── main.py              # 后端入口
```

## 🔧 常用命令

### Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f reader_nginx

# 停止所有服务
docker-compose down

# 停止并删除数据卷（慎用！会删除数据库数据）
docker-compose down -v

# 重启特定服务
docker-compose restart reader_nginx

# 重新加载 Nginx 配置
docker exec reader_nginx nginx -s reload
```

### 查看容器状态

```bash
# 查看所有容器
docker ps

# 查看 Nginx 容器
docker ps | grep reader_nginx

# 进入 Nginx 容器
docker exec -it reader_nginx sh

# 查看 Nginx 配置
docker exec reader_nginx cat /etc/nginx/conf.d/default.conf

# 测试 Nginx 配置
docker exec reader_nginx nginx -t
```

### 查看日志

```bash
# Nginx 访问日志
docker exec reader_nginx tail -f /var/log/nginx/access.log

# Nginx 错误日志
docker exec reader_nginx tail -f /var/log/nginx/error.log

# 所有服务日志
docker-compose logs -f --tail=100
```

## 🔍 故障排查

### 问题 1：前端页面 404

**排查步骤**：

```bash
# 1. 检查前端是否已构建
ls -lh /data/ht/workspace/Reader_QAQ/web/dist/index.html

# 2. 检查 Nginx 容器中的文件
docker exec reader_nginx ls -lh /usr/share/nginx/html/

# 3. 查看 Nginx 错误日志
docker-compose logs reader_nginx
```

**解决方案**：
```bash
# 重新构建前端
cd /data/ht/workspace/Reader_QAQ/web
npm run build

# 重启 Nginx
docker-compose restart reader_nginx
```

### 问题 2：后端 API 502 错误

**排查步骤**：

```bash
# 1. 检查后端是否在运行
curl http://localhost:8000/api/health

# 2. 检查 Nginx 能否访问宿主机
docker exec reader_nginx ping -c 3 host.docker.internal

# 3. 测试从容器内访问后端
docker exec reader_nginx wget -O- http://host.docker.internal:8000/api/health
```

**解决方案**：
- 确保后端在宿主机上运行
- 检查防火墙设置

### 问题 3：MinIO 文件无法访问

**排查步骤**：

```bash
# 1. 检查 MinIO 是否运行
docker ps | grep reader_minio

# 2. 测试 MinIO API
curl http://localhost:8999/minio/health/live

# 3. 从 Nginx 容器测试
docker exec reader_nginx wget -O- http://reader_minio:9000/minio/health/live
```

### 问题 4：端口被占用

**现象**：启动失败，提示端口已被占用

**解决方案**：

```bash
# 查看占用端口的进程
sudo lsof -i :3003
sudo lsof -i :8999
sudo lsof -i :5433
sudo lsof -i :6380

# 停止占用端口的容器
docker stop $(docker ps -q --filter "publish=3003")

# 或修改 docker-compose.yml 中的端口映射
```

### 问题 5：数据库连接失败

**排查步骤**：

```bash
# 1. 检查 PostgreSQL 是否运行
docker-compose ps reader_postgres

# 2. 测试连接
docker exec reader_postgres psql -U reader -d reader_qaq -c "SELECT 1;"

# 3. 查看日志
docker-compose logs reader_postgres
```

## 🔄 更新部署

### 更新前端

```bash
# 1. 构建新的前端
cd /data/ht/workspace/Reader_QAQ/web
npm run build

# 2. Nginx 会自动使用新的文件（挂载卷）
# 如果需要，可以重启 Nginx
docker-compose restart reader_nginx
```

### 更新 Nginx 配置

```bash
# 1. 修改配置文件
vim /data/ht/workspace/Reader_QAQ/nginx/nginx-docker.conf

# 2. 测试配置
docker exec reader_nginx nginx -t

# 3. 重新加载配置
docker exec reader_nginx nginx -s reload

# 或重启容器
docker-compose restart reader_nginx
```

### 更新后端

后端在宿主机运行，直接重启即可：

```bash
# 停止当前进程（Ctrl+C 或 kill）
# 然后重新启动
cd /data/ht/workspace/Reader_QAQ/src
python main.py
```

## 📊 性能监控

### 查看资源使用情况

```bash
# 查看所有容器资源使用
docker stats

# 查看特定容器
docker stats reader_nginx reader_minio
```

### 查看磁盘使用

```bash
# 查看 Docker 卷大小
docker system df -v

# 查看特定卷
docker volume ls
docker volume inspect reader_postgres_data
```

## 🔒 安全建议

### 1. 生产环境配置

修改 `docker-compose.yml`：

```yaml
# 移除端口映射（只通过 Nginx 访问）
reader_postgres:
  # ports:
  #   - "5433:5432"  # 注释掉，不对外暴露

reader_redis:
  # ports:
  #   - "6380:6379"  # 注释掉，不对外暴露

reader_minio:
  ports:
    # - "8999:9000"  # 注释掉，只通过 Nginx /minio/ 访问
    - "9002:9001"   # MinIO Console，可保留用于管理
```

### 2. 修改默认密码

```bash
# 修改 docker-compose.yml 中的密码
POSTGRES_PASSWORD: your-strong-password
MINIO_ROOT_PASSWORD: your-strong-password
```

### 3. 使用环境变量文件

创建 `.env` 文件：

```bash
# .env
POSTGRES_PASSWORD=your-strong-password
REDIS_PASSWORD=your-strong-password
MINIO_ROOT_PASSWORD=your-strong-password
```

修改 `docker-compose.yml`：

```yaml
environment:
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

## 📦 备份与恢复

### 备份数据库

```bash
# 备份
docker exec reader_postgres pg_dump -U reader reader_qaq > backup_$(date +%Y%m%d).sql

# 恢复
cat backup_20241024.sql | docker exec -i reader_postgres psql -U reader -d reader_qaq
```

### 备份 MinIO 数据

```bash
# 使用 docker cp 备份整个数据目录
docker cp reader_minio:/data ./minio_backup_$(date +%Y%m%d)

# 恢复
docker cp ./minio_backup_20241024 reader_minio:/data
```

## ✅ 完整部署检查清单

部署完成后，请逐一验证：

- [ ] Docker 服务已启动：`docker-compose ps`
- [ ] PostgreSQL 可连接
- [ ] Redis 可连接
- [ ] MinIO 可访问：`http://localhost:8999`
- [ ] 前端已构建：`web/dist/index.html` 存在
- [ ] 后端已启动：`http://localhost:8000/api/health` 返回 OK
- [ ] Nginx 已启动：`docker ps | grep reader_nginx`
- [ ] 公网可访问：`http://39.183.168.206:30003`
- [ ] 能够注册登录
- [ ] 能够上传文件
- [ ] 头像和文档能正常显示

## 🎉 完成！

现在您可以使用以下命令一键启动所有服务：

```bash
# 1. 启动 Docker 服务
cd /data/ht/workspace/Reader_QAQ/docker
docker-compose up -d

# 2. 启动后端
cd /data/ht/workspace/Reader_QAQ/src
python main.py
```

访问：**http://39.183.168.206:30003**

如有问题，请参考"故障排查"部分或查看日志。


