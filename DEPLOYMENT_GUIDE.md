# 部署说明

由于本地环境没有Flutter，需要在服务器上构建和部署。

## 手动部署步骤

在服务器上执行以下命令：

```bash
# 1. 更新后端代码
cd /opt/ai-study-platform
git pull

# 2. 重启后端服务
systemctl restart ai-study
systemctl status ai-study

# 3. 构建前端
cd /opt/ai-study-mobile
/opt/flutter/bin/flutter build web --release

# 4. 重启Nginx
systemctl restart nginx
```

## 验证部署

访问: https://45.78.5.184:8000

## 修复内容

### 问题4: Service Worker SSL错误 ✅
- 完全禁用Service Worker注册
- 在页面加载时卸载所有已注册的Service Worker

### 问题3: iPad听不见TTS ✅
- TTS onstart时停止语音识别
- TTS onend时恢复语音识别
- 增加300ms延迟确保识别正常恢复

### 问题5: Windows公放回声 ✅
- TTS播放期间完全暂停语音识别
- 避免AI说话声音被当作用户输入

### 问题6: 第一次后不能持续对话 ✅
- 优化识别重启逻辑
- 检查TTS播放状态，避免冲突
- 修复重复触发问题

### 问题2: 弹窗居中 ✅
- 使用DraggableScrollableSheet实现可拖拽弹窗
- AlertDialog使用Center和SingleChildScrollView包裹

### 问题1: 腾讯云TTS声音选择 ✅
- 创建/tts/voices API端点
- 返回18种腾讯云标准音色
- 前端动态加载声音列表
- 优化试听功能，使用真实声音名称和描述

## 文件修改

- mobile/web/index.html: 修复所有语音识别和TTS问题
- mobile/lib/screens/student/student_home_screen.dart: 实现声音选择UI和弹窗居中
- mobile/lib/services/api_service.dart: 添加getTTSVoices方法
- server/app/api/endpoints/tts.py: 新增TTS声音列表API
- server/app/api/router.py: 注册TTS路由
