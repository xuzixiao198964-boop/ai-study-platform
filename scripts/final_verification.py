import requests
import time

SERVER = "https://45.78.5.184"

def final_verification():
    """最终验证测试"""
    print("=" * 60)
    print("Final Verification Test")
    print("=" * 60)

    # 1. 测试HTTPS官网
    print("\n[1] Testing HTTPS website...")
    try:
        response = requests.get(f"{SERVER}/", verify=False, timeout=10)
        if response.status_code == 200:
            print(f"  [OK] HTTPS website accessible")
        else:
            print(f"  [FAIL] Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

    # 2. 测试HTTPS应用端
    print("\n[2] Testing HTTPS app (port 8000)...")
    try:
        response = requests.get(f"{SERVER}:8000/", verify=False, timeout=10)
        if response.status_code == 200 and 'DOCTYPE html' in response.text:
            print(f"  [OK] HTTPS app accessible")
        else:
            print(f"  [FAIL] Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

    # 3. 测试登录API
    print("\n[3] Testing login API...")
    try:
        response = requests.post(
            f"{SERVER}:8000/api/v1/auth/login",
            json={
                "username": "student1",
                "password": "password123",
                "device_type": "student_ipad"
            },
            verify=False,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"  [OK] Login successful")
            print(f"  User: {data.get('username')} ({data.get('nickname')})")
        else:
            print(f"  [FAIL] Login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

    # 4. 测试注册API
    print("\n[4] Testing registration API...")
    test_username = f"testuser_{int(time.time())}"
    try:
        response = requests.post(
            f"{SERVER}:8000/api/v1/auth/register",
            json={
                "username": test_username,
                "password": "test123456",
                "nickname": "Test User"
            },
            verify=False,
            timeout=10
        )
        if response.status_code == 200:
            print(f"  [OK] Registration successful")
        else:
            print(f"  [FAIL] Registration failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

    print("\n" + "=" * 60)
    print("[SUCCESS] All tests passed!")
    print("=" * 60)
    print("\nDeployment Complete!")
    print("\nAccess URLs:")
    print("  Official Website: https://45.78.5.184/")
    print("  Student/Parent App: https://45.78.5.184:8000/")
    print("\nTest Accounts:")
    print("  Student: student1 / password123")
    print("  Parent: parent1 / password123")
    print("\nKey Features:")
    print("  1. Auto-start voice mode on entry")
    print("  2. 1.5s silence auto-send")
    print("  3. AI concise replies (1-3 sentences)")
    print("  4. TTS voice output")
    print("\nIMPORTANT Notes:")
    print("  - MUST use HTTPS: https://45.78.5.184:8000/")
    print("  - Browser will show security warning (self-signed cert)")
    print("  - Click 'Advanced' -> 'Proceed to 45.78.5.184'")
    print("  - Allow microphone permission when prompted")
    print("  - Voice mode will auto-start after login")

    return True

if __name__ == '__main__':
    # 禁用SSL警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    success = final_verification()
    exit(0 if success else 1)
