// This file defines the Dart model for the input data sent to the backend.

import 'dart:convert';

class ProjectInput {
  final String projectType;
  final String clientName;
  final String budgetRange;
  final String location;
  final List<String> desiredFeatures;
  final String? initialIdeasUrl;
  final String projectDescription;
  final String projectSize;

  ProjectInput({
    required this.projectType,
    required this.clientName,
    required this.budgetRange,
    required this.location,
    required this.desiredFeatures,
    this.initialIdeasUrl,
    required this.projectDescription,
    required this.projectSize,
  });

  // Convert a ProjectInput instance to a JSON map
  Map<String, dynamic> toJson() {
    return {
      'project_type': projectType,
      'client_name': clientName,
      'budget_range': budgetRange,
      'location': location,
      'desired_features': desiredFeatures,
      'initial_ideas_url': initialIdeasUrl,
      'project_description': projectDescription,
      'project_size': projectSize,
    };
  }
}