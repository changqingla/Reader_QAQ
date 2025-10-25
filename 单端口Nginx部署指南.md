# 单端口 Nginx 反向代理部署指南

## 🎯 方案概述

通过 Nginx 反向代理，**仅使用一个公网端口（30003）** 即可访问所有服务：
- 前端静态文件
- 后端 API
- MinIO 文件存储

### 架构图
```
公网访问: http://39.183.168.206:30003
                    ↓
        Nginx (监听 0.0.0.0:3003)
                    ↓
    ┌───────────────┼───────────────┐
    ↓               ↓               ↓
前端静态        后端 API        MinIO 文件
  /           /api/*         /minio/*
  ↓               ↓               ↓
dist/     localhost:8000  localhost:8999
```

## 📋 部署步骤

### 步骤 1：安装 Nginx

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nginx -y

# CentOS/RHEL
sudo yum install nginx -y

# 启动 Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 步骤 2：部署 Nginx 配置

```bash
# 复制配置文件到 Nginx 配置目录
sudo cp /data/ht/workspace/Reader_QAQ/nginx/reader_qaq.conf /etc/nginx/conf.d/

# 测试配置是否正确
sudo nginx -t

# 如果测试通过，重新加载配置
sudo systemctl reload nginx
```

### 步骤 3：构建前端

```bash
cd /data/ht/workspace/Reader_QAQ/web

# 安装依赖（如果还没安装）
npm install

# 构建生产版本
npm run build

# 验证构建产物
ls -lh dist/
```

构建完成后，静态文件会在 `web/dist/` 目录。

### 步骤 4：启动后端服务

```bash
cd /data/ht/workspace/Reader_QAQ/src
python main.py
```

或使用后台运行：

```bash
# 使用 nohup
nohup python main.py > backend.log 2>&1 &

# 或使用 screen
screen -S reader-backend
python main.py
# 按 Ctrl+A 然后 D 退出 screen

# 或使用 systemd（推荐生产环境）
# 见下方 systemd 配置
```

### 步骤 5：确认 MinIO 正在运行

```bash
# 检查 MinIO 是否在运行
curl http://localhost:8999/minio/health/live

# 或查看 Docker 容器状态
docker ps | grep minio
```

### 步骤 6：验证部署

#### 1. 测试前端
```bash
curl http://localhost:3003/
# 应该返回 HTML 内容
```

#### 2. 测试后端 API
```bash
curl http://localhost:3003/api/health
# 应该返回: {"status":"ok"}
```

#### 3. 测试 MinIO 代理
```bash
curl http://localhost:3003/minio/reader-uploads/
# 应该返回 MinIO 响应
```

#### 4. 公网访问测试
在本地浏览器访问：`http://39.183.168.206:30003`

## 🔧 Systemd 服务配置（推荐）

### 创建后端服务

```bash
sudo tee /etc/systemd/system/reader-backend.service > /dev/null <<EOF
[Unit]
Description=Reader QAQ Backend API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=root
WorkingDirectory=/data/ht/workspace/Reader_QAQ/src
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# 重新加载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start reader-backend

# 设置开机自启
sudo systemctl enable reader-backend

# 查看状态
sudo systemctl status reader-backend

# 查看日志
sudo journalctl -u reader-backend -f
```

## 📝 配置说明

### Nginx 配置文件位置
`/etc/nginx/conf.d/reader_qaq.conf`

### 关键配置项

#### 1. 前端静态文件路径
```nginx
root /data/ht/workspace/Reader_QAQ/web/dist;
```
**重要**：确保此路径指向前端构建产物目录！

#### 2. 后端 API 代理
```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8000;
    # ...
}
```

#### 3. MinIO 文件代理
```nginx
location /minio/ {
    rewrite ^/minio/(.*)$ /$1 break;
    proxy_pass http://127.0.0.1:8999;
    # ...
}
```

#### 4. 文件上传大小限制
```nginx
client_max_body_size 100M;
```
根据需要调整此值。

## 🔍 常见问题排查

### 问题 1：前端页面 404

**现象**：访问 `http://39.183.168.206:30003` 返回 404

**排查步骤**：
```bash
# 1. 检查前端是否已构建
ls -lh /data/ht/workspace/Reader_QAQ/web/dist/index.html

# 2. 检查 Nginx 配置
sudo nginx -t

# 3. 检查 Nginx 错误日志
sudo tail -f /var/log/nginx/reader_qaq_error.log

# 4. 检查文件权限
sudo chmod -R 755 /data/ht/workspace/Reader_QAQ/web/dist/
```

### 问题 2：API 请求 502 Bad Gateway

**现象**：前端能访问，但 API 请求返回 502

**排查步骤**：
```bash
# 1. 检查后端是否运行
curl http://localhost:8000/api/health

# 2. 检查后端进程
ps aux | grep "python.*main.py"

# 3. 查看后端日志
sudo journalctl -u reader-backend -f

# 4. 检查端口占用
netstat -tlnp | grep 8000
```

### 问题 3：文件无法加载（MinIO）

**现象**：头像或文档显示不出来

**排查步骤**：
```bash
# 1. 检查 MinIO 是否运行
docker ps | grep minio

# 2. 测试 MinIO 直接访问
curl http://localhost:8999/minio/health/live

# 3. 测试 Nginx 代理
curl http://localhost:3003/minio/reader-uploads/

# 4. 检查 Nginx 错误日志
sudo tail -f /var/log/nginx/reader_qaq_error.log
```

### 问题 4：CORS 错误

**现象**：浏览器控制台显示 CORS 错误

**解决方案**：
后端 CORS 配置已包含 `"*"`，应该不会有 CORS 问题。如果仍然出现：

```bash
# 检查后端配置
grep "CORS_ORIGINS" /data/ht/workspace/Reader_QAQ/src/config/settings.py

# 重启后端
sudo systemctl restart reader-backend
```

### 问题 5：端口占用

**现象**：Nginx 启动失败，提示端口 3003 被占用

**解决方案**：
```bash
# 查看占用端口的进程
sudo lsof -i :3003
# 或
sudo netstat -tlnp | grep 3003

# 如果是旧的进程，kill 掉
sudo kill -9 <PID>

# 重启 Nginx
sudo systemctl restart nginx
```

## 🚀 一键部署脚本

```bash
#!/bin/bash
# 快速部署脚本

set -e

echo "🚀 开始部署 Reader QAQ..."

# 1. 安装 Nginx（如果需要）
if ! command -v nginx &> /dev/null; then
    echo "📦 安装 Nginx..."
    sudo apt update
    sudo apt install nginx -y
fi

# 2. 部署 Nginx 配置
echo "⚙️  配置 Nginx..."
sudo cp /data/ht/workspace/Reader_QAQ/nginx/reader_qaq.conf /etc/nginx/conf.d/
sudo nginx -t
sudo systemctl reload nginx

# 3. 构建前端
echo "🔨 构建前端..."
cd /data/ht/workspace/Reader_QAQ/web
npm install
npm run build

# 4. 启动后端（使用 systemd）
echo "🚀 启动后端..."
sudo systemctl restart reader-backend || echo "⚠️  后端服务配置文件不存在，请手动创建"

# 5. 验证
echo "✅ 部署完成！正在验证..."
sleep 2

echo "前端测试:"
curl -s http://localhost:3003/ | head -1

echo "后端测试:"
curl -s http://localhost:3003/api/health

echo ""
echo "🎉 部署成功！"
echo "📍 访问地址: http://39.183.168.206:30003"
echo ""
echo "📊 查看日志:"
echo "  - Nginx: sudo tail -f /var/log/nginx/reader_qaq_error.log"
echo "  - 后端: sudo journalctl -u reader-backend -f"
```

将此脚本保存为 `deploy.sh`，然后执行：
```bash
chmod +x deploy.sh
./deploy.sh
```

## 📊 服务管理命令

### Nginx
```bash
sudo systemctl start nginx      # 启动
sudo systemctl stop nginx       # 停止
sudo systemctl restart nginx    # 重启
sudo systemctl reload nginx     # 重新加载配置（推荐）
sudo systemctl status nginx     # 查看状态
sudo nginx -t                   # 测试配置
```

### 后端服务
```bash
sudo systemctl start reader-backend     # 启动
sudo systemctl stop reader-backend      # 停止
sudo systemctl restart reader-backend   # 重启
sudo systemctl status reader-backend    # 查看状态
sudo journalctl -u reader-backend -f    # 查看日志
```

### 日志查看
```bash
# Nginx 访问日志
sudo tail -f /var/log/nginx/reader_qaq_access.log

# Nginx 错误日志
sudo tail -f /var/log/nginx/reader_qaq_error.log

# 后端日志
sudo journalctl -u reader-backend -f --since "10 minutes ago"
```

## 🔒 安全建议

1. **防火墙配置**
```bash
# 只开放 3003 端口
sudo ufw allow 3003/tcp
sudo ufw enable
```

2. **HTTPS 配置**（可选）
如果有域名和 SSL 证书，建议启用 HTTPS：
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # ... 其他配置 ...
}
```

3. **移除 CORS 通配符**
生产环境应该从后端配置中移除 `"*"`：
```python
# src/config/settings.py
CORS_ORIGINS: List[str] = [
    "http://39.183.168.206:30003",  # 只允许实际的前端地址
]
```

## ✅ 验证清单

部署完成后，请逐一验证：

- [ ] 访问 `http://39.183.168.206:30003` 能看到登录页面
- [ ] 能够成功注册新用户
- [ ] 能够成功登录
- [ ] 能够创建知识库
- [ ] 能够上传文档
- [ ] 上传的文档能正常显示和预览
- [ ] 能够上传知识库头像
- [ ] 头像能正常显示
- [ ] 能够创建笔记
- [ ] 能够创建文件夹
- [ ] 文件夹和笔记的操作都正常

## 📞 需要帮助？

如果遇到问题：
1. 查看相关日志（Nginx 和后端）
2. 检查所有服务是否正常运行
3. 验证网络连通性
4. 参考上面的"常见问题排查"部分

祝部署顺利！🎉

