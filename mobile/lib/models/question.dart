class Question {
  final int id;
  final String sessionId;
  final int sequenceNo;
  final String subject;
  final String questionType;
  final String questionText;
  final String studentAnswer;
  final String correctAnswer;
  final String? imageUrl;
  final List<String>? knowledgePoints;
  final CorrectionResult? correction;

  Question({
    required this.id,
    required this.sessionId,
    required this.sequenceNo,
    required this.subject,
    required this.questionType,
    required this.questionText,
    required this.studentAnswer,
    required this.correctAnswer,
    this.imageUrl,
    this.knowledgePoints,
    this.correction,
  });

  factory Question.fromJson(Map<String, dynamic> json) => Question(
        id: json['id'],
        sessionId: json['session_id'] ?? '',
        sequenceNo: json['sequence_no'] ?? 0,
        subject: json['subject'] ?? 'other',
        questionType: json['question_type'] ?? 'other',
        questionText: json['question_text'] ?? '',
        studentAnswer: json['student_answer'] ?? '',
        correctAnswer: json['correct_answer'] ?? '',
        imageUrl: json['image_url'],
        knowledgePoints: (json['knowledge_points'] as List?)?.cast<String>(),
        correction: json['correction'] != null
            ? CorrectionResult.fromJson(json['correction'])
            : null,
      );
}

class CorrectionResult {
  final int id;
  final int questionId;
  final String status;
  final bool isCorrect;
  final String standardAnswer;
  final String solutionSteps;
  final String explanation;
  final String? errorReason;
  final String errorAnalysis;
  final double? aiConfidence;

  CorrectionResult({
    required this.id,
    required this.questionId,
    required this.status,
    required this.isCorrect,
    required this.standardAnswer,
    required this.solutionSteps,
    required this.explanation,
    this.errorReason,
    required this.errorAnalysis,
    this.aiConfidence,
  });

  factory CorrectionResult.fromJson(Map<String, dynamic> json) =>
      CorrectionResult(
        id: json['id'],
        questionId: json['question_id'],
        status: json['status'] ?? 'pending',
        isCorrect: json['is_correct'] ?? false,
        standardAnswer: json['standard_answer'] ?? '',
        solutionSteps: json['solution_steps'] ?? '',
        explanation: json['explanation'] ?? '',
        errorReason: json['error_reason'],
        errorAnalysis: json['error_analysis'] ?? '',
        aiConfidence: json['ai_confidence']?.toDouble(),
      );
}

class QuestionRegion {
  final int questionId;
  final double left;
  final double top;
  final double width;
  final double height;

  QuestionRegion({
    required this.questionId,
    required this.left,
    required this.top,
    required this.width,
    required this.height,
  });

  Map<String, dynamic> toJson() => {
        'question_id': questionId,
        'bbox': {
          'left': left,
          'top': top,
          'width': width,
          'height': height,
        },
      };
}
