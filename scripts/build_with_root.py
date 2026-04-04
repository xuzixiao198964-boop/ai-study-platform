#!/usr/bin/env python3
"""允许root用户构建Flutter Web"""
import paramiko
import sys

SERVER = "101.201.244.150"
USER = "root"
PASSWORD = "Xzx@123456"

def build():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("连接服务器...")
        ssh.connect(SERVER, username=USER, password=PASSWORD, timeout=30)

        # 使用--allow-root参数
        cmd = """
cd /opt/ai-study-mobile && \
export PATH=/opt/flutter/bin:$PATH && \
flutter build web --release --allow-root
"""

        print("开始构建...")
        stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)

        # 等待完成
        exit_status = stdout.channel.recv_exit_status()

        output = stdout.read().decode('utf-8', errors='replace')
        error = stderr.read().decode('utf-8', errors='replace')

        print("\n=== 输出 ===")
        print(output)

        if error:
            print("\n=== 错误 ===")
            print(error)

        print(f"\n退出码: {exit_status}")

        if exit_status == 0:
            print("\n✓ 构建成功!")
        else:
            print("\n✗ 构建失败")

        return exit_status == 0

    except Exception as e:
        print(f"错误: {e}")
        return False
    finally:
        ssh.close()

if __name__ == "__main__":
    success = build()
    sys.exit(0 if success else 1)
