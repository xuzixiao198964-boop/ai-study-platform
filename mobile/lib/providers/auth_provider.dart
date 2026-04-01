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
  bool get isAuthenticated => _authToken != null;
  String? get error => _error;
  String get deviceType =>
      _deviceRole == DeviceRole.student ? 'student_ipad' : 'parent_android';

  Future<void> init() async {
    await _api.loadToken();
    if (_api.isAuthenticated) {
      try {
        final data = await _api.getMe();
        _user = User.fromJson(data);

        final prefs = await SharedPreferences.getInstance();
        final role = prefs.getString('device_role');
        _deviceRole = role == 'parent' ? DeviceRole.parent : DeviceRole.student;

        await _ws.connect(deviceType);
      } catch (_) {
        await _api.clearToken();
      }
    }
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

      await _ws.connect(deviceType);

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
