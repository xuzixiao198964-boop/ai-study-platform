"""Verify regions API on remote server."""
import paramiko
import urllib.parse

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("101.201.244.150", 22, "root", "Xuzi-xiao198964", timeout=15)


def run(cmd):
    _, stdout, stderr = ssh.exec_command(cmd, timeout=15)
    out = stdout.read().decode().strip()
    code = stdout.channel.recv_exit_status()
    return code, out


print("=== 1. Check files exist ===")
code, out = run("ls -la /opt/ai-study-platform/app/api/endpoints/regions.py")
print(f"  regions endpoint: {out}")
code, out = run("ls -la /opt/ai-study-platform/app/data/regions.py")
print(f"  regions data: {out}")

print("\n=== 2. GET /api/v1/regions/provinces ===")
code, out = run("curl -sf http://127.0.0.1:8000/api/v1/regions/provinces")
print(f"  exit={code}, first 200 chars: {out[:200]}")

print("\n=== 3. GET /api/v1/regions/cities?province=广东省 ===")
p = urllib.parse.quote("广东省")
code, out = run(f"curl -sf 'http://127.0.0.1:8000/api/v1/regions/cities?province={p}'")
print(f"  exit={code}, body: {out}")

print("\n=== 4. GET /api/v1/regions/districts (北京市) ===")
p1 = urllib.parse.quote("北京市")
code, out = run(f"curl -sf 'http://127.0.0.1:8000/api/v1/regions/districts?province={p1}&city={p1}'")
print(f"  exit={code}, body: {out}")

print("\n=== 5. Public access test (port 8000) ===")
code, out = run("curl -sf http://101.201.244.150:8000/api/v1/regions/provinces | head -c 200")
print(f"  exit={code}, body: {out[:200]}")

ssh.close()
print("\nDone.")
