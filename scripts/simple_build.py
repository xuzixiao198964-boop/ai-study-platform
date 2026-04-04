#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER = "101.201.244.150"
USER = "root"
PASSWORD = "Xuzi-xiao198964"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER, username=USER, password=PASSWORD, timeout=30)

print("开始构建Flutter Web...")
stdin, stdout, stderr = ssh.exec_command(
    "cd /opt/ai-study-mobile && export PATH=/opt/flutter/bin:$PATH && flutter build web --release",
    timeout=600
)

# 等待完成
exit_code = stdout.channel.recv_exit_status()

# 读取输出
output = stdout.read().decode('utf-8', errors='replace')
error = stderr.read().decode('utf-8', errors='replace')

print("=== 标准输出 ===")
print(output)

if error:
    print("\n=== 错误输出 ===")
    print(error)

print(f"\n退出码: {exit_code}")

ssh.close()
sys.exit(exit_code)
