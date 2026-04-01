#!/bin/bash
# ============================================
# 学习指认AI平台 — 裸机部署脚本
# 适用于 Ubuntu 22.04+ / CentOS 8+
# ============================================

set -e

APP_DIR="/opt/ai-study-platform"
APP_USER="aistudy"
DB_NAME="ai_study"
DB_USER="aistudy"
DB_PASS="aistudy_db_2026"
PYTHON_VERSION="3.11"

echo "=========================================="
echo "  学习指认AI平台 — 部署安装"
echo "=========================================="

# 1. 系统依赖
echo "[1/8] 安装系统依赖..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update -y
    sudo apt-get install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-venv python${PYTHON_VERSION}-dev \
        postgresql postgresql-contrib redis-server \
        nginx git curl wget build-essential libpq-dev \
        libgl1-mesa-glx libglib2.0-0
elif command -v yum &> /dev/null; then
    sudo yum install -y python3 python3-devel python3-pip \
        postgresql-server postgresql-devel redis \
        nginx git curl wget gcc make \
        mesa-libGL glib2
fi

# 2. 创建应用用户
echo "[2/8] 创建应用用户..."
if ! id "$APP_USER" &>/dev/null; then
    sudo useradd -r -m -s /bin/bash $APP_USER
fi

# 3. 创建目录
echo "[3/8] 创建应用目录..."
sudo mkdir -p $APP_DIR
sudo chown $APP_USER:$APP_USER $APP_DIR

# 4. PostgreSQL 配置
echo "[4/8] 配置 PostgreSQL..."
sudo systemctl enable postgresql
sudo systemctl start postgresql

sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"

sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# 5. Redis 配置
echo "[5/8] 配置 Redis..."
sudo systemctl enable redis-server 2>/dev/null || sudo systemctl enable redis
sudo systemctl start redis-server 2>/dev/null || sudo systemctl start redis

# 6. 部署应用代码
echo "[6/8] 部署应用代码..."
sudo -u $APP_USER bash -c "
    cp -r server/* $APP_DIR/ 2>/dev/null || true
    cd $APP_DIR
    python${PYTHON_VERSION} -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
"

# 7. 配置环境变量
echo "[7/8] 配置环境变量..."
if [ ! -f "$APP_DIR/.env" ]; then
    sudo -u $APP_USER cp $APP_DIR/.env.example $APP_DIR/.env 2>/dev/null || true
    sudo -u $APP_USER sed -i "s|postgresql+asyncpg://postgres:password@localhost:5432/ai_study|postgresql+asyncpg://$DB_USER:$DB_PASS@localhost:5432/$DB_NAME|g" $APP_DIR/.env
fi

# 8. 初始化数据库
echo "[8/8] 初始化数据库..."
sudo -u $APP_USER bash -c "
    cd $APP_DIR
    source venv/bin/activate
    alembic upgrade head 2>/dev/null || python -c '
from app.core.database import Base, engine
import asyncio
from app.models import *
async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
asyncio.run(init())
'
"

echo ""
echo "=========================================="
echo "  安装完成！"
echo "=========================================="
echo ""
echo "后续步骤："
echo "  1. 编辑 $APP_DIR/.env 配置API Key"
echo "  2. sudo systemctl start ai-study"
echo "  3. sudo systemctl start nginx"
echo ""
