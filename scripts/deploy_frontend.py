#!/usr/bin/env python3
"""部署前端修复到服务器"""
import paramiko
import sys
from pathlib import Path

SERVER = "45.78.5.184"
PORT = 22
USER = "root"
PASSWORD = "FYCZWP2uPLjR"

def main():
    print("\n" + "="*60)
    print("部署前端修复到服务器")
    print("="*60 + "\n")

    # 连接服务器
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(SERVER, PORT, USER, PASSWORD, timeout=10)
        print("[OK] SSH连接成功\n")
    except Exception as e:
        print(f"[ERROR] SSH连接失败: {e}")
        return 1

    sftp = ssh.open_sftp()

    # 上传index.html
    local_file = Path("D:/work/ai-study-platform/mobile/web/index.html")
    remote_file = "/opt/ai-study-platform/mobile/web/index.html"

    try:
        sftp.put(str(local_file), remote_file)
        print(f"[OK] 上传: index.html")
    except Exception as e:
        print(f"[ERROR] 上传失败: {e}")
        sftp.close()
        ssh.close()
        return 1

    sftp.close()

    # 重启Nginx
    print("\n重启Nginx...")
    stdin, stdout, stderr = ssh.exec_command("systemctl restart nginx && systemctl status nginx | head -15")
    print(stdout.read().decode())

    # 测试前端
    print("\n" + "="*60)
    print("测试前端访问")
    print("="*60)

    stdin, stdout, stderr = ssh.exec_command("curl -I http://45.78.5.184:8000/ 2>&1 | head -5")
    print(stdout.read().decode())

    ssh.close()
    print("\n[OK] 部署完成！")
    print("\n请访问: http://45.78.5.184:8000")
    print("打开F12控制台查看日志，测试语音对话功能")
    return 0

if __name__ == "__main__":
    sys.exit(main())
