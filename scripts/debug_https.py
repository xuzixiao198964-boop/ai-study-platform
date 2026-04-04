import paramiko

SERVER = '45.78.5.184'
USER = 'root'
PASSWORD = 'wMOByjYmDKsp'

def debug_https():
    """调试HTTPS问题"""
    print("=" * 60)
    print("Debugging HTTPS")
    print("=" * 60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("\n[1] Connecting to server...")
        ssh.connect(SERVER, username=USER, password=PASSWORD, timeout=30)

        # 检查证书文件
        print("\n[2] Checking SSL certificates...")
        stdin, stdout, stderr = ssh.exec_command('ls -lh /etc/nginx/ssl/', timeout=30)
        output = stdout.read().decode('utf-8', errors='replace')
        print(output)

        # 检查Nginx配置
        print("\n[3] Checking Nginx config...")
        stdin, stdout, stderr = ssh.exec_command('nginx -T 2>&1 | grep -A 20 "listen 8000"', timeout=30)
        output = stdout.read().decode('utf-8', errors='replace')
        print(output[:1000])

        # 检查端口监听
        print("\n[4] Checking listening ports...")
        stdin, stdout, stderr = ssh.exec_command('netstat -tlnp | grep nginx', timeout=30)
        output = stdout.read().decode('utf-8', errors='replace')
        print(output)

        # 测试HTTPS连接
        print("\n[5] Testing HTTPS connection...")
        stdin, stdout, stderr = ssh.exec_command('curl -k -v https://127.0.0.1:8000/ 2>&1 | head -30', timeout=30)
        output = stdout.read().decode('utf-8', errors='replace')
        print(output)

        # 检查Flutter构建文件
        print("\n[6] Checking Flutter build files...")
        stdin, stdout, stderr = ssh.exec_command('ls -lh /opt/ai-study-mobile/build/web/ | head -10', timeout=30)
        output = stdout.read().decode('utf-8', errors='replace')
        print(output)

        ssh.close()

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == '__main__':
    debug_https()
