#!/bin/bash
# 安装 systemd 服务和 nginx 配置
set -e

echo "安装 systemd 服务..."
sudo cp ai-study.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ai-study
sudo systemctl start ai-study

echo "安装 nginx 配置..."
sudo cp nginx.conf /etc/nginx/sites-available/ai-study
sudo ln -sf /etc/nginx/sites-available/ai-study /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx

echo ""
echo "服务已启动！"
echo "  后端: http://localhost:8000"
echo "  Nginx: http://localhost:80"
echo "  API文档: http://localhost/docs"
echo ""
echo "管理命令："
echo "  sudo systemctl status ai-study    # 查看状态"
echo "  sudo systemctl restart ai-study   # 重启服务"
echo "  sudo journalctl -u ai-study -f    # 查看日志"
echo ""
