import paramiko
import os

# 服务器配置
SERVER = "45.78.5.184"
PORT = 22
USERNAME = "root"
PASSWORD = os.getenv("SERVER_PASSWORD", "")  # 从环境变量读取密码

def deploy():
    """部署到服务器"""
    print("=== 开始部署到服务器 ===\n")

    # 创建SSH客户端
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # 连接服务器
        print(f"[1/5] 连接服务器 {SERVER}...")
        ssh.connect(SERVER, PORT, USERNAME, PASSWORD)
        print("✓ 连接成功\n")

        # 更新后端代码
        print("[2/5] 更新后端代码...")
        stdin, stdout, stderr = ssh.exec_command("cd /opt/ai-study-platform && git pull")
        print(stdout.read().decode())
        error = stderr.read().decode()
        if error and "Already up to date" not in error:
            print(f"警告: {error}")
        print("✓ 后端代码已更新\n")

        # 重启后端服务
        print("[3/5] 重启后端服务...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart ai-study && sleep 2 && systemctl status ai-study --no-pager")
        output = stdout.read().decode()
        if "active (running)" in output:
            print("✓ 后端服务运行正常\n")
        else:
            print(f"警告: {output}\n")

        # 构建前端
        print("[4/5] 构建Flutter Web...")
        stdin, stdout, stderr = ssh.exec_command("cd /opt/ai-study-mobile && /opt/flutter/bin/flutter build web --release")
        # 等待构建完成
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("✓ 前端构建成功\n")
        else:
            print(f"错误: 构建失败\n{stderr.read().decode()}\n")
            return False

        # 重启Nginx
        print("[5/5] 重启Nginx...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart nginx")
        stdout.read()
        print("✓ Nginx已重启\n")

        print("=== 部署完成 ===")
        print(f"访问地址: https://{SERVER}:8000")
        return True

    except Exception as e:
        print(f"❌ 部署失败: {e}")
        return False
    finally:
        ssh.close()

if __name__ == "__main__":
    # 提示输入密码
    if not os.getenv("SERVER_PASSWORD"):
        import getpass
        password = getpass.getpass("请输入服务器密码: ")
        os.environ["SERVER_PASSWORD"] = password

    deploy()
