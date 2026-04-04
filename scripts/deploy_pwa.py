"""Upload Flutter Web build to the server PWA directory."""
import os
import paramiko

SERVER = "101.201.244.150"
USER = "root"
PASSWORD = "Xuzi-xiao198964"
LOCAL_BUILD = os.path.join(os.path.dirname(__file__), "..", "mobile", "build", "web")
REMOTE_DIR = "/opt/ai-study-mobile/build/web"


def mkdir_p(sftp, path):
    parts = path.split("/")
    current = ""
    for p in parts:
        if not p:
            current = "/"
            continue
        current = current + "/" + p if current != "/" else "/" + p
        try:
            sftp.stat(current)
        except FileNotFoundError:
            sftp.mkdir(current)


def upload_dir(sftp, local_dir, remote_dir):
    local_dir = os.path.abspath(local_dir)
    for root, dirs, files in os.walk(local_dir):
        dirs[:] = [d for d in dirs if d not in {"__pycache__", ".dart_tool"}]
        for f in files:
            local_path = os.path.join(root, f)
            rel = os.path.relpath(local_path, local_dir)
            remote_path = remote_dir + "/" + rel.replace("\\", "/")
            remote_parent = os.path.dirname(remote_path).replace("\\", "/")
            mkdir_p(sftp, remote_parent)
            print(f"  UPLOAD {rel}")
            sftp.put(local_path, remote_path)


def main():
    if not os.path.exists(LOCAL_BUILD):
        print(f"[ERROR] Build directory not found: {LOCAL_BUILD}")
        print("Run: cd mobile && flutter build web")
        return

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {SERVER}...")
    ssh.connect(SERVER, 22, USER, PASSWORD, timeout=15)
    sftp = ssh.open_sftp()

    print(f"\n=== Uploading PWA build to {REMOTE_DIR} ===")
    upload_dir(sftp, LOCAL_BUILD, REMOTE_DIR)

    sftp.close()

    print("\n=== Reloading Nginx ===")
    stdin, stdout, stderr = ssh.exec_command("nginx -t && systemctl reload nginx", timeout=30)
    print(stdout.read().decode())
    err = stderr.read().decode()
    if err:
        print(f"[STDERR] {err}")

    print("\n=== Verifying PWA ===")
    stdin, stdout, stderr = ssh.exec_command(
        "curl -sk -o /dev/null -w '%{http_code}' https://127.0.0.1:8000/", timeout=15
    )
    code = stdout.read().decode().strip()
    print(f"  PWA (port 8000 HTTPS): HTTP {code}")

    ssh.close()
    print("\n=== PWA deployment complete ===")


if __name__ == "__main__":
    main()
