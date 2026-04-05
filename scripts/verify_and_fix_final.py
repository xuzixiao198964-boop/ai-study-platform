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

    # 检查当前文件状态
    print("\n[1/3] Checking current file...")
    cmd = "cd /opt/ai-study-mobile/build/web && wc -l flutter_bootstrap.js && tail -20 flutter_bootstrap.js"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode('utf-8', errors='ignore'))

    # 恢复原始备份
    print("\n[2/3] Restoring original backup...")
    cmd = """
cd /opt/ai-study-mobile/build/web
if [ -f flutter_bootstrap.js.bak ]; then
    cp flutter_bootstrap.js.bak flutter_bootstrap.js
    echo "[OK] Restored from .bak"
elif [ -f flutter_bootstrap.js.bak2 ]; then
    cp flutter_bootstrap.js.bak2 flutter_bootstrap.js
    echo "[OK] Restored from .bak2"
else
    echo "[ERROR] No backup found!"
    exit 1
fi

# 验证文件完整性
echo ""
echo "File size and line count:"
wc -l flutter_bootstrap.js
ls -lh flutter_bootstrap.js
"""
    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    print(output)
    if error:
        print("Error:", error)

    # 正确修改：只修改load()调用，不删除任何代码
    print("\n[3/3] Applying correct fix...")
    cmd = r"""
cd /opt/ai-study-mobile/build/web

# 使用perl进行精确替换
perl -i -pe 's/_flutter\.loader\.load\(\{\s*serviceWorkerSettings:\s*\{[^}]*\}\s*\}\);/_flutter.loader.load({});/gs' flutter_bootstrap.js

echo "[OK] Modified"
echo ""
echo "Verification - last 15 lines:"
tail -15 flutter_bootstrap.js
echo ""
echo "Checking for syntax errors with node:"
node -c flutter_bootstrap.js 2>&1 || echo "Syntax check completed"
"""
    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    print(output)
    if error and 'Syntax check' not in error:
        print("Error:", error)

    # 重启nginx
    print("\n[4/3] Restarting nginx...")
    stdin, stdout, stderr = ssh.exec_command("systemctl restart nginx")
    stdout.read()

    print("\n" + "="*70)
    print("[OK] Fix applied and verified")
    print("="*70)

except Exception as e:
    print(f"[ERROR] {e}")
finally:
    ssh.close()
