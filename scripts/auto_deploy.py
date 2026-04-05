import paramiko
import time
import sys
import io

# 设置UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 服务器配置
SERVER = "45.78.5.184"
PORT = 22
USERNAME = "root"
PASSWORD = "FYCZWP2uPLjR"

def execute_command(ssh, command, description):
    """执行命令并打印输出"""
    print(f"\n{description}...")
    stdin, stdout, stderr = ssh.exec_command(command)

    # 等待命令执行完成
    exit_status = stdout.channel.recv_exit_status()

    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')

    if output:
        print(output)
    if error and exit_status != 0:
        print(f"错误: {error}")

    return exit_status == 0

def deploy():
    """部署到服务器"""
    print("=" * 50)
    print("  开始部署到服务器")
    print("=" * 50)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # 连接服务器
        print(f"\n[1/5] 连接服务器 {SERVER}...")
        ssh.connect(SERVER, PORT, USERNAME, PASSWORD, timeout=30)
        print("✓ 连接成功")

        # 更新后端代码
        success = execute_command(
            ssh,
            "cd /opt/ai-study-platform && git pull",
            "[2/5] 更新后端代码"
        )
        if success:
            print("✓ 后端代码已更新")

        # 重启后端服务
        success = execute_command(
            ssh,
            "systemctl restart ai-study && sleep 3 && systemctl status ai-study --no-pager | head -15",
            "[3/5] 重启后端服务"
        )
        if success:
            print("✓ 后端服务已重启")

        # 构建前端
        print("\n[4/5] 构建Flutter Web（需要2-3分钟）...")
        stdin, stdout, stderr = ssh.exec_command(
            "cd /opt/ai-study-mobile && /opt/flutter/bin/flutter build web --release",
            timeout=300
        )

        # 实时输出构建进度
        while True:
            line = stdout.readline()
            if not line:
                break
            print(line.strip())

        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("✓ 前端构建成功")
        else:
            error = stderr.read().decode('utf-8', errors='ignore')
            print(f"❌ 前端构建失败: {error}")
            return False

        # 重启Nginx
        success = execute_command(
            ssh,
            "systemctl restart nginx && systemctl status nginx --no-pager | head -10",
            "[5/5] 重启Nginx"
        )
        if success:
            print("✓ Nginx已重启")

        print("\n" + "=" * 50)
        print("  部署完成！")
        print("=" * 50)
        print(f"\n访问地址: https://{SERVER}:8000")
        print("\n修复内容:")
        print("  ✓ Service Worker SSL错误")
        print("  ✓ iPad TTS播放")
        print("  ✓ Windows公放回声")
        print("  ✓ 持续对话功能")
        print("  ✓ 弹窗居中显示")
        print("  ✓ 腾讯云TTS声音选择（18种音色）")

        return True

    except Exception as e:
        print(f"\n❌ 部署失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy()
