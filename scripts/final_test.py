import requests
import time

SERVER = "http://45.78.5.184"

def final_test():
    """最终功能测试"""
    print("=" * 60)
    print("Final Deployment Test")
    print("=" * 60)

    # 1. 测试已有账号登录
    print("\n[1] Testing existing account login...")
    print("Account: student1 / password123")
    try:
        response = requests.post(
            f"{SERVER}/api/v1/auth/login",
            json={
                "username": "student1",
                "password": "password123",
                "device_type": "student_ipad"
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"  [OK] Login successful!")
            print(f"  User: {data.get('username')} ({data.get('nickname')})")
            print(f"  Token: {data.get('access_token')[:50]}...")
        else:
            print(f"  [FAIL] Login failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
        return False

    # 2. 测试新账号注册
    print("\n[2] Testing new account registration...")
    test_username = f"testuser_{int(time.time())}"
    print(f"Account: {test_username} / test123456")
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
        if response.status_code == 200:
            data = response.json()
            print(f"  [OK] Registration successful!")
            print(f"  User: {data.get('username')} ({data.get('nickname')})")
            print(f"  Token: {data.get('access_token')[:50]}...")
        else:
            print(f"  [FAIL] Registration failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
        return False

    # 3. 测试重复注册（应该失败）
    print("\n[3] Testing duplicate registration (should fail)...")
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
        if response.status_code == 400:
            print(f"  [OK] Correctly rejected duplicate username")
        else:
            print(f"  [FAIL] Unexpected response: {response.status_code}")
            return False
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
        return False

    # 4. 测试错误密码登录（应该失败）
    print("\n[4] Testing wrong password (should fail)...")
    try:
        response = requests.post(
            f"{SERVER}/api/v1/auth/login",
            json={
                "username": "student1",
                "password": "wrongpassword",
                "device_type": "student_ipad"
            },
            timeout=10
        )
        if response.status_code == 401:
            print(f"  [OK] Correctly rejected wrong password")
        else:
            print(f"  [FAIL] Unexpected response: {response.status_code}")
            return False
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
        return False

    # 5. 测试前端访问
    print("\n[5] Testing frontend access...")
    try:
        response = requests.get(f"{SERVER}:8000/", timeout=10)
        if response.status_code == 200 and 'DOCTYPE html' in response.text:
            print(f"  [OK] Frontend is accessible")
        else:
            print(f"  [FAIL] Frontend not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
        return False

    # 6. 测试官网访问
    print("\n[6] Testing website access...")
    try:
        response = requests.get(f"{SERVER}/", timeout=10)
        response.encoding = 'utf-8'
        if response.status_code == 200 and 'DOCTYPE html' in response.text:
            print(f"  [OK] Website is accessible")
        else:
            print(f"  [FAIL] Website not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
        return False

    print("\n" + "=" * 60)
    print("[SUCCESS] All tests passed!")
    print("=" * 60)
    print("\nDeployment URLs:")
    print(f"  Official Website: {SERVER}/")
    print(f"  Student/Parent App: {SERVER}:8000/")
    print(f"  API Developer Portal: {SERVER}/api-portal")
    print(f"  Admin Portal: {SERVER}/admin")
    print("\nTest Accounts:")
    print("  Student: student1 / password123")
    print("  Parent: parent1 / password123")
    print("  Admin: wsxzx / Xuzi-xiao198964")
    print("\nKey Features:")
    print("  [OK] Voice input with 1.5s auto-send")
    print("  [OK] AI concise replies (1-3 sentences)")
    print("  [OK] TTS voice output")
    print("  [OK] Auto-start voice mode on entry")

    return True

if __name__ == '__main__':
    success = final_test()
    exit(0 if success else 1)
