#!/usr/bin/env python3
import paramiko
import time

HOST = "45.78.5.184"
PORT = 22
USERNAME = "root"
PASSWORD = "wMOByjYmDKsp"

def exec_cmd(client, cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=600)
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    return out + err

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USERNAME, PASSWORD, timeout=30)

print("[Cleaning Flutter build...]")
output = exec_cmd(client, """
cd /opt/ai-study-mobile
export PATH=/opt/flutter/bin:$PATH
flutter clean
""")
print(output[:500])

print("[Running flutter pub get...]")
output = exec_cmd(client, """
cd /opt/ai-study-mobile
export PATH=/opt/flutter/bin:$PATH
flutter pub get
""")
print(output[:500])

print("[Building Flutter Web with verbose output...]")
output = exec_cmd(client, """
cd /opt/ai-study-mobile
export PATH=/opt/flutter/bin:$PATH
flutter build web --release --no-tree-shake-icons --verbose 2>&1 | tail -100
echo "EXIT_CODE: $?"
""")

with open('D:/flutter_rebuild.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print("Output saved to D:/flutter_rebuild.txt")
print(output[-1000:])

client.close()
