import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SERVER = "45.78.5.184"
PORT = 22
USERNAME = "root"
PASSWORD = "FYCZWP2uPLjR"

def check_current_code():
    """检查服务器上当前的代码"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(SERVER, PORT, USERNAME, PASSWORD, timeout=30)

        print("=== 检查问题1: TTS声音选择 ===")
        stdin, stdout, stderr = ssh.exec_command("ls -la /opt/ai-study-platform/server/app/api/endpoints/tts.py")
        print(stdout.read().decode())
        print(stderr.read().decode())

        print("\n=== 检查问题4: Service Worker ===")
        stdin, stdout, stderr = ssh.exec_command("grep -n 'Service Worker' /opt/ai-study-mobile/build/web/index.html | head -5")
        print(stdout.read().decode())

        print("\n=== 检查问题3/5/6: TTS和STT协调 ===")
        stdin, stdout, stderr = ssh.exec_command("grep -n '_tts.speaking' /opt/ai-study-mobile/build/web/index.html | head -5")
        print(stdout.read().decode())

        print("\n=== 检查前端源文件 ===")
        stdin, stdout, stderr = ssh.exec_command("grep -n 'Service Worker' /opt/ai-study-mobile/web/index.html | head -5")
        print(stdout.read().decode())

        print("\n=== 检查构建时间 ===")
        stdin, stdout, stderr = ssh.exec_command("stat /opt/ai-study-mobile/build/web/index.html | grep Modify")
        print(stdout.read().decode())

    except Exception as e:
        print(f"错误: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    check_current_code()
