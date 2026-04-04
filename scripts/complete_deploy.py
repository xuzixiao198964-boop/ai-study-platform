#!/usr/bin/env python3
import paramiko
import time

HOST = "45.78.5.184"
PORT = 22
USERNAME = "root"
PASSWORD = "wMOByjYmDKsp"

def exec_cmd(client, cmd, timeout=300):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    return out + err

try:
    print("[Connecting to server...]")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, PORT, USERNAME, PASSWORD, timeout=30)
    print("[Connected!]\n")

    print("=== Installing Python dependencies ===")
    output = exec_cmd(client, """
cd /opt/ai-study-platform
python3 -m pip install -r requirements.txt
""")
    print(output[-500:])

    print("\n=== Building Flutter Web ===")
    output = exec_cmd(client, """
cd /opt/ai-study-mobile
export PATH=/opt/flutter/bin:$PATH
flutter clean
flutter pub get
flutter build web --release --no-tree-shake-icons 2>&1 | tail -50
echo "EXIT_CODE: $?"
""", timeout=600)

    with open('D:/final_build.txt', 'w', encoding='utf-8') as f:
        f.write(output)
    print(output[-1000:])

    print("\n=== Configuring systemd service ===")
    service_content = """[Unit]
Description=AI Study Platform Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ai-study-platform
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

    stdin, stdout, stderr = client.exec_command("cat > /etc/systemd/system/ai-study.service")
    stdin.write(service_content)
    stdin.channel.shutdown_write()
    stdout.read()

    print("Service file created")

    print("\n=== Starting backend service ===")
    output = exec_cmd(client, """
systemctl daemon-reload
systemctl enable ai-study
systemctl restart ai-study
sleep 3
systemctl status ai-study
""")
    print(output)

    print("\n=== Checking health ===")
    output = exec_cmd(client, "curl -s http://127.0.0.1:8001/health")
    print(output)

    client.close()
    print("\n[Deployment completed!]")

except Exception as e:
    print(f"Error: {e}")
    with open('D:/deploy_error.txt', 'w', encoding='utf-8') as f:
        f.write(str(e))
