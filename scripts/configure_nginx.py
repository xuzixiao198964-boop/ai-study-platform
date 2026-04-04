import paramiko

SERVER = {
    'hostname': '45.78.5.184',
    'port': 22,
    'username': 'root',
    'password': 'wMOByjYmDKsp'
}

NGINX_CONFIG = """
# 官网 - 80端口
server {
    listen 80;
    server_name _;

    # 官网根目录
    location / {
        root /opt/ai-study-website;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # API开发者中心
    location /api-portal {
        root /opt/ai-study-website;
        try_files /api-portal.html =404;
    }

    # 管理后台
    location /admin {
        root /opt/ai-study-website;
        try_files /admin.html =404;
    }

    # 后端API代理
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

    # 管理后台API代理
    location /admin/api/ {
        rewrite ^/admin/api/(.*) /api/v1/admin/$1 break;
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

# 应用端 - 8000端口
server {
    listen 8000;
    server_name _;

    # Flutter Web应用
    location / {
        root /opt/ai-study-mobile/build/web;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
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

    # WebSocket支持
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
"""

def configure_nginx():
    """配置Nginx"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("Connecting to server...")
        ssh.connect(**SERVER)

        # 备份现有配置
        print("\nBacking up existing nginx config...")
        ssh.exec_command('cp /etc/nginx/sites-available/ai-study /etc/nginx/sites-available/ai-study.bak')

        # 写入新配置
        print("\nWriting new nginx config...")
        sftp = ssh.open_sftp()
        with sftp.file('/etc/nginx/sites-available/ai-study', 'w') as f:
            f.write(NGINX_CONFIG)
        sftp.close()

        # 测试配置
        print("\nTesting nginx config...")
        stdin, stdout, stderr = ssh.exec_command('nginx -t')
        output = stdout.read().decode('utf-8', errors='replace')
        error = stderr.read().decode('utf-8', errors='replace')
        print(output + error)

        # 重启Nginx
        print("\nRestarting nginx...")
        stdin, stdout, stderr = ssh.exec_command('systemctl restart nginx')
        stdout.channel.recv_exit_status()

        # 检查Nginx状态
        print("\nChecking nginx status...")
        stdin, stdout, stderr = ssh.exec_command('systemctl status nginx --no-pager')
        output = stdout.read().decode('utf-8', errors='replace')
        print(output)

        print("\n[OK] Nginx configured successfully!")

    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        ssh.close()

if __name__ == '__main__':
    configure_nginx()
