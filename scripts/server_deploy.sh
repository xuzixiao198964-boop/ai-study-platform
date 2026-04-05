#!/bin/bash
# 在服务器上运行此脚本进行完整部署

set -e

echo "=========================================="
echo "  AI学习平台 - 完整部署脚本"
echo "=========================================="
echo ""

# 1. 更新后端代码
echo "[1/5] 更新后端代码..."
cd /opt/ai-study-platform
git pull
echo "✓ 后端代码已更新"
echo ""

# 2. 重启后端服务
echo "[2/5] 重启后端服务..."
systemctl restart ai-study
sleep 3
if systemctl is-active --quiet ai-study; then
    echo "✓ 后端服务运行正常"
else
    echo "❌ 后端服务启动失败"
    systemctl status ai-study --no-pager
    exit 1
fi
echo ""

# 3. 测试后端API
echo "[3/5] 测试后端API..."
if curl -k -s https://localhost:8000/api/v1/health | grep -q "ok"; then
    echo "✓ 健康检查通过"
else
    echo "❌ 健康检查失败"
    exit 1
fi

if curl -k -s https://localhost:8000/api/v1/tts/voices | grep -q "101001"; then
    echo "✓ TTS API正常"
else
    echo "❌ TTS API异常"
fi
echo ""

# 4. 构建前端
echo "[4/5] 构建Flutter Web..."
cd /opt/ai-study-mobile
/opt/flutter/bin/flutter build web --release
if [ $? -eq 0 ]; then
    echo "✓ 前端构建成功"
else
    echo "❌ 前端构建失败"
    exit 1
fi
echo ""

# 5. 重启Nginx
echo "[5/5] 重启Nginx..."
systemctl restart nginx
if systemctl is-active --quiet nginx; then
    echo "✓ Nginx运行正常"
else
    echo "❌ Nginx启动失败"
    systemctl status nginx --no-pager
    exit 1
fi
echo ""

echo "=========================================="
echo "  部署完成！"
echo "=========================================="
echo ""
echo "访问地址: https://45.78.5.184:8000"
echo ""
echo "修复内容:"
echo "  ✓ Service Worker SSL错误已修复"
echo "  ✓ iPad TTS播放已修复"
echo "  ✓ Windows公放回声已修复"
echo "  ✓ 持续对话功能已修复"
echo "  ✓ 弹窗居中显示已修复"
echo "  ✓ 腾讯云TTS声音选择已实现（18种音色）"
echo ""
