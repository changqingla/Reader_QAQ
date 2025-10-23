# Docker 服务说明

本目录包含 Reader QAQ 后端所需的所有基础服务。

## 🐳 服务列表

### PostgreSQL
- **版本**: 16-alpine
- **端口**: 5433
- **数据库**: reader_qaq
- **用户**: reader
- **密码**: reader_dev_password

### Redis
- **版本**: 7-alpine
- **端口**: 6380
- **密码**: reader_dev_password

### MinIO
- **版本**: latest
- **端口**: 
  - 8999 (API)
  - 9002 (控制台)
- **用户**: reader
- **密码**: reader_dev_password
- **控制台**: http://localhost:9002

## 🚀 使用方法

### 启动所有服务
```bash
docker-compose up -d
```

### 查看日志
```bash
docker-compose logs -f
```

### 查看服务状态
```bash
docker-compose ps
```

### 停止服务
```bash
docker-compose down
```

### 清理数据（⚠️ 谨慎使用）
```bash
docker-compose down -v
```

## 📁 初始化脚本

`init-db/` 目录下的 SQL 文件会在 PostgreSQL 首次启动时自动执行，用于：
- 创建必要的扩展（uuid-ossp, pg_trgm）
- 创建触发器函数

## 🏥 健康检查

所有服务都配置了健康检查：

```bash
# 检查 PostgreSQL
docker exec reader_postgres pg_isready -U reader

# 检查 Redis  
docker exec reader_redis redis-cli -a reader_dev_password ping

# 检查 MinIO
curl http://localhost:8999/minio/health/live
```

## ⚠️ 注意事项

**生产环境部署时请修改：**
1. ✅ 所有默认密码
2. ✅ 网络配置
3. ✅ 数据卷持久化位置
4. ✅ 启用 SSL/TLS
5. ✅ 配置防火墙规则

## 📝 开发提示

- 数据持久化在 Docker volumes 中
- 重启容器不会丢失数据
- 使用 `docker-compose down -v` 会删除所有数据
- MinIO 控制台可以查看上传的文件

