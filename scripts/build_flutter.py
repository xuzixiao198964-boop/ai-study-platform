#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import paramiko
import sys
import io

# 设置stdout为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER = "101.201.244.150"
USER = "root"
PASSWORD = "Xuzi-xiao198964"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER, username=USER, password=PASSWORD, timeout=30)

print("开始构建Flutter Web...")
stdin, stdout, stderr = ssh.exec_command(
    "cd /opt/ai-study-mobile && export PATH=/opt/flutter/bin:$PATH && flutter build web --release 2>&1",
    get_pty=True
)

# 实时输出
while not stdout.channel.exit_status_ready():
    if stdout.channel.recv_ready():
        data = stdout.channel.recv(1024).decode('utf-8', errors='replace')
        print(data, end='', flush=True)

# 获取剩余输出
data = stdout.read().decode('utf-8', errors='replace')
print(data, end='', flush=True)

exit_code = stdout.channel.recv_exit_status()
print(f"\n构建完成，退出码: {exit_code}")

ssh.close()
sys.exit(exit_code)
