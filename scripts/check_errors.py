#!/usr/bin/env python3
import paramiko

HOST = "45.78.5.184"
PORT = 22
USERNAME = "root"
PASSWORD = "wMOByjYmDKsp"

def exec_cmd(client, cmd):
    stdin, stdout, stderr = client.exec_command(cmd, get_pty=True)
    output = stdout.read().decode('utf-8', errors='ignore')
    return output

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USERNAME, PASSWORD, timeout=30)

print("=== Flutter build error ===")
output = exec_cmd(client, """
    export PATH=/opt/flutter/bin:$PATH && \
    cd /opt/ai-study-mobile && \
    flutter build web --release --allow-root 2>&1 | tail -50
""")

with open("D:/flutter_error.txt", "w", encoding="utf-8") as f:
    f.write(output)
print("Saved to D:/flutter_error.txt")

print("\n=== Backend service error ===")
output = exec_cmd(client, "journalctl -u ai-study -n 30 --no-pager")

with open("D:/service_error.txt", "w", encoding="utf-8") as f:
    f.write(output)
print("Saved to D:/service_error.txt")

client.close()
