class User {
  final int id;
  final String username;
  final String nickname;
  final String? avatarUrl;
  final bool isActive;

  User({
    required this.id,
    required this.username,
    required this.nickname,
    this.avatarUrl,
    this.isActive = true,
  });

  factory User.fromJson(Map<String, dynamic> json) => User(
        id: json['id'],
        username: json['username'],
        nickname: json['nickname'] ?? '',
        avatarUrl: json['avatar_url'],
        isActive: json['is_active'] ?? true,
      );
}

class AuthToken {
  final String accessToken;
  final int userId;
  final String username;
  final String nickname;
  final String deviceType;

  AuthToken({
    required this.accessToken,
    required this.userId,
    required this.username,
    required this.nickname,
    required this.deviceType,
  });

  factory AuthToken.fromJson(Map<String, dynamic> json) => AuthToken(
        accessToken: json['access_token'],
        userId: json['user_id'],
        username: json['username'],
        nickname: json['nickname'] ?? '',
        deviceType: json['device_type'],
      );
}
