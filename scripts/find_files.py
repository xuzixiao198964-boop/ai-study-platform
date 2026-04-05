#!/usr/bin/env python3
import paramiko

HOST = "45.78.5.184"
PORT = 22
USER = "root"
PASSWORD = "FYCZWP2uPLjR"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(HOST, PORT, USER, PASSWORD)
    print("[OK] Connected")

    # 查找flutter_bootstrap.js
    cmd = "find /opt/ai-study-platform -name 'flutter_bootstrap.js' -o -name 'index.html' | grep -v node_modules"

    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read().decode('utf-8', errors='ignore')
    print("Found files:")
    print(output)

    # 检查nginx配置
    print("\nChecking nginx config:")
    stdin, stdout, stderr = ssh.exec_command("grep -r 'root.*ai-study' /etc/nginx/")
    print(stdout.read().decode('utf-8', errors='ignore'))

except Exception as e:
    print(f"[ERROR] {e}")
finally:
    ssh.close()
