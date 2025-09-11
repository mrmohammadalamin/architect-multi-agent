import 'dart:convert';

class ProjectCreationResponse {
  final String message;
  final String projectId;
  // The stage_1_results can be complex, representing it as a map for now.
  final Map<String, dynamic> stage1Results;

  ProjectCreationResponse({
    required this.message,
    required this.projectId,
    required this.stage1Results,
  });

  factory ProjectCreationResponse.fromJson(Map<String, dynamic> json) {
    return ProjectCreationResponse(
      message: json['message'],
      projectId: json['project_id'],
      stage1Results: json['stage_1_results'] as Map<String, dynamic>,
    );
  }
}
