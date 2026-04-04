import 'dart:convert';
import 'dart:js_interop';
import 'package:flutter/foundation.dart';

@JS('ttsSpeak')
external void _ttsSpeak(JSString text, JSNumber rate, JSNumber pitch);

@JS('ttsStop')
external void _ttsStop();

@JS('ttsSetVoice')
external void _ttsSetVoice(JSString voiceUri);

@JS('ttsGetVoices')
external JSString _ttsGetVoices();

@JS('ttsIsSpeaking')
external JSBoolean _ttsIsSpeaking();

@JS('ttsIsSupported')
external JSBoolean _ttsIsSupported();

class TtsVoice {
  final String name;
  final String lang;
  final String uri;
  final bool isDefault;

  TtsVoice({
    required this.name,
    required this.lang,
    required this.uri,
    this.isDefault = false,
  });

  @override
  String toString() => '$name ($lang)';
}

class TtsService {
  double rate = 1.0;
  double pitch = 1.0;
  String? _selectedVoiceUri;

  bool get isSupported {
    if (!kIsWeb) return false;
    try {
      return _ttsIsSupported().toDart;
    } catch (_) {
      return false;
    }
  }

  bool get isSpeaking {
    if (!kIsWeb) return false;
    try {
      return _ttsIsSpeaking().toDart;
    } catch (_) {
      return false;
    }
  }

  List<TtsVoice> getVoices() {
    if (!kIsWeb) return [];
    try {
      final data = json.decode(_ttsGetVoices().toDart) as List;
      return data
          .map((v) => TtsVoice(
                name: v['name'] ?? '',
                lang: v['lang'] ?? '',
                uri: v['uri'] ?? '',
                isDefault: v['isDefault'] == true,
              ))
          .toList();
    } catch (_) {
      return [];
    }
  }

  void setVoice(String voiceUri) {
    _selectedVoiceUri = voiceUri;
    if (kIsWeb) {
      try {
        _ttsSetVoice(voiceUri.toJS);
      } catch (_) {}
    }
  }

  String? get selectedVoiceUri => _selectedVoiceUri;

  void speak(String text) {
    if (!kIsWeb || text.trim().isEmpty) return;
    try {
      _ttsSpeak(text.toJS, rate.toJS, pitch.toJS);
    } catch (_) {}
  }

  void stop() {
    if (!kIsWeb) return;
    try {
      _ttsStop();
    } catch (_) {}
  }

  void dispose() {
    stop();
  }
}
