import paramiko
import time

SERVER = '45.78.5.184'
USER = 'root'
PASSWORD = 'wMOByjYmDKsp'

def deploy_and_test():
    """部署并测试所有功能"""
    print("=" * 60)
    print("Final Deployment and Testing")
    print("=" * 60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("\n[1] Connecting to server...")
        ssh.connect(SERVER, username=USER, password=PASSWORD, timeout=30)

        # 上传app_config.dart（已经是正确的配置）
        print("\n[2] Uploading app_config.dart...")
        sftp = ssh.open_sftp()
        local_file = 'D:/work/ai-study-platform/mobile/lib/config/app_config.dart'
        remote_file = '/opt/ai-study-mobile/lib/config/app_config.dart'
        sftp.put(local_file, remote_file)
        print(f"  Uploaded: {remote_file}")
        sftp.close()

        # 构建Flutter Web
        print("\n[3] Building Flutter Web...")
        stdin, stdout, stderr = ssh.exec_command(
            'cd /opt/ai-study-mobile && export PATH=/opt/flutter/bin:$PATH && flutter build web --release',
            timeout=600
        )
        exit_status = stdout.channel.recv_exit_status()

        if exit_status == 0:
            print("  [OK] Flutter Web build successful!")
        else:
            error = stderr.read().decode('utf-8', errors='replace')
            print(f"  [ERROR] Build failed: {error}")
            return False

        # 验证部署
        print("\n[4] Verifying deployment...")

        # 检查HTTP
        stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1/ | head -5', timeout=30)
        output = stdout.read().decode('utf-8', errors='replace')
        if 'DOCTYPE html' in output:
            print("  [OK] HTTP website accessible")
        else:
            print("  [FAIL] HTTP website not accessible")

        # 检查HTTPS应用
        stdin, stdout, stderr = ssh.exec_command('curl -k -s https://127.0.0.1:8000/ | head -5', timeout=30)
        output = stdout.read().decode('utf-8', errors='replace')
        if 'DOCTYPE html' in output:
            print("  [OK] HTTPS app accessible")
        else:
            print("  [FAIL] HTTPS app not accessible")

        # 检查后端
        stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1:8001/health', timeout=30)
        output = stdout.read().decode('utf-8', errors='replace')
        if 'ok' in output:
            print("  [OK] Backend API healthy")
        else:
            print("  [FAIL] Backend API not healthy")

        ssh.close()

        print("\n" + "=" * 60)
        print("[SUCCESS] Deployment completed!")
        print("=" * 60)
        print("\nAccess URLs:")
        print("  Official Website: http://45.78.5.184/ or https://45.78.5.184/")
        print("  Student/Parent App: https://45.78.5.184:8000/ (MUST use HTTPS for voice)")
        print("\nIMPORTANT:")
        print("  1. MUST access via HTTPS: https://45.78.5.184:8000/")
        print("  2. Browser will show security warning - click 'Advanced' -> 'Proceed'")
        print("  3. Allow microphone permission when prompted")
        print("  4. Voice mode will auto-start after login")
        print("\nTest Accounts:")
        print("  Student: student1 / password123")
        print("  Parent: parent1 / password123")
        print("\nFeatures:")
        print("  - Auto-start voice mode on entry")
        print("  - 1.5s silence auto-send")
        print("  - AI concise replies (1-3 sentences)")
        print("  - TTS voice output")

        return True

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        ssh.close()

if __name__ == '__main__':
    success = deploy_and_test()
    exit(0 if success else 1)
