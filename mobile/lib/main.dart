import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'config/theme.dart';
import 'providers/auth_provider.dart';
import 'providers/study_provider.dart';
import 'providers/error_book_provider.dart';
import 'providers/permission_provider.dart';
import 'screens/auth/login_screen.dart';
import 'screens/student/student_home_screen.dart';
import 'screens/parent/parent_home_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const AiStudyApp());
}

class AiStudyApp extends StatelessWidget {
  const AiStudyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()..init()),
        ChangeNotifierProvider(create: (_) => StudyProvider()),
        ChangeNotifierProvider(create: (_) => ErrorBookProvider()),
        ChangeNotifierProvider(create: (_) => PermissionProvider()),
      ],
      child: MaterialApp(
        title: '学习指认AI',
        theme: AppTheme.lightTheme,
        debugShowCheckedModeBanner: false,
        home: const _AuthGate(),
        routes: {
          '/login': (_) => const LoginScreen(),
          '/student': (_) => const StudentHomeScreen(),
          '/parent': (_) => const ParentHomeScreen(),
        },
      ),
    );
  }
}

class _AuthGate extends StatelessWidget {
  const _AuthGate();

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();

    if (!auth.isAuthenticated) {
      return const LoginScreen();
    }

    if (auth.deviceRole == DeviceRole.parent) {
      return const ParentHomeScreen();
    }

    return const StudentHomeScreen();
  }
}
