#!/bin/bash
# Reader QAQ 一键启动脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_DIR="/data/ht/workspace/Reader_QAQ"

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}    Reader QAQ 一键启动${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# 步骤 1: 检查并构建前端
echo -e "${YELLOW}📦 步骤 1/3: 检查前端构建${NC}"
if [ ! -f "$PROJECT_DIR/web/dist/index.html" ]; then
    echo "前端未构建，开始构建..."
    cd "$PROJECT_DIR/web"
    
    if [ ! -d "node_modules" ]; then
        echo "安装前端依赖..."
        npm install
    fi
    
    echo "构建前端..."
    npm run build
    echo -e "${GREEN}✓ 前端构建完成${NC}"
else
    echo -e "${GREEN}✓ 前端已构建${NC}"
fi

# 步骤 2: 启动 Docker 服务
echo ""
echo -e "${YELLOW}🐳 步骤 2/3: 启动 Docker 服务${NC}"
cd "$PROJECT_DIR/docker"

# 检查是否已启动
if docker-compose ps | grep -q "Up"; then
    echo "Docker 服务已在运行，重启中..."
    docker-compose restart
else
    echo "启动 Docker 服务..."
    docker-compose up -d
fi

echo "等待服务就绪..."
sleep 3

# 检查服务状态
echo ""
echo "检查服务状态:"
docker-compose ps

if docker-compose ps | grep -q "reader_nginx.*Up"; then
    echo -e "${GREEN}✓ Nginx 已启动${NC}"
else
    echo -e "${RED}✗ Nginx 启动失败${NC}"
    exit 1
fi

if docker-compose ps | grep -q "reader_postgres.*Up"; then
    echo -e "${GREEN}✓ PostgreSQL 已启动${NC}"
else
    echo -e "${RED}✗ PostgreSQL 启动失败${NC}"
    exit 1
fi

if docker-compose ps | grep -q "reader_redis.*Up"; then
    echo -e "${GREEN}✓ Redis 已启动${NC}"
else
    echo -e "${RED}✗ Redis 启动失败${NC}"
    exit 1
fi

if docker-compose ps | grep -q "reader_minio.*Up"; then
    echo -e "${GREEN}✓ MinIO 已启动${NC}"
else
    echo -e "${RED}✗ MinIO 启动失败${NC}"
    exit 1
fi

# 步骤 3: 提示启动后端
echo ""
echo -e "${YELLOW}🚀 步骤 3/3: 启动后端${NC}"
echo -e "${BLUE}请在新终端中执行以下命令启动后端：${NC}"
echo ""
echo -e "  ${GREEN}cd $PROJECT_DIR/src${NC}"
echo -e "  ${GREEN}python main.py${NC}"
echo ""

# 完成
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}🎉 Docker 服务启动成功！${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo -e "📍 服务地址:"
echo -e "   前端: ${BLUE}http://39.183.168.206:30003${NC}"
echo -e "   后端健康检查: ${BLUE}http://localhost:8000/api/health${NC}"
echo -e "   MinIO Console: ${BLUE}http://localhost:9002${NC}"
echo ""
echo -e "📊 常用命令:"
echo -e "   查看日志: ${GREEN}cd docker && docker-compose logs -f${NC}"
echo -e "   停止服务: ${GREEN}cd docker && docker-compose down${NC}"
echo -e "   重启 Nginx: ${GREEN}docker-compose restart reader_nginx${NC}"
echo ""
echo -e "${YELLOW}⚠️  记得启动后端服务！${NC}"
echo ""


