"""Deploy user management feature: DB migration + backend + website."""
import time
import paramiko

SERVER = "101.201.244.150"
USER = "root"
PASSWORD = "Xuzi-xiao198964"


def run(ssh, cmd, desc=""):
    if desc:
        print(f"\n--- {desc} ---")
    print(f"  $ {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out.strip():
        print(out.rstrip())
    if err.strip():
        print(f"  [STDERR] {err.rstrip()}")
    return out, err


def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {SERVER}...")
    ssh.connect(SERVER, 22, USER, PASSWORD, timeout=15)
    sftp = ssh.open_sftp()

    # 1. Add plain_password column to users table
    run(ssh, """PGPASSWORD=aistudy_db_2026 psql -h localhost -U aistudy -d ai_study -c "ALTER TABLE users ADD COLUMN IF NOT EXISTS plain_password VARCHAR(255);" """,
        "DB: add plain_password column")

    # 2. Upload updated backend files
    files = {
        r"server\app\models\user.py": "/opt/ai-study-platform/app/models/user.py",
        r"server\app\api\endpoints\auth.py": "/opt/ai-study-platform/app/api/endpoints/auth.py",
        r"server\app\api\endpoints\admin.py": "/opt/ai-study-platform/app/api/endpoints/admin.py",
    }
    print("\n--- Upload backend files ---")
    import os
    base = os.path.join(os.path.dirname(__file__), "..")
    for local_rel, remote in files.items():
        local_path = os.path.join(base, local_rel)
        sftp.put(local_path, remote)
        print(f"  UPLOAD {local_rel}")

    # 3. Upload website
    print("\n--- Upload website ---")
    sftp.put(os.path.join(base, "website", "admin.html"), "/opt/ai-study-website/admin.html")
    print("  UPLOAD admin.html")
    sftp.close()

    # 4. Restart backend service
    run(ssh, "systemctl restart ai-study", "Restart backend service")
    print("  Waiting for service to start...")
    time.sleep(5)

    # 5. Verify health
    run(ssh, "curl -sk -o /dev/null -w '%{http_code}' https://127.0.0.1:8000/health", "Health check")

    # 6. Test admin login
    run(ssh, """curl -sk -X POST https://127.0.0.1:8000/api/v1/admin/login -H 'Content-Type: application/json' -d '{"username":"wsxzx","password":"Xuzi-xiao198964"}' -o /dev/null -w '%{http_code}' """,
        "Admin login test")

    # 7. Test users endpoint (get token first, then list users)
    out, _ = run(ssh, """curl -sk -X POST https://127.0.0.1:8000/api/v1/admin/login -H 'Content-Type: application/json' -d '{"username":"wsxzx","password":"Xuzi-xiao198964"}' """,
        "Get admin token")
    import json
    try:
        token = json.loads(out.strip())["access_token"]
        out2, _ = run(ssh, f"""curl -sk https://127.0.0.1:8000/api/v1/admin/users -H 'Authorization: Bearer {token}' """,
            "List users API test")
        users = json.loads(out2.strip())
        print(f"\n  Found {len(users)} users:")
        for u in users:
            print(f"    ID={u['id']}  username={u['username']}  password={u['plain_password']}  nickname={u['nickname']}  active={u['is_active']}")
    except Exception as e:
        print(f"  [ERROR] {e}")

    # 8. Verify website
    run(ssh, "curl -so /dev/null -w '%{http_code}' http://127.0.0.1/admin.html", "Website admin.html check")

    ssh.close()
    print("\n=== Deployment complete ===")


if __name__ == "__main__":
    main()
