#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""简化部署脚本"""
import paramiko
import os
import sys
from pathlib import Path

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SERVER = "45.78.5.184"
USERNAME = "root"
PASSWORD = "FYCZWP2uPLjR"
PORT = 22

def main():
    base_dir = Path(__file__).parent.parent

    # 连接服务器
    print(f"连接到服务器 {SERVER}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER, PORT, USERNAME, PASSWORD)
    sftp = ssh.open_sftp()

    try:
        # 1. 上传后端chat_service.py
        print("\n=== 上传后端文件 ===")
        print("上传 chat_service.py")
        sftp.put(
            str(base_dir / "server/app/services/chat_service.py"),
            "/opt/ai-study-platform/app/services/chat_service.py"
        )

        # 2. 创建mobile目录
        print("\n=== 创建目录结构 ===")
        ssh.exec_command("mkdir -p /opt/ai-study-platform/mobile/lib/screens/student")
        ssh.exec_command("mkdir -p /opt/ai-study-platform/mobile/web")

        # 3. 上传前端文件
        print("\n=== 上传前端文件 ===")
        print("上传 student_home_screen.dart")
        sftp.put(
            str(base_dir / "mobile/lib/screens/student/student_home_screen.dart"),
            "/opt/ai-study-platform/mobile/lib/screens/student/student_home_screen.dart"
        )
        print("上传 index.html")
        sftp.put(
            str(base_dir / "mobile/web/index.html"),
            "/opt/ai-study-platform/mobile/web/index.html"
        )

        # 4. 重启后端服务
        print("\n=== 重启后端服务 ===")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart ai-study")
        stdout.channel.recv_exit_status()
        print("后端服务已重启")

        # 5. 构建Flutter Web
        print("\n=== 构建Flutter Web ===")
        cmd = "cd /opt/ai-study-platform/mobile && /root/flutter/bin/flutter build web --release"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        exit_code = stdout.channel.recv_exit_status()

        if exit_code == 0:
            print("Flutter构建成功")

            # 6. 复制构建文件
            print("\n=== 复制构建文件 ===")
            stdin, stdout, stderr = ssh.exec_command(
                "cp -r /opt/ai-study-platform/mobile/build/web/* /opt/ai-study-mobile/build/web/"
            )
            stdout.channel.recv_exit_status()
            print("构建文件已复制")

            # 7. 重启Nginx
            print("\n=== 重启Nginx ===")
            stdin, stdout, stderr = ssh.exec_command("systemctl restart nginx")
            stdout.channel.recv_exit_status()
            print("Nginx已重启")

            print("\n[OK] 部署完成！")
            print("学生端: https://45.78.5.184:8000")
        else:
            error_msg = stderr.read().decode('utf-8', errors='ignore')
            print("[ERROR] Flutter构建失败")
            print(error_msg)

    finally:
        sftp.close()
        ssh.close()

if __name__ == "__main__":
    main()
