import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../providers/auth_provider.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _usernameCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  bool _isRegister = false;
  bool _obscurePassword = true;

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    final size = MediaQuery.of(context).size;

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [AppTheme.primaryColor, AppTheme.secondaryColor],
          ),
        ),
        child: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(32),
              child: Column(
                children: [
                  const Icon(Icons.school_rounded, size: 80, color: Colors.white),
                  const SizedBox(height: 16),
                  const Text(
                    '学习指认AI',
                    style: TextStyle(
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    auth.deviceRole == DeviceRole.student ? '学生端' : '家长端',
                    style: const TextStyle(fontSize: 16, color: Colors.white70),
                  ),
                  const SizedBox(height: 40),

                  // 角色切换
                  Container(
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      children: [
                        _buildRoleTab('学生端', DeviceRole.student, auth),
                        _buildRoleTab('家长端', DeviceRole.parent, auth),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),

                  // 登录表单
                  Card(
                    elevation: 8,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                    child: Padding(
                      padding: const EdgeInsets.all(24),
                      child: Form(
                        key: _formKey,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            Text(
                              _isRegister ? '注册新账号' : '登录',
                              style: const TextStyle(
                                fontSize: 22,
                                fontWeight: FontWeight.bold,
                                color: AppTheme.textPrimary,
                              ),
                              textAlign: TextAlign.center,
                            ),
                            const SizedBox(height: 24),
                            TextFormField(
                              controller: _usernameCtrl,
                              decoration: const InputDecoration(
                                labelText: '用户名',
                                prefixIcon: Icon(Icons.person_outline),
                              ),
                              validator: (v) => (v == null || v.length < 3) ? '用户名至少3个字符' : null,
                            ),
                            const SizedBox(height: 16),
                            TextFormField(
                              controller: _passwordCtrl,
                              obscureText: _obscurePassword,
                              decoration: InputDecoration(
                                labelText: '密码',
                                prefixIcon: const Icon(Icons.lock_outline),
                                suffixIcon: IconButton(
                                  icon: Icon(_obscurePassword
                                      ? Icons.visibility_off
                                      : Icons.visibility),
                                  onPressed: () => setState(
                                      () => _obscurePassword = !_obscurePassword),
                                ),
                              ),
                              validator: (v) => (v == null || v.length < 6) ? '密码至少6个字符' : null,
                            ),
                            if (auth.error != null) ...[
                              const SizedBox(height: 12),
                              Text(
                                auth.error!,
                                style: const TextStyle(color: AppTheme.errorColor, fontSize: 14),
                                textAlign: TextAlign.center,
                              ),
                            ],
                            const SizedBox(height: 24),
                            ElevatedButton(
                              onPressed: auth.isLoading ? null : _submit,
                              child: auth.isLoading
                                  ? const SizedBox(
                                      height: 20,
                                      width: 20,
                                      child: CircularProgressIndicator(
                                          strokeWidth: 2, color: Colors.white))
                                  : Text(_isRegister ? '注册' : '登录'),
                            ),
                            const SizedBox(height: 12),
                            TextButton(
                              onPressed: () => setState(() => _isRegister = !_isRegister),
                              child: Text(_isRegister ? '已有账号？去登录' : '没有账号？去注册'),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildRoleTab(String label, DeviceRole role, AuthProvider auth) {
    final isSelected = auth.deviceRole == role;
    return Expanded(
      child: GestureDetector(
        onTap: () => auth.setDeviceRole(role),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 14),
          decoration: BoxDecoration(
            color: isSelected ? Colors.white : Colors.transparent,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            label,
            textAlign: TextAlign.center,
            style: TextStyle(
              fontWeight: FontWeight.w600,
              color: isSelected ? AppTheme.primaryColor : Colors.white,
            ),
          ),
        ),
      ),
    );
  }

  void _submit() async {
    if (!_formKey.currentState!.validate()) return;
    final auth = context.read<AuthProvider>();
    bool success;
    if (_isRegister) {
      success = await auth.register(_usernameCtrl.text, _passwordCtrl.text);
    } else {
      success = await auth.login(_usernameCtrl.text, _passwordCtrl.text);
    }
    if (success && mounted) {
      Navigator.of(context).pushReplacementNamed(
        auth.deviceRole == DeviceRole.student ? '/student' : '/parent',
      );
    }
  }

  @override
  void dispose() {
    _usernameCtrl.dispose();
    _passwordCtrl.dispose();
    super.dispose();
  }
}
