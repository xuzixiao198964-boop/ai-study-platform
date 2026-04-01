import 'package:flutter/material.dart';
import '../models/permission.dart';
import '../services/api_service.dart';
import '../services/websocket_service.dart';

class PermissionProvider extends ChangeNotifier {
  final ApiService _api = ApiService();
  final WebSocketService _ws = WebSocketService();

  Permission? _permission;
  bool _isLoading = false;

  Permission? get permission => _permission;
  bool get isLoading => _isLoading;
  bool get aiAnswerEnabled => _permission?.aiAnswerEnabled ?? true;
  bool get aiExplanationEnabled => _permission?.aiExplanationEnabled ?? true;

  PermissionProvider() {
    _ws.on('permission_changed', _onPermissionChanged);
  }

  void _onPermissionChanged(Map<String, dynamic> message) {
    final payload = message['payload'] as Map<String, dynamic>?;
    if (payload != null) {
      _permission = Permission.fromJson(payload);
      notifyListeners();
    }
  }

  Future<void> loadPermissions() async {
    _isLoading = true;
    notifyListeners();

    try {
      final data = await _api.getPermissions();
      _permission = Permission.fromJson(data);
    } catch (_) {}

    _isLoading = false;
    notifyListeners();
  }

  Future<bool> updatePermissions({
    bool? aiAnswerEnabled,
    bool? aiExplanationEnabled,
    bool? aiSimilarQuestionsEnabled,
  }) async {
    try {
      final data = <String, dynamic>{};
      if (aiAnswerEnabled != null) data['ai_answer_enabled'] = aiAnswerEnabled;
      if (aiExplanationEnabled != null) data['ai_explanation_enabled'] = aiExplanationEnabled;
      if (aiSimilarQuestionsEnabled != null) data['ai_similar_questions_enabled'] = aiSimilarQuestionsEnabled;

      final result = await _api.updatePermissions(data);
      _permission = Permission.fromJson(result);
      notifyListeners();
      return true;
    } catch (_) {
      return false;
    }
  }

  @override
  void dispose() {
    _ws.off('permission_changed');
    super.dispose();
  }
}
