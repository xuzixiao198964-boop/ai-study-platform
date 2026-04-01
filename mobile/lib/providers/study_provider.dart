import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/websocket_service.dart';

class StudyProvider extends ChangeNotifier {
  final ApiService _api = ApiService();
  final WebSocketService _ws = WebSocketService();

  String _sessionId = '';
  bool _isProcessing = false;
  bool _isCameraActive = false;
  String? _lastOcrRawText;

  String get sessionId => _sessionId;
  bool get isProcessing => _isProcessing;
  bool get isCameraActive => _isCameraActive;
  String? get lastOcrRawText => _lastOcrRawText;

  void startNewSession() {
    _sessionId = DateTime.now().millisecondsSinceEpoch.toString();
    _lastOcrRawText = null;
    notifyListeners();
  }

  void setCameraActive(bool active) {
    _isCameraActive = active;
    notifyListeners();
  }

  Future<void> recognizeQuestions(String imageBase64) async {
    _isProcessing = true;
    notifyListeners();

    try {
      final result = await _api.ocrRecognize(imageBase64);
      _lastOcrRawText = result['raw_text'];

      _ws.send('screen_update', {
        'session_id': _sessionId,
        'ocr_text': _lastOcrRawText,
        'question_count': (result['questions'] as List).length,
      }, targetDevice: 'parent_android');
    } catch (e) {
      debugPrint('OCR failed: $e');
    }

    _isProcessing = false;
    notifyListeners();
  }
}
