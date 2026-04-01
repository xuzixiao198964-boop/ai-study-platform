import 'package:flutter/material.dart';
import '../config/theme.dart';

class OnlineStatusIndicator extends StatelessWidget {
  final bool isOnline;
  final String label;

  const OnlineStatusIndicator({
    super.key,
    required this.isOnline,
    this.label = '',
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 10,
          height: 10,
          decoration: BoxDecoration(
            color: isOnline ? AppTheme.correctColor : Colors.grey,
            shape: BoxShape.circle,
            boxShadow: isOnline
                ? [BoxShadow(color: AppTheme.correctColor.withValues(alpha: 0.4), blurRadius: 6)]
                : null,
          ),
        ),
        if (label.isNotEmpty) ...[
          const SizedBox(width: 6),
          Text(
            label.isEmpty ? (isOnline ? '在线' : '离线') : label,
            style: TextStyle(
              fontSize: 12,
              color: isOnline ? AppTheme.correctColor : Colors.grey,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ],
    );
  }
}

class PermissionBanner extends StatelessWidget {
  final bool isEnabled;
  final String disabledMessage;

  const PermissionBanner({
    super.key,
    required this.isEnabled,
    this.disabledMessage = '家长已关闭AI解答权限，请联系家长',
  });

  @override
  Widget build(BuildContext context) {
    if (isEnabled) return const SizedBox.shrink();

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        color: AppTheme.warningColor.withValues(alpha: 0.1),
        border: Border(
          bottom: BorderSide(color: AppTheme.warningColor.withValues(alpha: 0.3)),
        ),
      ),
      child: Row(
        children: [
          const Icon(Icons.lock_outline, size: 18, color: AppTheme.warningColor),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              disabledMessage,
              style: const TextStyle(color: AppTheme.warningColor, fontSize: 13),
            ),
          ),
        ],
      ),
    );
  }
}

class ApprovalStatusChip extends StatelessWidget {
  final String status;

  const ApprovalStatusChip({super.key, required this.status});

  @override
  Widget build(BuildContext context) {
    Color color;
    String text;
    IconData icon;

    switch (status) {
      case 'pending_approval':
        color = AppTheme.warningColor;
        text = '待审批';
        icon = Icons.pending;
        break;
      case 'approved':
        color = AppTheme.correctColor;
        text = '已通过';
        icon = Icons.check_circle;
        break;
      case 'rejected':
        color = AppTheme.errorColor;
        text = '已驳回';
        icon = Icons.cancel;
        break;
      case 'regenerating':
        color = AppTheme.primaryColor;
        text = '重新生成中';
        icon = Icons.refresh;
        break;
      default:
        color = Colors.grey;
        text = '草稿';
        icon = Icons.drafts;
    }

    return Chip(
      avatar: Icon(icon, size: 16, color: color),
      label: Text(text, style: TextStyle(color: color, fontSize: 12)),
      backgroundColor: color.withValues(alpha: 0.1),
      side: BorderSide.none,
      padding: EdgeInsets.zero,
      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
    );
  }
}
