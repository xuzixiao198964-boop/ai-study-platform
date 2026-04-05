#!/usr/bin/env python3
"""
验证腾讯云TTS声音并修复映射
"""
import paramiko
import sys

# 服务器信息
HOST = "45.78.5.184"
PORT = 22
USER = "root"
PASSWORD = "FYCZWP2uPLjR"

# 验证脚本
VERIFY_SCRIPT = """
cd /opt/ai-study-platform
source venv/bin/activate

python3 - <<'PYEOF'
import os
import sys
import base64
from tencentcloud.common import credential
from tencentcloud.tts.v20190823 import tts_client, models

# 从.env读取密钥
with open('.env') as f:
    for line in f:
        if line.startswith('TENCENT_'):
            key, val = line.strip().split('=', 1)
            os.environ[key] = val

secret_id = os.getenv('TENCENT_SECRET_ID')
secret_key = os.getenv('TENCENT_SECRET_KEY')

cred = credential.Credential(secret_id, secret_key)
client = tts_client.TtsClient(cred, 'ap-guangzhou')

voice_types = [0, 1, 2, 3, 4, 5, 6, 7, 1001, 1002, 1003]

print('=' * 70)
print('腾讯云TTS VoiceType验证')
print('=' * 70)

for voice_id in voice_types:
    try:
        req = models.TextToVoiceRequest()
        req.Text = f'你好，我是声音{voice_id}号'
        req.SessionId = f'test_{voice_id}'
        req.VoiceType = voice_id
        req.Codec = 'mp3'
        req.SampleRate = 16000

        resp = client.TextToVoice(req)
        audio_data = base64.b64decode(resp.Audio)
        size = len(audio_data)

        print(f'VoiceType {voice_id:4d}: SUCCESS ({size:6d} bytes)')

    except Exception as e:
        error = str(e)[:80]
        print(f'VoiceType {voice_id:4d}: FAILED - {error}')

print('=' * 70)
PYEOF
"""

def main():
    print("Connecting to server to verify Tencent TTS voices...")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(HOST, PORT, USER, PASSWORD)
        print(f"[OK] Connected to {HOST}")

        stdin, stdout, stderr = ssh.exec_command(VERIFY_SCRIPT)

        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')

        print("\n" + output)

        if error:
            print("Error output:")
            print(error)

        return stdout.channel.recv_exit_status()

    except Exception as e:
        print(f"[ERROR] {e}")
        return 1
    finally:
        ssh.close()

if __name__ == "__main__":
    sys.exit(main())
