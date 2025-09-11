// This is the main UI screen where users interact with the system.

import 'package:flutter/material.dart';
import 'package:frontend/models/project_input.dart';
import 'package:frontend/models/project_output.dart';
import 'package:frontend/services/api_service.dart';
import 'dart:convert'; // For base64 decoding

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _formKey = GlobalKey<FormState>();
  final ApiService _apiService = ApiService();

  // Text editing controllers for form fields
  final TextEditingController _projectTypeController = TextEditingController(text: 'residential');
  final TextEditingController _clientNameController = TextEditingController(text: 'EcoHome Developers');
  final TextEditingController _budgetRangeController = TextEditingController(text: '\$750,000 - \$1,200,000');
  final TextEditingController _locationController = TextEditingController(text: 'London, UK');
  final TextEditingController _desiredFeaturesController = TextEditingController(text: 'Smart Home Tech, Green Roof, Open Concept Living');
  final TextEditingController _initialIdeasUrlController = TextEditingController(text: 'https://example.com/eco-home-ideas');
  final TextEditingController _projectDescriptionController = TextEditingController(text: 'Design and build a two-story modern eco-friendly family house with smart home technology, a green roof, and an emphasis on energy efficiency and natural light.');
  final TextEditingController _projectSizeController = TextEditingController(text: 'medium');

  ProjectOutput? _projectOutput;
  bool _isLoading = false;
  String? _errorMessage;

  Future<void> _processProject() async {
    if (_formKey.currentState!.validate()) {
      setState(() {
        _isLoading = true;
        _errorMessage = null;
        _projectOutput = null;
      });

      final projectInput = ProjectInput(
        projectType: _projectTypeController.text,
        clientName: _clientNameController.text,
        budgetRange: _budgetRangeController.text,
        location: _locationController.text,
        desiredFeatures: _desiredFeaturesController.text.split(',').map((s) => s.trim()).where((s) => s.isNotEmpty).toList(),
        initialIdeasUrl: _initialIdeasUrlController.text.isEmpty ? null : _initialIdeasUrlController.text,
        projectDescription: _projectDescriptionController.text,
        projectSize: _projectSizeController.text,
      );

      try {
        final output = await _apiService.processProject(projectInput);
        setState(() {
          _projectOutput = output;
        });
      } catch (e) {
        setState(() {
          _errorMessage = e.toString();
        });
      } finally {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  void dispose() {
    _projectTypeController.dispose();
    _clientNameController.dispose();
    _budgetRangeController.dispose();
    _locationController.dispose();
    _desiredFeaturesController.dispose();
    _initialIdeasUrlController.dispose();
    _projectDescriptionController.dispose();
    _projectSizeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Construction AI Assistant'),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Form(
                  key: _formKey,
                  child: Column(
                    children: [
                      Text('Enter Project Details', style: Theme.of(context).textTheme.headlineMedium),
                      const SizedBox(height: 20),
                      _buildTextField(_projectDescriptionController, 'Project Description', maxLines: 3),
                      _buildTextField(_projectTypeController, 'Project Type (e.g., residential, commercial)'),
                      _buildTextField(_clientNameController, 'Client Name'),
                      _buildTextField(_budgetRangeController, 'Budget Range (e.g., \$750,000 - \$1,200,000)'),
                      _buildTextField(_locationController, 'Location (e.g., London, UK)'),
                      _buildTextField(_desiredFeaturesController, 'Desired Features (comma-separated)', hintText: 'e.g., Smart Home, Green Roof'),
                      _buildTextField(_initialIdeasUrlController, 'Initial Ideas URL (Optional)'),
                      _buildTextField(_projectSizeController, 'Project Size (e.g., small, medium, large)'),
                      const SizedBox(height: 20),
                      _isLoading
                          ? const CircularProgressIndicator()
                          : ElevatedButton(
                              onPressed: _processProject,
                              child: const Text('Get AI Analysis'),
                            ),
                      const SizedBox(height: 10),
                      ElevatedButton(
                        onPressed: () {
                          Navigator.push(context, MaterialPageRoute(builder: (context) => const ProjectListScreen()));
                        },
                        child: const Text('View All Projects'),
                      ),
                      if (_errorMessage != null)
                        Padding(
                          padding: const EdgeInsets.only(top: 16.0),
                          child: Text(
                            'Error: $_errorMessage',
                            style: const TextStyle(color: Colors.red),
                            textAlign: TextAlign.center,
                          ),
                        ),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: 20),
            if (_projectOutput != null)
              _buildOutputDisplay(_projectOutput!),
          ],
        ),
      ),
    );
  }

  Widget _buildTextField(TextEditingController controller, String label, {int maxLines = 1, String? hintText}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: TextFormField(
        controller: controller,
        decoration: InputDecoration(
          labelText: label,
          hintText: hintText,
        ),
        maxLines: maxLines,
        validator: (value) {
          if (label.contains('Optional')) return null;
          if (value == null || value.isEmpty) {
            return 'Please enter $label';
          }
          return null;
        },
      ),
    );
  }

  Widget _buildOutputDisplay(ProjectOutput output) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('AI Analysis Results', style: Theme.of(context).textTheme.headlineMedium),
        const SizedBox(height: 10),
        _buildResultRow('Overall Status:', output.overallStatus, color: _getStatusColor(output.overallStatus)),
        _buildResultRow('Summary Message:', output.summaryMessage),
        const SizedBox(height: 20),
        Text('Agent Analysis:', style: Theme.of(context).textTheme.headlineSmall),
        const SizedBox(height: 10),
        _buildAgentAnalysis(output.consolidatedProjectData),
      ],
    );
  }

  Widget _buildAgentAnalysis(Map<String, dynamic> data) {
    return Column(
      children: [
        _buildAgentCard('Site Intelligence & Regulatory Compliance', data['site_feasibility_report']),
        _buildAgentCard('Generative Architectural Design', data['architectural_concept']),
        _buildAgentCard('Integrated Systems Engineering', data['system_design']),
        _buildAgentCard('Interior Experiential Design', data['experiential_design']),
        _buildAgentCard('Hyper-Realistic 3D Digital Twin', data['digital_twin_output']),
        _buildAgentCard('Predictive Cost & Supply Chain', data['cost_supply_chain_analysis']),
        _buildAgentCard('Adaptive Project Management', data['master_project_plan']),
        _buildAgentCard('Proactive Risk & Safety Management', data['risk_safety_assessment']),
        _buildAgentCard('AI-Driven Quality Assurance & Control', data['quality_assurance_plan']),
        _buildAgentCard('Semantic Data Integration & Ontology', data['data_integration_analysis']),
        _buildAgentCard('Learning & Adaptation', data['learning_adaptation_insights']),
        _buildAgentCard('Human-AI Collaboration & Explainability', data['human_collaboration_summary']),
        _buildAgentCard('Sustainability & Green Building', data['sustainability_analysis']),
        _buildAgentCard('Financial Investment Analysis', data['financial_analysis']),
        _buildAgentCard('Legal & Contract Management', data['legal_contract_analysis']),
        _buildAgentCard('Workforce Management & HR', data['workforce_hr_analysis']),
        _buildAgentCard('Post-Construction & Facility Management', data['post_construction_fm_analysis']),
        _buildAgentCard('Public Relations & Stakeholder Communication', data['public_relations_strategy']),
      ],
    );
  }

  Widget _buildAgentCard(String title, dynamic agentData) {
    if (agentData == null || agentData is! Map<String, dynamic>) {
      return const SizedBox.shrink();
    }

    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8.0),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: Theme.of(context).textTheme.titleLarge),
            const Divider(height: 20, thickness: 1),
            ...agentData.entries.map((entry) {
              if (entry.key.contains('_base64')) {
                return _buildImageDisplay(_formatKey(entry.key), entry.value as String?);
              }
              if (entry.value is Map<String, dynamic>) {
                return _buildNestedMap(entry.key, entry.value as Map<String, dynamic>);
              }
              if (entry.value is List) {
                return _buildNestedList(entry.key, entry.value as List);
              }
              return _buildResultRow('${_formatKey(entry.key)}:', entry.value.toString());
            }).toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildNestedMap(String title, Map<String, dynamic> data) {
    return Padding(
      padding: const EdgeInsets.only(left: 16.0, top: 8.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(_formatKey(title), style: const TextStyle(fontWeight: FontWeight.bold)),
          ...data.entries.map((entry) => _buildResultRow('  ${_formatKey(entry.key)}:', entry.value.toString())).toList(),
        ],
      ),
    );
  }

  Widget _buildNestedList(String title, List data) {
    return Padding(
      padding: const EdgeInsets.only(left: 16.0, top: 8.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(_formatKey(title), style: const TextStyle(fontWeight: FontWeight.bold)),
          ...data.map((item) => Text('  - ${item.toString()}')).toList(),
        ],
      ),
    );
  }

  Widget _buildResultRow(String label, String value, {Color? color}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(width: 8),
          Expanded(
            child: Text(value, style: TextStyle(color: color ?? Colors.black87)),
          ),
        ],
      ),
    );
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'success':
        return Colors.green.shade700;
      case 'partial_success':
        return Colors.orange.shade700;
      case 'failure':
        return Colors.red.shade700;
      default:
        return Colors.black87;
    }
  }

  Widget _buildImageDisplay(String title, String? base64String) {
    if (base64String == null || base64String.isEmpty || base64String == 'N/A') {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 8.0),
        child: Text('$title: No image generated or available.', style: const TextStyle(fontStyle: FontStyle.italic)),
      );
    }
    try {
      final bytes = base64Decode(base64String);
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 8.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Image.memory(bytes, fit: BoxFit.contain, errorBuilder: (context, error, stackTrace) {
              return Text('Failed to load image for $title: $error');
            }),
          ],
        ),
      );
    } catch (e) {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 8.0),
        child: Text('Error decoding image for $title: $e', style: const TextStyle(color: Colors.red)),
      );
    }
  }

  String _formatKey(String key) {
    return key.replaceAll('_', ' ').split(' ').map((word) => word[0].toUpperCase() + word.substring(1)).join(' ');
  }
}