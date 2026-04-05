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

    # 上传后端TTS文件
    print("\n[1/2] Uploading backend TTS file...")
    sftp.put(
        "D:/work/ai-study-platform/server/app/api/endpoints/tts.py",
        "/opt/ai-study-platform/app/api/endpoints/tts.py"
    )
    print("[OK] Uploaded tts.py")

    sftp.close()

    # 重启后端
    print("\n[2/2] Restarting backend...")
    stdin, stdout, stderr = ssh.exec_command("systemctl restart ai-study && systemctl status ai-study --no-pager -l | head -15")
    print(stdout.read().decode('utf-8', errors='ignore'))

    print("\n" + "="*70)
    print("[OK] Backend updated!")
    print("="*70)
    print("\nVoice names updated to teacher format:")
    print("Female: 宁老师, 彬老师, 安老师, 欣老师, 瑜老师, 聆老师, 美老师")
    print("Male: 希老师, 晚老师, 刚老师, 叶老师")
    print("\nNow building Flutter frontend...")

except Exception as e:
    print(f"[ERROR] {e}")
finally:
    ssh.close()
