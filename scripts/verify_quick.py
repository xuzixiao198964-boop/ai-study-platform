"""Quick post-deploy verification."""
import paramiko
import time
import json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("101.201.244.150", 22, "root", "Xuzi-xiao198964", timeout=15)

time.sleep(5)

def run(cmd):
    _, stdout, stderr = ssh.exec_command(cmd, timeout=15)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    code = stdout.channel.recv_exit_status()
    return code, out, err

print("--- Health check (8001) ---")
code, out, _ = run("curl -sf http://127.0.0.1:8001/health")
print(f"  exit={code}  body={out}")

print("--- Health check via Nginx (8000) ---")
code, out, _ = run("curl -sf http://127.0.0.1:8000/health")
print(f"  exit={code}  body={out}")

print("--- Admin login (8001) ---")
login_body = json.dumps({"username": "wsxzx", "password": "Xuzi-xiao198964"})
code, out, _ = run(
    f"curl -sf -X POST http://127.0.0.1:8001/api/v1/admin/login "
    f"-H 'Content-Type: application/json' -d '{login_body}'"
)
print(f"  exit={code}  body={out}")

print("--- Admin login via Nginx (8000) ---")
code, out, _ = run(
    f"curl -sf -X POST http://127.0.0.1:8000/api/v1/admin/login "
    f"-H 'Content-Type: application/json' -d '{login_body}'"
)
print(f"  exit={code}  body={out}")

ssh.close()
print("\nDone.")
