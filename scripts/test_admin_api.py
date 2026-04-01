"""Test admin panel API endpoints end-to-end"""
import paramiko
import json
import sys

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', errors='replace')

SERVER = "101.201.244.150"
USER = "root"
PASSWORD = "Xuzi-xiao198964"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER, 22, USER, PASSWORD, timeout=15)


def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    out = stdout.read().decode('utf-8', 'replace').strip()
    err = stderr.read().decode('utf-8', 'replace').strip()
    code = stdout.channel.recv_exit_status()
    return out, err, code


print("=" * 60)
print("1. Admin Login")
print("=" * 60)
out, err, code = run(
    '''curl -s -X POST http://127.0.0.1:8001/api/v1/admin/login '''
    '''-H "Content-Type: application/json" '''
    '''-d '{"username":"admin","password":"AiStudy@2026"}' '''
)
print(f"Response: {out}")
if err:
    print(f"Stderr: {err}")

try:
    login_data = json.loads(out)
    token = login_data["access_token"]
    print(f"Token obtained: {token[:20]}...")
except Exception as e:
    print(f"FAILED to parse login response: {e}")
    ssh.close()
    sys.exit(1)

print()
print("=" * 60)
print("2. Get API Keys")
print("=" * 60)
out, err, code = run(
    f'''curl -s http://127.0.0.1:8001/api/v1/admin/api-keys '''
    f'''-H "Authorization: Bearer {token}" '''
)
print(f"Response: {out}")
if err:
    print(f"Stderr: {err}")

try:
    keys_data = json.loads(out)
    print(f"\nFound {len(keys_data)} keys:")
    for k in keys_data:
        print(f"  {k['label']}: masked={k['masked_value']}")
except Exception as e:
    print(f"FAILED to parse keys: {e}")

print()
print("=" * 60)
print("3. Update API Keys (test with DEEPSEEK_API_KEY)")
print("=" * 60)
out, err, code = run(
    f'''curl -s -X PUT http://127.0.0.1:8001/api/v1/admin/api-keys '''
    f'''-H "Authorization: Bearer {token}" '''
    f'''-H "Content-Type: application/json" '''
    f"""-d '{{"keys": {{"DEEPSEEK_API_KEY": "sk-test-12345678"}}}}' """
)
print(f"Response: {out}")
if err:
    print(f"Stderr: {err}")

print()
print("=" * 60)
print("4. Verify Key was updated")
print("=" * 60)
out, err, code = run(
    f'''curl -s http://127.0.0.1:8001/api/v1/admin/api-keys '''
    f'''-H "Authorization: Bearer {token}" '''
)
print(f"Response: {out}")

try:
    keys_data = json.loads(out)
    for k in keys_data:
        if k['key'] == 'DEEPSEEK_API_KEY':
            print(f"\n  DEEPSEEK_API_KEY value: {k['value']}")
            print(f"  DEEPSEEK_API_KEY masked: {k['masked_value']}")
            if k['value'] == 'sk-test-12345678':
                print("  >>> UPDATE VERIFIED OK")
            else:
                print(f"  >>> UPDATE FAILED: got '{k['value']}'")
except Exception as e:
    print(f"FAILED: {e}")

print()
print("=" * 60)
print("5. Restore original key")
print("=" * 60)
out, err, code = run(
    f'''curl -s -X PUT http://127.0.0.1:8001/api/v1/admin/api-keys '''
    f'''-H "Authorization: Bearer {token}" '''
    f'''-H "Content-Type: application/json" '''
    f"""-d '{{"keys": {{"DEEPSEEK_API_KEY": "sk-9fcc8f6d0ce94fdbbe66b152b7d3e485"}}}}' """
)
print(f"Response: {out}")

print()
print("=" * 60)
print("6. Get Stats")
print("=" * 60)
out, err, code = run(
    f'''curl -s http://127.0.0.1:8001/api/v1/admin/stats '''
    f'''-H "Authorization: Bearer {token}" '''
)
print(f"Response: {out}")

print()
print("=" * 60)
print("7. Test via Nginx port 80 (same flow the browser uses)")
print("=" * 60)
out, err, code = run(
    '''curl -s -X PUT http://127.0.0.1:80/api/v1/admin/api-keys '''
    f'''-H "Authorization: Bearer {token}" '''
    '''-H "Content-Type: application/json" '''
    """-d '{"keys": {"AGORA_APP_ID": "test-agora-id-123"}}' """
)
print(f"PUT via port 80: {out}")
if err:
    print(f"Stderr: {err}")

out, err, code = run(
    f'''curl -s http://127.0.0.1:80/api/v1/admin/api-keys '''
    f'''-H "Authorization: Bearer {token}" '''
)
print(f"GET via port 80: {out}")

# Restore
run(
    f'''curl -s -X PUT http://127.0.0.1:80/api/v1/admin/api-keys '''
    f'''-H "Authorization: Bearer {token}" '''
    f'''-H "Content-Type: application/json" '''
    f"""-d '{{"keys": {{"AGORA_APP_ID": ""}}}}' """
)

print()
print("=" * 60)
print("8. Check .env file on server")
print("=" * 60)
out, err, code = run("cat /opt/ai-study-platform/.env")
print(out)

ssh.close()
print("\n\nAll tests completed.")
