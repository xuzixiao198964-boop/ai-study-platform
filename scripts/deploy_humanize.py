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

    sftp = ssh.open_sftp()

    # 1. 上传后端TTS文件
    print("\n[1/3] Uploading backend TTS file...")
    sftp.put(
        "D:/work/ai-study-platform/server/app/api/endpoints/tts.py",
        "/opt/ai-study-platform/app/api/endpoints/tts.py"
    )
    print("[OK] Uploaded tts.py")

    # 2. 上传前端Dart文件
    print("\n[2/3] Uploading frontend Dart file...")
    sftp.put(
        "D:/work/ai-study-platform/mobile/lib/screens/student/student_home_screen.dart",
        "/opt/ai-study-platform/mobile/lib/screens/student/student_home_screen.dart"
    )
    print("[OK] Uploaded student_home_screen.dart")

    sftp.close()

    # 3. 重启后端
    print("\n[3/3] Restarting backend...")
    stdin, stdout, stderr = ssh.exec_command("systemctl restart ai-study")
    stdout.read()
    print("[OK] Backend restarted")

    # 4. 重新构建Flutter
    print("\n[4/3] Rebuilding Flutter Web...")
    cmd = """
cd /opt/ai-study-platform/mobile
/opt/flutter/bin/flutter build web --release
cp -r build/web/* /opt/ai-study-mobile/build/web/
systemctl restart nginx
echo "[OK] Flutter rebuilt and deployed"
"""
    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    
    print(output)
    if error and 'Building' not in error:
        print("Errors:", error)

    print("\n" + "="*70)
    print("Deployment completed!")
    print("="*70)
    print("\nChanges:")
    print("1. Voice names updated to teacher format:")
    print("   - 宁老师, 彬老师, 安老师, 欣老师 (female)")
    print("   - 希老师, 晚老师, 刚老师, 叶老师 (male)")
    print("   - 瑜老师, 聆老师, 美老师 (premium female)")
    print("")
    print("2. UI text humanized:")
    print("   - '欢迎使用学习指认AI' -> '欢迎使用学习助手'")
    print("   - '给AI起个名字' -> '给老师起个名字'")
    print("   - '选择AI声音' -> '选择老师声音'")
    print("\nPlease test at: https://45.78.5.184:8000")
    print("Press Ctrl+Shift+R to force refresh")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
