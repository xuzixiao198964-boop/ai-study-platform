import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../providers/auth_provider.dart';
import '../../providers/permission_provider.dart';
import '../../services/api_service.dart';
import '../../services/speech_service.dart';
import '../../services/tts_service.dart';

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
      } else if (mounted) {
        // 如果没有profile，设置为false显示设置页面
        setState(() {
          _hasProfile = false;
        });
      }
    } catch (_) {
      // 出错时也显示设置页面
      if (mounted) {
        setState(() {
          _hasProfile = false;
        });
      }
    }
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
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => DraggableScrollableSheet(
        initialChildSize: 0.5,
        minChildSize: 0.3,
        maxChildSize: 0.9,
        expand: false,
        builder: (_, controller) => Padding(
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
      ),
    );
  }

  void _editAIName(BuildContext parentCtx) {
    final controller = TextEditingController(text: _aiName);
    showDialog(
      context: parentCtx,
      builder: (ctx) => Center(
        child: SingleChildScrollView(
          child: AlertDialog(
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
        ),
      ),
    );
  }

  void _showProfileSheet(BuildContext context, AuthProvider auth) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => DraggableScrollableSheet(
        initialChildSize: 0.4,
        minChildSize: 0.3,
        maxChildSize: 0.7,
        expand: false,
        builder: (_, controller) => Padding(
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
  int _grade = 3;
  bool _loading = false;

  List<String> _provinces = [];
  List<String> _cities = [];
  List<String> _districts = [];
  String? _selectedProvince;
  String? _selectedCity;
  String? _selectedDistrict;
  bool _loadingRegions = true;

  // 声音选择
  String _selectedVoice = '101001';
  final TtsService _tts = TtsService();
  List<Map<String, dynamic>> _voiceOptions = [];
  bool _loadingVoices = true;

  @override
  void initState() {
    super.initState();
    _loadProvinces();
    _loadVoices();
  }

  Future<void> _loadVoices() async {
    try {
      final voices = await ApiService().getTTSVoices();
      if (mounted) {
        setState(() {
          _voiceOptions = List<Map<String, dynamic>>.from(voices);
          _loadingVoices = false;
          if (_voiceOptions.isNotEmpty) {
            _selectedVoice = _voiceOptions[0]['id'];
          }
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _loadingVoices = false);
      }
    }
  }

  Future<void> _loadProvinces() async {
    try {
      final list = await ApiService().getProvinces();
      if (mounted) setState(() { _provinces = list; _loadingRegions = false; });
    } catch (_) {
      if (mounted) setState(() => _loadingRegions = false);
    }
  }

  Future<void> _onProvinceChanged(String? value) async {
    setState(() {
      _selectedProvince = value;
      _selectedCity = null;
      _selectedDistrict = null;
      _cities = [];
      _districts = [];
    });
    if (value == null) return;
    try {
      final list = await ApiService().getCities(value);
      if (mounted) setState(() => _cities = list);
    } catch (_) {}
  }

  Future<void> _onCityChanged(String? value) async {
    setState(() {
      _selectedCity = value;
      _selectedDistrict = null;
      _districts = [];
    });
    if (value == null || _selectedProvince == null) return;
    try {
      final list = await ApiService().getDistricts(_selectedProvince!, value);
      if (mounted) setState(() => _districts = list);
    } catch (_) {}
  }

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
                selectedColor: AppTheme.primaryColor.withOpacity(0.2),
              );
            }),
          ),
          const SizedBox(height: 24),
          const Text('就读区域', style: TextStyle(fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          if (_loadingRegions)
            const Center(child: Padding(
              padding: EdgeInsets.symmetric(vertical: 16),
              child: CircularProgressIndicator(),
            ))
          else ...[
            DropdownButtonFormField<String>(
              value: _selectedProvince,
              decoration: const InputDecoration(
                labelText: '省/自治区/直辖市',
                border: OutlineInputBorder(),
              ),
              isExpanded: true,
              items: _provinces.map((p) => DropdownMenuItem(value: p, child: Text(p))).toList(),
              onChanged: _onProvinceChanged,
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              value: _selectedCity,
              decoration: const InputDecoration(
                labelText: '市/州',
                border: OutlineInputBorder(),
              ),
              isExpanded: true,
              items: _cities.map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
              onChanged: _onCityChanged,
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              value: _selectedDistrict,
              decoration: const InputDecoration(
                labelText: '区/县',
                border: OutlineInputBorder(),
              ),
              isExpanded: true,
              items: _districts.map((d) => DropdownMenuItem(value: d, child: Text(d))).toList(),
              onChanged: (value) => setState(() => _selectedDistrict = value),
            ),
          ],
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
          const SizedBox(height: 24),
          const Text('选择AI声音', style: TextStyle(fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          if (_loadingVoices)
            const Center(child: Padding(
              padding: EdgeInsets.symmetric(vertical: 16),
              child: CircularProgressIndicator(),
            ))
          else
            ..._voiceOptions.map((voice) {
              final voiceId = voice['id'] as String;
              final voiceName = voice['name'] as String;
              final voiceDesc = voice['description'] as String;
              final gender = voice['gender'] as String;
              return Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: InkWell(
                  onTap: () {
                    setState(() => _selectedVoice = voiceId);
                    _playVoiceSample(voiceName, voiceDesc);
                  },
                  borderRadius: BorderRadius.circular(8),
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      border: Border.all(
                        color: _selectedVoice == voiceId
                            ? AppTheme.primaryColor
                            : Colors.grey.shade300,
                        width: 2,
                      ),
                      borderRadius: BorderRadius.circular(8),
                      color: _selectedVoice == voiceId
                          ? AppTheme.primaryColor.withOpacity(0.1)
                          : Colors.transparent,
                    ),
                    child: Row(
                      children: [
                        Icon(
                          _selectedVoice == voiceId
                              ? Icons.radio_button_checked
                              : Icons.radio_button_unchecked,
                          color: _selectedVoice == voiceId
                              ? AppTheme.primaryColor
                              : Colors.grey,
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                voiceName,
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: _selectedVoice == voiceId
                                      ? FontWeight.w600
                                      : FontWeight.normal,
                                ),
                              ),
                              Text(
                                voiceDesc,
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.grey.shade600,
                                ),
                              ),
                            ],
                          ),
                        ),
                        IconButton(
                          icon: const Icon(Icons.play_circle_outline),
                          onPressed: () => _playVoiceSample(voiceName, voiceDesc),
                          tooltip: '试听',
                        ),
                      ],
                    ),
                  ),
                ),
              );
            }).toList(),
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

  void _playVoiceSample(String voiceName, String voiceDesc) {
    final text = '你好，我是$voiceName，$voiceDesc';
    _tts.speak(text, rate: 1.0, pitch: 1.0);
  }

  Future<void> _submit() async {
    if (_selectedProvince == null || _selectedCity == null || _selectedDistrict == null) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('请选择完整的就读区域（省/市/区）')));
      return;
    }
    setState(() => _loading = true);
    try {
      await ApiService().setupStudent(
        grade: _grade,
        province: _selectedProvince!,
        city: _selectedCity!,
        district: _selectedDistrict!,
        aiName: _nameCtrl.text.trim().isEmpty ? '小智' : _nameCtrl.text.trim(),
        aiVoice: _selectedVoice,
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
    _tts.stop();
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
  bool _voiceMode = false;
  String _speechText = '';
  int _silenceMs = 0;
  late final SpeechService _speech;
  late final TtsService _tts;

  @override
  void initState() {
    super.initState();
    _speech = SpeechService();
    _speech.silenceTimeoutMs = 1000;
    _speech.onUpdate = _onSpeechUpdate;
    _speech.onAutoSend = _onSpeechAutoSend;
    _speech.onError = _onSpeechError;

    _tts = TtsService();

    _messages.add(_ChatMsg(
      role: 'assistant',
      content: '你好！我是${widget.aiName}，你的学习小助手。点击麦克风开始语音对话，或者说"我要做作业"我帮你打开摄像头～',
    ));

    // 延迟自动开启语音模式并播放欢迎语音
    Future.delayed(const Duration(milliseconds: 800), () {
      if (mounted && !_isListening) {
        // 先开启语音识别
        _autoStartListening();
        // 延迟后播放欢迎语音
        Future.delayed(const Duration(milliseconds: 500), () {
          if (mounted && _tts.isSupported) {
            _tts.speak('你好！我是${widget.aiName}，你的学习小助手。');
          }
        });
      }
    });
  }

  void _autoStartListening() {
    final info = _speech.getInfo();
    if (!info.supported) return;

    setState(() {
      _isListening = true;
      _speechText = '';
      _silenceMs = 0;
    });
    _speech.start(lang: 'zh-CN');
  }

  void _onSpeechUpdate(String text, int silenceMs) {
    if (!mounted) return;
    setState(() {
      _speechText = text;
      _silenceMs = silenceMs;
    });
  }

  void _onSpeechAutoSend(String text) {
    if (!mounted) return;
    // 重置状态，保持语音识别继续运行
    setState(() {
      _speechText = '';
      _silenceMs = 0;
    });
    if (text.trim().isNotEmpty) {
      _voiceMode = true;
      _sendMessage(text);
    }
  }

  void _onSpeechError(String error) {
    if (!mounted) return;
    setState(() {
      _isListening = false;
      _speechText = '';
      _silenceMs = 0;
    });
    String msg;
    if (error == 'NOT_SUPPORTED') {
      msg = _speech.getInfo().unsupportedReason;
    } else if (error == 'not-allowed') {
      msg = '请允许麦克风权限后重试';
    } else {
      msg = '语音识别出错: $error';
    }
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg), duration: const Duration(seconds: 4)));
  }

  void _toggleListening() {
    _tts.stop();
    if (_isListening) {
      // Manual stop: grab text and send
      final text = _speech.getText();
      _speech.stop();
      setState(() {
        _isListening = false;
        _speechText = '';
        _silenceMs = 0;
      });
      if (text.trim().isNotEmpty) {
        _voiceMode = true;
        _sendMessage(text);
      }
    } else {
      final info = _speech.getInfo();
      if (!info.supported) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(info.unsupportedReason), duration: const Duration(seconds: 5)),
        );
        return;
      }
      setState(() {
        _isListening = true;
        _speechText = '';
        _silenceMs = 0;
      });
      _speech.start(lang: 'zh-CN');
    }
  }

  Future<void> _sendMessage(String text) async {
    if (text.trim().isEmpty || _isSending) return;
    final content = text.trim();
    final wasVoice = _voiceMode;
    _inputCtrl.clear();

    // 语音模式下不关闭语音识别
    // if (_isListening) {
    //   _speech.stop();
    //   setState(() {
    //     _isListening = false;
    //     _speechText = '';
    //   });
    // }

    setState(() {
      _messages.add(_ChatMsg(role: 'user', content: content));
      _isSending = true;
    });
    _scrollToBottom();

    try {
      final result = await ApiService().sendChatMessage(widget.sessionId, content, scene: 'chat');
      if (mounted) {
        final reply = result['reply'] ?? '';
        setState(() {
          _messages.add(_ChatMsg(role: 'assistant', content: reply));
        });
        _scrollToBottom();

        // 语音模式下自动播放AI回复，但不关闭语音识别
        if (wasVoice && reply.isNotEmpty && _tts.isSupported) {
          _tts.speak(reply);
        }

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
      // 保持语音模式
      // _voiceMode = false;
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

  String get _listeningStatus {
    if (_speechText.isEmpty) return '正在听你说话...（1秒停顿后自动发送）';
    if (_silenceMs > 0) {
      final remain = ((_speech.silenceTimeoutMs - _silenceMs) / 1000).clamp(0.0, 9.9).toStringAsFixed(1);
      return '${remain}秒后自动发送';
    }
    return '识别中...';
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Voice recognition banner (separate from input field)
        if (_isListening)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            decoration: BoxDecoration(
              color: AppTheme.primaryColor.withOpacity(0.06),
              border: Border(bottom: BorderSide(color: AppTheme.primaryColor.withOpacity(0.15))),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Row(
                  children: [
                    Icon(
                      _speechText.isEmpty ? Icons.mic : Icons.graphic_eq,
                      color: _silenceMs > 0 ? Colors.orange : AppTheme.errorColor,
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        _listeningStatus,
                        style: TextStyle(
                          color: _silenceMs > 0 ? Colors.orange : AppTheme.textSecondary,
                          fontSize: 12,
                          fontWeight: _silenceMs > 0 ? FontWeight.bold : FontWeight.normal,
                        ),
                      ),
                    ),
                    if (_speechText.isNotEmpty)
                      TextButton(
                        onPressed: _toggleListening,
                        child: const Text('立即发送', style: TextStyle(fontWeight: FontWeight.bold)),
                      )
                    else
                      TextButton(
                        onPressed: () {
                          _speech.stop();
                          setState(() {
                            _isListening = false;
                            _speechText = '';
                          });
                        },
                        child: const Text('取消'),
                      ),
                  ],
                ),
                if (_speechText.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(top: 6, left: 28, right: 8),
                    child: Text(
                      _speechText,
                      style: const TextStyle(fontSize: 16, color: AppTheme.textPrimary, height: 1.4),
                      maxLines: 5,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
              ],
            ),
          ),
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
                boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 4, offset: const Offset(0, 2))],
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
            color: AppTheme.primaryColor.withOpacity(0.6),
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
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 8, offset: const Offset(0, -2))],
      ),
      child: Row(
        children: [
          IconButton(
            icon: Icon(
              _isListening ? Icons.stop_circle : Icons.mic_none,
              color: _isListening ? AppTheme.errorColor : AppTheme.primaryColor,
              size: 28,
            ),
            onPressed: _toggleListening,
            tooltip: _isListening ? '停止语音' : '语音输入',
          ),
          Expanded(
            child: TextField(
              controller: _inputCtrl,
              decoration: InputDecoration(
                hintText: '语音对话中...或输入文字消息',
                hintStyle: TextStyle(color: Colors.grey[400]),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(24),
                  borderSide: BorderSide(color: Colors.grey[300]!),
                ),
                contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                filled: true,
                fillColor: Colors.grey[50],
              ),
              onSubmitted: (t) {
                _voiceMode = false;
                _sendMessage(t);
              },
              textInputAction: TextInputAction.send,
            ),
          ),
          const SizedBox(width: 4),
          if (_tts.isSpeaking)
            IconButton(
              icon: const Icon(Icons.stop, color: AppTheme.errorColor),
              tooltip: '停止朗读',
              onPressed: () => setState(() => _tts.stop()),
            )
          else
            IconButton(
              icon: const Icon(Icons.send_rounded, color: AppTheme.primaryColor),
              onPressed: () {
                _voiceMode = false;
                _sendMessage(_inputCtrl.text);
              },
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
    _speech.dispose();
    _tts.dispose();
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
          color: AppTheme.primaryColor.withOpacity(0.1),
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
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 8, offset: const Offset(0, -2))],
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
