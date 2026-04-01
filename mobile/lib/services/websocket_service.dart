import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../config/app_config.dart';
import 'api_service.dart';

typedef WsMessageHandler = void Function(Map<String, dynamic> message);

class WebSocketService {
  static final WebSocketService _instance = WebSocketService._internal();
  factory WebSocketService() => _instance;

  WebSocketChannel? _channel;
  StreamSubscription? _subscription;
  Timer? _pingTimer;
  Timer? _reconnectTimer;
  bool _isConnected = false;
  String? _deviceType;

  final Map<String, List<WsMessageHandler>> _handlers = {};

  WebSocketService._internal();

  bool get isConnected => _isConnected;

  Future<void> connect(String deviceType) async {
    _deviceType = deviceType;
    final token = ApiService().token;
    if (token == null) return;

    final uri = Uri.parse(
        '${AppConfig.wsBaseUrl}?token=$token&device_type=$deviceType');

    try {
      _channel = WebSocketChannel.connect(uri);
      _isConnected = true;

      _subscription = _channel!.stream.listen(
        (data) {
          try {
            final message = jsonDecode(data as String) as Map<String, dynamic>;
            _dispatchMessage(message);
          } catch (_) {}
        },
        onDone: () {
          _isConnected = false;
          _scheduleReconnect();
        },
        onError: (_) {
          _isConnected = false;
          _scheduleReconnect();
        },
      );

      _startPing();
    } catch (_) {
      _isConnected = false;
      _scheduleReconnect();
    }
  }

  void disconnect() {
    _pingTimer?.cancel();
    _reconnectTimer?.cancel();
    _subscription?.cancel();
    _channel?.sink.close();
    _isConnected = false;
  }

  void send(String type, Map<String, dynamic> payload, {String targetDevice = 'all'}) {
    if (!_isConnected || _channel == null) return;
    _channel!.sink.add(jsonEncode({
      'type': type,
      'payload': payload,
      'target_device': targetDevice,
    }));
  }

  void on(String type, WsMessageHandler handler) {
    _handlers.putIfAbsent(type, () => []).add(handler);
  }

  void off(String type, [WsMessageHandler? handler]) {
    if (handler != null) {
      _handlers[type]?.remove(handler);
    } else {
      _handlers.remove(type);
    }
  }

  void _dispatchMessage(Map<String, dynamic> message) {
    final type = message['type'] as String?;
    if (type == null) return;

    final handlers = _handlers[type];
    if (handlers != null) {
      for (final handler in handlers) {
        handler(message);
      }
    }

    // 通配符监听
    final allHandlers = _handlers['*'];
    if (allHandlers != null) {
      for (final handler in allHandlers) {
        handler(message);
      }
    }
  }

  void _startPing() {
    _pingTimer?.cancel();
    _pingTimer = Timer.periodic(const Duration(seconds: 30), (_) {
      send('ping', {});
    });
  }

  void _scheduleReconnect() {
    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(
      Duration(seconds: AppConfig.wsReconnectDelay),
      () {
        if (_deviceType != null && !_isConnected) {
          connect(_deviceType!);
        }
      },
    );
  }
}
