class AppConfig {
  static const String appName = '学习指认AI';
  static const String serverHost = '101.201.244.150';
  static const int serverPort = 8000;
  static const String apiBaseUrl = 'http://$serverHost:$serverPort/api/v1';
  static const String wsBaseUrl = 'ws://$serverHost:$serverPort/ws';

  static const int wsReconnectDelay = 3;
  static const int fingerDwellThreshold = 1000;
  static const int screenShareFps = 15;
  static const double silenceThreshold = 1.5;

  static String agoraAppId = '';
}
