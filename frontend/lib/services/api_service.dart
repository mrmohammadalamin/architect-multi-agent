import 'dart:convert';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:http/http.dart' as http;
import '../models/project_creation_request.dart';
import '../models/project_creation_response.dart';
import '../models/project_status.dart';
import '../models/gate_approval_request.dart';

class ApiService {
  // Use 10.0.2.2 for Android emulator to connect to localhost
  static final String _baseUrl = dotenv.env['BASE_URL'] ?? 'http://127.0.0.1:8000';

  Future<ProjectCreationResponse> createProject(ProjectCreationRequest request) async {
    final url = Uri.parse('$_baseUrl/projects');
    final headers = {'Content-Type': 'application/json'};
    final body = jsonEncode(request.toJson());

    try {
      final response = await http.post(url, headers: headers, body: body);

      if (response.statusCode == 201) { // Check for 201 Created status
        final Map<String, dynamic> jsonResponse = jsonDecode(response.body);
        return ProjectCreationResponse.fromJson(jsonResponse);
      } else {
        // Handle non-201 status codes
        print('Backend error: ${response.statusCode} - ${response.body}');
        throw Exception('Failed to create project: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      // Handle network errors or other exceptions
      print('Error sending request: $e');
      throw Exception('Failed to connect to backend: $e');
    }
  }

  Future<ProjectStatus> getProjectStatus(String projectId) async {
    final url = Uri.parse('$_baseUrl/projects/$projectId');
    try {
      final response = await http.get(url);

      if (response.statusCode == 200) {
        final Map<String, dynamic> jsonResponse = jsonDecode(response.body);
        return ProjectStatus.fromJson(jsonResponse);
      } else {
        throw Exception('Failed to load project status: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to connect to backend: $e');
    }
  }

  Future<Map<String, dynamic>> getArtifactContent(String projectId, int stageId, String artifactName) async {
    final url = Uri.parse('$_baseUrl/projects/$projectId/artifacts/$stageId/$artifactName');
    try {
      final response = await http.get(url);

      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      } else {
        throw Exception('Failed to load artifact content: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('Failed to connect to backend for artifact: $e');
    }
  }

  Future<Map<String, dynamic>> getRiskSummary(String projectId) async {
    final url = Uri.parse('$_baseUrl/projects/$projectId/risks');
    try {
      final response = await http.get(url);

      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      } else {
        throw Exception('Failed to load risk summary: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('Failed to connect to backend for risk summary: $e');
    }
  }

  Future<Map<String, dynamic>> getFinancialSummary(String projectId) async {
    final url = Uri.parse('$_baseUrl/projects/$projectId/financials');
    try {
      final response = await http.get(url);

      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      } else {
        throw Exception('Failed to load financial summary: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('Failed to connect to backend for financial summary: $e');
    }
  }

  Future<Map<String, dynamic>> getKnowledgeSummary(String projectId) async {
    final url = Uri.parse('$_baseUrl/projects/$projectId/knowledge');
    try {
      final response = await http.get(url);

      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      } else {
        throw Exception('Failed to load knowledge summary: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('Failed to connect to backend for knowledge summary: $e');
    }
  }

  Future<void> approveGate(String projectId, String gateId, GateApprovalRequest request) async {
    final url = Uri.parse('$_baseUrl/projects/$projectId/approve/$gateId');
    final headers = {'Content-Type': 'application/json'};
    final body = jsonEncode(request.toJson());

    try {
      final response = await http.post(url, headers: headers, body: body);

      if (response.statusCode != 200) {
        throw Exception('Failed to approve gate: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('Failed to connect to backend for gate approval: $e');
    }
  }

  Future<List<String>> getProjectList() async {
    final url = Uri.parse('$_baseUrl/projects');
    try {
      final response = await http.get(url);

      if (response.statusCode == 200) {
        final Map<String, dynamic> jsonResponse = jsonDecode(response.body);
        final List<dynamic> projectsJson = jsonResponse['projects'];
        return projectsJson.map((id) => id.toString()).toList();
      } else {
        throw Exception('Failed to load project list: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('Failed to connect to backend for project list: $e');
    }
  }
}
