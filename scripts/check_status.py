import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SERVER = "45.78.5.184"
PORT = 22
USERNAME = "root"
PASSWORD = "FYCZWP2uPLjR"

def check_and_fix():
    """检查并修复部署"""
    print("=" * 50)
    print("  检查部署状态")
    print("=" * 50)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(SERVER, PORT, USERNAME, PASSWORD, timeout=30)

        # 检查后端目录
        print("\n[1] 检查后端目录...")
        stdin, stdout, stderr = ssh.exec_command("ls -la /opt/ai-study-platform/")
        print(stdout.read().decode())

        # 检查是否是git仓库
        print("\n[2] 检查git状态...")
        stdin, stdout, stderr = ssh.exec_command("cd /opt/ai-study-platform && git status")
        output = stdout.read().decode()
        error = stderr.read().decode()
        if error:
            print(f"错误: {error}")
        else:
            print(output)

        # 检查当前提交
        print("\n[3] 检查当前提交...")
        stdin, stdout, stderr = ssh.exec_command("cd /opt/ai-study-platform && git log --oneline -3")
        print(stdout.read().decode())

        # 检查TTS文件是否存在
        print("\n[4] 检查TTS文件...")
        stdin, stdout, stderr = ssh.exec_command("ls -la /opt/ai-study-platform/server/app/api/endpoints/tts.py")
        output = stdout.read().decode()
        error = stderr.read().decode()
        if error:
            print(f"TTS文件不存在: {error}")
        else:
            print(output)

        # 检查前端目录
        print("\n[5] 检查前端目录...")
        stdin, stdout, stderr = ssh.exec_command("ls -la /opt/ai-study-mobile/")
        print(stdout.read().decode())

        # 检查前端git状态
        print("\n[6] 检查前端git状态...")
        stdin, stdout, stderr = ssh.exec_command("cd /opt/ai-study-mobile && git status")
        output = stdout.read().decode()
        error = stderr.read().decode()
        if error:
            print(f"错误: {error}")
        else:
            print(output)

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    check_and_fix()
