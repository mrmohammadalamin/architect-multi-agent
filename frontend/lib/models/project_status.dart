import './workflow_stage.dart';

class ProjectStatus {
  final String projectId;
  final String? pendingGate;
  final List<WorkflowStage> stages;

  ProjectStatus({
    required this.projectId,
    this.pendingGate,
    required this.stages,
  });

  factory ProjectStatus.fromJson(Map<String, dynamic> json) {
    var stagesList = <WorkflowStage>[];
    if (json['stages'] != null && json['stages'] is List) {
      stagesList = (json['stages'] as List)
          .map((stageJson) => WorkflowStage.fromJson(stageJson as Map<String, dynamic>))
          .toList();
    }

    return ProjectStatus(
      projectId: json['project_id'],
      pendingGate: json['pending_gate'],
      stages: stagesList,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'project_id': projectId,
      'pending_gate': pendingGate,
      'stages': stages.map((s) => s.toJson()).toList(),
    };
  }
}
