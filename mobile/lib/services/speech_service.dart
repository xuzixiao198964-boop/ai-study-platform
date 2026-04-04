import 'dart:async';
import 'dart:convert';
import 'dart:js_interop';
import 'package:flutter/foundation.dart';

@JS('sttGetInfo')
external JSString _sttGetInfo();

@JS('sttStart')
external void _sttStart(JSString lang);

@JS('sttStop')
external void _sttStop();

@JS('sttPoll')
external JSString _sttPoll();

@JS('sttReset')
external void _sttReset();

class SpeechInfo {
  final bool supported;
  final bool secureContext;
  final String protocol;
  final String? jsError;

  SpeechInfo({
    required this.supported,
    required this.secureContext,
    required this.protocol,
    this.jsError,
  });

  String get unsupportedReason {
    if (jsError != null) return '语音服务初始化失败: $jsError';
    if (!secureContext) {
      return '语音识别需要 HTTPS 安全连接，当前为 HTTP ($protocol)。请使用 HTTPS 访问。';
    }
    return '此浏览器不支持语音识别';
  }
}

class SpeechService {
  Timer? _pollTimer;
  bool _active = false;

  /// Silence duration (ms) before auto-sending. Default 1.0s.
  int silenceTimeoutMs = 1000;

  /// Called with (currentText, silenceMs). silenceMs=0 means still talking.
  void Function(String text, int silenceMs)? onUpdate;

  /// Called with the final text when silence timeout is reached.
  void Function(String text)? onAutoSend;

  /// Called on error.
  void Function(String error)? onError;

  bool get isActive => _active;

  SpeechInfo getInfo() {
    if (!kIsWeb) {
      return SpeechInfo(supported: false, secureContext: false, protocol: 'n/a');
    }
    try {
      final result = _sttGetInfo();
      if (result == null) {
        return SpeechInfo(
          supported: false,
          secureContext: false,
          protocol: '',
          jsError: 'sttGetInfo returned null',
        );
      }
      final data = json.decode(result.toDart) as Map<String, dynamic>;
      return SpeechInfo(
        supported: data['supported'] == true,
        secureContext: data['secureContext'] == true,
        protocol: data['protocol']?.toString() ?? '',
      );
    } catch (e) {
      return SpeechInfo(
        supported: false,
        secureContext: false,
        protocol: '',
        jsError: e.toString(),
      );
    }
  }

  bool get isSupported => getInfo().supported;

  void start({String lang = 'zh-CN'}) {
    if (!kIsWeb || _active) return;
    _active = true;

    try {
      _sttReset();
      _sttStart(lang.toJS);
    } catch (e) {
      _active = false;
      onError?.call('START_FAILED: $e');
      return;
    }

    _pollTimer?.cancel();
    _pollTimer = Timer.periodic(const Duration(milliseconds: 200), _poll);
  }

  /// Returns the current recognized text (may be empty).
  String getText() {
    if (!kIsWeb) return '';
    try {
      final state = json.decode(_sttPoll().toDart) as Map<String, dynamic>;
      return (state['text'] as String?) ?? '';
    } catch (_) {
      return '';
    }
  }

  void _poll(Timer t) {
    if (!_active) {
      t.cancel();
      return;
    }
    try {
      final state = json.decode(_sttPoll().toDart) as Map<String, dynamic>;
      final text = (state['text'] as String?) ?? '';
      final silenceMs = (state['silenceMs'] as num?)?.toInt() ?? 0;
      final hasText = state['hasText'] == true;
      final error = state['error'];

      if (error != null) {
        _active = false;
        _pollTimer?.cancel();
        onError?.call(error.toString());
        return;
      }

      // Update UI with current text and silence duration
      onUpdate?.call(text, hasText ? silenceMs : 0);

      // Auto-send: text exists AND silence exceeds threshold
      if (hasText && silenceMs >= silenceTimeoutMs) {
        stop();
        onAutoSend?.call(text);
      }
    } catch (_) {}
  }

  void stop() {
    _active = false;
    _pollTimer?.cancel();
    if (!kIsWeb) return;
    try {
      _sttStop();
    } catch (_) {}
  }

  void reset() {
    if (!kIsWeb) return;
    try {
      _sttReset();
    } catch (_) {}
  }

  void dispose() {
    stop();
    onUpdate = null;
    onAutoSend = null;
    onError = null;
  }
}
