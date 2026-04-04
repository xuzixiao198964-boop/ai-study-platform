#!/usr/bin/env python3
"""
快速上传关键文件并配置服务
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
    """上传单个文件"""
    try:
        # 确保远程目录存在
        remote_dir = os.path.dirname(remote_path)
        try:
            sftp.stat(remote_dir)
        except:
            # 递归创建目录
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
        log(f"  Uploaded: {local_path} -> {remote_path}")
        return True
    except Exception as e:
        log(f"  Failed: {local_path} - {e}")
        return False

def exec_cmd(client, cmd, description=""):
    if description:
        log(description)
    stdin, stdout, stderr = client.exec_command(cmd, get_pty=True)
    output = stdout.read().decode('utf-8', errors='ignore')
    exit_code = stdout.channel.recv_exit_status()
    if exit_code != 0:
        log(f"  Exit code: {exit_code}")
    return output, exit_code

def main():
    log("Quick deployment starting...")

    try:
        # SSH连接
        log("Connecting...")
        transport = paramiko.Transport((HOST, PORT))
        transport.connect(username=USERNAME, password=PASSWORD)
        sftp = paramiko.SFTPClient.from_transport(transport)

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOST, PORT, USERNAME, PASSWORD, timeout=30)

        log("Connected!")

        # 1. 上传后端关键文件
        log("\n=== Uploading backend files ===")
        backend_files = [
            ("server/requirements.txt", "/opt/ai-study-platform/requirements.txt"),
            ("server/app/main.py", "/opt/ai-study-platform/app/main.py"),
            ("server/app/__init__.py", "/opt/ai-study-platform/app/__init__.py"),
            ("server/app/core/config.py", "/opt/ai-study-platform/app/core/config.py"),
            ("server/app/core/database.py", "/opt/ai-study-platform/app/core/database.py"),
            ("server/app/core/security.py", "/opt/ai-study-platform/app/core/security.py"),
            ("server/app/core/__init__.py", "/opt/ai-study-platform/app/core/__init__.py"),
            ("server/app/services/chat_service.py", "/opt/ai-study-platform/app/services/chat_service.py"),
            ("server/app/services/__init__.py", "/opt/ai-study-platform/app/services/__init__.py"),
        ]

        for local, remote in backend_files:
            local_path = f"D:/work/ai-study-platform/{local}"
            if os.path.exists(local_path):
                upload_file(sftp, local_path, remote)

        # 2. 上传前端关键文件
        log("\n=== Uploading frontend files ===")
        frontend_files = [
            ("mobile/pubspec.yaml", "/opt/ai-study-mobile/pubspec.yaml"),
            ("mobile/web/index.html", "/opt/ai-study-mobile/web/index.html"),
            ("mobile/lib/main.dart", "/opt/ai-study-mobile/lib/main.dart"),
            ("mobile/lib/services/speech_service.dart", "/opt/ai-study-mobile/lib/services/speech_service.dart"),
            ("mobile/lib/services/tts_service.dart", "/opt/ai-study-mobile/lib/services/tts_service.dart"),
            ("mobile/lib/services/api_service.dart", "/opt/ai-study-mobile/lib/services/api_service.dart"),
            ("mobile/lib/screens/student/student_home_screen.dart", "/opt/ai-study-mobile/lib/screens/student/student_home_screen.dart"),
        ]

        for local, remote in frontend_files:
            local_path = f"D:/work/ai-study-platform/{local}"
            if os.path.exists(local_path):
                upload_file(sftp, local_path, remote)

        sftp.close()
        transport.close()

        # 3. 安装Python依赖
        log("\n=== Installing Python dependencies ===")
        exec_cmd(client, """
            cd /opt/ai-study-platform && \
            python3 -m venv venv && \
            source venv/bin/activate && \
            pip install --upgrade pip && \
            pip install fastapi uvicorn sqlalchemy pymysql cryptography python-jose passlib python-multipart redis httpx
        """, "Installing packages...")

        # 4. 构建Flutter Web
        log("\n=== Building Flutter Web ===")
        exec_cmd(client, """
            export PATH=/opt/flutter/bin:$PATH && \
            export PUB_HOSTED_URL=https://pub.flutter-io.cn && \
            export FLUTTER_STORAGE_BASE_URL=https://storage.flutter-io.cn && \
            cd /opt/ai-study-mobile && \
            flutter pub get && \
            flutter build web --release --allow-root
        """, "Building...")

        log("\nQuick deployment completed!")
        log("Next: Configure and start services")

        client.close()

    except Exception as e:
        log(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
