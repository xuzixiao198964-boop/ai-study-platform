#!/usr/bin/env python3
"""
全新服务器部署脚本
服务器: 45.78.5.184
"""
import paramiko
import os
import sys
from datetime import datetime

# 服务器配置
HOST = "45.78.5.184"
PORT = 22
USERNAME = "root"
PASSWORD = "wMOByjYmDKsp"

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def exec_cmd(client, cmd, description=""):
    if description:
        log(description)
    stdin, stdout, stderr = client.exec_command(cmd, get_pty=True)
    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    exit_code = stdout.channel.recv_exit_status()

    if exit_code != 0 and error:
        log(f"Warning: {error}")

    return output, error, exit_code

def main():
    log("Starting fresh server deployment...")

    try:
        # 连接服务器
        log("Connecting to server...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOST, PORT, USERNAME, PASSWORD, timeout=30)
        log("Connected successfully!")

        # 1. 安装系统依赖
        log("\n=== Step 1: Installing system dependencies ===")
        exec_cmd(client, """
            apt-get update && \
            apt-get install -y python3 python3-pip python3-venv git nginx curl wget unzip xz-utils
        """, "Installing Python, Nginx, Git...")

        # 2. 安装Flutter
        log("\n=== Step 2: Installing Flutter SDK ===")
        exec_cmd(client, """
            cd /opt && \
            wget -q https://storage.flutter-io.cn/flutter_infra_release/releases/stable/linux/flutter_linux_3.24.5-stable.tar.xz && \
            tar xf flutter_linux_3.24.5-stable.tar.xz && \
            rm flutter_linux_3.24.5-stable.tar.xz && \
            export PATH=/opt/flutter/bin:$PATH && \
            flutter --version
        """, "Downloading and installing Flutter...")

        # 3. 配置Flutter
        exec_cmd(client, """
            export PATH=/opt/flutter/bin:$PATH && \
            export PUB_HOSTED_URL=https://pub.flutter-io.cn && \
            export FLUTTER_STORAGE_BASE_URL=https://storage.flutter-io.cn && \
            flutter config --no-analytics && \
            flutter doctor
        """, "Configuring Flutter...")

        # 4. 创建项目目录
        log("\n=== Step 3: Creating project directories ===")
        exec_cmd(client, """
            mkdir -p /opt/ai-study-platform && \
            mkdir -p /opt/ai-study-mobile && \
            mkdir -p /var/log/ai-study
        """, "Creating directories...")

        log("\nServer preparation completed!")
        log("Next: Upload project files")

        client.close()

    except Exception as e:
        log(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
