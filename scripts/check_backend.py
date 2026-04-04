import paramiko

SERVER = {
    'hostname': '45.78.5.184',
    'port': 22,
    'username': 'root',
    'password': 'wMOByjYmDKsp'
}

def check_backend():
    """检查后端服务状态"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("Connecting to server...")
        ssh.connect(**SERVER)

        # 检查服务状态
        print("\n[1] Checking service status...")
        stdin, stdout, stderr = ssh.exec_command('systemctl status ai-study --no-pager')
        output = stdout.read().decode('utf-8', errors='replace')
        print(output)

        # 查看最近的日志
        print("\n[2] Checking recent logs...")
        stdin, stdout, stderr = ssh.exec_command('journalctl -u ai-study -n 50 --no-pager')
        output = stdout.read().decode('utf-8', errors='replace')
        print(output)

        # 检查端口监听
        print("\n[3] Checking port 8001...")
        stdin, stdout, stderr = ssh.exec_command('netstat -tlnp | grep 8001')
        output = stdout.read().decode('utf-8', errors='replace')
        print(output if output else "Port 8001 not listening")

        # 尝试本地curl
        print("\n[4] Testing local curl...")
        stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1:8001/health')
        output = stdout.read().decode('utf-8', errors='replace')
        error = stderr.read().decode('utf-8', errors='replace')
        print(f"Output: {output}")
        print(f"Error: {error}")

        # 检查Python进程
        print("\n[5] Checking Python processes...")
        stdin, stdout, stderr = ssh.exec_command('ps aux | grep python')
        output = stdout.read().decode('utf-8', errors='replace')
        print(output)

    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        ssh.close()

if __name__ == '__main__':
    check_backend()
