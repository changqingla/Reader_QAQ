#!/bin/bash
# 后端服务启动脚本

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}  Reader QAQ Backend Service${NC}"
echo -e "${GREEN}======================================${NC}"

# 检查 Python 版本
# if ! command -v python3 &> /dev/null; then
#     echo -e "${RED}❌ Python 3 not found${NC}"
#     exit 1
# fi

# PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
# echo -e "${YELLOW}🐍 Python version: $PYTHON_VERSION${NC}"

# # 检查虚拟环境
# if [ ! -d "venv" ]; then
#     echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
#     python3 -m venv venv
# fi

# # 激活虚拟环境
# echo -e "${YELLOW}🔧 Activating virtual environment...${NC}"
# source venv/bin/activate

# # 安装依赖
# echo -e "${YELLOW}📚 Installing dependencies...${NC}"
# pip install -q --upgrade pip
# pip install -q -r requirements.txt

# 检查 Docker 服务
echo -e "${YELLOW}🐳 Checking Docker services...${NC}"
if ! docker ps | grep -q reader_postgres; then
    echo -e "${RED}⚠️  PostgreSQL not running. Please start Docker services:${NC}"
    echo -e "${YELLOW}   cd ../docker && docker-compose up -d${NC}"
    exit 1
fi

# 启动服务
echo -e "${GREEN}🚀 Starting API server...${NC}"
python main.py

