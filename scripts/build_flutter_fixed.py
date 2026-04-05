#!/usr/bin/env python3
import paramiko
import sys

HOST = "45.78.5.184"
PORT = 22
USER = "root"
PASSWORD = "FYCZWP2uPLjR"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(HOST, PORT, USER, PASSWORD)
    print("[OK] Connected")

    # 构建Flutter
    print("\n[1/2] Building Flutter Web...")
    cmd = """
cd /opt/ai-study-mobile
/opt/flutter/bin/flutter build web --release
echo "BUILD_COMPLETE"
"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=300)
    
    # 逐行读取避免编码问题
    for line in stdout:
        try:
            print(line.strip())
        except:
            print("[output line]")
    
    # 重启nginx
    print("\n[2/2] Restarting nginx...")
    stdin, stdout, stderr = ssh.exec_command("systemctl restart nginx")
    stdout.read()

    print("\n" + "="*70)
    print("[OK] Deployment completed!")
    print("="*70)
    print("\nChanges:")
    print("1. Backend: Voice names updated to teacher format")
    print("2. Frontend: UI text humanized (AI -> Teacher)")
    print("\nPlease test at: https://45.78.5.184:8000")
    print("Press Ctrl+Shift+R to force refresh")

except Exception as e:
    print(f"[ERROR] {e}")
finally:
    ssh.close()
