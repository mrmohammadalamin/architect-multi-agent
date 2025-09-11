import './artifact.dart';

class WorkflowStage {
  final int stageId;
  final String name;
  final String status; // e.g., "Completed", "Pending", "Locked"
  final List<Artifact> artifacts;

  WorkflowStage({
    required this.stageId,
    required this.name,
    required this.status,
    required this.artifacts,
  });

  factory WorkflowStage.fromJson(Map<String, dynamic> json) {
    var artifactsList = <Artifact>[];
    if (json['artifacts'] != null && json['artifacts'] is List) {
      artifactsList = (json['artifacts'] as List)
          .map((artifactJson) => Artifact.fromJson(artifactJson as Map<String, dynamic>))
          .toList();
    }

    return WorkflowStage(
      stageId: json['stage_id'],
      name: json['name'],
      status: json['status'],
      artifacts: artifactsList,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'stage_id': stageId,
      'name': name,
      'status': status,
      'artifacts': artifacts.map((a) => a.toJson()).toList(),
    };
  }
}
