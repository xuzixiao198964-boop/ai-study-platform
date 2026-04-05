#!/usr/bin/env python3
"""
验证腾讯云TTS声音ID的真实性别和音色
通过实际调用API生成音频来确认每个VoiceType的真实属性
"""
import os
import sys
import base64
from tencentcloud.common import credential
from tencentcloud.tts.v20190823 import tts_client, models

# 从环境变量读取密钥
secret_id = os.getenv("TENCENT_SECRET_ID")
secret_key = os.getenv("TENCENT_SECRET_KEY")

if not secret_id or not secret_key:
    print("错误: 未设置TENCENT_SECRET_ID或TENCENT_SECRET_KEY环境变量")
    sys.exit(1)

# 创建客户端
cred = credential.Credential(secret_id, secret_key)
client = tts_client.TtsClient(cred, "ap-guangzhou")

# 测试的VoiceType列表
voice_types = [0, 1, 2, 3, 4, 5, 6, 7, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010]

print("=" * 80)
print("腾讯云TTS VoiceType验证")
print("=" * 80)
print()

results = []

for voice_id in voice_types:
    try:
        req = models.TextToVoiceRequest()
        req.Text = f"你好，我是声音{voice_id}号"
        req.SessionId = f"test_{voice_id}"
        req.VoiceType = voice_id
        req.Codec = "mp3"
        req.SampleRate = 16000

        resp = client.TextToVoice(req)
        audio_data = base64.b64decode(resp.Audio)
        audio_size = len(audio_data)

        # 保存音频文件用于人工验证
        output_file = f"/tmp/voice_{voice_id}.mp3"
        with open(output_file, "wb") as f:
            f.write(audio_data)

        result = {
            "id": voice_id,
            "status": "成功",
            "size": audio_size,
            "file": output_file
        }
        results.append(result)

        print(f"✓ VoiceType {voice_id:4d}: 成功生成 {audio_size:6d} 字节 -> {output_file}")

    except Exception as e:
        error_msg = str(e)
        result = {
            "id": voice_id,
            "status": "失败",
            "error": error_msg
        }
        results.append(result)

        print(f"✗ VoiceType {voice_id:4d}: 失败 - {error_msg}")

print()
print("=" * 80)
print("验证完成")
print("=" * 80)
print()
print("可用的VoiceType:")
for r in results:
    if r["status"] == "成功":
        print(f"  - {r['id']}")

print()
print("请手动试听 /tmp/voice_*.mp3 文件来确认每个声音的真实性别和音色特征")
print()
