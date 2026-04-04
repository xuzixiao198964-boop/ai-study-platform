#!/usr/bin/env python3
"""部署所有修复到服务器"""
import paramiko
import sys
import os

SERVER = "45.78.5.184"
PORT = 22
USERNAME = "root"
PASSWORD = "wMOByjYmDKsp"

def exec_cmd(client, cmd, description=""):
    """执行命令"""
    if description:
        print(f"\n[{description}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    exit_code = stdout.channel.recv_exit_status()

    try:
        if output:
            print(output)
        if error and exit_code != 0:
            print(f"ERROR: {error}")
    except UnicodeEncodeError:
        with open("D:/deploy_output.txt", "w", encoding="utf-8") as f:
            f.write(output)
            if error:
                f.write("\n\nERROR:\n" + error)
        print("(Output saved to D:/deploy_output.txt)")

    return exit_code == 0, output, error

def upload_file(sftp, local_path, remote_path):
    """上传文件"""
    print(f"Uploading {local_path} -> {remote_path}")
    try:
        sftp.put(local_path, remote_path)
        return True
    except Exception as e:
        print(f"Failed to upload {local_path}: {e}")
        return False

def main():
    print("=" * 60)
    print("Deploying fixes to server")
    print("=" * 60)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(SERVER, PORT, USERNAME, PASSWORD, timeout=30)
        print("[OK] SSH connected")
    except Exception as e:
        print(f"[FAIL] SSH connection failed: {e}")
        return False

    sftp = client.open_sftp()

    # 1. 上传修复的index.html
    print("\n[1] Uploading fixed index.html...")
    if not upload_file(sftp,
                      "D:/work/ai-study-platform/mobile/web/index.html",
                      "/opt/ai-study-mobile/build/web/index.html"):
        print("Failed to upload index.html")
        sftp.close()
        client.close()
        return False

    # 2. 上传修复的student_home_screen.dart
    print("\n[2] Uploading fixed student_home_screen.dart...")
    if not upload_file(sftp,
                      "D:/work/ai-study-platform/mobile/lib/screens/student/student_home_screen.dart",
                      "/opt/ai-study-mobile/lib/screens/student/student_home_screen.dart"):
        print("Failed to upload student_home_screen.dart")
        sftp.close()
        client.close()
        return False

    sftp.close()

    # 3. 重新构建Flutter Web
    print("\n[3] Rebuilding Flutter Web...")
    success, output, error = exec_cmd(client,
        "cd /opt/ai-study-mobile && /opt/flutter/bin/flutter build web --release --web-renderer html",
        "Building Flutter Web")

    if not success:
        print("Flutter build failed!")
        client.close()
        return False

    # 4. 重启Nginx
    print("\n[4] Restarting Nginx...")
    exec_cmd(client, "systemctl restart nginx", "Restarting Nginx")

    # 5. 检查服务状态
    print("\n[5] Checking service status...")
    exec_cmd(client, "systemctl status nginx --no-pager -l", "Nginx status")
    exec_cmd(client, "systemctl status ai-study --no-pager -l", "Backend status")

    print("\n" + "=" * 60)
    print("Deployment completed!")
    print("=" * 60)
    print("\nAccess URLs:")
    print("- Website: https://45.78.5.184/")
    print("- App: https://45.78.5.184:8000/")
    print("\nTest accounts:")
    print("- Student: student1 / password123")
    print("- Parent: parent1 / password123")

    client.close()
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
