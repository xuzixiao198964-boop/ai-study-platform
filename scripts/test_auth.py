import requests
import time

SERVER = "http://45.78.5.184"

def test_auth():
    """测试认证功能"""
    print("=" * 60)
    print("Testing Authentication")
    print("=" * 60)

    # 1. 测试已有账号登录
    print("\n[1] Testing existing account login...")
    print("Trying: student1 / password123")
    try:
        response = requests.post(
            f"{SERVER}/api/v1/auth/login",
            json={
                "username": "student1",
                "password": "password123"
            },
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

    # 2. 测试新账号注册
    print("\n[2] Testing new account registration...")
    test_username = f"testuser_{int(time.time())}"
    print(f"Trying to register: {test_username}")
    try:
        response = requests.post(
            f"{SERVER}/api/v1/auth/register",
            json={
                "username": test_username,
                "password": "test123456",
                "nickname": "Test User"
            },
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            # 尝试用新账号登录
            print(f"\n[3] Testing login with new account: {test_username}")
            response = requests.post(
                f"{SERVER}/api/v1/auth/login",
                json={
                    "username": test_username,
                    "password": "test123456"
                },
                timeout=10
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

    # 3. 检查数据库中的用户
    print("\n[4] Checking database users...")
    import paramiko
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect('45.78.5.184', username='root', password='wMOByjYmDKsp', timeout=30)
        stdin, stdout, stderr = ssh.exec_command(
            'psql -U postgres -d ai_study -c "SELECT id, username, nickname, is_active FROM users LIMIT 10;"'
        )
        output = stdout.read().decode('utf-8', errors='replace')
        print(output)
        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_auth()
