#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('45.78.5.184', 22, 'root', 'FYCZWP2uPLjR')

# 构建Flutter Web
print("=== 开始构建Flutter Web ===")
stdin, stdout, stderr = ssh.exec_command('cd /opt/ai-study-platform/mobile && /root/flutter/bin/flutter build web --release 2>&1', get_pty=True)

# 实时读取输出
while True:
    line = stdout.readline()
    if not line:
        break
    # 移除所有非ASCII字符
    try:
        line = ''.join(c for c in line if ord(c) < 128 or c.isspace())
        if line.strip():
            print(line.rstrip())
    except:
        pass

exit_code = stdout.channel.recv_exit_status()
print(f"\n构建退出码: {exit_code}")

if exit_code == 0:
    print("\n=== 复制构建文件 ===")
    stdin, stdout, stderr = ssh.exec_command('cp -r /opt/ai-study-platform/mobile/build/web/* /opt/ai-study-mobile/build/web/')
    stdout.channel.recv_exit_status()
    print("构建文件已复制")

    print("\n=== 重启Nginx ===")
    stdin, stdout, stderr = ssh.exec_command('systemctl restart nginx')
    stdout.channel.recv_exit_status()
    print("Nginx已重启")

    print("\n[OK] 部署完成！")
    print("学生端: https://45.78.5.184:8000")

ssh.close()
