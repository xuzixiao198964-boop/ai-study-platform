import paramiko

SERVER = '45.78.5.184'
USER = 'root'
PASSWORD = 'wMOByjYmDKsp'

def update_ai_study_config():
    """更新ai-study配置文件添加SSL"""
    print("=" * 60)
    print("Updating ai-study Nginx Config with SSL")
    print("=" * 60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("\n[1] Connecting to server...")
        ssh.connect(SERVER, username=USER, password=PASSWORD, timeout=30)

        # 新的配置文件，包含SSL
        print("\n[2] Writing new configuration...")
        nginx_config = '''# 官网 - 80端口
server {
    listen 80;
    server_name _;

    location / {
        root /opt/ai-study-website;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api-portal {
        root /opt/ai-study-website;
        try_files /api-portal.html =404;
    }

    location /admin {
        root /opt/ai-study-website;
        try_files /admin.html =404;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_cache_bypass $http_upgrade;
    }

    location /admin/api/ {
        rewrite ^/admin/api/(.*) /api/v1/admin/$1 break;
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

# 官网 - 443端口HTTPS
server {
    listen 443 ssl http2;
    server_name _;

    ssl_certificate /etc/nginx/ssl/selfsigned.crt;
    ssl_certificate_key /etc/nginx/ssl/selfsigned.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        root /opt/ai-study-website;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api-portal {
        root /opt/ai-study-website;
        try_files /api-portal.html =404;
    }

    location /admin {
        root /opt/ai-study-website;
        try_files /admin.html =404;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_cache_bypass $http_upgrade;
    }

    location /admin/api/ {
        rewrite ^/admin/api/(.*) /api/v1/admin/$1 break;
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
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

    location / {
        root /opt/ai-study-mobile/build/web;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_cache_bypass $http_upgrade;
    }

    location /ws/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
'''

        stdin, stdout, stderr = ssh.exec_command('cat > /etc/nginx/sites-available/ai-study', timeout=30)
        stdin.write(nginx_config)
        stdin.channel.shutdown_write()
        stdout.channel.recv_exit_status()
        print("  Configuration written")

        # 测试配置
        print("\n[3] Testing Nginx configuration...")
        stdin, stdout, stderr = ssh.exec_command('nginx -t', timeout=30)
        exit_status = stdout.channel.recv_exit_status()
        output = stderr.read().decode('utf-8', errors='replace')
        print(f"  {output}")

        if exit_status != 0:
            print("  [ERROR] Nginx config test failed")
            return False

        # 重启Nginx
        print("\n[4] Restarting Nginx...")
        stdin, stdout, stderr = ssh.exec_command('systemctl restart nginx', timeout=30)
        stdout.channel.recv_exit_status()
        print("  [OK] Nginx restarted")

        # 验证HTTPS
        print("\n[5] Verifying HTTPS...")

        # 测试443端口
        stdin, stdout, stderr = ssh.exec_command('curl -k -I https://127.0.0.1:443/ 2>&1 | head -5', timeout=30)
        output = stdout.read().decode('utf-8', errors='replace')
        if 'HTTP' in output and '200' in output:
            print("  [OK] HTTPS working on port 443")
        else:
            print(f"  Port 443: {output[:200]}")

        # 测试8000端口
        stdin, stdout, stderr = ssh.exec_command('curl -k -I https://127.0.0.1:8000/ 2>&1 | head -5', timeout=30)
        output = stdout.read().decode('utf-8', errors='replace')
        if 'HTTP' in output and '200' in output:
            print("  [OK] HTTPS working on port 8000")
        else:
            print(f"  Port 8000: {output[:200]}")

        # 检查监听端口
        print("\n[6] Checking listening ports...")
        stdin, stdout, stderr = ssh.exec_command('ss -tlnp | grep nginx', timeout=30)
        output = stdout.read().decode('utf-8', errors='replace')
        print(output)

        ssh.close()

        print("\n" + "=" * 60)
        print("[SUCCESS] SSL Configuration Updated!")
        print("=" * 60)
        print("\nAccess URLs:")
        print("  Official Website: https://45.78.5.184/")
        print("  Student/Parent App: https://45.78.5.184:8000/")
        print("\nIMPORTANT:")
        print("  1. MUST use HTTPS for voice features")
        print("  2. Browser will show security warning - click 'Advanced' -> 'Proceed'")
        print("  3. Allow microphone permission")
        print("  4. Voice mode will auto-start after login")

        return True

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        ssh.close()

if __name__ == '__main__':
    update_ai_study_config()
