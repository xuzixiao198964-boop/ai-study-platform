import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../providers/auth_provider.dart';
import '../../providers/study_provider.dart';
import '../../providers/permission_provider.dart';
import '../../services/api_service.dart';

class StudentHomeScreen extends StatefulWidget {
  const StudentHomeScreen({super.key});

  @override
  State<StudentHomeScreen> createState() => _StudentHomeScreenState();
}

class _StudentHomeScreenState extends State<StudentHomeScreen> {
  int _currentIndex = 0;

  @override
  void initState() {
    super.initState();
    context.read<PermissionProvider>().loadPermissions();
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('学习指认AI'),
        actions: [
          _buildOnlineIndicator(),
          IconButton(
            icon: const Icon(Icons.person_outline),
            onPressed: () => _showProfileSheet(context, auth),
          ),
        ],
      ),
      body: IndexedStack(
        index: _currentIndex,
        children: const [
          _StudyTab(),
          _ErrorBookTab(),
          _RecordsTab(),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (i) => setState(() => _currentIndex = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.camera_alt_outlined), selectedIcon: Icon(Icons.camera_alt), label: '学习'),
          NavigationDestination(icon: Icon(Icons.book_outlined), selectedIcon: Icon(Icons.book), label: '错题集'),
          NavigationDestination(icon: Icon(Icons.history_outlined), selectedIcon: Icon(Icons.history), label: '记录'),
        ],
      ),
    );
  }

  Widget _buildOnlineIndicator() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 8, height: 8,
            decoration: const BoxDecoration(color: AppTheme.correctColor, shape: BoxShape.circle),
          ),
          const SizedBox(width: 4),
          const Text('在线', style: TextStyle(fontSize: 12)),
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
              radius: 36, backgroundColor: AppTheme.primaryColor,
              child: Text((auth.user?.nickname ?? '学')[0], style: const TextStyle(fontSize: 28, color: Colors.white)),
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

class _StudyTab extends StatefulWidget {
  const _StudyTab();

  @override
  State<_StudyTab> createState() => _StudyTabState();
}

class _StudyTabState extends State<_StudyTab> {
  final ImagePicker _picker = ImagePicker();
  bool _isProcessing = false;
  Map<String, dynamic>? _lastResult;
  String? _capturedImageBase64;

  Future<void> _captureAndRecognize() async {
    final XFile? photo = await _picker.pickImage(source: ImageSource.camera, maxWidth: 1920, imageQuality: 85);
    if (photo == null) return;

    setState(() { _isProcessing = true; _lastResult = null; });

    try {
      final bytes = await photo.readAsBytes();
      final base64Str = base64Encode(bytes);
      setState(() => _capturedImageBase64 = base64Str);

      final result = await ApiService().visionCorrect(base64Str);
      setState(() => _lastResult = result);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('识别失败: $e')));
      }
    } finally {
      setState(() => _isProcessing = false);
    }
  }

  Future<void> _pickAndRecognize() async {
    final XFile? image = await _picker.pickImage(source: ImageSource.gallery, maxWidth: 1920, imageQuality: 85);
    if (image == null) return;

    setState(() { _isProcessing = true; _lastResult = null; });

    try {
      final bytes = await image.readAsBytes();
      final base64Str = base64Encode(bytes);
      setState(() => _capturedImageBase64 = base64Str);

      final result = await ApiService().visionCorrect(base64Str);
      setState(() => _lastResult = result);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('识别失败: $e')));
      }
    } finally {
      setState(() => _isProcessing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final perm = context.watch<PermissionProvider>();

    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          // 结果区域
          Expanded(
            flex: 3,
            child: Card(
              clipBehavior: Clip.antiAlias,
              child: Container(
                width: double.infinity,
                decoration: BoxDecoration(color: Colors.grey[50], borderRadius: BorderRadius.circular(16)),
                child: _isProcessing
                    ? const Center(child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          CircularProgressIndicator(),
                          SizedBox(height: 16),
                          Text('AI正在识别和批改...', style: TextStyle(color: Colors.grey)),
                        ],
                      ))
                    : _lastResult != null
                        ? _buildResultView()
                        : Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(Icons.camera_alt, size: 64, color: Colors.grey[400]),
                                const SizedBox(height: 16),
                                const Text('拍照或上传试卷', style: TextStyle(fontSize: 16, color: Colors.grey)),
                                const SizedBox(height: 8),
                                const Text('AI将自动识别题目并批改', style: TextStyle(fontSize: 13, color: Colors.grey)),
                                const SizedBox(height: 24),
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    ElevatedButton.icon(
                                      onPressed: _captureAndRecognize,
                                      icon: const Icon(Icons.camera_alt),
                                      label: const Text('拍照'),
                                    ),
                                    const SizedBox(width: 16),
                                    OutlinedButton.icon(
                                      onPressed: _pickAndRecognize,
                                      icon: const Icon(Icons.photo_library),
                                      label: const Text('相册'),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ),
              ),
            ),
          ),
          const SizedBox(height: 16),

          // 快捷操作
          Expanded(
            flex: 2,
            child: GridView.count(
              crossAxisCount: 3,
              mainAxisSpacing: 12,
              crossAxisSpacing: 12,
              children: [
                _QuickActionCard(icon: Icons.camera_alt, label: '拍照识题', color: AppTheme.primaryColor, onTap: _captureAndRecognize),
                _QuickActionCard(icon: Icons.photo_library, label: '相册选题', color: AppTheme.secondaryColor, onTap: _pickAndRecognize),
                _QuickActionCard(icon: Icons.auto_fix_high, label: 'AI批改', color: AppTheme.accentColor, enabled: perm.aiAnswerEnabled, onTap: _captureAndRecognize),
                _QuickActionCard(icon: Icons.lightbulb_outline, label: 'AI讲解', color: Colors.orange, enabled: perm.aiExplanationEnabled, onTap: () {}),
                _QuickActionCard(icon: Icons.book_outlined, label: '生成错题集', color: Colors.purple, onTap: () {}),
                _QuickActionCard(icon: Icons.video_call, label: '视频通话', color: Colors.teal, onTap: () {}),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildResultView() {
    final result = _lastResult!;
    final isCorrect = result['is_correct'] == true;
    final question = result['question_text'] ?? '';
    final answer = result['student_answer'] ?? '';
    final correctAnswer = result['correct_answer'] ?? '';
    final explanation = result['explanation'] ?? '';

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(isCorrect ? Icons.check_circle : Icons.cancel, color: isCorrect ? AppTheme.correctColor : AppTheme.errorColor, size: 32),
              const SizedBox(width: 8),
              Text(isCorrect ? '回答正确!' : '回答有误', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: isCorrect ? AppTheme.correctColor : AppTheme.errorColor)),
            ],
          ),
          const SizedBox(height: 16),
          const Text('题目：', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
          Text(question, style: const TextStyle(fontSize: 14)),
          const SizedBox(height: 12),
          const Text('你的答案：', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
          Text(answer, style: TextStyle(fontSize: 14, color: isCorrect ? AppTheme.correctColor : AppTheme.errorColor)),
          if (!isCorrect && correctAnswer.isNotEmpty) ...[
            const SizedBox(height: 12),
            const Text('正确答案：', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
            Text(correctAnswer, style: const TextStyle(fontSize: 14, color: AppTheme.correctColor)),
          ],
          if (explanation.isNotEmpty) ...[
            const SizedBox(height: 16),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(color: Colors.blue[50], borderRadius: BorderRadius.circular(8)),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('AI解析：', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: AppTheme.primaryColor)),
                  const SizedBox(height: 4),
                  Text(explanation, style: const TextStyle(fontSize: 14)),
                ],
              ),
            ),
          ],
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: _captureAndRecognize,
                  icon: const Icon(Icons.camera_alt),
                  label: const Text('继续拍照'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: _pickAndRecognize,
                  icon: const Icon(Icons.photo_library),
                  label: const Text('选择图片'),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _QuickActionCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;
  final bool enabled;

  const _QuickActionCard({
    required this.icon, required this.label, required this.color, required this.onTap, this.enabled = true,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: enabled ? 2 : 0,
      color: enabled ? Colors.white : Colors.grey[200],
      child: InkWell(
        onTap: enabled
            ? onTap
            : () => ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('家长已关闭该功能权限，请联系家长'))),
        borderRadius: BorderRadius.circular(16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 32, color: enabled ? color : Colors.grey),
            const SizedBox(height: 8),
            Text(label, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: enabled ? AppTheme.textPrimary : Colors.grey)),
          ],
        ),
      ),
    );
  }
}

class _ErrorBookTab extends StatelessWidget {
  const _ErrorBookTab();

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.book, size: 64, color: Colors.grey),
          SizedBox(height: 16),
          Text('错题集', style: TextStyle(fontSize: 18, color: Colors.grey)),
          SizedBox(height: 8),
          Text('完成学习后自动生成', style: TextStyle(color: Colors.grey)),
        ],
      ),
    );
  }
}

class _RecordsTab extends StatelessWidget {
  const _RecordsTab();

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.history, size: 64, color: Colors.grey),
          SizedBox(height: 16),
          Text('学习记录', style: TextStyle(fontSize: 18, color: Colors.grey)),
        ],
      ),
    );
  }
}
