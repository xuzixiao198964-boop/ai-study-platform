#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('45.78.5.184', 22, 'root', 'FYCZWP2uPLjR')

# 检查目录结构
stdin, stdout, stderr = ssh.exec_command('ls -la /opt/ai-study-platform/mobile/')
print("=== mobile目录内容 ===")
print(stdout.read().decode('utf-8', errors='ignore'))

# 检查pubspec.yaml
stdin, stdout, stderr = ssh.exec_command('cat /opt/ai-study-platform/mobile/pubspec.yaml | head -20')
print("\n=== pubspec.yaml ===")
print(stdout.read().decode('utf-8', errors='ignore'))

# 尝试flutter pub get
stdin, stdout, stderr = ssh.exec_command('cd /opt/ai-study-platform/mobile && /root/flutter/bin/flutter pub get 2>&1')
print("\n=== flutter pub get ===")
output = stdout.read().decode('utf-8', errors='ignore')
# 移除emoji字符
output = ''.join(c for c in output if ord(c) < 0x10000)
print(output)

ssh.close()
