#!/usr/bin/env python3
"""
部署修复到服务器
"""
import paramiko
import sys
import os

HOST = "45.78.5.184"
PORT = 22
USER = "root"
PASSWORD = "FYCZWP2uPLjR"

def upload_file(sftp, local_path, remote_path):
    """上传文件"""
    try:
        sftp.put(local_path, remote_path)
        print(f"[OK] Uploaded: {local_path} -> {remote_path}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to upload {local_path}: {e}")
        return False

def main():
    print("Deploying fixes to server...")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(HOST, PORT, USER, PASSWORD)
        print(f"[OK] Connected to {HOST}")

        sftp = ssh.open_sftp()

        # 1. 上传后端TTS文件
        print("\n[1/3] Uploading backend TTS file...")
        upload_file(
            sftp,
            "D:/work/ai-study-platform/server/app/api/endpoints/tts.py",
            "/opt/ai-study-platform/app/api/endpoints/tts.py"
        )

        # 2. 上传前端flutter_bootstrap.js
        print("\n[2/3] Uploading frontend flutter_bootstrap.js...")
        upload_file(
            sftp,
            "D:/work/ai-study-platform/mobile/build/web/flutter_bootstrap.js",
            "/opt/ai-study-platform/mobile/build/web/flutter_bootstrap.js"
        )

        sftp.close()

        # 3. 重启服务
        print("\n[3/3] Restarting services...")

        commands = [
            "systemctl restart ai-study",
            "systemctl restart nginx",
            "systemctl status ai-study --no-pager -l"
        ]

        for cmd in commands:
            print(f"\nExecuting: {cmd}")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            output = stdout.read().decode('utf-8', errors='ignore')
            error = stderr.read().decode('utf-8', errors='ignore')

            if output:
                print(output)
            if error and 'status' not in cmd:
                print(f"Error: {error}")

        print("\n" + "="*70)
        print("Deployment completed!")
        print("="*70)
        print("\nFixed issues:")
        print("1. Service Worker SSL error - Disabled in flutter_bootstrap.js")
        print("2. Voice gender mapping - Corrected based on actual audio:")
        print("   - ID 1 (云小希): female -> male")
        print("   - ID 2 (云小晚): female -> male")
        print("   - ID 3 (云小刚): Updated description")
        print("   - ID 4 (云小彬): male -> female")
        print("   - ID 5 (云小安): male -> female")
        print("   - ID 6 (云小叶): female -> male")
        print("\nPlease test at: https://45.78.5.184:8000")

        return 0

    except Exception as e:
        print(f"[ERROR] {e}")
        return 1
    finally:
        ssh.close()

if __name__ == "__main__":
    sys.exit(main())
