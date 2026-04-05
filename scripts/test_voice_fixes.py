#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试已部署的语音功能"""
import requests
import json
import sys
import io

# 修复Windows控制台编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_URL = "https://45.78.5.184:8000"

def test_frontend():
    print("\n" + "="*60)
    print("测试前端访问")
    print("="*60)

    try:
        # 跳过SSL验证
        resp = requests.get(BASE_URL, verify=False, timeout=10)
        print(f"状态码: {resp.status_code}")

        # 检查关键修复
        content = resp.text
        checks = {
            "Service Worker已禁用": "// serviceWorkerSettings" in content,
            "静默触发标志": "silenceTriggered" in content,
            "TTS iPad修复": "iPad修复" in content or "iPad兼容" in content,
            "回声消除": "暂停识别以播放TTS" in content,
        }

        print("\n修复验证:")
        for name, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"{status} {name}")

        return all(checks.values())
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def print_test_instructions():
    print("\n" + "="*60)
    print("手动测试步骤")
    print("="*60)
    print("""
1. 访问 https://45.78.5.184:8000
2. 打开F12开发者工具 -> Console标签
3. 完成引导设置（年级、地区、AI名字）
4. 点击"开始学习"

测试项目：

✅ Service Worker错误
   - Console不应出现SSL证书错误

✅ 语音识别静默时间（1秒）
   - 点击麦克风图标
   - 说一句话，停顿1秒
   - 观察Console: [静默检测] 触发发送, 静默时长: 1000+ ms
   - 消息应该在1秒后自动发送

✅ 持续对话
   - 等待AI回复
   - 再说第二句话，停顿1秒
   - 第二句话也应该自动发送
   - 可以连续对话多轮

✅ iPad TTS播放
   - 使用iPad访问
   - 完成对话
   - 应该能听到AI语音回复
   - Console显示: [TTS] 开始播放

✅ 回声消除
   - 使用公放（不用耳机）
   - 进行对话
   - AI说话时不应该被识别为用户输入
   - Console显示: [STT] 暂停识别以播放TTS

⚠️ 声音选择功能
   - 当前版本：引导设置中没有声音选择
   - 需要重新构建Flutter应用才能启用
""")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    print("="*60)
    print("语音功能部署验证")
    print("="*60)

    success = test_frontend()
    print_test_instructions()

    if success:
        print("\n✅ 前端修复已部署")
    else:
        print("\n⚠️ 部分修复可能未生效")

    print("\n" + "="*60)
    print("关于声音选择功能")
    print("="*60)
    print("""
声音选择功能代码已修改，但需要重新构建Flutter应用。

选项1: 在有Flutter环境的机器上构建
  1. 安装Flutter SDK
  2. cd /d/work/ai-study-platform/mobile
  3. flutter pub get
  4. flutter build web --release
  5. 上传 build/web 目录到服务器

选项2: 在服务器上安装Flutter
  1. SSH到服务器
  2. 安装Flutter: https://docs.flutter.dev/get-started/install/linux
  3. cd /opt/ai-study-mobile
  4. flutter build web --release
  5. 重启Nginx

选项3: 使用CI/CD
  - 配置GitHub Actions自动构建部署
""")
