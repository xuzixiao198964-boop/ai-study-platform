#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""上传修复后的代码并重启服务"""
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

    sftp = ssh.open_sftp()

    # 上传文件
    files = [
        ("D:/work/ai-study-platform/server/app/api/endpoints/initialization.py",
         f"{PROJECT_PATH}/app/api/endpoints/initialization.py"),
        ("D:/work/ai-study-platform/server/app/schemas/initialization.py",
         f"{PROJECT_PATH}/app/schemas/initialization.py"),
    ]

    for local, remote in files:
        sftp.put(local, remote)
        print(f"[OK] 上传: {local.split('/')[-1]}")

    sftp.close()

    # 重启服务
    print("\n重启后端服务...")
    cmd = "systemctl restart ai-study && sleep 2 && systemctl status ai-study --no-pager | head -15"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode('utf-8'))

    # 测试修复
    print("\n" + "="*60)
    print("测试修复后的初始化API")
    print("="*60)

    test_cmd = f"""
cd {PROJECT_PATH} && \
source venv/bin/activate && \
python3 << 'PYEOF'
import asyncio
import httpx
import time

async def test():
    async with httpx.AsyncClient(timeout=60.0, verify=False) as client:
        username = f"test_{{int(time.time())}}"

        # 注册
        r = await client.post(
            'https://localhost:8000/api/v1/auth/register',
            json={{'username': username, 'password': 'Test123456'}}
        )
        print(f"注册: {{r.status_code}}")

        if r.status_code == 200:
            token = r.json().get('access_token')

            # 测试字符串格式的年级
            print("\\n测试1: 字符串年级 '小学三年级'")
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
            print(f"状态: {{r2.status_code}}, 耗时: {{elapsed:.2f}}秒")
            if r2.status_code == 200:
                print(f"成功! grade={{r2.json().get('grade')}}")
            else:
                print(f"失败: {{r2.text[:200]}}")

asyncio.run(test())
PYEOF
"""
    stdin, stdout, stderr = ssh.exec_command(test_cmd)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    print(output)
    if error:
        print("错误:", error[:500])

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    ssh.close()
