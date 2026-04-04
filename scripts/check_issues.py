#!/usr/bin/env python3
"""检查并修复所有问题"""
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
        if error:
            print(f"STDERR: {error}")
    except UnicodeEncodeError:
        with open("D:/cmd_output.txt", "w", encoding="utf-8") as f:
            f.write(output)
            f.write("\n\n")
            f.write(error)
        print("(Output saved to D:/cmd_output.txt)")

    return exit_code == 0, output, error

def main():
    print("=" * 60)
    print("Checking and fixing issues")
    print("=" * 60)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(SERVER, PORT, USERNAME, PASSWORD, timeout=30)
        print("[OK] SSH connected")
    except Exception as e:
        print(f"[FAIL] SSH connection failed: {e}")
        return False

    # 检查Nginx配置
    print("\n[1] Checking Nginx configuration...")
    success, output, error = exec_cmd(client, "cat /etc/nginx/sites-available/ai-study", "Current Nginx config")

    # 保存配置到文件
    with open("D:/nginx_config.txt", "w", encoding="utf-8") as f:
        f.write(output)
    print("Nginx config saved to D:/nginx_config.txt")

    # 检查WebSocket是否配置
    if "ws" not in output.lower():
        print("[WARNING] WebSocket proxy not configured in Nginx")

    # 检查后端WebSocket端点
    print("\n[2] Checking backend WebSocket endpoint...")
    success, output, error = exec_cmd(client, "grep -r 'websocket\\|WebSocket\\|/ws' /opt/ai-study-platform/server/app/ | head -20", "Backend WS code")

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
