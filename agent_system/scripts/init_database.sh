#!/bin/bash
# ============================================================================
# 数据库初始化脚本
# ============================================================================

set -e

echo "=========================================="
echo "初始化上下文管理数据库"
echo "=========================================="

# 配置
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5434}"
POSTGRES_DB="${POSTGRES_DB:-wangyue_postgres}"
POSTGRES_USER="${POSTGRES_USER:-wangyue}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-wangyue_dev_password}"

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SCHEMA_FILE="$SCRIPT_DIR/../context/schema.sql"

# 检查schema文件是否存在
if [ ! -f "$SCHEMA_FILE" ]; then
    echo "错误: 找不到schema文件: $SCHEMA_FILE"
    exit 1
fi

echo "连接信息:"
echo "  Host: $POSTGRES_HOST"
echo "  Port: $POSTGRES_PORT"
echo "  Database: $POSTGRES_DB"
echo "  User: $POSTGRES_USER"
echo ""

# 等待PostgreSQL就绪
echo "等待PostgreSQL就绪..."
for i in {1..30}; do
    if PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d postgres -c '\q' 2>/dev/null; then
        echo "PostgreSQL已就绪"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "错误: 无法连接到PostgreSQL"
        exit 1
    fi
    echo "等待中... ($i/30)"
    sleep 1
done

# 创建数据库（如果不存在）
echo ""
echo "检查数据库..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d postgres -tc \
    "SELECT 1 FROM pg_database WHERE datname = '$POSTGRES_DB'" | grep -q 1 || \
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d postgres -c \
    "CREATE DATABASE $POSTGRES_DB"

echo "数据库 $POSTGRES_DB 已就绪"

# 执行schema
echo ""
echo "执行数据库schema..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -f $SCHEMA_FILE

echo ""
echo "=========================================="
echo "数据库初始化完成!"
echo "=========================================="
echo ""
echo "创建的表:"
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -c "\dt"

echo ""
echo "创建的视图:"
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -c "\dv"

echo ""
echo "✅ 所有操作已完成"

