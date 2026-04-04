#!/usr/bin/env python3
import paramiko
import sys

host = "45.78.5.184"
port = 22
username = "root"
password = "wMOByjYmDKsp"

print(f"正在连接到 {host}:{port}...")

try:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=host,
        port=port,
        username=username,
        password=password,
        timeout=15,
        banner_timeout=30
    )

    print("SSH connected successfully!")

    # 测试基本命令
    stdin, stdout, stderr = client.exec_command("uname -a && cat /etc/os-release")
    output = stdout.read().decode('utf-8')
    print("\nServer info:")
    print(output)

    client.close()
    print("\nConnection test completed")

except Exception as e:
    print(f"Connection failed: {e}")
    sys.exit(1)
