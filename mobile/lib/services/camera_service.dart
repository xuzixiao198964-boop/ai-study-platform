import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';
import 'package:camera/camera.dart';

class CameraService {
  static final CameraService _instance = CameraService._internal();
  factory CameraService() => _instance;

  CameraController? _controller;
  List<CameraDescription> _cameras = [];
  bool _isInitialized = false;
  StreamController<CameraImage>? _frameStream;

  CameraService._internal();

  bool get isInitialized => _isInitialized;
  CameraController? get controller => _controller;

  Future<void> initialize({bool useExternalCamera = true}) async {
    _cameras = await availableCameras();
    if (_cameras.isEmpty) return;

    // 优先使用外接USB摄像头（通常排在列表后面）
    CameraDescription selectedCamera = _cameras.first;
    if (useExternalCamera && _cameras.length > 1) {
      selectedCamera = _cameras.last;
    }

    _controller = CameraController(
      selectedCamera,
      ResolutionPreset.high,
      enableAudio: false,
      imageFormatGroup: ImageFormatGroup.jpeg,
    );

    await _controller!.initialize();
    _isInitialized = true;
  }

  Future<String?> captureBase64() async {
    if (!_isInitialized || _controller == null) return null;
    final file = await _controller!.takePicture();
    final bytes = await file.readAsBytes();
    return base64Encode(bytes);
  }

  void startFrameStream(void Function(CameraImage) onFrame) {
    if (!_isInitialized || _controller == null) return;
    _controller!.startImageStream(onFrame);
  }

  void stopFrameStream() {
    if (!_isInitialized || _controller == null) return;
    _controller!.stopImageStream();
  }

  Future<void> dispose() async {
    await _controller?.dispose();
    _isInitialized = false;
  }

  List<CameraDescription> get availableCameraList => _cameras;
}
