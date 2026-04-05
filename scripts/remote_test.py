#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
远程服务器测试脚本
连接到服务器并执行完整的单元测试和集成测试
"""
import paramiko
import sys
import time
import io
from pathlib import Path

# 设置标准输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 服务器配置
SERVER_HOST = "45.78.5.184"
SERVER_PORT = 22
SERVER_USER = "root"
SERVER_PASSWORD = "FYCZWP2uPLjR"
PROJECT_PATH = "/opt/ai-study-platform"
SERVER_PATH = PROJECT_PATH  # 服务器上server代码在根目录

def execute_command(ssh, command, description=""):
    """执行SSH命令并返回结果"""
    if description:
        print(f"\n{'='*60}")
        print(f"执行: {description}")
        print(f"命令: {command}")
        print(f"{'='*60}")

    stdin, stdout, stderr = ssh.exec_command(command)
    exit_code = stdout.channel.recv_exit_status()

    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')

    if output:
        print(output)
    if error:
        print(f"错误输出:\n{error}", file=sys.stderr)

    return exit_code, output, error

def main():
    print(f"连接到服务器 {SERVER_HOST}...")

    # 创建SSH客户端
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # 连接服务器
        ssh.connect(
            hostname=SERVER_HOST,
            port=SERVER_PORT,
            username=SERVER_USER,
            password=SERVER_PASSWORD,
            timeout=30
        )
        print("[OK] SSH连接成功")

        # 1. 检查项目目录
        exit_code, output, error = execute_command(
            ssh,
            f"cd {PROJECT_PATH} && pwd && ls -la",
            "检查项目目录"
        )
        if exit_code != 0:
            print(f"[ERROR] 项目目录不存在或无法访问")
            return 1

        # 2. 检查服务状态
        execute_command(
            ssh,
            "systemctl status ai-study --no-pager || echo 'Service not found'",
            "检查后端服务状态"
        )

        execute_command(
            ssh,
            "systemctl status nginx --no-pager",
            "检查Nginx状态"
        )

        # 3. 检查端口监听
        execute_command(
            ssh,
            "netstat -tlnp | grep -E ':(80|8000|8001|5432|6379)' || ss -tlnp | grep -E ':(80|8000|8001|5432|6379)'",
            "检查端口监听状态"
        )

        # 4. 检查Python环境
        exit_code, output, error = execute_command(
            ssh,
            f"cd {SERVER_PATH} && python3 --version && which python3",
            "检查Python版本"
        )

        # 5. 检查虚拟环境
        execute_command(
            ssh,
            f"cd {SERVER_PATH} && ls -la venv/ 2>/dev/null || echo 'No venv found'",
            "检查虚拟环境"
        )

        # 6. 安装测试依赖
        print("\n" + "="*60)
        print("安装测试依赖...")
        print("="*60)

        commands = [
            f"cd {SERVER_PATH}",
            "[ -d venv ] || python3 -m venv venv",
            "source venv/bin/activate",
            "pip install -q pytest pytest-asyncio pytest-cov httpx 2>&1 | tail -3",
            "pip install -q -r requirements.txt 2>&1 | tail -3"
        ]

        exit_code, output, error = execute_command(
            ssh,
            " && ".join(commands),
            "安装依赖"
        )

        # 7. 运行单元测试（非集成测试）
        print("\n" + "="*60)
        print("运行单元测试（排除集成测试）")
        print("="*60)

        test_command = f"""
cd {SERVER_PATH} && \
source venv/bin/activate && \
export DATABASE_URL='sqlite+aiosqlite:///:memory:' && \
export REDIS_URL='redis://localhost:6379/1' && \
python -m pytest tests/ -v -m "not integration" --tb=short --maxfail=3 2>&1
"""

        exit_code, output, error = execute_command(
            ssh,
            test_command,
            "单元测试"
        )

        if exit_code != 0:
            print(f"\n[FAIL] 单元测试失败 (退出码: {exit_code})")
        else:
            print(f"\n[PASS] 单元测试通过")

        # 8. 运行集成测试
        print("\n" + "="*60)
        print("运行集成测试")
        print("="*60)

        integration_command = f"""
cd {SERVER_PATH} && \
source venv/bin/activate && \
export INTEGRATION_BASE_URL='https://localhost:8000' && \
export INTEGRATION_ADMIN_USER='wsxzx' && \
export INTEGRATION_ADMIN_PASSWORD='$(grep ADMIN_PASSWORD .env | cut -d= -f2)' && \
python -m pytest tests/test_integration_remote.py -v -m integration --tb=short 2>&1
"""

        exit_code, output, error = execute_command(
            ssh,
            integration_command,
            "集成测试"
        )

        if exit_code != 0:
            print(f"\n[FAIL] 集成测试失败 (退出码: {exit_code})")
        else:
            print(f"\n[PASS] 集成测试通过")

        # 9. 测试API健康检查
        print("\n" + "="*60)
        print("测试API端点")
        print("="*60)

        api_tests = [
            ("健康检查", "curl -s -k https://localhost:8000/health"),
            ("API文档", "curl -s -k -o /dev/null -w '%{http_code}' https://localhost:8000/docs"),
            ("OpenAPI", "curl -s -k -o /dev/null -w '%{http_code}' https://localhost:8000/openapi.json"),
            ("直接访问8001", "curl -s http://localhost:8001/health"),
        ]

        for name, cmd in api_tests:
            execute_command(ssh, cmd, f"测试 {name}")

        # 10. 检查日志
        print("\n" + "="*60)
        print("检查最近的错误日志")
        print("="*60)

        execute_command(
            ssh,
            f"tail -50 {PROJECT_PATH}/logs/*.log 2>/dev/null || echo 'No logs found'",
            "查看日志"
        )

        print("\n" + "="*60)
        print("测试完成")
        print("="*60)

    except paramiko.AuthenticationException:
        print("[ERROR] SSH认证失败，请检查用户名和密码")
        return 1
    except paramiko.SSHException as e:
        print(f"[ERROR] SSH连接错误: {e}")
        return 1
    except Exception as e:
        print(f"[ERROR] 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        ssh.close()
        print("\nSSH连接已关闭")

    return 0

if __name__ == "__main__":
    sys.exit(main())
