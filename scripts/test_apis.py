#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""完整的API端点测试"""
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
    print("测试API端点")
    print("="*60)

    # API测试脚本
    test_cmd = f"""
cd {PROJECT_PATH} && \
source venv/bin/activate && \
python3 << 'PYEOF'
import asyncio
import httpx

async def test_apis():
    async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
        tests = [
            ("健康检查 (8001)", "GET", "http://localhost:8001/health", None),
            ("API文档", "GET", "https://localhost:8000/docs", None),
            ("OpenAPI", "GET", "https://localhost:8000/openapi.json", None),
            ("省份列表", "GET", "https://localhost:8000/api/v1/regions/provinces", None),
            ("注册接口", "POST", "https://localhost:8000/api/v1/auth/register",
             {{"username": "test_user_" + str(asyncio.get_event_loop().time()), "password": "Test123456"}}),
        ]

        for name, method, url, data in tests:
            try:
                if method == "GET":
                    r = await client.get(url)
                else:
                    r = await client.post(url, json=data)

                status = "✓" if r.status_code < 400 else "✗"
                print(f"{{status}} {{name}}: {{r.status_code}}")

                if r.status_code >= 400:
                    print(f"  响应: {{r.text[:100]}}")
            except Exception as e:
                print(f"✗ {{name}}: 错误 - {{str(e)[:100]}}")

asyncio.run(test_apis())
PYEOF
"""
    stdin, stdout, stderr = ssh.exec_command(test_cmd)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    print(output)
    if error:
        print("错误:", error[:500])

    print("\n" + "="*60)
    print("检查服务状态")
    print("="*60)

    status_cmd = """
systemctl is-active ai-study && echo "[OK] 后端服务运行中" || echo "[ERROR] 后端服务未运行"
systemctl is-active nginx && echo "[OK] Nginx运行中" || echo "[ERROR] Nginx未运行"
systemctl is-active postgresql && echo "[OK] PostgreSQL运行中" || echo "[ERROR] PostgreSQL未运行"
"""
    stdin, stdout, stderr = ssh.exec_command(status_cmd)
    print(stdout.read().decode('utf-8'))

except Exception as e:
    print(f"[ERROR] {e}")
    sys.exit(1)
finally:
    ssh.close()
