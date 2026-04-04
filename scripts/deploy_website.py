"""Upload website files to the server."""
import os
import paramiko

SERVER = "101.201.244.150"
USER = "root"
PASSWORD = "Xuzi-xiao198964"
LOCAL_DIR = os.path.join(os.path.dirname(__file__), "..", "website")
REMOTE_DIR = "/opt/ai-study-website"


def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {SERVER}...")
    ssh.connect(SERVER, 22, USER, PASSWORD, timeout=15)
    sftp = ssh.open_sftp()

    local_index = os.path.join(LOCAL_DIR, "index.html")
    if os.path.exists(local_index):
        sftp.put(local_index, f"{REMOTE_DIR}/index.html")
        print("  UPLOAD index.html")

    local_admin = os.path.join(LOCAL_DIR, "admin.html")
    if os.path.exists(local_admin):
        sftp.put(local_admin, f"{REMOTE_DIR}/admin.html")
        print("  UPLOAD admin.html")

    sftp.close()

    print("\n=== Verifying website ===")
    stdin, stdout, stderr = ssh.exec_command(
        "curl -so /dev/null -w '%{http_code}' http://127.0.0.1/", timeout=15
    )
    code = stdout.read().decode().strip()
    print(f"  Website (port 80): HTTP {code}")

    stdin, stdout, stderr = ssh.exec_command(
        "grep -c 'https://101.201.244.150:8000' /opt/ai-study-website/index.html"
    )
    count = stdout.read().decode().strip()
    print(f"  HTTPS links count: {count}")

    ssh.close()
    print("\n=== Website deployment complete ===")


if __name__ == "__main__":
    main()
