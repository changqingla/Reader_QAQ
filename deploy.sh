#!/bin/bash
# Reader QAQ 一键部署脚本
# 单端口 Nginx 反向代理方案

set -e

echo "🚀 开始部署 Reader QAQ..."
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 项目路径
PROJECT_DIR="/data/ht/workspace/Reader_QAQ"

# 1. 检查并安装 Nginx
echo -e "${YELLOW}📦 检查 Nginx...${NC}"
if ! command -v nginx &> /dev/null; then
    echo "Nginx 未安装，正在安装..."
    sudo apt update
    sudo apt install nginx -y
else
    echo -e "${GREEN}✓ Nginx 已安装${NC}"
fi

# 2. 部署 Nginx 配置
echo ""
echo -e "${YELLOW}⚙️  部署 Nginx 配置...${NC}"
sudo cp $PROJECT_DIR/nginx/reader_qaq.conf /etc/nginx/conf.d/

echo "测试 Nginx 配置..."
if sudo nginx -t 2>&1 | grep "successful"; then
    echo -e "${GREEN}✓ Nginx 配置正确${NC}"
    sudo systemctl reload nginx
    echo -e "${GREEN}✓ Nginx 已重载${NC}"
else
    echo -e "${RED}✗ Nginx 配置有误，请检查${NC}"
    exit 1
fi

# 3. 构建前端
echo ""
echo -e "${YELLOW}🔨 构建前端...${NC}"
cd $PROJECT_DIR/web

if [ ! -d "node_modules" ]; then
    echo "安装依赖..."
    npm install
fi

echo "构建生产版本..."
npm run build

if [ -f "dist/index.html" ]; then
    echo -e "${GREEN}✓ 前端构建成功${NC}"
    echo "构建产物大小:"
    du -sh dist/
else
    echo -e "${RED}✗ 前端构建失败${NC}"
    exit 1
fi

# 4. 配置后端 systemd 服务
echo ""
echo -e "${YELLOW}🔧 配置后端服务...${NC}"

sudo tee /etc/systemd/system/reader-backend.service > /dev/null <<EOF
[Unit]
Description=Reader QAQ Backend API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR/src
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
echo -e "${GREEN}✓ Systemd 服务配置完成${NC}"

# 5. 启动后端服务
echo ""
echo -e "${YELLOW}🚀 启动后端服务...${NC}"
sudo systemctl restart reader-backend
sudo systemctl enable reader-backend

sleep 2

if sudo systemctl is-active --quiet reader-backend; then
    echo -e "${GREEN}✓ 后端服务已启动${NC}"
else
    echo -e "${RED}✗ 后端服务启动失败，查看日志:${NC}"
    echo "  sudo journalctl -u reader-backend -n 50"
    exit 1
fi

# 6. 验证部署
echo ""
echo -e "${YELLOW}✅ 验证部署...${NC}"
sleep 2

echo -n "前端测试: "
if curl -s http://localhost:3003/ | head -1 | grep -q "<!doctype html"; then
    echo -e "${GREEN}✓ 通过${NC}"
else
    echo -e "${RED}✗ 失败${NC}"
fi

echo -n "后端测试: "
if curl -s http://localhost:3003/api/health | grep -q '"status"'; then
    echo -e "${GREEN}✓ 通过${NC}"
else
    echo -e "${RED}✗ 失败${NC}"
fi

# 7. 完成
echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}🎉 部署成功！${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo -e "📍 访问地址: ${YELLOW}http://39.183.168.206:30003${NC}"
echo ""
echo "📊 常用命令:"
echo "  查看后端状态: sudo systemctl status reader-backend"
echo "  查看后端日志: sudo journalctl -u reader-backend -f"
echo "  查看 Nginx 日志: sudo tail -f /var/log/nginx/reader_qaq_error.log"
echo "  重启后端: sudo systemctl restart reader-backend"
echo "  重载 Nginx: sudo systemctl reload nginx"
echo ""
echo -e "${YELLOW}注意: 确保所有依赖服务（PostgreSQL, Redis, MinIO）都在运行${NC}"
echo ""


