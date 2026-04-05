#!/usr/bin/env python3
import paramiko
import sys

HOST = "45.78.5.184"
PORT = 22
USER = "root"
PASSWORD = "FYCZWP2uPLjR"

print("Deploying voice fixes...")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
sftp = None

try:
    ssh.connect(HOST, PORT, USER, PASSWORD)
    sftp = ssh.open_sftp()
    print("[OK] Connected")

    # 1. 上传后端TTS文件
    print("\n[1/4] Uploading backend TTS...")
    sftp.put("D:/work/ai-study-platform/server/app/api/endpoints/tts.py",
             "/opt/ai-study-platform/app/api/endpoints/tts.py")
    print("[OK] Backend uploaded")

    # 2. 重启后端服务
    print("\n[2/4] Restarting backend...")
    stdin, stdout, stderr = ssh.exec_command("systemctl restart ai-study")
    stdout.read()
    print("[OK] Backend restarted")

    # 3. 上传前端文件
    print("\n[3/4] Uploading frontend...")
    sftp.put("D:/work/ai-study-platform/mobile/lib/screens/student/student_home_screen.dart",
             "/opt/ai-study-mobile/lib/screens/student/student_home_screen.dart")
    print("[OK] Frontend uploaded")

    # 4. 构建Flutter
    print("\n[4/4] Building Flutter Web...")
    cmd = """
cd /opt/ai-study-mobile
/opt/flutter/bin/flutter build web --release
systemctl restart nginx
echo "DONE"
"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=300)
    
    for line in stdout:
        try:
            print(line.strip())
        except:
            pass

    print("\n" + "="*70)
    print("[OK] Deployment completed!")
    print("="*70)
    print("\nChanges:")
    print("1. Removed duplicate voice (Bin Teacher)")
    print("2. User selected voice now used for TTS playback")
    print("\nTest at: https://45.78.5.184:8000")
    print("Press Ctrl+Shift+R to refresh")

except Exception as e:
    print(f"[ERROR] {e}")
    sys.exit(1)
finally:
    if sftp:
        sftp.close()
    ssh.close()
