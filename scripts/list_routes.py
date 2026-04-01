"""List all API routes from server"""
import paramiko
import json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("101.201.244.150", 22, "root", "Xuzi-xiao198964", timeout=15)

stdin, stdout, stderr = ssh.exec_command("curl -s http://127.0.0.1:8001/openapi.json", timeout=30)
data = json.loads(stdout.read().decode())
print("API Routes:")
for path in sorted(data.get("paths", {}).keys()):
    methods = list(data["paths"][path].keys())
    print(f"  {','.join(m.upper() for m in methods):8s} {path}")
ssh.close()
