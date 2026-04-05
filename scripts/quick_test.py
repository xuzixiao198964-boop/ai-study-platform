#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速测试脚本 - 只运行单元测试和集成测试"""
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

    # 运行单元测试
    print("="*60)
    print("运行单元测试")
    print("="*60)

    test_cmd = f"""
cd {PROJECT_PATH} && \
source venv/bin/activate && \
export DATABASE_URL='sqlite+aiosqlite:///:memory:' && \
export REDIS_URL='redis://localhost:6379/1' && \
python -m pytest tests/ -v -m "not integration" --tb=short 2>&1
"""
    stdin, stdout, stderr = ssh.exec_command(test_cmd)
    output = stdout.read().decode('utf-8')
    print(output)
    exit_code = stdout.channel.recv_exit_status()

    if exit_code == 0:
        print("\n[PASS] 单元测试通过")
    else:
        print(f"\n[FAIL] 单元测试失败 (退出码: {exit_code})")

    # 运行集成测试
    print("\n" + "="*60)
    print("运行集成测试")
    print("="*60)

    integration_cmd = f"""
cd {PROJECT_PATH} && \
source venv/bin/activate && \
export INTEGRATION_BASE_URL='https://localhost:8000' && \
export INTEGRATION_ADMIN_USER='wsxzx' && \
export INTEGRATION_ADMIN_PASSWORD='Xuzi-xiao198964' && \
python -m pytest tests/test_integration_remote.py -v -m integration --tb=short 2>&1
"""
    stdin, stdout, stderr = ssh.exec_command(integration_cmd)
    output = stdout.read().decode('utf-8')
    print(output)
    exit_code = stdout.channel.recv_exit_status()

    if exit_code == 0:
        print("\n[PASS] 集成测试通过")
    else:
        print(f"\n[FAIL] 集成测试失败 (退出码: {exit_code})")

except Exception as e:
    print(f"[ERROR] {e}")
    sys.exit(1)
finally:
    ssh.close()
