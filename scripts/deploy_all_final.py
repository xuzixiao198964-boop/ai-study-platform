#!/usr/bin/env python3
"""部署所有最终修复到服务器"""
import paramiko
import os
from pathlib import Path

SERVER = "45.78.5.184"
USERNAME = "root"
PASSWORD = "FYCZWP2uPLjR"
PORT = 22

def upload_file(sftp, local_path, remote_path):
    """上传文件"""
    print(f"上传 {local_path} -> {remote_path}")
    sftp.put(local_path, remote_path)

def main():
    base_dir = Path(__file__).parent.parent

    # 连接服务器
    print(f"连接到服务器 {SERVER}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER, PORT, USERNAME, PASSWORD)
    sftp = ssh.open_sftp()

    try:
        # 1. 上传后端文件
        print("\n=== 上传后端文件 ===")
        upload_file(
            sftp,
            str(base_dir / "server/app/services/chat_service.py"),
            "/opt/ai-study-platform/app/services/chat_service.py"
        )

        # 2. 上传前端文件
        print("\n=== 上传前端文件 ===")
        upload_file(
            sftp,
            str(base_dir / "mobile/lib/screens/student/student_home_screen.dart"),
            "/opt/ai-study-platform/mobile/lib/screens/student/student_home_screen.dart"
        )
        upload_file(
            sftp,
            str(base_dir / "mobile/web/index.html"),
            "/opt/ai-study-platform/mobile/web/index.html"
        )

        # 3. 重启后端服务
        print("\n=== 重启后端服务 ===")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart ai-study")
        stdout.channel.recv_exit_status()
        print("后端服务已重启")

        # 4. 构建Flutter Web
        print("\n=== 构建Flutter Web ===")
        stdin, stdout, stderr = ssh.exec_command(
            "cd /opt/ai-study-platform/mobile && "
            "/root/flutter/bin/flutter build web --release"
        )
        exit_code = stdout.channel.recv_exit_status()
        if exit_code == 0:
            print("Flutter构建成功")
        else:
            print(f"Flutter构建失败: {stderr.read().decode()}")
            return

        # 5. 复制构建文件
        print("\n=== 复制构建文件 ===")
        stdin, stdout, stderr = ssh.exec_command(
            "cp -r /opt/ai-study-platform/mobile/build/web/* /opt/ai-study-mobile/build/web/"
        )
        stdout.channel.recv_exit_status()
        print("构建文件已复制")

        # 6. 重启Nginx
        print("\n=== 重启Nginx ===")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart nginx")
        stdout.channel.recv_exit_status()
        print("Nginx已重启")

        # 7. 检查服务状态
        print("\n=== 检查服务状态 ===")
        stdin, stdout, stderr = ssh.exec_command("systemctl status ai-study nginx --no-pager")
        print(stdout.read().decode())

        print("\n部署完成！")
        print("学生端: https://45.78.5.184:8000")

    finally:
        sftp.close()
        ssh.close()

if __name__ == "__main__":
    main()
