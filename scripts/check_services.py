#!/usr/bin/env python3
import paramiko

SERVER = "101.201.244.150"
USER = "root"
PASSWORD = "Xuzi-xiao198964"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER, username=USER, password=PASSWORD, timeout=30)

# 检查services目录
stdin, stdout, stderr = ssh.exec_command("ls -la /opt/ai-study-mobile/lib/services/")
print("Services目录:")
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()
