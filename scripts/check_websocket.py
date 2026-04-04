#!/usr/bin/env python3
"""检查WebSocket后端实现"""
import paramiko
import sys

SERVER = "45.78.5.184"
PORT = 22
USERNAME = "root"
PASSWORD = "wMOByjYmDKsp"

def exec_cmd(client, cmd, description=""):
    """执行命令"""
    if description:
        print(f"\n[{description}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    exit_code = stdout.channel.recv_exit_status()

    try:
        if output:
            print(output)
    except UnicodeEncodeError:
        with open("D:/cmd_output.txt", "w", encoding="utf-8") as f:
            f.write(output)
        print("(Output saved to D:/cmd_output.txt)")

    return exit_code == 0, output, error

def main():
    print("=" * 60)
    print("Checking WebSocket backend")
    print("=" * 60)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(SERVER, PORT, USERNAME, PASSWORD, timeout=30)
        print("[OK] SSH connected")
    except Exception as e:
        print(f"[FAIL] SSH connection failed: {e}")
        return False

    # 检查后端目录结构
    print("\n[1] Checking backend directory...")
    exec_cmd(client, "ls -la /opt/ai-study-platform/server/", "Backend directory")

    # 检查main.py中的WebSocket路由
    print("\n[2] Checking main.py for WebSocket routes...")
    exec_cmd(client, "grep -n 'websocket\\|WebSocket\\|/ws' /opt/ai-study-platform/server/main.py | head -20", "WebSocket in main.py")

    # 检查是否有WebSocket相关文件
    print("\n[3] Searching for WebSocket implementation...")
    exec_cmd(client, "find /opt/ai-study-platform/server -name '*.py' -exec grep -l 'websocket\\|WebSocket' {} \\; | head -10", "Files with WebSocket")

    # 检查后端日志
    print("\n[4] Checking backend logs...")
    exec_cmd(client, "journalctl -u ai-study -n 50 --no-pager", "Backend logs")

    client.close()
    return True

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
