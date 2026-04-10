import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user.dart';
import '../services/api_service.dart';
import '../services/websocket_service.dart';

enum DeviceRole { student, parent }

class AuthProvider extends ChangeNotifier {
  final ApiService _api = ApiService();
  final WebSocketService _ws = WebSocketService();

  User? _user;
  AuthToken? _authToken;
  DeviceRole _deviceRole = DeviceRole.student;
  bool _isLoading = false;
  String? _error;

  User? get user => _user;
  AuthToken? get authToken => _authToken;
  DeviceRole get deviceRole => _deviceRole;
  bool get isLoading => _isLoading;
  bool get isAuthenticated => _user != null;
  String? get error => _error;
  String get deviceType =>
      _deviceRole == DeviceRole.student ? 'student_ipad' : 'parent_android';

  Future<void> init() async {
    print('[AuthProvider] init() 开始');
    await _api.loadToken();
    print('[AuthProvider] loadToken完成, isAuthenticated=${_api.isAuthenticated}');

    if (_api.isAuthenticated) {
      try {
        print('[AuthProvider] 调用getMe()...');
        final data = await _api.getMe();
        _user = User.fromJson(data);
        print('[AuthProvider] getMe()成功, user=${_user?.username}');

        final prefs = await SharedPreferences.getInstance();
        final role = prefs.getString('device_role');
        _deviceRole = role == 'parent' ? DeviceRole.parent : DeviceRole.student;
        print('[AuthProvider] deviceRole=$_deviceRole');

        // WebSocket连接失败不应该影响登录状态
        try {
          await _ws.connect(deviceType);
          print('[AuthProvider] WebSocket连接成功');
        } catch (e) {
          print('[AuthProvider] WebSocket连接失败: $e');
        }
      } catch (e) {
        print('[AuthProvider] getMe()失败: $e');
        // getMe()失败，清除token
        await _api.clearToken();
      }
    }

    print('[AuthProvider] init()完成, isAuthenticated=$isAuthenticated');
    notifyListeners();
  }

  Future<bool> login(String username, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final data = await _api.login(username, password, deviceType);
      _authToken = AuthToken.fromJson(data);
      await _api.setToken(_authToken!.accessToken);

      final userData = await _api.getMe();
      _user = User.fromJson(userData);

      // WebSocket连接失败不应该影响登录
      try {
        await _ws.connect(deviceType);
      } catch (_) {
        // WebSocket连接失败，但登录仍然成功
      }

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = '登录失败，请检查用户名和密码';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> register(String username, String password, {String? nickname}) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final data = await _api.register(username, password, nickname: nickname);
      _authToken = AuthToken.fromJson(data);
      await _api.setToken(_authToken!.accessToken);

      final userData = await _api.getMe();
      _user = User.fromJson(userData);

      // WebSocket连接失败不应该影响注册
      try {
        await _ws.connect(deviceType);
      } catch (_) {
        // WebSocket连接失败，但注册仍然成功
      }

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = '注册失败，用户名可能已存在';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<void> logout() async {
    try {
      await _api.logout();
    } catch (_) {}
    _ws.disconnect();
    _user = null;
    _authToken = null;
    notifyListeners();
  }

  Future<void> setDeviceRole(DeviceRole role) async {
    _deviceRole = role;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('device_role', role == DeviceRole.parent ? 'parent' : 'student');
    notifyListeners();
  }
}
