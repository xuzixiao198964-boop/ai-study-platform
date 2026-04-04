import paramiko

SERVER = '45.78.5.184'
USER = 'root'
PASSWORD = 'wMOByjYmDKsp'

def force_restart_nginx():
    """强制重启Nginx并检查"""
    print("=" * 60)
    print("Force Restart Nginx")
    print("=" * 60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("\n[1] Connecting to server...")
        ssh.connect(SERVER, username=USER, password=PASSWORD, timeout=30)

        # 停止Nginx
        print("\n[2] Stopping Nginx...")
        stdin, stdout, stderr = ssh.exec_command('systemctl stop nginx', timeout=30)
        stdout.channel.recv_exit_status()
        print("  Nginx stopped")

        # 检查是否还有nginx进程
        print("\n[3] Checking for remaining nginx processes...")
        stdin, stdout, stderr = ssh.exec_command('ps aux | grep nginx | grep -v grep', timeout=30)
        output = stdout.read().decode('utf-8', errors='replace')
        if output.strip():
            print(f"  Found processes:\n{output}")
            print("  Killing remaining processes...")
            stdin, stdout, stderr = ssh.exec_command('killall nginx', timeout=30)
            stdout.channel.recv_exit_status()
        else:
            print("  No remaining processes")

        # 检查错误日志
        print("\n[4] Checking error log...")
        stdin, stdout, stderr = ssh.exec_command('tail -20 /var/log/nginx/error.log', timeout=30)
        output = stdout.read().decode('utf-8', errors='replace')
        if output.strip():
            print(f"  Recent errors:\n{output}")

        # 启动Nginx
        print("\n[5] Starting Nginx...")
        stdin, stdout, stderr = ssh.exec_command('systemctl start nginx', timeout=30)
        stdout.channel.recv_exit_status()

        # 检查状态
        stdin, stdout, stderr = ssh.exec_command('systemctl status nginx', timeout=30)
        output = stdout.read().decode('utf-8', errors='replace')
        if 'active (running)' in output:
            print("  [OK] Nginx is running")
        else:
            print("  [FAIL] Nginx failed to start")
            print(output)
            return False

        # 检查监听端口
        print("\n[6] Checking listening ports...")
        stdin, stdout, stderr = ssh.exec_command('ss -tlnp | grep nginx', timeout=30)
        output = stdout.read().decode('utf-8', errors='replace')
        print(output)

        # 测试HTTPS
        print("\n[7] Testing HTTPS on port 8000...")
        stdin, stdout, stderr = ssh.exec_command('timeout 5 openssl s_client -connect 127.0.0.1:8000 < /dev/null 2>&1 | grep -E "^(SSL|subject|issuer)"', timeout=30)
        output = stdout.read().decode('utf-8', errors='replace')
        if 'SSL' in output or 'subject' in output:
            print("  [OK] SSL handshake successful")
            print(output)
        else:
            print("  [FAIL] SSL handshake failed")
            print(output)

        # 测试HTTP请求
        print("\n[8] Testing HTTPS request...")
        stdin, stdout, stderr = ssh.exec_command('curl -k -I https://127.0.0.1:8000/ 2>&1', timeout=30)
        output = stdout.read().decode('utf-8', errors='replace')
        print(output[:500])

        ssh.close()

        print("\n" + "=" * 60)
        print("Nginx restart completed")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        ssh.close()

if __name__ == '__main__':
    force_restart_nginx()
