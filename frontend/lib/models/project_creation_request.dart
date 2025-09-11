import 'dart:convert';

class ProjectCreationRequest {
  final String projectName;
  final String clientName;
  final String projectDescription;
  final String projectType;
  final String budgetRange;
  final String location;
  final List<String> desiredFeatures;

  ProjectCreationRequest({
    required this.projectName,
    required this.clientName,
    required this.projectDescription,
    required this.projectType,
    required this.budgetRange,
    required this.location,
    required this.desiredFeatures,
  });

  Map<String, dynamic> toJson() {
    return {
      'project_name': projectName,
      'client_name': clientName,
      'project_description': projectDescription,
      'project_type': projectType,
      'budget_range': budgetRange,
      'location': location,
      'desired_features': desiredFeatures,
    };
  }
}
