import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../providers/auth_provider.dart';
import '../../providers/permission_provider.dart';
import '../../providers/error_book_provider.dart';
import '../../services/api_service.dart';
import '../../services/websocket_service.dart';

class ParentHomeScreen extends StatefulWidget {
  const ParentHomeScreen({super.key});

  @override
  State<ParentHomeScreen> createState() => _ParentHomeScreenState();
}

class _ParentHomeScreenState extends State<ParentHomeScreen> {
  int _currentIndex = 0;

  @override
  void initState() {
    super.initState();
    context.read<PermissionProvider>().loadPermissions();
    context.read<ErrorBookProvider>().loadErrorBooks();
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('学习指认AI · 家长端'),
        actions: [
          IconButton(
            icon: const Icon(Icons.person_outline),
            onPressed: () => _showProfileSheet(context, auth),
          ),
        ],
      ),
      body: IndexedStack(
        index: _currentIndex,
        children: const [
          _MonitorTab(),
          _ErrorBookApprovalTab(),
          _PermissionTab(),
          _RecordsTab(),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (i) => setState(() => _currentIndex = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.visibility_outlined), selectedIcon: Icon(Icons.visibility), label: '监控'),
          NavigationDestination(icon: Icon(Icons.grading_outlined), selectedIcon: Icon(Icons.grading), label: '审批'),
          NavigationDestination(icon: Icon(Icons.admin_panel_settings_outlined), selectedIcon: Icon(Icons.admin_panel_settings), label: '权限'),
          NavigationDestination(icon: Icon(Icons.history_outlined), selectedIcon: Icon(Icons.history), label: '记录'),
        ],
      ),
    );
  }

  void _showProfileSheet(BuildContext context, AuthProvider auth) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CircleAvatar(
              radius: 36,
              backgroundColor: AppTheme.secondaryColor,
              child: Text(
                (auth.user?.nickname ?? '家')[0],
                style: const TextStyle(fontSize: 28, color: Colors.white),
              ),
            ),
            const SizedBox(height: 12),
            Text(auth.user?.nickname ?? '', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 4),
            Text('家长端 · ${auth.user?.username ?? ""}', style: const TextStyle(color: AppTheme.textSecondary)),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: () {
                  Navigator.pop(ctx);
                  auth.logout();
                  Navigator.of(context).pushReplacementNamed('/login');
                },
                icon: const Icon(Icons.logout, color: AppTheme.errorColor),
                label: const Text('退出登录', style: TextStyle(color: AppTheme.errorColor)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// 远程实时监控Tab
class _MonitorTab extends StatefulWidget {
  const _MonitorTab();

  @override
  State<_MonitorTab> createState() => _MonitorTabState();
}

class _MonitorTabState extends State<_MonitorTab> {
  final WebSocketService _ws = WebSocketService();
  bool _studentOnline = false;
  String _lastActivity = '等待学生端连接...';

  @override
  void initState() {
    super.initState();
    _ws.on('device_online', (msg) {
      if (msg['payload']?['device_type'] == 'student_ipad') {
        setState(() {
          _studentOnline = true;
          _lastActivity = '学生端已上线';
        });
      }
    });
    _ws.on('device_offline', (msg) {
      if (msg['payload']?['device_type'] == 'student_ipad') {
        setState(() {
          _studentOnline = false;
          _lastActivity = '学生端已离线';
        });
      }
    });
    _ws.on('screen_update', (msg) {
      setState(() => _lastActivity = 'OCR识别完成，发现${msg['payload']?['question_count'] ?? 0}道题');
    });
    _ws.on('correction_result', (msg) {
      final correct = msg['payload']?['is_correct'] == true;
      setState(() => _lastActivity = '批改结果：${correct ? "正确" : "错误"}');
    });
    _checkDeviceStatus();
  }

  Future<void> _checkDeviceStatus() async {
    try {
      final status = await ApiService().getDeviceStatus();
      setState(() {
        _studentOnline = status['student_online'] == true;
        _lastActivity = _studentOnline ? '学生端在线' : '学生端离线';
      });
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          // 学生端状态
          Card(
            child: ListTile(
              leading: CircleAvatar(
                backgroundColor: _studentOnline ? AppTheme.correctColor : Colors.grey,
                child: Icon(
                  _studentOnline ? Icons.tablet_mac : Icons.tablet_mac_outlined,
                  color: Colors.white,
                ),
              ),
              title: Text('学生端iPad', style: TextStyle(fontWeight: FontWeight.bold)),
              subtitle: Text(_lastActivity),
              trailing: _studentOnline
                  ? const Chip(label: Text('在线', style: TextStyle(color: Colors.white, fontSize: 12)),
                      backgroundColor: AppTheme.correctColor)
                  : const Chip(label: Text('离线', style: TextStyle(fontSize: 12))),
            ),
          ),
          const SizedBox(height: 16),

          // 投屏画面
          Expanded(
            child: Card(
              clipBehavior: Clip.antiAlias,
              child: Container(
                width: double.infinity,
                color: Colors.grey[100],
                child: _studentOnline
                    ? const Center(child: Text('学生端投屏画面（实时同步）', style: TextStyle(color: Colors.grey)))
                    : const Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.tv_off, size: 64, color: Colors.grey),
                            SizedBox(height: 16),
                            Text('学生端未在线', style: TextStyle(color: Colors.grey, fontSize: 16)),
                            Text('学生登录后将自动同步画面', style: TextStyle(color: Colors.grey)),
                          ],
                        ),
                      ),
              ),
            ),
          ),
          const SizedBox(height: 16),

          // 远程操作按钮
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: _studentOnline ? () => Navigator.of(context).pushNamed('/parent/video-call') : null,
                  icon: const Icon(Icons.video_call),
                  label: const Text('视频通话'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: _studentOnline
                      ? () => _ws.send('remote_cmd', {'command': 're_recognize'}, targetDevice: 'student_ipad')
                      : null,
                  icon: const Icon(Icons.refresh),
                  label: const Text('重新识别'),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

/// 错题集审批Tab
class _ErrorBookApprovalTab extends StatelessWidget {
  const _ErrorBookApprovalTab();

  @override
  Widget build(BuildContext context) {
    final ebp = context.watch<ErrorBookProvider>();

    if (ebp.isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (ebp.errorBooks.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.grading, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text('暂无错题集', style: TextStyle(color: Colors.grey, fontSize: 16)),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () => ebp.loadErrorBooks(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: ebp.errorBooks.length,
        itemBuilder: (ctx, i) {
          final book = ebp.errorBooks[i];
          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            child: ListTile(
              leading: CircleAvatar(
                backgroundColor: book.isPending
                    ? AppTheme.warningColor
                    : book.isApproved
                        ? AppTheme.correctColor
                        : AppTheme.errorColor,
                child: Icon(
                  book.isPending ? Icons.pending : book.isApproved ? Icons.check : Icons.close,
                  color: Colors.white,
                ),
              ),
              title: Text(book.title, style: const TextStyle(fontWeight: FontWeight.bold)),
              subtitle: Text('${book.totalQuestions}道错题 · ${book.subject}'),
              trailing: book.isPending
                  ? ElevatedButton(
                      onPressed: () => _showApprovalDialog(ctx, book, ebp),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTheme.warningColor,
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                      ),
                      child: const Text('待审批'),
                    )
                  : Text(
                      book.isApproved ? '已通过' : '已驳回',
                      style: TextStyle(
                        color: book.isApproved ? AppTheme.correctColor : AppTheme.errorColor,
                      ),
                    ),
              onTap: () {},
            ),
          );
        },
      ),
    );
  }

  void _showApprovalDialog(BuildContext context, dynamic book, ErrorBookProvider ebp) {
    final reasonCtrl = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text('审批：${book.title}'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('共${book.totalQuestions}道错题'),
            const SizedBox(height: 16),
            TextField(
              controller: reasonCtrl,
              decoration: const InputDecoration(
                labelText: '驳回原因（可选）',
                border: OutlineInputBorder(),
              ),
              maxLines: 2,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () async {
              Navigator.pop(ctx);
              await ebp.approveErrorBook(book.id, false, reason: reasonCtrl.text);
            },
            child: const Text('驳回', style: TextStyle(color: AppTheme.errorColor)),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(ctx);
              await ebp.approveErrorBook(book.id, true);
            },
            child: const Text('通过'),
          ),
        ],
      ),
    );
  }
}

/// 权限管控Tab
class _PermissionTab extends StatelessWidget {
  const _PermissionTab();

  @override
  Widget build(BuildContext context) {
    final perm = context.watch<PermissionProvider>();

    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('AI功能权限管控', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          const Text('控制学生端可使用的AI功能', style: TextStyle(color: AppTheme.textSecondary)),
          const SizedBox(height: 24),

          Card(
            child: Column(
              children: [
                SwitchListTile(
                  title: const Text('AI解答功能'),
                  subtitle: const Text('允许学生使用AI自动批改答案'),
                  value: perm.permission?.aiAnswerEnabled ?? true,
                  onChanged: (v) => perm.updatePermissions(aiAnswerEnabled: v),
                  secondary: const Icon(Icons.auto_fix_high),
                ),
                const Divider(height: 1),
                SwitchListTile(
                  title: const Text('AI讲解功能'),
                  subtitle: const Text('允许学生查看AI题目讲解'),
                  value: perm.permission?.aiExplanationEnabled ?? true,
                  onChanged: (v) => perm.updatePermissions(aiExplanationEnabled: v),
                  secondary: const Icon(Icons.lightbulb_outline),
                ),
                const Divider(height: 1),
                SwitchListTile(
                  title: const Text('相似题推送'),
                  subtitle: const Text('允许学生获取AI推荐的相似练习题'),
                  value: perm.permission?.aiSimilarQuestionsEnabled ?? true,
                  onChanged: (v) => perm.updatePermissions(aiSimilarQuestionsEnabled: v),
                  secondary: const Icon(Icons.content_copy),
                ),
              ],
            ),
          ),

          const SizedBox(height: 24),
          Card(
            color: AppTheme.warningColor.withValues(alpha: 0.1),
            child: const Padding(
              padding: EdgeInsets.all(16),
              child: Row(
                children: [
                  Icon(Icons.info_outline, color: AppTheme.warningColor),
                  SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      '权限修改将实时同步至学生端，修改后立即生效',
                      style: TextStyle(color: AppTheme.warningColor, fontSize: 13),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// 学习记录Tab
class _RecordsTab extends StatelessWidget {
  const _RecordsTab();

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.history, size: 64, color: Colors.grey),
          SizedBox(height: 16),
          Text('学习记录', style: TextStyle(fontSize: 18, color: Colors.grey)),
          SizedBox(height: 8),
          Text('查看学生的完整学习历史', style: TextStyle(color: Colors.grey)),
        ],
      ),
    );
  }
}
