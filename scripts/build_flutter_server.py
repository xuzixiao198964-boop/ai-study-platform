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

    # 检查服务器上的mobile目录
    print("\n[1/4] Checking mobile directory...")
    stdin, stdout, stderr = ssh.exec_command("ls -la /opt/ai-study-platform/ | grep mobile")
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output if output else "[WARN] No mobile directory found")

    # 查找student_home_screen.dart
    print("\n[2/4] Finding student_home_screen.dart...")
    stdin, stdout, stderr = ssh.exec_command("find /opt -name 'student_home_screen.dart' 2>/dev/null")
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output if output else "[WARN] File not found")

    # 上传修改后的文件
    print("\n[3/4] Uploading modified Dart file...")
    
    sftp = ssh.open_sftp()
    
    # 尝试上传到可能的位置
    remote_path = "/opt/ai-study-mobile/lib/screens/student/student_home_screen.dart"
    local_path = "D:/work/ai-study-platform/mobile/lib/screens/student/student_home_screen.dart"
    
    try:
        sftp.put(local_path, remote_path)
        print(f"[OK] Uploaded to {remote_path}")
    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        print("Trying to create directory structure...")
        
        # 创建目录
        stdin, stdout, stderr = ssh.exec_command(f"mkdir -p /opt/ai-study-mobile/lib/screens/student")
        stdout.read()
        
        sftp.put(local_path, remote_path)
        print(f"[OK] Uploaded to {remote_path}")
    
    sftp.close()

    # 构建Flutter
    print("\n[4/4] Building Flutter Web...")
    cmd = """
cd /opt/ai-study-mobile
/opt/flutter/bin/flutter build web --release 2>&1 | tail -30
"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=300)
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)

    # 重启nginx
    print("\nRestarting nginx...")
    stdin, stdout, stderr = ssh.exec_command("systemctl restart nginx")
    stdout.read()

    print("\n" + "="*70)
    print("[OK] Frontend updated!")
    print("="*70)
    print("\nUI text humanized:")
    print("- 'AI' -> 'Teacher/Assistant'")
    print("- Voice names now use teacher format")
    print("\nPlease test at: https://45.78.5.184:8000")
    print("Press Ctrl+Shift+R to force refresh")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
