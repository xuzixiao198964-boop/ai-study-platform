class ErrorBook {
  final int id;
  final int userId;
  final String title;
  final String subject;
  final String approvalStatus;
  final String? rejectionReason;
  final int totalQuestions;
  final DateTime createdAt;
  final List<ErrorBookItem>? items;

  ErrorBook({
    required this.id,
    required this.userId,
    required this.title,
    required this.subject,
    required this.approvalStatus,
    this.rejectionReason,
    required this.totalQuestions,
    required this.createdAt,
    this.items,
  });

  factory ErrorBook.fromJson(Map<String, dynamic> json) => ErrorBook(
        id: json['id'],
        userId: json['user_id'],
        title: json['title'] ?? '',
        subject: json['subject'] ?? '',
        approvalStatus: json['approval_status'] ?? 'draft',
        rejectionReason: json['rejection_reason'],
        totalQuestions: json['total_questions'] ?? 0,
        createdAt: DateTime.parse(json['created_at']),
        items: (json['items'] as List?)
            ?.map((e) => ErrorBookItem.fromJson(e))
            .toList(),
      );

  bool get isPending => approvalStatus == 'pending_approval';
  bool get isApproved => approvalStatus == 'approved';
  bool get isRejected => approvalStatus == 'rejected';
}

class ErrorBookItem {
  final int id;
  final int errorBookId;
  final int questionId;
  final String questionText;
  final String studentAnswer;
  final String correctAnswer;
  final String errorAnalysis;
  final List<String>? knowledgeTags;
  final String? originalImageUrl;

  ErrorBookItem({
    required this.id,
    required this.errorBookId,
    required this.questionId,
    required this.questionText,
    required this.studentAnswer,
    required this.correctAnswer,
    required this.errorAnalysis,
    this.knowledgeTags,
    this.originalImageUrl,
  });

  factory ErrorBookItem.fromJson(Map<String, dynamic> json) => ErrorBookItem(
        id: json['id'],
        errorBookId: json['error_book_id'],
        questionId: json['question_id'],
        questionText: json['question_text'] ?? '',
        studentAnswer: json['student_answer'] ?? '',
        correctAnswer: json['correct_answer'] ?? '',
        errorAnalysis: json['error_analysis'] ?? '',
        knowledgeTags: (json['knowledge_tags'] as List?)?.cast<String>(),
        originalImageUrl: json['original_image_url'],
      );
}
