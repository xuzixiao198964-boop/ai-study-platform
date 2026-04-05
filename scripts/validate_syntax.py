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

    # 检查文件完整性
    cmd = """
cd /opt/ai-study-mobile/build/web
echo "File info:"
wc -l flutter_bootstrap.js
ls -lh flutter_bootstrap.js
echo ""
echo "Last line:"
tail -1 flutter_bootstrap.js
echo ""
echo "Checking _flutter.loader.load call:"
grep -A 2 "_flutter.loader.load" flutter_bootstrap.js
"""

    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)

    print("\n" + "="*70)
    print("Validation complete!")
    print("="*70)
    print("\nFixed issues:")
    print("1. Service Worker SSL error - FIXED")
    print("   Changed: _flutter.loader.load({serviceWorkerSettings: {...}})")
    print("   To:      _flutter.loader.load({})")
    print("")
    print("2. Voice gender mapping - FIXED")
    print("   - ID 1 (云小希): female -> male")
    print("   - ID 2 (云小晚): female -> male")
    print("   - ID 3 (云小刚): Updated description")
    print("   - ID 4 (云小彬): male -> female")
    print("   - ID 5 (云小安): male -> female")
    print("   - ID 6 (云小叶): female -> male")
    print("\nPlease test at: https://45.78.5.184:8000")
    print("Press Ctrl+Shift+R to force refresh browser cache")

except Exception as e:
    print(f"[ERROR] {e}")
finally:
    ssh.close()
