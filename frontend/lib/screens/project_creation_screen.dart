import 'package:flutter/material.dart';
import './project_workflow_screen.dart';
import '../models/project_creation_request.dart';
import '../services/api_service.dart';

class ProjectCreationScreen extends StatefulWidget {
  const ProjectCreationScreen({super.key});

  @override
  State<ProjectCreationScreen> createState() => _ProjectCreationScreenState();
}

class _ProjectCreationScreenState extends State<ProjectCreationScreen> {
  final _formKey = GlobalKey<FormState>();
  final ApiService _apiService = ApiService();

  // Text editing controllers for the new form
  final _projectNameController = TextEditingController(text: 'Modern Eco-Friendly Family House');
  final _clientNameController = TextEditingController(text: 'The Future Homes Co.');
  final _projectDescriptionController = TextEditingController(text: 'A two-story modern house with a focus on sustainability and smart home tech.');
  final _projectTypeController = TextEditingController(text: 'Residential');
  final _budgetRangeController = TextEditingController(text: '\$800,000 - \$1,500,000');
  final _locationController = TextEditingController(text: 'Austin, TX');
  final _desiredFeaturesController = TextEditingController(text: 'Green Roof, Solar Panels, Rainwater Harvesting, Smart HVAC');

  bool _isLoading = false;

  Future<void> _createProject() async {
    if (_formKey.currentState!.validate()) {
      setState(() => _isLoading = true);

      final request = ProjectCreationRequest(
        projectName: _projectNameController.text,
        clientName: _clientNameController.text,
        projectDescription: _projectDescriptionController.text,
        projectType: _projectTypeController.text,
        budgetRange: _budgetRangeController.text,
        location: _locationController.text,
        desiredFeatures: _desiredFeaturesController.text.split(',').map((s) => s.trim()).toList(),
      );

      try {
        final response = await _apiService.createProject(request);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Project created successfully! ID: ${response.projectId}')),
        );
        // Navigate to the workflow screen
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (context) => ProjectWorkflowScreen(projectId: response.projectId),
          ),
        );
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error creating project: $e'), backgroundColor: Colors.red),
        );
      } finally {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Create New Construction Project'),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 800),
            child: Card(
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text('Project Briefing', style: Theme.of(context).textTheme.headlineMedium),
                      const SizedBox(height: 24),
                      _buildTextField(_projectNameController, 'Project Name'),
                      _buildTextField(_clientNameController, 'Client Name'),
                      _buildTextField(_projectDescriptionController, 'Project Description', maxLines: 3),
                      _buildTextField(_projectTypeController, 'Project Type'),
                      _buildTextField(_budgetRangeController, 'Budget Range'),
                      _buildTextField(_locationController, 'Location'),
                      _buildTextField(_desiredFeaturesController, 'Desired Features (comma-separated)'),
                      const SizedBox(height: 24),
                      _isLoading
                          ? const Center(child: CircularProgressIndicator())
                          : ElevatedButton(
                              onPressed: _createProject,
                              child: const Text('Create Project & Run Stage 1'),
                            ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildTextField(TextEditingController controller, String label, {int maxLines = 1}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 10.0),
      child: TextFormField(
        controller: controller,
        decoration: InputDecoration(labelText: label),
        maxLines: maxLines,
        validator: (value) {
          if (value == null || value.isEmpty) {
            return 'Please enter the $label';
          }
          return null;
        },
      ),
    );
  }
  
  @override
  void dispose() {
    _projectNameController.dispose();
    _clientNameController.dispose();
    _projectDescriptionController.dispose();
    _projectTypeController.dispose();
    _budgetRangeController.dispose();
    _locationController.dispose();
    _desiredFeaturesController.dispose();
    super.dispose();
  }
}
