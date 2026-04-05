#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""诊断前端问题"""
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

    print("="*60)
    print("1. 检查.env配置")
    print("="*60)

    cmd = f"cd {PROJECT_PATH} && cat .env"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode('utf-8'))

    print("\n" + "="*60)
    print("2. 测试初始化设置API")
    print("="*60)

    test_cmd = f"""
cd {PROJECT_PATH} && \
source venv/bin/activate && \
python3 << 'PYEOF'
import asyncio
import httpx
import time

async def test_init():
    async with httpx.AsyncClient(timeout=60.0, verify=False) as client:
        # 先注册
        username = f"test_user_{{int(time.time())}}"
        print(f"注册用户: {{username}}")

        r = await client.post(
            'https://localhost:8000/api/v1/auth/register',
            json={{'username': username, 'password': 'Test123456'}}
        )
        print(f"注册状态: {{r.status_code}}")

        if r.status_code == 200:
            token = r.json().get('access_token')
            print(f"Token: {{token[:20]}}...")

            # 测试初始化设置
            print("\\n测试初始化设置...")
            start = time.time()

            r2 = await client.post(
                'https://localhost:8000/api/v1/init/setup',
                headers={{'Authorization': f'Bearer {{token}}'}},
                json={{
                    'grade': '小学三年级',
                    'province': '北京市',
                    'city': '北京市',
                    'district': '海淀区',
                    'ai_name': '小助手'
                }}
            )

            elapsed = time.time() - start
            print(f"初始化状态: {{r2.status_code}}")
            print(f"响应时间: {{elapsed:.2f}}秒")
            print(f"响应内容: {{r2.text[:200]}}")

asyncio.run(test_init())
PYEOF
"""
    stdin, stdout, stderr = ssh.exec_command(test_cmd)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    print(output)
    if error:
        print("错误:", error[:500])

    print("\n" + "="*60)
    print("3. 检查后端日志")
    print("="*60)

    cmd = "journalctl -u ai-study --no-pager -n 50 | tail -20"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode('utf-8'))

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    ssh.close()
