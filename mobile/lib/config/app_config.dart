import 'package:flutter/foundation.dart' show kIsWeb;

class AppConfig {
  static const String appName = '学习指认AI';
  static const String serverHost = '45.78.5.184';
  static const int serverPort = 8000;

  static String get _scheme {
    if (!kIsWeb) return 'http';
    final pageScheme = Uri.base.scheme;
    return pageScheme == 'https' ? 'https' : 'http';
  }

  static String get _wsScheme => _scheme == 'https' ? 'wss' : 'ws';

  static String get apiBaseUrl => '$_scheme://$serverHost:$serverPort/api/v1';
  static String get wsBaseUrl => '$_wsScheme://$serverHost:$serverPort/ws';

  static const int wsReconnectDelay = 3;
  static const int fingerDwellThreshold = 1000;
  static const int screenShareFps = 15;
  static const double silenceThreshold = 1.5;

  static String agoraAppId = '';
}
