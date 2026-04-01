class AppConfig {
  static const String appName = '学习指认AI';
  static const String serverHost = '101.201.244.150';
  static const String apiBaseUrl = 'http://$serverHost/api/v1';
  static const String wsBaseUrl = 'ws://$serverHost/ws';

  static const int wsReconnectDelay = 3; // seconds
  static const int fingerDwellThreshold = 1000; // milliseconds
  static const int screenShareFps = 15;

  static String agoraAppId = '';
}
