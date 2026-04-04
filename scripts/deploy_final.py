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

def save_output(filename, content):
    with open(filename, 'w', encoding='utf-8', errors='ignore') as f:
        f.write(content)

try:
    print("[Connecting...]")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, PORT, USERNAME, PASSWORD, timeout=30)
    print("[Connected!]\n")

    print("=== Installing Python dependencies ===")
    output = exec_cmd(client, """
cd /opt/ai-study-platform
python3 -m pip install --break-system-packages -r requirements.txt 2>&1 | tail -20
""")
    save_output('D:/pip_install.txt', output)
    print(output[-500:])

    print("\n=== Building Flutter Web ===")
    output = exec_cmd(client, """
cd /opt/ai-study-mobile
export PATH=/opt/flutter/bin:$PATH
flutter clean > /dev/null 2>&1
flutter pub get > /dev/null 2>&1
flutter build web --release --no-tree-shake-icons 2>&1
echo "EXIT_CODE: $?"
ls -la build/web/ 2>&1
""", timeout=600)

    save_output('D:/flutter_final.txt', output)

    # 只打印最后部分避免编码问题
    lines = output.split('\n')
    print('\n'.join(lines[-30:]))

    print("\n=== Configuring systemd ===")
    service_content = """[Unit]
Description=AI Study Platform
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
    print("Service configured")

    print("\n=== Starting service ===")
    output = exec_cmd(client, """
systemctl daemon-reload
systemctl enable ai-study
systemctl restart ai-study
sleep 3
systemctl is-active ai-study
curl -s http://127.0.0.1:8001/health
""")
    print(output)

    client.close()
    print("\n[Done!]")

except Exception as e:
    print(f"Error: {e}")
    save_output('D:/deploy_error.txt', str(e))
