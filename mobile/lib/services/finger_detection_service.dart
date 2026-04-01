import 'dart:async';
import '../config/app_config.dart';
import 'api_service.dart';

/// 端侧手指指认服务
/// 检测手指位置并映射到题目区域
class FingerDetectionService {
  static final FingerDetectionService _instance = FingerDetectionService._internal();
  factory FingerDetectionService() => _instance;

  Timer? _dwellTimer;
  int? _lastPointedQuestionId;
  DateTime? _pointStartTime;
  void Function(int questionId)? onQuestionSelected;

  FingerDetectionService._internal();

  /// 处理从摄像头帧中检测到的指尖坐标
  /// tipX, tipY 为归一化坐标 (0.0 ~ 1.0)
  Future<void> processFingerTip(
    double tipX,
    double tipY,
    List<Map<String, dynamic>> questionRegions,
  ) async {
    // 本地匹配题目区域
    final matched = _matchLocalRegion(tipX, tipY, questionRegions);

    if (matched != null) {
      final qid = matched['question_id'] as int;
      if (qid == _lastPointedQuestionId) {
        // 持续指向同一题目，检查停留时间
        if (_pointStartTime != null) {
          final elapsed = DateTime.now().difference(_pointStartTime!).inMilliseconds;
          if (elapsed >= AppConfig.fingerDwellThreshold) {
            onQuestionSelected?.call(qid);
            _resetDwell();
          }
        }
      } else {
        _lastPointedQuestionId = qid;
        _pointStartTime = DateTime.now();
      }
    } else {
      _resetDwell();
    }
  }

  /// 备用方案：发送到服务端检测
  Future<Map<String, dynamic>?> detectViaServer(
    String imageBase64,
    List<Map<String, dynamic>> questionRegions,
  ) async {
    final result = await ApiService().detectFingerPoint(imageBase64, questionRegions);
    if (result['detected'] == true && result['pointed_question_id'] != null) {
      return result;
    }
    return null;
  }

  Map<String, dynamic>? _matchLocalRegion(
    double tipX,
    double tipY,
    List<Map<String, dynamic>> regions,
  ) {
    for (final region in regions) {
      final bbox = region['bbox'] as Map<String, dynamic>? ?? {};
      final left = (bbox['left'] as num?)?.toDouble() ?? 0;
      final top = (bbox['top'] as num?)?.toDouble() ?? 0;
      final width = (bbox['width'] as num?)?.toDouble() ?? 0;
      final height = (bbox['height'] as num?)?.toDouble() ?? 0;

      if (tipX >= left && tipX <= left + width && tipY >= top && tipY <= top + height) {
        return region;
      }
    }
    return null;
  }

  void _resetDwell() {
    _lastPointedQuestionId = null;
    _pointStartTime = null;
  }

  void dispose() {
    _dwellTimer?.cancel();
    _resetDwell();
  }
}
