import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../providers/study_provider.dart';
import '../../providers/permission_provider.dart';
import '../../services/camera_service.dart';
import '../../services/finger_detection_service.dart';
import '../../services/websocket_service.dart';

class CameraScreen extends StatefulWidget {
  const CameraScreen({super.key});

  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  final CameraService _camera = CameraService();
  final FingerDetectionService _finger = FingerDetectionService();
  final WebSocketService _ws = WebSocketService();

  bool _isInitializing = true;
  bool _isFullScreen = false;
  int? _highlightedQuestionId;
  String _statusText = '正在初始化摄像头...';

  @override
  void initState() {
    super.initState();
    _initCamera();
    _finger.onQuestionSelected = _onFingerSelect;

    _ws.on('remote_cmd', _handleRemoteCommand);
  }

  Future<void> _initCamera() async {
    try {
      await _camera.initialize(useExternalCamera: true);
      setState(() {
        _isInitializing = false;
        _statusText = '摄像头已就绪，请将试题放在摄像头下';
      });
      context.read<StudyProvider>().setCameraActive(true);
    } catch (e) {
      setState(() {
        _isInitializing = false;
        _statusText = '摄像头初始化失败: $e';
      });
    }
  }

  void _onFingerSelect(int questionId) {
    setState(() => _highlightedQuestionId = questionId);
    context.read<StudyProvider>().selectQuestion(questionId);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('已选中第$questionId题'),
        duration: const Duration(seconds: 1),
        backgroundColor: AppTheme.accentColor,
      ),
    );
  }

  void _handleRemoteCommand(Map<String, dynamic> message) {
    final payload = message['payload'] as Map<String, dynamic>? ?? {};
    final cmd = payload['command'] as String?;
    if (cmd == 'focus_question') {
      final qid = payload['question_id'] as int?;
      if (qid != null) {
        setState(() => _highlightedQuestionId = qid);
        context.read<StudyProvider>().selectQuestion(qid);
      }
    } else if (cmd == 're_recognize') {
      _captureAndRecognize();
    }
  }

  Future<void> _captureAndRecognize() async {
    setState(() => _statusText = 'AI正在识别试题...');
    final base64 = await _camera.captureBase64();
    if (base64 != null) {
      await context.read<StudyProvider>().recognizeQuestions(base64);
      setState(() => _statusText = '识别完成');
    }
  }

  @override
  Widget build(BuildContext context) {
    final study = context.watch<StudyProvider>();
    final perm = context.watch<PermissionProvider>();

    return Scaffold(
      appBar: _isFullScreen
          ? null
          : AppBar(
              title: const Text('试题投屏'),
              actions: [
                IconButton(
                  icon: const Icon(Icons.fullscreen),
                  onPressed: () => setState(() => _isFullScreen = true),
                ),
              ],
            ),
      body: Column(
        children: [
          // 摄像头预览区
          Expanded(
            flex: 3,
            child: GestureDetector(
              onTap: _isFullScreen
                  ? () => setState(() => _isFullScreen = false)
                  : null,
              child: Stack(
                children: [
                  Container(
                    width: double.infinity,
                    color: Colors.black,
                    child: _isInitializing
                        ? const Center(child: CircularProgressIndicator(color: Colors.white))
                        : _camera.isInitialized && _camera.controller != null
                            ? const Center(
                                child: Text(
                                  '摄像头预览画面',
                                  style: TextStyle(color: Colors.white54, fontSize: 18),
                                ),
                              )
                            : Center(
                                child: Text(
                                  _statusText,
                                  style: const TextStyle(color: Colors.white70),
                                ),
                              ),
                  ),

                  // 指认指示器
                  if (_highlightedQuestionId != null)
                    Positioned(
                      top: 8,
                      left: 8,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                        decoration: BoxDecoration(
                          color: AppTheme.accentColor,
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          '已选中第$_highlightedQuestionId题',
                          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                        ),
                      ),
                    ),

                  // 状态栏
                  Positioned(
                    bottom: 0,
                    left: 0,
                    right: 0,
                    child: Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                          colors: [Colors.transparent, Colors.black.withOpacity(0.7)],
                        ),
                      ),
                      child: Text(
                        _statusText,
                        style: const TextStyle(color: Colors.white, fontSize: 13),
                        textAlign: TextAlign.center,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),

          // 操作面板
          if (!_isFullScreen)
            Container(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  // 处理状态
                  if (study.isProcessing)
                    const Padding(
                      padding: EdgeInsets.only(bottom: 12),
                      child: LinearProgressIndicator(),
                    ),

                  // 操作按钮
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: study.isProcessing ? null : _captureAndRecognize,
                          icon: const Icon(Icons.document_scanner, size: 20),
                          label: const Text('识别试题'),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: (study.selectedQuestionId != null && perm.aiAnswerEnabled)
                              ? () => _correctQuestion(study)
                              : null,
                          icon: const Icon(Icons.auto_fix_high, size: 20),
                          label: const Text('AI批改'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppTheme.accentColor,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: (study.selectedQuestionId != null && perm.aiExplanationEnabled)
                              ? () => _explainQuestion(study)
                              : null,
                          icon: const Icon(Icons.lightbulb_outline, size: 20),
                          label: const Text('AI讲解'),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: study.questions.isNotEmpty
                              ? () => _generateErrorBook(study)
                              : null,
                          icon: const Icon(Icons.book_outlined, size: 20),
                          label: const Text('生成错题集'),
                        ),
                      ),
                    ],
                  ),

                  if (!perm.aiAnswerEnabled)
                    const Padding(
                      padding: EdgeInsets.only(top: 8),
                      child: Text(
                        '家长已关闭AI解答权限',
                        style: TextStyle(color: AppTheme.warningColor, fontSize: 12),
                      ),
                    ),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Future<void> _correctQuestion(StudyProvider study) async {
    try {
      final result = await study.correctSelectedQuestion();
      if (result != null && mounted) {
        _showResultDialog(result.isCorrect ? '回答正确！' : '回答有误',
            result.isCorrect ? '继续加油！' : result.explanation);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('批改失败: $e'), backgroundColor: AppTheme.errorColor),
        );
      }
    }
  }

  Future<void> _explainQuestion(StudyProvider study) async {
    try {
      final result = await study.explainSelectedQuestion();
      if (result != null && mounted) {
        _showExplanationSheet(result);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('讲解获取失败: $e'), backgroundColor: AppTheme.errorColor),
        );
      }
    }
  }

  Future<void> _generateErrorBook(StudyProvider study) async {
    // 跳转或弹窗确认生成
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('正在生成错题集...'), backgroundColor: AppTheme.primaryColor),
    );
  }

  void _showResultDialog(String title, String content) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(title),
        content: Text(content),
        actions: [TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('知道了'))],
      ),
    );
  }

  void _showExplanationSheet(Map<String, dynamic> data) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => DraggableScrollableSheet(
        initialChildSize: 0.6,
        maxChildSize: 0.9,
        expand: false,
        builder: (_, scrollCtrl) => ListView(
          controller: scrollCtrl,
          padding: const EdgeInsets.all(24),
          children: [
            const Text('AI讲解', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            Text(data['explanation_text'] ?? '', style: const TextStyle(fontSize: 15, height: 1.6)),
            const SizedBox(height: 16),
            const Text('解题步骤', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Text(data['solution_steps'] ?? '', style: const TextStyle(fontSize: 14, height: 1.5)),
            const SizedBox(height: 16),
            if (data['tips'] != null) ...[
              const Text('易错提醒', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.warningColor)),
              const SizedBox(height: 8),
              ...((data['tips'] as List).map((t) => Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Icon(Icons.warning_amber, size: 16, color: AppTheme.warningColor),
                        const SizedBox(width: 8),
                        Expanded(child: Text(t.toString())),
                      ],
                    ),
                  ))),
            ],
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _camera.dispose();
    _finger.dispose();
    _ws.off('remote_cmd');
    super.dispose();
  }
}
