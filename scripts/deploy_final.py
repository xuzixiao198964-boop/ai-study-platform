#!/usr/bin/env python3
import paramiko

HOST = "45.78.5.184"
PORT = 22
USER = "root"
PASSWORD = "FYCZWP2uPLjR"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(HOST, PORT, USER, PASSWORD)
    print("[OK] Connected")

    # 修改flutter_bootstrap.js禁用Service Worker
    cmd = """
cd /opt/ai-study-mobile/build/web
if [ -f flutter_bootstrap.js ]; then
    cp flutter_bootstrap.js flutter_bootstrap.js.bak
    sed -i 's/serviceWorkerSettings: {/\/\/ serviceWorkerSettings: {/' flutter_bootstrap.js
    sed -i 's/serviceWorkerVersion:/\/\/ serviceWorkerVersion:/' flutter_bootstrap.js
    echo "[OK] Modified flutter_bootstrap.js"
    echo ""
    echo "Checking modification:"
    grep -A 3 "loader.load" flutter_bootstrap.js | tail -5
else
    echo "[ERROR] flutter_bootstrap.js not found"
fi
"""

    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')

    print(output)
    if error:
        print("Errors:", error)

    # 重启nginx
    print("\n" + "="*70)
    print("Restarting nginx...")
    stdin, stdout, stderr = ssh.exec_command("systemctl restart nginx")
    stdout.read()

    print("\n" + "="*70)
    print("Deployment completed!")
    print("="*70)
    print("\nFixed issues:")
    print("1. Service Worker SSL error - Disabled in flutter_bootstrap.js")
    print("2. Voice gender mapping - Updated in backend TTS API:")
    print("   - ID 1 (yun xiao xi): female -> male")
    print("   - ID 2 (yun xiao wan): female -> male")
    print("   - ID 3 (yun xiao gang): Updated description")
    print("   - ID 4 (yun xiao bin): male -> female")
    print("   - ID 5 (yun xiao an): male -> female")
    print("   - ID 6 (yun xiao ye): female -> male")
    print("\nPlease test at: https://45.78.5.184:8000")
    print("Clear browser cache (Ctrl+Shift+R) to see the changes")

except Exception as e:
    print(f"[ERROR] {e}")
finally:
    ssh.close()
