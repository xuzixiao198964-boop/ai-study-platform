#!/usr/bin/env python3
"""测试腾讯云TTS声音ID映射"""

import requests
import json
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

API_BASE = 'https://45.78.5.184:8000/api/v1'

print('=== 测试腾讯云TTS声音映射 ===\n')

# 获取声音列表
resp = requests.get(f'{API_BASE}/tts/voices', verify=False)
voices = resp.json()

print(f'总共 {len(voices)} 种声音:\n')

# 测试每个声音
for voice in voices:
    voice_id = voice['id']
    name = voice['name']
    gender = voice['gender']
    desc = voice['description']

    # 获取音频
    resp = requests.get(f'{API_BASE}/tts/preview/{voice_id}', verify=False)

    if resp.status_code == 200:
        size = len(resp.content)
        gender_cn = '女声' if gender == 'female' else '男声'
        print(f'ID {voice_id:4s} | {name:6s} | {gender_cn} | {desc:20s} | {size:5d} bytes')
    else:
        print(f'ID {voice_id:4s} | {name:6s} | 错误: HTTP {resp.status_code}')

print('\n=== 说明 ===')
print('请在浏览器中逐个试听，确认：')
print('1. 标注为"女声"的确实是女声')
print('2. 标注为"男声"的确实是男声')
print('3. 如果不匹配，请告诉我具体哪个ID的性别错了')
