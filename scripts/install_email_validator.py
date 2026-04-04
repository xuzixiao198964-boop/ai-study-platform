import paramiko

SERVER = {
    'hostname': '45.78.5.184',
    'port': 22,
    'username': 'root',
    'password': 'wMOByjYmDKsp'
}

def install_deps():
    """安装缺失的Python依赖"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("Connecting to server...")
        ssh.connect(**SERVER)

        # 检查当前pip list
        print("\n[1] Checking current packages...")
        stdin, stdout, stderr = ssh.exec_command('pip list | grep email')
        output = stdout.read().decode('utf-8', errors='replace')
        print(f"Email packages: {output if output else 'None'}")

        # 使用pip3安装
        print("\n[2] Installing email-validator with pip3...")
        stdin, stdout, stderr = ssh.exec_command('pip3 install email-validator')
        stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8', errors='replace')
        error = stderr.read().decode('utf-8', errors='replace')
        print(output[-500:] if len(output) > 500 else output)
        if error:
            print(f"Errors: {error[-500:]}")

        # 验证安装
        print("\n[3] Verifying installation...")
        stdin, stdout, stderr = ssh.exec_command('python3 -c "import email_validator; print(email_validator.__version__)"')
        output = stdout.read().decode('utf-8', errors='replace')
        error = stderr.read().decode('utf-8', errors='replace')
        print(f"email-validator version: {output}")
        if error:
            print(f"Error: {error}")

        # 重启服务
        print("\n[4] Restarting service...")
        stdin, stdout, stderr = ssh.exec_command('systemctl restart ai-study')
        stdout.channel.recv_exit_status()

        # 等待启动
        import time
        time.sleep(5)

        # 检查状态
        print("\n[5] Checking service status...")
        stdin, stdout, stderr = ssh.exec_command('systemctl status ai-study --no-pager -l')
        output = stdout.read().decode('utf-8', errors='replace')
        print(output)

        # 测试API
        print("\n[6] Testing API...")
        stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1:8001/health')
        output = stdout.read().decode('utf-8', errors='replace')
        print(f"Health: {output}")

        print("\n[OK] Done!")

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == '__main__':
    install_deps()
