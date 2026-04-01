#!/bin/bash
# ============================================
# 快速部署/更新脚本
# ============================================

set -e

APP_DIR="/opt/ai-study-platform"
APP_USER="aistudy"

echo "正在部署更新..."

# 1. 复制代码
echo "[1/4] 更新代码..."
sudo cp -r server/* $APP_DIR/
sudo chown -R $APP_USER:$APP_USER $APP_DIR

# 2. 更新依赖
echo "[2/4] 更新依赖..."
sudo -u $APP_USER bash -c "
    cd $APP_DIR
    source venv/bin/activate
    pip install -r requirements.txt --quiet
"

# 3. 数据库迁移
echo "[3/4] 数据库迁移..."
sudo -u $APP_USER bash -c "
    cd $APP_DIR
    source venv/bin/activate
    alembic upgrade head 2>/dev/null || echo '跳过迁移'
"

# 4. 重启服务
echo "[4/4] 重启服务..."
sudo systemctl restart ai-study
sudo systemctl reload nginx

echo ""
echo "部署完成！"
echo "服务状态: $(sudo systemctl is-active ai-study)"
echo ""
