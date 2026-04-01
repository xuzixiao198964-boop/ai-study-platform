"""Verify deployment status"""
import paramiko
import sys, os
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', errors='replace')

SERVER = "101.201.244.150"
USER = "root"
PASSWORD = "Xuzi-xiao198964"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER, 22, USER, PASSWORD, timeout=15)

checks = [
    ("Backend health (8001)", 'curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/health'),
    ("App health (8000)", 'curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health'),
    ("Admin page (80)", 'curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:80/admin.html'),
    ("Admin login API (8001)", """curl -s -w "\\n%{http_code}" -X POST http://127.0.0.1:8001/api/v1/admin/login -H "Content-Type: application/json" -d '{"username":"admin","password":"AiStudy@2026"}'"""),
    ("Admin login API via nginx (80)", """curl -s -w "\\n%{http_code}" -X POST http://127.0.0.1:80/api/v1/admin/login -H "Content-Type: application/json" -d '{"username":"admin","password":"AiStudy@2026"}'"""),
    ("Admin stats (8001)", None),
]

for label, cmd in checks:
    if cmd is None:
        continue
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', 'replace').strip()
    print(f"{label}: {out}")

ssh.close()
print("\nDone.")
