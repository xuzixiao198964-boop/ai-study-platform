import paramiko
import time

SERVER = '45.78.5.184'
USER = 'root'
PASSWORD = 'wMOByjYmDKsp'

def setup_https():
    """配置HTTPS证书和Nginx"""
    print("=" * 60)
    print("Setting up HTTPS")
    print("=" * 60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("\n[1] Connecting to server...")
        ssh.connect(SERVER, username=USER, password=PASSWORD, timeout=30)

        # 安装certbot
        print("\n[2] Installing certbot...")
        commands = [
            'apt-get update',
            'apt-get install -y certbot python3-certbot-nginx'
        ]
        for cmd in commands:
            stdin, stdout, stderr = ssh.exec_command(cmd, timeout=300)
            stdout.channel.recv_exit_status()
            print(f"  Executed: {cmd}")

        # 检查域名是否指向服务器
        print("\n[3] Checking DNS...")
        print("  Note: You need a domain name pointing to 45.78.5.184")
        print("  If you don't have a domain, we'll use self-signed certificate")

        # 生成自签名证书
        print("\n[4] Generating self-signed certificate...")
        cert_commands = [
            'mkdir -p /etc/nginx/ssl',
            'openssl req -x509 -nodes -days 365 -newkey rsa:2048 '
            '-keyout /etc/nginx/ssl/selfsigned.key '
            '-out /etc/nginx/ssl/selfsigned.crt '
            '-subj "/C=CN/ST=Beijing/L=Beijing/O=AI Study/CN=45.78.5.184"'
        ]
        for cmd in cert_commands:
            stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
            stdout.channel.recv_exit_status()
            print(f"  Executed: {cmd}")

        # 更新Nginx配置
        print("\n[5] Updating Nginx configuration...")
        nginx_config = '''
# 官网 - 80端口重定向到HTTPS
server {
    listen 80;
    server_name _;
    return 301 https://$host$request_uri;
}

# 官网 - 443端口HTTPS
server {
    listen 443 ssl http2;
    server_name _;

    ssl_certificate /etc/nginx/ssl/selfsigned.crt;
    ssl_certificate_key /etc/nginx/ssl/selfsigned.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    root /opt/ai-study-website;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api-portal {
        try_files /api-portal.html =404;
    }

    location /admin {
        try_files /admin.html =404;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /admin/api/ {
        proxy_pass http://127.0.0.1:8001/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# 应用端 - 8000端口HTTPS
server {
    listen 8000 ssl http2;
    server_name _;

    ssl_certificate /etc/nginx/ssl/selfsigned.crt;
    ssl_certificate_key /etc/nginx/ssl/selfsigned.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    root /opt/ai-study-mobile/build/web;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
'''

        # 写入Nginx配置
        stdin, stdout, stderr = ssh.exec_command('cat > /etc/nginx/sites-available/default', timeout=30)
        stdin.write(nginx_config)
        stdin.channel.shutdown_write()
        stdout.channel.recv_exit_status()
        print("  Nginx config updated")

        # 测试并重启Nginx
        print("\n[6] Testing and restarting Nginx...")
        stdin, stdout, stderr = ssh.exec_command('nginx -t', timeout=30)
        exit_status = stdout.channel.recv_exit_status()
        output = stderr.read().decode('utf-8', errors='replace')
        print(f"  {output}")

        if exit_status == 0:
            stdin, stdout, stderr = ssh.exec_command('systemctl restart nginx', timeout=30)
            stdout.channel.recv_exit_status()
            print("  [OK] Nginx restarted")
        else:
            print("  [ERROR] Nginx config test failed")
            return False

        # 验证HTTPS
        print("\n[7] Verifying HTTPS...")
        time.sleep(2)
        stdin, stdout, stderr = ssh.exec_command('curl -k -s https://127.0.0.1/ | head -5', timeout=30)
        output = stdout.read().decode('utf-8', errors='replace')
        if 'DOCTYPE html' in output:
            print("  [OK] HTTPS is working")
        else:
            print("  [WARNING] HTTPS may not be working properly")

        ssh.close()

        print("\n" + "=" * 60)
        print("[SUCCESS] HTTPS configured!")
        print("=" * 60)
        print("\nAccess URLs (HTTPS):")
        print("  Official Website: https://45.78.5.184/")
        print("  Student/Parent App: https://45.78.5.184:8000/")
        print("\nNote: You'll see a security warning because it's a self-signed certificate.")
        print("Click 'Advanced' -> 'Proceed to 45.78.5.184' to continue.")

        return True

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        ssh.close()

if __name__ == '__main__':
    setup_https()
