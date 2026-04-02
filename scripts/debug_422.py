"""Debug: test APIs from outside + check server logs."""
import paramiko
import httpx
import json

SERVER = "101.201.244.150"

# 1. Test regions API from outside (like a browser would)
print("=== 1. Test regions API from outside ===")
try:
    r = httpx.get(f"http://{SERVER}:8000/api/v1/regions/provinces", timeout=10)
    print(f"  GET /regions/provinces: HTTP {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"  Got {len(data)} provinces, first 3: {data[:3]}")
    else:
        print(f"  Body: {r.text[:300]}")
except Exception as e:
    print(f"  ERROR: {e}")

# 2. Test what 422 looks like when sending old format
print("\n=== 2. Simulate OLD frontend request (with region field) ===")
try:
    # First register+login to get a token
    r = httpx.post(f"http://{SERVER}:8000/api/v1/auth/register", json={
        "username": f"debug_test_422",
        "password": "testpass123",
    }, timeout=10)
    if r.status_code == 200:
        token = r.json()["access_token"]
    else:
        # user exists, try login
        r = httpx.post(f"http://{SERVER}:8000/api/v1/auth/login", json={
            "username": "debug_test_422",
            "password": "testpass123",
            "device_type": "student_ipad",
        }, timeout=10)
        token = r.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # OLD format (region string)
    r = httpx.post(f"http://{SERVER}:8000/api/v1/init/setup",
        headers=headers,
        json={"grade": 3, "region": "北京市海淀区", "ai_name": "小智"},
        timeout=10,
    )
    print(f"  OLD format -> HTTP {r.status_code}")
    print(f"  Body: {r.text[:500]}")

    # NEW format (province/city/district)
    print("\n=== 3. Simulate NEW frontend request (with province/city/district) ===")
    r = httpx.post(f"http://{SERVER}:8000/api/v1/init/setup",
        headers=headers,
        json={"grade": 3, "province": "北京市", "city": "北京市", "district": "海淀区", "ai_name": "小智"},
        timeout=10,
    )
    print(f"  NEW format -> HTTP {r.status_code}")
    print(f"  Body: {r.text[:500]}")

except Exception as e:
    print(f"  ERROR: {e}")

# 3. Check what main.dart.js the server is actually serving
print("\n=== 4. Check served main.dart.js contains new code ===")
try:
    r = httpx.get(f"http://{SERVER}:8000/main.dart.js", timeout=15)
    print(f"  HTTP {r.status_code}, size={len(r.content)} bytes")
    content = r.text
    print(f"  Contains 'regions/provinces': {'regions/provinces' in content}")
    print(f"  Contains 'province': {'province' in content}")
    print(f"  Contains '_selectedProvince': {'_selectedProvince' in content or 'selectedProvince' in content}")
    print(f"  Contains 'DropdownButtonFormField': {'DropdownButtonFormField' in content}")
    # Check if old code is there
    print(f"  Contains old '例如：北京市海淀区': {'北京市海淀区' in content}")
except Exception as e:
    print(f"  ERROR: {e}")

# 4. Check server journal for recent errors
print("\n=== 5. Check server logs ===")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER, 22, "root", "Xuzi-xiao198964", timeout=15)
_, stdout, _ = ssh.exec_command("journalctl -u ai-study --no-pager -n 30", timeout=15)
print(stdout.read().decode()[-1500:])
ssh.close()
