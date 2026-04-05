# 语音功能修复报告

## 修复时间
2026-04-05

## 修复的问题

### 1. ❌ 语音识别静默时间问题
**问题描述**: 用户每次点开始要两个1秒才会发送（应该是1秒静默自动发送）

**根本原因**: 
- 静默检测窗口设置为 `elapsed >= SILENCE_MS && elapsed < SILENCE_MS + 300`
- 这个窗口太窄，可能错过触发时机
- 没有防重复触发机制

**修复方案**:
```javascript
// 添加触发标志
var _stt = {
  // ...
  silenceTriggered: false  // 防止重复触发
};

// 改进静默检测逻辑
if (elapsed >= _stt.SILENCE_MS && !_stt.silenceTriggered) {
  _stt.silenceTriggered = true;  // 标记已触发
  console.log('[静默检测] 触发发送, 静默时长:', elapsed, 'ms');
  _vcOnSilence(text);
}

// 有新内容时重置标志
rec.onresult = function(e) {
  // ...
  _stt.silenceTriggered = false;  // 有新内容时重置
};
```

### 2. ❌ 语音识别第一次后停止工作
**问题描述**: 用户说过第一次话以后就不会再识别

**根本原因**:
- 发送消息后执行 `_stt.lastResultMs = 0`
- 重置时间戳导致后续无法触发静默检测
- 条件 `if (text.length === 0 || _stt.lastResultMs === 0) return;` 阻止了后续触发

**修复方案**:
```javascript
function _vcOnSilence(rawText) {
  // ...
  // 清空文本但不重置lastResultMs，让识别继续
  _stt.finalText = '';
  _stt.interimText = '';
  _stt.silenceTriggered = false;  // 重置触发标志，准备下一次
  // 不再执行: _stt.lastResultMs = 0;
}
```

### 3. ❌ TTS语音不播放
**问题描述**: AI回复的语音不播放

**根本原因**: 
- 缺少调试日志，无法定位问题
- 可能是API响应格式问题或浏览器权限问题

**修复方案**:
```javascript
// 添加详细日志
window.ttsSpeak = function(text, rate, pitch) {
  console.log('[TTS] ttsSpeak调用, text:', text, 'supported:', !!window.speechSynthesis);
  // ...
  u.onstart = function() { console.log('[TTS] 开始播放'); };
  u.onend = function() { console.log('[TTS] 播放结束'); };
  u.onerror = function(e) { console.error('[TTS] 播放错误:', e); };
  console.log('[TTS] 调用speak');
  window.speechSynthesis.speak(u);
};

// XHR响应处理添加日志
xhr.onload = function() {
  console.log('[XHR] 响应状态:', xhr.status);
  var data = JSON.parse(xhr.responseText);
  console.log('[XHR] 响应数据:', data);
  if (data.reply && data.reply.trim()) {
    console.log('[TTS] 准备播放:', data.reply.trim());
    ttsSpeak(data.reply.trim(), 1.0, 1.0);
  } else {
    console.warn('[TTS] 没有reply字段或为空');
  }
};
```

### 4. ⚠️ Service Worker SSL证书警告
**问题描述**: F12控制台显示Service Worker SSL证书错误

**根本原因**: 
- 服务器使用自签名SSL证书
- 浏览器不信任自签名证书

**建议方案** (未实施):
- 使用Let's Encrypt申请免费正式SSL证书
- 或在浏览器中信任自签名证书
- 此问题不影响功能，仅为警告

## 部署记录

### 后端部署
- ✅ 已部署 initialization.py 修复
- ✅ 后端服务重启成功
- ✅ API测试通过

### 前端部署
- ✅ 已上传修复后的 index.html
- ✅ 部署路径: `/opt/ai-study-mobile/build/web/index.html`
- ✅ Nginx重启成功

## 测试验证步骤

请按以下步骤验证修复：

1. **访问应用**
   - 打开浏览器访问: https://45.78.5.184:8000
   - 打开F12开发者工具，切换到Console标签

2. **完成引导设置**
   - 选择年级、地区等信息
   - 点击"开始学习"

3. **测试语音识别**
   - 点击"开始对话"按钮
   - 说一句话，停顿1秒
   - 观察Console日志，应该看到：
     ```
     [静默检测] 触发发送, 静默时长: 1000+ ms, 文本: xxx
     [_vcOnSilence] 收到文本: xxx
     [XHR] 发送请求: {...}
     ```

4. **测试连续对话**
   - 等待AI回复后，再说第二句话
   - 停顿1秒，观察是否自动发送
   - 验证语音识别没有停止工作

5. **测试TTS播放**
   - 观察Console日志，应该看到：
     ```
     [XHR] 响应状态: 200
     [XHR] 响应数据: {reply: "..."}
     [TTS] 准备播放: ...
     [TTS] ttsSpeak调用, text: ...
     [TTS] 调用speak
     [TTS] 开始播放
     [TTS] 播放结束
     ```
   - 听到AI语音回复

6. **检查问题**
   - 如果TTS不播放，查看Console是否有错误
   - 如果识别停止，查看是否有 `[STT] 错误` 日志
   - 如果静默时间不对，查看 `[静默检测]` 日志中的时长

## 关键改进

1. **防重复触发机制**: 使用 `silenceTriggered` 标志防止同一段话多次发送
2. **保持识别状态**: 发送后不重置 `lastResultMs`，让识别持续工作
3. **详细日志**: 添加完整的调试日志，便于定位问题
4. **识别重启**: onend事件中自动重启识别，保持连续对话

## 已知限制

1. Service Worker SSL警告仍存在（不影响功能）
2. 需要HTTPS环境才能使用语音识别
3. 需要用户授权麦克风权限

## 下一步

如果测试中发现问题，请提供：
1. F12 Console中的完整日志
2. 具体的错误现象描述
3. 浏览器类型和版本
