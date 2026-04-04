import requests
import json

SERVER = "http://45.78.5.184"
APP_SERVER = "http://45.78.5.184:8000"

def test_all():
    """测试所有功能"""
    print("=" * 60)
    print("AI Study Platform - Full Deployment Test")
    print("=" * 60)

    # 1. 测试官网
    print("\n[1] Testing Official Website (Port 80)...")
    try:
        response = requests.get(f"{SERVER}/", timeout=10)
        if response.status_code == 200 and "学习指认AI" in response.text:
            print("  [OK] Homepage loaded successfully")
        else:
            print(f"  [FAIL] Homepage status: {response.status_code}")
    except Exception as e:
        print(f"  [ERROR] {e}")

    # 2. 测试API开发者中心
    print("\n[2] Testing API Developer Portal...")
    try:
        response = requests.get(f"{SERVER}/api-portal", timeout=10)
        if response.status_code == 200 and "API开发者中心" in response.text:
            print("  [OK] API Portal loaded successfully")
        else:
            print(f"  [FAIL] API Portal status: {response.status_code}")
    except Exception as e:
        print(f"  [ERROR] {e}")

    # 3. 测试管理后台
    print("\n[3] Testing Admin Panel...")
    try:
        response = requests.get(f"{SERVER}/admin", timeout=10)
        if response.status_code == 200:
            print("  [OK] Admin panel loaded successfully")
        else:
            print(f"  [FAIL] Admin panel status: {response.status_code}")
    except Exception as e:
        print(f"  [ERROR] {e}")

    # 4. 测试后端API健康检查
    print("\n[4] Testing Backend API Health...")
    try:
        response = requests.get(f"{SERVER}/api/v1/health", timeout=10)
        if response.status_code == 200:
            print(f"  [OK] Backend API health: {response.json()}")
        else:
            print(f"  [FAIL] Backend API status: {response.status_code}")
    except Exception as e:
        print(f"  [ERROR] {e}")

    # 5. 测试开发者注册API
    print("\n[5] Testing Developer Registration API...")
    try:
        test_email = f"test_{int(requests.get('http://worldtimeapi.org/api/timezone/Etc/UTC').json()['unixtime'])}@example.com"
        response = requests.post(
            f"{SERVER}/api/v1/developer/register",
            json={
                "company": "Test Company",
                "name": "Test User",
                "email": test_email,
                "password": "testpass123",
                "use_case": "Testing API"
            },
            timeout=10
        )
        if response.status_code == 200:
            print(f"  [OK] Developer registration successful")
            print(f"  Email: {test_email}")
        else:
            print(f"  [FAIL] Registration status: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"  [ERROR] {e}")

    # 6. 测试开发者登录API
    print("\n[6] Testing Developer Login API...")
    try:
        response = requests.post(
            f"{SERVER}/api/v1/developer/login",
            json={
                "email": test_email,
                "password": "testpass123"
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print(f"  [OK] Developer login successful")
            print(f"  Token: {token[:20]}...")
        else:
            print(f"  [FAIL] Login status: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"  [ERROR] {e}")

    # 7. 测试管理员登录
    print("\n[7] Testing Admin Login...")
    try:
        response = requests.post(
            f"{SERVER}/api/v1/admin/login",
            json={
                "username": "wsxzx",
                "password": "Xuzi-xiao198964"
            },
            timeout=10
        )
        if response.status_code == 200:
            print(f"  [OK] Admin login successful")
        else:
            print(f"  [FAIL] Admin login status: {response.status_code}")
    except Exception as e:
        print(f"  [ERROR] {e}")

    # 8. 测试学生端应用
    print("\n[8] Testing Student App (Port 8000)...")
    try:
        response = requests.get(f"{APP_SERVER}/", timeout=10)
        if response.status_code == 200:
            print("  [OK] Student app loaded successfully")
        else:
            print(f"  [FAIL] Student app status: {response.status_code}")
    except Exception as e:
        print(f"  [ERROR] {e}")

    # 9. 测试学生登录
    print("\n[9] Testing Student Login...")
    try:
        response = requests.post(
            f"{APP_SERVER}/api/v1/auth/login",
            json={
                "username": "student1",
                "password": "password123"
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"  [OK] Student login successful")
            print(f"  User: {data.get('user', {}).get('nickname', 'N/A')}")
        else:
            print(f"  [FAIL] Student login status: {response.status_code}")
    except Exception as e:
        print(f"  [ERROR] {e}")

    # 10. 测试家长登录
    print("\n[10] Testing Parent Login...")
    try:
        response = requests.post(
            f"{APP_SERVER}/api/v1/auth/login",
            json={
                "username": "parent1",
                "password": "password123"
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"  [OK] Parent login successful")
            print(f"  User: {data.get('user', {}).get('nickname', 'N/A')}")
        else:
            print(f"  [FAIL] Parent login status: {response.status_code}")
    except Exception as e:
        print(f"  [ERROR] {e}")

    # 总结
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print("\nAccess URLs:")
    print(f"  Official Website:    {SERVER}/")
    print(f"  API Developer Portal: {SERVER}/api-portal")
    print(f"  Admin Panel:         {SERVER}/admin")
    print(f"  Student/Parent App:  {APP_SERVER}/")
    print("\nAdmin Credentials:")
    print("  Username: wsxzx")
    print("  Password: Xuzi-xiao198964")
    print("\nTest Accounts:")
    print("  Student: student1 / password123")
    print("  Parent:  parent1 / password123")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_all()
