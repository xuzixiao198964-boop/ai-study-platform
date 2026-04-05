#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速部署单个文件"""
import paramiko

SERVER = "45.78.5.184"
USERNAME = "root"
PASSWORD = "FYCZWP2uPLjR"
PORT = 22

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER, PORT, USERNAME, PASSWORD)
sftp = ssh.open_sftp()

try:
    # 上传修改的文件
    print("上传 student_home_screen.dart")
    sftp.put(
        "D:/work/ai-study-platform/mobile/lib/screens/student/student_home_screen.dart",
        "/opt/ai-study-platform/mobile/lib/screens/student/student_home_screen.dart"
    )

    # 构建Flutter Web
    print("\n构建Flutter Web...")
    stdin, stdout, stderr = ssh.exec_command(
        'cd /opt/ai-study-platform/mobile && /root/flutter/bin/flutter build web --release 2>&1',
        get_pty=True
    )

    # 等待构建完成
    exit_code = stdout.channel.recv_exit_status()

    if exit_code == 0:
        print("构建成功")

        # 复制文件
        print("复制构建文件...")
        ssh.exec_command('cp -r /opt/ai-study-platform/mobile/build/web/* /opt/ai-study-mobile/build/web/')

        # 重启Nginx
        print("重启Nginx...")
        ssh.exec_command('systemctl restart nginx')

        print("\n[OK] 部署完成！")
        print("学生端: https://45.78.5.184:8000")
    else:
        print("[ERROR] 构建失败")

finally:
    sftp.close()
    ssh.close()
