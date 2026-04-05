import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../config/app_config.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;

  late Dio _dio;
  String? _token;

  ApiService._internal() {
    _dio = Dio(BaseOptions(
      baseUrl: AppConfig.apiBaseUrl,
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 30),
      headers: {'Content-Type': 'application/json'},
    ));

    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        if (_token != null) {
          options.headers['Authorization'] = 'Bearer $_token';
        }
        return handler.next(options);
      },
      onError: (error, handler) {
        if (error.response?.statusCode == 401) {
          clearToken();
        }
        return handler.next(error);
      },
    ));
  }

  Future<void> loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('access_token');
  }

  Future<void> setToken(String token) async {
    _token = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('access_token', token);
  }

  Future<void> clearToken() async {
    _token = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
  }

  String? get token => _token;
  bool get isAuthenticated => _token != null;

  // === 认证 ===
  Future<Map<String, dynamic>> register(String username, String password, {String? nickname}) async {
    final resp = await _dio.post('/auth/register', data: {
      'username': username,
      'password': password,
      'nickname': nickname ?? username,
    });
    return resp.data;
  }

  Future<Map<String, dynamic>> login(String username, String password, String deviceType, {String? deviceName}) async {
    final resp = await _dio.post('/auth/login', data: {
      'username': username,
      'password': password,
      'device_type': deviceType,
      'device_name': deviceName ?? '',
    });
    return resp.data;
  }

  Future<void> logout() async {
    await _dio.post('/auth/logout');
    await clearToken();
  }

  Future<Map<String, dynamic>> getMe() async {
    final resp = await _dio.get('/auth/me');
    return resp.data;
  }

  // === 试题（DeepSeek Vision 多模态识别）===
  Future<Map<String, dynamic>> ocrRecognize(String imageBase64, {bool detectHandwriting = true}) async {
    final resp = await _dio.post('/questions/ocr', data: {
      'image_base64': imageBase64,
      'detect_handwriting': detectHandwriting,
    });
    return resp.data;
  }

  /// 直接看图批改：发送图片给DeepSeek Vision，一步完成识别+批改
  Future<Map<String, dynamic>> visionCorrect(String imageBase64, {String questionText = ''}) async {
    final resp = await _dio.post('/questions/vision-correct', data: {
      'image_base64': imageBase64,
      'question_text': questionText,
    });
    return resp.data;
  }

  Future<Map<String, dynamic>> detectFingerPoint(String payload, List<Map<String, dynamic>> regions) async {
    final resp = await _dio.post('/questions/finger-point', data: {
      'image_base64': payload,
      'question_regions': regions,
    });
    return resp.data;
  }

  Future<Map<String, dynamic>> correctQuestion(int questionId) async {
    final resp = await _dio.post('/questions/$questionId/correct');
    return resp.data;
  }

  Future<Map<String, dynamic>> explainQuestion(int questionId) async {
    final resp = await _dio.post('/questions/$questionId/explain');
    return resp.data;
  }

  Future<Map<String, dynamic>> generateSimilar(int questionId, {int count = 3}) async {
    final resp = await _dio.post('/questions/$questionId/similar', queryParameters: {'count': count});
    return resp.data;
  }

  Future<List<dynamic>> getSessionQuestions(String sessionId) async {
    final resp = await _dio.get('/questions/session/$sessionId');
    return resp.data;
  }

  // === 错题集 ===
  Future<Map<String, dynamic>> generateErrorBook(String sessionId, {String subject = 'other'}) async {
    final resp = await _dio.post('/error-books/generate', queryParameters: {
      'session_id': sessionId,
      'subject': subject,
    });
    return resp.data;
  }

  Future<List<dynamic>> listErrorBooks({String? status}) async {
    final resp = await _dio.get('/error-books/', queryParameters: {
      if (status != null) 'status': status,
    });
    return resp.data;
  }

  Future<Map<String, dynamic>> getErrorBook(int id) async {
    final resp = await _dio.get('/error-books/$id');
    return resp.data;
  }

  Future<Map<String, dynamic>> approveErrorBook(int id, bool approved, {String? reason}) async {
    final resp = await _dio.post('/error-books/$id/approve', data: {
      'approved': approved,
      'rejection_reason': reason,
    });
    return resp.data;
  }

  // === 权限 ===
  Future<Map<String, dynamic>> getPermissions() async {
    final resp = await _dio.get('/permissions/');
    return resp.data;
  }

  Future<Map<String, dynamic>> updatePermissions(Map<String, dynamic> data) async {
    final resp = await _dio.put('/permissions/', data: data);
    return resp.data;
  }

  // === 同步 ===
  Future<Map<String, dynamic>> getDeviceStatus() async {
    final resp = await _dio.get('/sync/device-status');
    return resp.data;
  }

  Future<Map<String, dynamic>> getVideoCallToken() async {
    final resp = await _dio.post('/sync/video-call-token');
    return resp.data;
  }

  // === 学习记录 ===
  Future<Map<String, dynamic>> getStudyRecords({int limit = 50, int offset = 0}) async {
    final resp = await _dio.get('/study-records/', queryParameters: {
      'limit': limit,
      'offset': offset,
    });
    return resp.data;
  }

  // === 对话 ===
  Future<Map<String, dynamic>> sendChatMessage(String sessionId, String content, {String scene = 'chat'}) async {
    final resp = await _dio.post('/chat/message', data: {
      'session_id': sessionId,
      'content': content,
      'scene': scene,
    });
    return resp.data;
  }

  Future<List<dynamic>> getChatHistory(String sessionId, {int limit = 50}) async {
    final resp = await _dio.get('/chat/history/$sessionId', queryParameters: {'limit': limit});
    return resp.data;
  }

  // === 省市区 ===
  Future<List<String>> getProvinces() async {
    final resp = await _dio.get('/regions/provinces');
    return List<String>.from(resp.data);
  }

  Future<List<String>> getCities(String province) async {
    final resp = await _dio.get('/regions/cities', queryParameters: {'province': province});
    return List<String>.from(resp.data);
  }

  Future<List<String>> getDistricts(String province, String city) async {
    final resp = await _dio.get('/regions/districts', queryParameters: {'province': province, 'city': city});
    return List<String>.from(resp.data);
  }

  // === 初始化 ===
  Future<Map<String, dynamic>> setupStudent({
    required int grade,
    required String province,
    required String city,
    required String district,
    String aiName = '小智',
    String aiVoice = 'gentle_female',
    String aiSpeed = 'medium',
  }) async {
    final resp = await _dio.post('/init/setup', data: {
      'grade': grade,
      'province': province,
      'city': city,
      'district': district,
      'ai_name': aiName,
      'ai_voice': aiVoice,
      'ai_speed': aiSpeed,
    });
    return resp.data;
  }

  Future<Map<String, dynamic>?> getProfile() async {
    final resp = await _dio.get('/init/profile');
    if (resp.statusCode == 200 && resp.data != null) return resp.data;
    return null;
  }

  Future<Map<String, dynamic>> updateAIConfig({String? aiName, String? aiVoice, String? aiSpeed}) async {
    final resp = await _dio.put('/init/ai-config', data: {
      if (aiName != null) 'ai_name': aiName,
      if (aiVoice != null) 'ai_voice': aiVoice,
      if (aiSpeed != null) 'ai_speed': aiSpeed,
    });
    return resp.data;
  }

  // === TTS声音 ===
  Future<List<dynamic>> getTTSVoices() async {
    final resp = await _dio.get('/tts/voices');
    return resp.data;
  }
}
