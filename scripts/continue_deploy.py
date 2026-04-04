#!/usr/bin/env python3
"""
继续部署 - 上传缺失文件并配置服务
"""
import paramiko
import os
import sys
from datetime import datetime

HOST = "45.78.5.184"
PORT = 22
USERNAME = "root"
PASSWORD = "wMOByjYmDKsp"

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def upload_file(sftp, local_path, remote_path):
    try:
        remote_dir = os.path.dirname(remote_path)
        dirs = []
        while remote_dir and remote_dir != '/':
            dirs.append(remote_dir)
            remote_dir = os.path.dirname(remote_dir)
        dirs.reverse()
        for d in dirs:
            try:
                sftp.mkdir(d)
            except:
                pass
        sftp.put(local_path, remote_path)
        log(f"  OK: {os.path.basename(local_path)}")
        return True
    except Exception as e:
        log(f"  FAIL: {os.path.basename(local_path)} - {e}")
        return False

def exec_cmd(client, cmd, description="", timeout=300):
    if description:
        log(description)
    stdin, stdout, stderr = client.exec_command(cmd, get_pty=True, timeout=timeout)
    output = stdout.read().decode('utf-8', errors='ignore')
    exit_code = stdout.channel.recv_exit_status()
    return output, exit_code

def main():
    log("Continuing deployment...")

    try:
        # 新建连接
        log("Connecting...")
        transport = paramiko.Transport((HOST, PORT))
        transport.connect(username=USERNAME, password=PASSWORD)
        sftp = paramiko.SFTPClient.from_transport(transport)

        # 上传缺失的文件
        log("\n=== Uploading missing files ===")
        files = [
            ("mobile/lib/services/api_service.dart", "/opt/ai-study-mobile/lib/services/api_service.dart"),
            ("mobile/lib/screens/student/student_home_screen.dart", "/opt/ai-study-mobile/lib/screens/student/student_home_screen.dart"),
            ("server/app/main.py", "/opt/ai-study-platform/app/main.py"),
        ]

        for local, remote in files:
            local_path = f"D:/work/ai-study-platform/{local}"
            if os.path.exists(local_path):
                upload_file(sftp, local_path, remote)

        sftp.close()
        transport.close()
        log("Files uploaded!")

        # 新建SSH客户端执行命令
        log("\n=== Installing dependencies ===")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOST, PORT, USERNAME, PASSWORD, timeout=30)

        exec_cmd(client, """
            cd /opt/ai-study-platform && \
            python3 -m venv venv && \
            source venv/bin/activate && \
            pip install -q fastapi uvicorn sqlalchemy pymysql cryptography python-jose passlib python-multipart redis httpx
        """, "Installing Python packages...", timeout=180)

        log("\n=== Building Flutter Web ===")
        output, code = exec_cmd(client, """
            export PATH=/opt/flutter/bin:$PATH && \
            cd /opt/ai-study-mobile && \
            flutter pub get && \
            flutter build web --release --allow-root 2>&1 | tail -20
        """, "Building Flutter...", timeout=300)

        if "Built build/web" in output or code == 0:
            log("Flutter build SUCCESS")
        else:
            log(f"Flutter build may have issues (exit code: {code})")

        log("\n=== Configuring services ===")

        # systemd服务
        exec_cmd(client, """cat > /etc/systemd/system/ai-study.service << 'EOF'
[Unit]
Description=AI Study Platform
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ai-study-platform
Environment="PATH=/opt/ai-study-platform/venv/bin:/usr/bin:/bin"
ExecStart=/opt/ai-study-platform/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
EOF""")

        # Nginx配置
        exec_cmd(client, """cat > /etc/nginx/sites-available/ai-study << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        root /opt/ai-study-mobile/build/web;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF""")

        exec_cmd(client, "ln -sf /etc/nginx/sites-available/ai-study /etc/nginx/sites-enabled/")
        exec_cmd(client, "rm -f /etc/nginx/sites-enabled/default")

        log("\n=== Starting services ===")
        exec_cmd(client, "systemctl daemon-reload")
        exec_cmd(client, "systemctl enable ai-study")
        exec_cmd(client, "systemctl restart ai-study")
        exec_cmd(client, "systemctl restart nginx")

        log("\n=== Checking status ===")
        output, _ = exec_cmd(client, "systemctl is-active ai-study && systemctl is-active nginx")
        log(f"Services: {output.strip()}")

        log(f"\nDeployment completed! Access: http://{HOST}")

        client.close()

    except Exception as e:
        log(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
