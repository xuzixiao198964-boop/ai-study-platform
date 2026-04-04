#!/usr/bin/env python3
"""检查远程构建状态"""
import paramiko
import sys

SERVER = "101.201.244.150"
USER = "root"
PASSWORD = "Xzx@123456"

def check_build():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("连接服务器...")
        ssh.connect(SERVER, username=USER, password=PASSWORD, timeout=30)

        # 检查是否有flutter进程在运行
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep flutter | grep -v grep")
        processes = stdout.read().decode('utf-8', errors='replace')

        if processes.strip():
            print("✓ Flutter构建进程正在运行:")
            print(processes)
        else:
            print("✗ 没有发现Flutter构建进程")

            # 检查构建结果
            stdin, stdout, stderr = ssh.exec_command("ls -lh /opt/ai-study-mobile/build/web/index.html")
            result = stdout.read().decode('utf-8', errors='replace')
            error = stderr.read().decode('utf-8', errors='replace')

            if result.strip():
                print("\n✓ 构建产物存在:")
                print(result)
            else:
                print("\n✗ 构建产物不存在")
                print(error)

    except Exception as e:
        print(f"错误: {e}")
        return False
    finally:
        ssh.close()

    return True

if __name__ == "__main__":
    check_build()
