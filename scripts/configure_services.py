#!/usr/bin/env python3
"""
配置并启动服务
"""
import paramiko
import sys
from datetime import datetime

HOST = "45.78.5.184"
PORT = 22
USERNAME = "root"
PASSWORD = "wMOByjYmDKsp"

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def exec_cmd(client, cmd, description=""):
    if description:
        log(description)
    stdin, stdout, stderr = client.exec_command(cmd, get_pty=True)
    output = stdout.read().decode('utf-8', errors='ignore')
    exit_code = stdout.channel.recv_exit_status()
    return output, exit_code

def main():
    log("Starting service configuration...")

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOST, PORT, USERNAME, PASSWORD, timeout=30)
        log("Connected!")

        # 1. 安装Python依赖
        log("\n=== Installing Python dependencies ===")
        exec_cmd(client, """
            cd /opt/ai-study-platform && \
            python3 -m venv venv && \
            source venv/bin/activate && \
            pip install -r requirements.txt
        """, "Installing backend dependencies...")

        # 2. 构建Flutter Web
        log("\n=== Building Flutter Web ===")
        exec_cmd(client, """
            export PATH=/opt/flutter/bin:$PATH && \
            export PUB_HOSTED_URL=https://pub.flutter-io.cn && \
            export FLUTTER_STORAGE_BASE_URL=https://storage.flutter-io.cn && \
            cd /opt/ai-study-mobile && \
            flutter pub get && \
            flutter build web --release --allow-root
        """, "Building Flutter Web app...")

        # 3. 创建systemd服务
        log("\n=== Creating systemd service ===")
        service_content = """[Unit]
Description=AI Study Platform Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ai-study-platform
Environment="PATH=/opt/ai-study-platform/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/opt/ai-study-platform/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        exec_cmd(client, f"cat > /etc/systemd/system/ai-study.service << 'EOF'\n{service_content}\nEOF")

        # 4. 配置Nginx
        log("\n=== Configuring Nginx ===")
        nginx_config = """server {
    listen 80;
    server_name _;

    # Flutter Web静态文件
    location / {
        root /opt/ai-study-mobile/build/web;
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache";
    }

    # API代理
    location /api/ {
        proxy_pass http://127.0.0.1:8001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
"""
        exec_cmd(client, f"cat > /etc/nginx/sites-available/ai-study << 'EOF'\n{nginx_config}\nEOF")
        exec_cmd(client, "ln -sf /etc/nginx/sites-available/ai-study /etc/nginx/sites-enabled/")
        exec_cmd(client, "rm -f /etc/nginx/sites-enabled/default")

        # 5. 启动服务
        log("\n=== Starting services ===")
        exec_cmd(client, "systemctl daemon-reload")
        exec_cmd(client, "systemctl enable ai-study")
        exec_cmd(client, "systemctl start ai-study")
        exec_cmd(client, "systemctl restart nginx")

        # 6. 检查状态
        log("\n=== Checking service status ===")
        output, _ = exec_cmd(client, "systemctl is-active ai-study")
        log(f"Backend service: {output.strip()}")

        output, _ = exec_cmd(client, "systemctl is-active nginx")
        log(f"Nginx service: {output.strip()}")

        output, _ = exec_cmd(client, "curl -s http://127.0.0.1:8001/health || echo 'Health check failed'")
        log(f"Health check: {output.strip()}")

        log("\nDeployment completed!")
        log(f"Access the app at: http://{HOST}")

        client.close()

    except Exception as e:
        log(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
