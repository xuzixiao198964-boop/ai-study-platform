#!/bin/bash
# 部署脚本 - 需要在服务器上运行

set -e

echo "=== 开始部署 ==="

# 1. 更新代码
echo "[1/4] 拉取最新代码..."
cd /opt/ai-study-platform
git pull

# 2. 重启后端服务
echo "[2/4] 重启后端服务..."
systemctl restart ai-study
sleep 3
systemctl status ai-study --no-pager

# 3. 构建前端
echo "[3/4] 构建Flutter Web..."
cd /opt/ai-study-mobile
/opt/flutter/bin/flutter build web --release

# 4. 重启Nginx
echo "[4/4] 重启Nginx..."
systemctl restart nginx

echo "=== 部署完成 ==="
echo "访问: https://45.78.5.184:8000"
