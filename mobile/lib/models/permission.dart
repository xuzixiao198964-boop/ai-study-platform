class Permission {
  final bool aiAnswerEnabled;
  final bool aiExplanationEnabled;
  final bool aiSimilarQuestionsEnabled;

  Permission({
    required this.aiAnswerEnabled,
    required this.aiExplanationEnabled,
    required this.aiSimilarQuestionsEnabled,
  });

  factory Permission.fromJson(Map<String, dynamic> json) => Permission(
        aiAnswerEnabled: json['ai_answer_enabled'] ?? true,
        aiExplanationEnabled: json['ai_explanation_enabled'] ?? true,
        aiSimilarQuestionsEnabled: json['ai_similar_questions_enabled'] ?? true,
      );

  Map<String, dynamic> toJson() => {
        'ai_answer_enabled': aiAnswerEnabled,
        'ai_explanation_enabled': aiExplanationEnabled,
        'ai_similar_questions_enabled': aiSimilarQuestionsEnabled,
      };
}
