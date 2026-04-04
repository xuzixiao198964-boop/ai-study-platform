#!/usr/bin/env python3
import paramiko
import time

HOST = "45.78.5.184"
PORT = 22
USERNAME = "root"
PASSWORD = "wMOByjYmDKsp"

def exec_cmd(client, cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    return stdout.read().decode('utf-8', errors='ignore') + stderr.read().decode('utf-8', errors='ignore')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USERNAME, PASSWORD)

print("[Restarting backend service...]")
output = exec_cmd(client, "systemctl restart ai-study")
print(output)

time.sleep(2)

print("[Checking service status...]")
output = exec_cmd(client, "systemctl status ai-study")
print(output)

print("[Checking health endpoint...]")
output = exec_cmd(client, "curl -s http://127.0.0.1:8001/health")
print(output)

print("[Checking recent logs...]")
output = exec_cmd(client, "journalctl -u ai-study -n 20 --no-pager")
with open('D:/service_logs.txt', 'w', encoding='utf-8') as f:
    f.write(output)
print("Logs saved to D:/service_logs.txt")

client.close()
print("[Done]")
