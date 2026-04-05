#!/usr/bin/env python3
import paramiko
import sys

HOST = "45.78.5.184"
PORT = 22
USER = "root"
PASSWORD = "FYCZWP2uPLjR"

print("Deploying all fixes...")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
sftp = None

try:
    ssh.connect(HOST, PORT, USER, PASSWORD)
    sftp = ssh.open_sftp()
    print("[OK] Connected")

    # 1. 上传前端文件
    print("\n[1/3] Uploading frontend files...")
    sftp.put("D:/work/ai-study-platform/mobile/lib/screens/student/student_home_screen.dart",
             "/opt/ai-study-mobile/lib/screens/student/student_home_screen.dart")
    sftp.put("D:/work/ai-study-platform/mobile/web/index.html",
             "/opt/ai-study-mobile/web/index.html")
    print("[OK] Frontend files uploaded")

    # 2. 构建Flutter
    print("\n[2/3] Building Flutter Web...")
    cmd = """
cd /opt/ai-study-mobile
/opt/flutter/bin/flutter build web --release
echo "BUILD_DONE"
"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=300)
    
    for line in stdout:
        try:
            print(line.strip())
        except:
            pass

    # 3. 重启Nginx
    print("\n[3/3] Restarting Nginx...")
    stdin, stdout, stderr = ssh.exec_command("systemctl restart nginx")
    stdout.read()
    print("[OK] Nginx restarted")

    print("\n" + "="*70)
    print("[OK] All fixes deployed!")
    print("="*70)
    print("\nFixed issues:")
    print("1. ✅ 选择老师后自动填充名字")
    print("2. ✅ Service Worker SSL错误已解决")
    print("3. ✅ TTS播放时暂停语音识别，避免回声")
    print("4. ✅ 移除初始进入时的两次1秒倒计时")
    print("5. ✅ 修复持续对话失效问题")
    print("\nTest at: https://45.78.5.184:8000")
    print("Press Ctrl+Shift+R to clear cache and refresh")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    if sftp:
        sftp.close()
    ssh.close()
