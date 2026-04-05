#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查服务器配置"""
import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

SERVER_HOST = "45.78.5.184"
SERVER_PORT = 22
SERVER_USER = "root"
SERVER_PASSWORD = "FYCZWP2uPLjR"
PROJECT_PATH = "/opt/ai-study-platform"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(hostname=SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
    print("[OK] SSH连接成功\n")

    # 检查.env文件
    cmd = f"cd {PROJECT_PATH} && grep -E '(ADMIN_USER|ADMIN_PASSWORD)' .env"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read().decode('utf-8')
    print("服务器.env配置:")
    print(output)

    # 测试管理员登录
    print("\n测试管理员登录:")
    test_cmd = f"""
cd {PROJECT_PATH} && \
source venv/bin/activate && \
python3 << 'PYEOF'
import asyncio
import httpx

async def test_login():
    async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
        # 测试不同的密码
        passwords = ['admin123', 'wsxzx123', '']
        for pwd in passwords:
            try:
                r = await client.post(
                    'https://localhost:8000/api/v1/admin/login',
                    json={{'username': 'wsxzx', 'password': pwd}}
                )
                print(f"密码 '{pwd}': 状态码 {{r.status_code}}")
                if r.status_code == 200:
                    print(f"  成功! Token: {{r.json().get('access_token', '')[:20]}}...")
                else:
                    print(f"  失败: {{r.text[:100]}}")
            except Exception as e:
                print(f"密码 '{pwd}': 错误 {{e}}")

asyncio.run(test_login())
PYEOF
"""
    stdin, stdout, stderr = ssh.exec_command(test_cmd)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    print(output)
    if error:
        print("错误:", error)

except Exception as e:
    print(f"[ERROR] {e}")
    sys.exit(1)
finally:
    ssh.close()
