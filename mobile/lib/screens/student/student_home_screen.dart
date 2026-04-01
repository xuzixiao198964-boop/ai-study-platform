import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../providers/auth_provider.dart';
import '../../providers/permission_provider.dart';
import '../../services/api_service.dart';

class StudentHomeScreen extends StatefulWidget {
  const StudentHomeScreen({super.key});

  @override
  State<StudentHomeScreen> createState() => _StudentHomeScreenState();
}

class _StudentHomeScreenState extends State<StudentHomeScreen> {
  String _scene = 'chat'; // chat | camera
  String _sessionId = '';
  String _aiName = '小智';
  bool _hasProfile = false;

  @override
  void initState() {
    super.initState();
    _sessionId = 'session_${DateTime.now().millisecondsSinceEpoch}';
    context.read<PermissionProvider>().loadPermissions();
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    try {
      final profile = await ApiService().getProfile();
      if (profile != null && mounted) {
        setState(() {
          _aiName = profile['ai_name'] ?? '小智';
          _hasProfile = true;
        });
      }
    } catch (_) {}
  }

  void _switchScene(String newScene) {
    setState(() => _scene = newScene);
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();

    return Scaffold(
      appBar: AppBar(
        title: Text(_scene == 'chat' ? '与$_aiName对话' : '作业辅导'),
        actions: [
          if (_scene == 'camera')
            IconButton(
              icon: const Icon(Icons.chat_bubble_outline),
              tooltip: '返回聊天',
              onPressed: () => _switchScene('chat'),
            ),
          IconButton(
            icon: const Icon(Icons.settings_outlined),
            onPressed: () => _showSettingsSheet(context),
          ),
          IconButton(
            icon: const Icon(Icons.person_outline),
            onPressed: () => _showProfileSheet(context, auth),
          ),
        ],
      ),
      body: _hasProfile
          ? (_scene == 'chat' ? _ChatView(
              sessionId: _sessionId,
              aiName: _aiName,
              onSceneSwitch: _switchScene,
            ) : _CameraView(
              sessionId: _sessionId,
              aiName: _aiName,
              onSceneSwitch: _switchScene,
            ))
          : _InitSetupView(onComplete: () {
              _loadProfile();
            }),
    );
  }

  void _showSettingsSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('AI 设置', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 20),
            ListTile(
              leading: const Icon(Icons.badge_outlined),
              title: const Text('AI 名字'),
              subtitle: Text(_aiName),
              onTap: () => _editAIName(ctx),
            ),
            ListTile(
              leading: const Icon(Icons.record_voice_over_outlined),
              title: const Text('声音 & 语速'),
              subtitle: const Text('温柔女声 · 中速'),
              onTap: () {},
            ),
          ],
        ),
      ),
    );
  }

  void _editAIName(BuildContext parentCtx) {
    final controller = TextEditingController(text: _aiName);
    showDialog(
      context: parentCtx,
      builder: (ctx) => AlertDialog(
        title: const Text('修改 AI 名字'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(hintText: '给AI起个名字'),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('取消')),
          ElevatedButton(
            onPressed: () async {
              final name = controller.text.trim();
              if (name.isEmpty) return;
              try {
                await ApiService().updateAIConfig(aiName: name);
                setState(() => _aiName = name);
                if (ctx.mounted) Navigator.pop(ctx);
                if (parentCtx.mounted) Navigator.pop(parentCtx);
              } catch (e) {
                if (ctx.mounted) {
                  ScaffoldMessenger.of(ctx).showSnackBar(SnackBar(content: Text('$e')));
                }
              }
            },
            child: const Text('确定'),
          ),
        ],
      ),
    );
  }

  void _showProfileSheet(BuildContext context, AuthProvider auth) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CircleAvatar(
              radius: 36,
              backgroundColor: AppTheme.primaryColor,
              child: Text(
                (auth.user?.nickname ?? '学')[0],
                style: const TextStyle(fontSize: 28, color: Colors.white),
              ),
            ),
            const SizedBox(height: 12),
            Text(auth.user?.nickname ?? '', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 4),
            Text('学生端 · ${auth.user?.username ?? ""}', style: const TextStyle(color: AppTheme.textSecondary)),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: () {
                  Navigator.pop(ctx);
                  auth.logout();
                  Navigator.of(context).pushReplacementNamed('/login');
                },
                icon: const Icon(Icons.logout, color: AppTheme.errorColor),
                label: const Text('退出登录', style: TextStyle(color: AppTheme.errorColor)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ============================================================
// 初始化设置视图
// ============================================================
class _InitSetupView extends StatefulWidget {
  final VoidCallback onComplete;
  const _InitSetupView({required this.onComplete});

  @override
  State<_InitSetupView> createState() => _InitSetupViewState();
}

class _InitSetupViewState extends State<_InitSetupView> {
  final _nameCtrl = TextEditingController(text: '小智');
  final _regionCtrl = TextEditingController();
  int _grade = 3;
  bool _loading = false;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const SizedBox(height: 40),
          const Icon(Icons.waving_hand, size: 64, color: AppTheme.primaryColor),
          const SizedBox(height: 16),
          const Text(
            '欢迎使用学习指认AI！',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          const Text(
            '先来做一些基本设置吧',
            style: TextStyle(fontSize: 16, color: AppTheme.textSecondary),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 40),
          const Text('你的年级', style: TextStyle(fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: List.generate(12, (i) {
              final g = i + 1;
              final label = g <= 6 ? '小学$g年级' : (g <= 9 ? '初${g - 6}' : '高${g - 9}');
              return ChoiceChip(
                label: Text(label),
                selected: _grade == g,
                onSelected: (_) => setState(() => _grade = g),
                selectedColor: AppTheme.primaryColor.withValues(alpha: 0.2),
              );
            }),
          ),
          const SizedBox(height: 24),
          const Text('就读区域', style: TextStyle(fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          TextField(
            controller: _regionCtrl,
            decoration: const InputDecoration(
              hintText: '例如：北京市海淀区',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 24),
          const Text('给AI起个名字', style: TextStyle(fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          TextField(
            controller: _nameCtrl,
            decoration: const InputDecoration(
              hintText: '随便起个名字吧（不能用爸爸妈妈等称呼）',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 32),
          ElevatedButton(
            onPressed: _loading ? null : _submit,
            style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16)),
            child: _loading
                ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                : const Text('开始学习', style: TextStyle(fontSize: 16)),
          ),
        ],
      ),
    );
  }

  Future<void> _submit() async {
    if (_regionCtrl.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('请填写就读区域')));
      return;
    }
    setState(() => _loading = true);
    try {
      await ApiService().setupStudent(
        grade: _grade,
        region: _regionCtrl.text.trim(),
        aiName: _nameCtrl.text.trim().isEmpty ? '小智' : _nameCtrl.text.trim(),
      );
      widget.onComplete();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('设置失败: $e')));
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    _regionCtrl.dispose();
    super.dispose();
  }
}

// ============================================================
// 语音聊天视图（默认界面）
// ============================================================
class _ChatView extends StatefulWidget {
  final String sessionId;
  final String aiName;
  final void Function(String) onSceneSwitch;

  const _ChatView({
    required this.sessionId,
    required this.aiName,
    required this.onSceneSwitch,
  });

  @override
  State<_ChatView> createState() => _ChatViewState();
}

class _ChatViewState extends State<_ChatView> {
  final List<_ChatMsg> _messages = [];
  final ScrollController _scrollCtrl = ScrollController();
  final TextEditingController _inputCtrl = TextEditingController();
  bool _isSending = false;
  bool _isListening = false;

  @override
  void initState() {
    super.initState();
    _messages.add(_ChatMsg(
      role: 'assistant',
      content: '你好！我是${widget.aiName}，你的学习小助手。有什么想聊的，或者说"我要做作业"我帮你打开摄像头～',
    ));
  }

  Future<void> _sendMessage(String text) async {
    if (text.trim().isEmpty || _isSending) return;
    final content = text.trim();
    _inputCtrl.clear();

    setState(() {
      _messages.add(_ChatMsg(role: 'user', content: content));
      _isSending = true;
    });
    _scrollToBottom();

    try {
      final result = await ApiService().sendChatMessage(widget.sessionId, content, scene: 'chat');
      if (mounted) {
        setState(() {
          _messages.add(_ChatMsg(role: 'assistant', content: result['reply'] ?? ''));
        });
        _scrollToBottom();

        if (result['scene_changed'] == true && result['new_scene'] == 'camera') {
          await Future.delayed(const Duration(milliseconds: 800));
          widget.onSceneSwitch('camera');
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _messages.add(_ChatMsg(role: 'assistant', content: '抱歉，我遇到了一点问题，请再试一次。'));
        });
      }
    } finally {
      if (mounted) setState(() => _isSending = false);
    }
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollCtrl.hasClients) {
        _scrollCtrl.animateTo(
          _scrollCtrl.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Expanded(
          child: ListView.builder(
            controller: _scrollCtrl,
            padding: const EdgeInsets.all(16),
            itemCount: _messages.length + (_isSending ? 1 : 0),
            itemBuilder: (ctx, i) {
              if (i == _messages.length) {
                return _buildTypingIndicator();
              }
              return _buildMessageBubble(_messages[i]);
            },
          ),
        ),
        _buildInputBar(),
      ],
    );
  }

  Widget _buildMessageBubble(_ChatMsg msg) {
    final isUser = msg.role == 'user';
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isUser) ...[
            CircleAvatar(
              radius: 18,
              backgroundColor: AppTheme.primaryColor,
              child: Text(widget.aiName[0], style: const TextStyle(color: Colors.white, fontSize: 14)),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                color: isUser ? AppTheme.primaryColor : Colors.white,
                borderRadius: BorderRadius.only(
                  topLeft: const Radius.circular(16),
                  topRight: const Radius.circular(16),
                  bottomLeft: Radius.circular(isUser ? 16 : 4),
                  bottomRight: Radius.circular(isUser ? 4 : 16),
                ),
                boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.05), blurRadius: 4, offset: const Offset(0, 2))],
              ),
              child: Text(
                msg.content,
                style: TextStyle(
                  color: isUser ? Colors.white : AppTheme.textPrimary,
                  fontSize: 15,
                  height: 1.5,
                ),
              ),
            ),
          ),
          if (isUser) ...[
            const SizedBox(width: 8),
            const CircleAvatar(
              radius: 18,
              backgroundColor: AppTheme.secondaryColor,
              child: Icon(Icons.person, size: 20, color: Colors.white),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildTypingIndicator() {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          CircleAvatar(
            radius: 18,
            backgroundColor: AppTheme.primaryColor,
            child: Text(widget.aiName[0], style: const TextStyle(color: Colors.white, fontSize: 14)),
          ),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                _buildDot(0),
                const SizedBox(width: 4),
                _buildDot(1),
                const SizedBox(width: 4),
                _buildDot(2),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDot(int index) {
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0.3, end: 1.0),
      duration: Duration(milliseconds: 600 + index * 200),
      builder: (ctx, value, child) => Opacity(
        opacity: value,
        child: Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(
            color: AppTheme.primaryColor.withValues(alpha: 0.6),
            shape: BoxShape.circle,
          ),
        ),
      ),
    );
  }

  Widget _buildInputBar() {
    return Container(
      padding: EdgeInsets.only(
        left: 16,
        right: 8,
        top: 12,
        bottom: MediaQuery.of(context).padding.bottom + 12,
      ),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.05), blurRadius: 8, offset: const Offset(0, -2))],
      ),
      child: Row(
        children: [
          IconButton(
            icon: Icon(
              _isListening ? Icons.mic : Icons.mic_none,
              color: _isListening ? AppTheme.errorColor : AppTheme.primaryColor,
              size: 28,
            ),
            onPressed: () {
              setState(() => _isListening = !_isListening);
              if (!_isListening && _inputCtrl.text.isNotEmpty) {
                _sendMessage(_inputCtrl.text);
              }
            },
          ),
          Expanded(
            child: TextField(
              controller: _inputCtrl,
              decoration: InputDecoration(
                hintText: '输入消息或点击麦克风语音输入...',
                hintStyle: TextStyle(color: Colors.grey[400]),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(24),
                  borderSide: BorderSide(color: Colors.grey[300]!),
                ),
                contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                filled: true,
                fillColor: Colors.grey[50],
              ),
              onSubmitted: _sendMessage,
              textInputAction: TextInputAction.send,
            ),
          ),
          const SizedBox(width: 4),
          IconButton(
            icon: const Icon(Icons.send_rounded, color: AppTheme.primaryColor),
            onPressed: () => _sendMessage(_inputCtrl.text),
          ),
          IconButton(
            icon: const Icon(Icons.camera_alt_outlined, color: AppTheme.primaryColor),
            tooltip: '打开摄像头',
            onPressed: () => widget.onSceneSwitch('camera'),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _scrollCtrl.dispose();
    _inputCtrl.dispose();
    super.dispose();
  }
}

class _ChatMsg {
  final String role;
  final String content;
  _ChatMsg({required this.role, required this.content});
}

// ============================================================
// 摄像头模式视图
// ============================================================
class _CameraView extends StatefulWidget {
  final String sessionId;
  final String aiName;
  final void Function(String) onSceneSwitch;

  const _CameraView({
    required this.sessionId,
    required this.aiName,
    required this.onSceneSwitch,
  });

  @override
  State<_CameraView> createState() => _CameraViewState();
}

class _CameraViewState extends State<_CameraView> {
  final ImagePicker _picker = ImagePicker();
  bool _isProcessing = false;
  Map<String, dynamic>? _ocrResult;
  String? _capturedImageBase64;
  String _statusMessage = '请将试卷放在摄像头前，或点击拍照按钮';

  Future<void> _captureAndRecognize() async {
    final XFile? photo = await _picker.pickImage(source: ImageSource.camera, maxWidth: 1920, imageQuality: 85);
    if (photo == null) return;
    await _processImage(photo);
  }

  Future<void> _pickAndRecognize() async {
    final XFile? image = await _picker.pickImage(source: ImageSource.gallery, maxWidth: 1920, imageQuality: 85);
    if (image == null) return;
    await _processImage(image);
  }

  Future<void> _processImage(XFile file) async {
    setState(() {
      _isProcessing = true;
      _ocrResult = null;
      _statusMessage = 'AI正在识别试题...';
    });

    try {
      final bytes = await file.readAsBytes();
      final base64Str = base64Encode(bytes);
      setState(() => _capturedImageBase64 = base64Str);

      final result = await ApiService().visionCorrect(base64Str);
      setState(() {
        _ocrResult = result;
        _statusMessage = '识别完成，可以指着题目问我';
      });
    } catch (e) {
      setState(() => _statusMessage = '识别失败，请重试');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('识别失败: $e')));
      }
    } finally {
      setState(() => _isProcessing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // 状态栏
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
          color: AppTheme.primaryColor.withValues(alpha: 0.1),
          child: Row(
            children: [
              Icon(
                _isProcessing ? Icons.hourglass_top : (_ocrResult != null ? Icons.check_circle : Icons.videocam),
                color: AppTheme.primaryColor,
                size: 20,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(_statusMessage, style: const TextStyle(fontSize: 14, color: AppTheme.textSecondary)),
              ),
              TextButton.icon(
                onPressed: () => widget.onSceneSwitch('chat'),
                icon: const Icon(Icons.chat, size: 16),
                label: const Text('返回聊天'),
              ),
            ],
          ),
        ),
        // 主内容区：左右分屏
        Expanded(
          child: _ocrResult != null
              ? Row(
                  children: [
                    // 左侧：拍摄的图片
                    Expanded(
                      flex: 2,
                      child: Container(
                        color: Colors.black,
                        child: _capturedImageBase64 != null
                            ? Image.memory(
                                base64Decode(_capturedImageBase64!),
                                fit: BoxFit.contain,
                              )
                            : const Center(
                                child: Icon(Icons.image, size: 64, color: Colors.white38),
                              ),
                      ),
                    ),
                    // 右侧：OCR结果
                    Expanded(
                      flex: 3,
                      child: _buildOCRResultPanel(),
                    ),
                  ],
                )
              : _buildCaptureView(),
        ),
        // 底部操作栏
        _buildBottomBar(),
      ],
    );
  }

  Widget _buildCaptureView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          if (_isProcessing) ...[
            const CircularProgressIndicator(),
            const SizedBox(height: 16),
            const Text('AI正在识别和分析...', style: TextStyle(color: AppTheme.textSecondary)),
          ] else ...[
            Icon(Icons.document_scanner_outlined, size: 80, color: Colors.grey[400]),
            const SizedBox(height: 16),
            const Text('拍摄试卷或从相册选择', style: TextStyle(fontSize: 18, color: AppTheme.textSecondary)),
            const SizedBox(height: 8),
            Text(
              '${widget.aiName}会帮你识别题目并进行批改',
              style: TextStyle(fontSize: 14, color: Colors.grey[500]),
            ),
            const SizedBox(height: 32),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                ElevatedButton.icon(
                  onPressed: _captureAndRecognize,
                  icon: const Icon(Icons.camera_alt),
                  label: const Text('拍照'),
                  style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14)),
                ),
                const SizedBox(width: 16),
                OutlinedButton.icon(
                  onPressed: _pickAndRecognize,
                  icon: const Icon(Icons.photo_library),
                  label: const Text('相册'),
                  style: OutlinedButton.styleFrom(padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14)),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildOCRResultPanel() {
    final result = _ocrResult!;
    final questionText = result['question_text'] ?? '';
    final studentAnswer = result['student_answer'] ?? '';
    final isCorrect = result['is_correct'] == true;
    final standardAnswer = result['standard_answer'] ?? result['correct_answer'] ?? '';
    final explanation = result['explanation'] ?? '';
    final solutionSteps = result['solution_steps'] ?? '';

    return Container(
      color: Colors.grey[50],
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 批改结果头
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: isCorrect ? Colors.green[50] : Colors.red[50],
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  Icon(
                    isCorrect ? Icons.check_circle : Icons.cancel,
                    color: isCorrect ? Colors.green : Colors.red,
                    size: 28,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    isCorrect ? '回答正确！' : '回答有误',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: isCorrect ? Colors.green[700] : Colors.red[700],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            if (questionText.isNotEmpty) ...[
              const Text('题目：', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
              const SizedBox(height: 4),
              Text(questionText, style: const TextStyle(fontSize: 14, height: 1.5)),
              const SizedBox(height: 12),
            ],
            if (studentAnswer.isNotEmpty) ...[
              const Text('你的答案：', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
              const SizedBox(height: 4),
              Text(studentAnswer, style: TextStyle(fontSize: 14, color: isCorrect ? Colors.green : Colors.red)),
              const SizedBox(height: 12),
            ],
            if (!isCorrect && standardAnswer.isNotEmpty) ...[
              const Text('正确答案：', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
              const SizedBox(height: 4),
              Text(standardAnswer, style: const TextStyle(fontSize: 14, color: Colors.green)),
              const SizedBox(height: 12),
            ],
            if (explanation.isNotEmpty || solutionSteps.isNotEmpty) ...[
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.blue[50],
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('AI 解析：', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: AppTheme.primaryColor)),
                    const SizedBox(height: 8),
                    if (solutionSteps.isNotEmpty) Text(solutionSteps, style: const TextStyle(fontSize: 14, height: 1.6)),
                    if (explanation.isNotEmpty) ...[
                      const SizedBox(height: 8),
                      Text(explanation, style: const TextStyle(fontSize: 14, height: 1.6)),
                    ],
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildBottomBar() {
    return Container(
      padding: EdgeInsets.only(
        left: 16,
        right: 16,
        top: 12,
        bottom: MediaQuery.of(context).padding.bottom + 12,
      ),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.05), blurRadius: 8, offset: const Offset(0, -2))],
      ),
      child: Row(
        children: [
          Expanded(
            child: ElevatedButton.icon(
              onPressed: _isProcessing ? null : _captureAndRecognize,
              icon: const Icon(Icons.camera_alt),
              label: const Text('拍照识题'),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: OutlinedButton.icon(
              onPressed: _isProcessing ? null : _pickAndRecognize,
              icon: const Icon(Icons.photo_library),
              label: const Text('相册选题'),
            ),
          ),
        ],
      ),
    );
  }
}
