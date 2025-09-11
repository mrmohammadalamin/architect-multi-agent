// This file defines the Dart models for the backend's response.

import 'dart:convert';

class ProjectOutput {
  final String overallStatus;
  final Map<String, dynamic> userInputReceived;
  final Map<String, dynamic> consolidatedProjectData;
  final Map<String, dynamic> agentOutputsRaw;
  final String summaryMessage;

  ProjectOutput({
    required this.overallStatus,
    required this.userInputReceived,
    required this.consolidatedProjectData,
    required this.agentOutputsRaw,
    required this.summaryMessage,
  });

  factory ProjectOutput.fromJson(Map<String, dynamic> json) {
    return ProjectOutput(
      overallStatus: json['overall_status'] as String,
      userInputReceived: json['user_input_received'] as Map<String, dynamic>,
      consolidatedProjectData: json['consolidated_project_data'] as Map<String, dynamic>,
      agentOutputsRaw: json['agent_outputs_raw'] as Map<String, dynamic>,
      summaryMessage: json['summary_message'] as String,
    );
  }
}