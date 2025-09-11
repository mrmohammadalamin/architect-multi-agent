import 'package:flutter/material.dart';
import 'dart:convert'; // For base64Decode
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:frontend/bloc/workflow_bloc.dart';
import 'package:frontend/widgets/plan_2d_widget.dart';
import 'package:frontend/widgets/map_3d_avr_widget.dart';
import 'package:frontend/widgets/video_player_widget.dart';
import 'package:frontend/widgets/svg_viewer.dart';
import 'package:frontend/widgets/url_viewer.dart';
import './financial_dashboard_screen.dart';
import './knowledge_dashboard_screen.dart';
import './risk_dashboard_screen.dart';
import '../models/gate_approval_request.dart';
import '../models/project_status.dart';
import '../models/workflow_stage.dart';
import '../services/api_service.dart';
import '../models/artifact.dart';

// A static map to hold stage-to-gate relationships on the frontend
const Map<int, String?> STAGE_GATES = {
  1: "G0", 4: "G1", 6: "G2", 8: "G3", 10: "G4", 12: "G5", 18: "G6"
};

class ProjectWorkflowScreen extends StatelessWidget {
  final String projectId;

  const ProjectWorkflowScreen({super.key, required this.projectId});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => WorkflowBloc(ApiService())..add(LoadWorkflow(projectId)),
      child: const _ProjectWorkflowScreenView(),
    );
  }
}

class _ProjectWorkflowScreenView extends StatelessWidget {
  const _ProjectWorkflowScreenView();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: BlocBuilder<WorkflowBloc, WorkflowState>(
          builder: (context, state) {
            if (state is WorkflowLoaded) {
              return Text('Project: ${state.projectStatus.projectId}');
            } else {
              return const Text('Project');
            }
          },
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              final projectId = (context.read<WorkflowBloc>().state as WorkflowLoaded).projectStatus.projectId;
              context.read<WorkflowBloc>().add(LoadWorkflow(projectId));
            },
            tooltip: 'Refresh Status',
          ),
          IconButton(
            icon: const Icon(Icons.analytics),
            onPressed: () {
              final projectId = (context.read<WorkflowBloc>().state as WorkflowLoaded).projectStatus.projectId;
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => RiskDashboardScreen(projectId: projectId),
                ),
              );
            },
            tooltip: 'View Risk Dashboard',
          ),
          IconButton(
            icon: const Icon(Icons.attach_money),
            onPressed: () {
              final projectId = (context.read<WorkflowBloc>().state as WorkflowLoaded).projectStatus.projectId;
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => FinancialDashboardScreen(projectId: projectId),
                ),
              );
            },
            tooltip: 'View Financial Dashboard',
          ),
          IconButton(
            icon: const Icon(Icons.lightbulb_outline),
            onPressed: () {
              final projectId = (context.read<WorkflowBloc>().state as WorkflowLoaded).projectStatus.projectId;
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => KnowledgeDashboardScreen(projectId: projectId),
                ),
              );
            },
            tooltip: 'View Knowledge Dashboard',
          ),
        ],
      ),
      body: BlocBuilder<WorkflowBloc, WorkflowState>(
        builder: (context, state) {
          if (state is WorkflowLoading) {
            return const Center(child: CircularProgressIndicator());
          } else if (state is WorkflowError) {
            return Center(child: Text('Error: ${state.message}'));
          } else if (state is WorkflowLoaded) {
            final projectStatus = state.projectStatus;
            return ListView.builder(
              itemCount: projectStatus.stages.length,
              itemBuilder: (context, index) {
                final stage = projectStatus.stages[index];
                return _buildStage(context, stage, state.projectStatus.pendingGate);
              },
            );
          } else {
            return const Center(child: Text('No project data found.'));
          }
        },
      ),
    );
  }

  Widget _buildStage(BuildContext context, WorkflowStage stage, String? pendingGate) {
    Widget? subtitle;

    if (stage.status == 'Completed') {
      subtitle = Text('${stage.artifacts.length} artifacts generated');
    } else if (stage.status == 'Pending') {
      subtitle = const Text('This stage is ready');
    }

    final gateForThisStage = STAGE_GATES[stage.stageId];

    return ExpansionTile(
      title: Text('${stage.stageId}. ${stage.name}'),
      subtitle: subtitle,
      initiallyExpanded: stage.status == 'Pending',
      children: [
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (stage.status == 'Completed') ...[
                const Text('Artifacts:', style: TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                ...stage.artifacts.map((artifact) => _buildArtifactContent(context, artifact)).toList(),
              ],
              if (stage.status == 'Pending' && pendingGate != null && gateForThisStage == pendingGate) ...[
                 ElevatedButton(
                    onPressed: () => _showApprovalDialog(context, pendingGate),
                    child: Text('Approve Gate $pendingGate'),
                  )
              ],
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildArtifactContent(BuildContext context, Artifact artifact) {
    if (artifact.type == '2d_plan') {
      final bytes = base64Decode(artifact.content as String);
      return Image.memory(bytes);
    } else if (artifact.type == '3d_plan') {
      return ElevatedButton(
        onPressed: () {
          showDialog(
            context: context,
            builder: (context) {
              return AlertDialog(
                title: const Text('Save 3D Model'),
                content: SingleChildScrollView(
                  child: SelectableText(artifact.content as String),
                ),
                actions: [
                  TextButton(
                    onPressed: () {
                      Navigator.of(context).pop();
                    },
                    child: const Text('Close'),
                  ),
                ],
              );
            },
          );
        },
        child: const Text('View 3D Model'),
      );
    } else if (artifact.type == 'video') {
      final decodedContent = utf8.decode(base64.decode(artifact.content as String));
      return Text(decodedContent);
    } else if (artifact.type == 'image_base64') {
      return _buildBase64Image(artifact.name, artifact.content as String);
    } else if (artifact.type == 'site_plan_image') {
      return _buildBase64Image(artifact.name, artifact.content as String);
    } else if (artifact.type == 'mep_drawing_image') {
      return _buildBase64Image(artifact.name, artifact.content as String);
    } else if (artifact.type == 'floor_plan_image') {
      return _buildBase64Image(artifact.name, artifact.content as String);
    } else if (artifact.type == 'elevation_drawing_image') {
      return _buildBase64Image(artifact.name, artifact.content as String);
    } else if (artifact.type == 'cross_section_drawing_image') {
      return _buildBase64Image(artifact.name, artifact.content as String);
    } else if (artifact.type == 'roof_plan_drawing_image') {
      return _buildBase64Image(artifact.name, artifact.content as String);
    } else if (artifact.type == 'structural_drawing_image') {
      return _buildBase64Image(artifact.name, artifact.content as String);
    } else if (artifact.type == 'furniture_layout_image') {
      return _buildBase64Image(artifact.name, artifact.content as String);
    } else if (artifact.type == 'rcp_drawing_image') {
      return _buildBase64Image(artifact.name, artifact.content as String);
    } else if (artifact.type == 'interior_elevation_image') {
      return _buildBase64Image(artifact.name, artifact.content as String);
    } else if (artifact.type == 'lighting_plan_image') {
      return _buildBase64Image(artifact.name, artifact.content as String);
    } else if (artifact.type == 'finishing_schedule_image') {
      return _buildBase64Image(artifact.name, artifact.content as String);
    } else if (artifact.type == 'millwork_drawing_image') {
      return _buildBase64Image(artifact.name, artifact.content as String);
    } else if (artifact.type == 'interior_plumbing_electrical_layout_image') {
      return _buildBase64Image(artifact.name, artifact.content as String);
    } else if (artifact.type == '3d_rendering') {
      return UrlViewer(title: artifact.name, url: (artifact.content as Map<String, dynamic>)['url']);
    } else if (artifact.type == 'virtual_tour') {
      return UrlViewer(title: artifact.name, url: (artifact.content as Map<String, dynamic>)['url']);
    } else if (artifact.type == 'code_compliance_sheet_image') {
      return _buildBase64Image(artifact.name, artifact.content as String);
    } else if (artifact.type == 'shop_drawing_image') {
      return _buildBase64Image(artifact.name, artifact.content as String);
    } else if (artifact.type == 'demolition_plan_image') {
      return _buildBase64Image(artifact.name, artifact.content as String);
    } else if (artifact.type == 'phasing_drawing_image') {
      return _buildBase64Image(artifact.name, artifact.content as String);
    } else if (artifact.type == 'mood_board') {
      return UrlViewer(title: artifact.name, url: (artifact.content as Map<String, dynamic>)['url']);
    } else if (artifact.type == '3d_conceptual_sketch') {
      return UrlViewer(title: artifact.name, url: (artifact.content as Map<String, dynamic>)['url']);
    } else if (artifact.type == 'photorealistic_rendering') {
      return UrlViewer(title: artifact.name, url: (artifact.content as Map<String, dynamic>)['url']);
    } else if (artifact.type == 'vr_walkthrough') {
      return UrlViewer(title: artifact.name, url: (artifact.content as Map<String, dynamic>)['url']);
    } else if (artifact.content is Map<String, dynamic>) {
      return _buildJsonContentDisplay(artifact.name, artifact.content as Map<String, dynamic>);
    } else if (artifact.content is String) {
      return Text(artifact.content as String);
    } else {
      return Text('Unsupported artifact type');
    }
  }

  Widget _buildBase64Image(String name, String content) {
    debugPrint('Building base64 image for $name');
    try {
      final bytes = base64Decode(content);
      return ExpansionTile(
        title: Text(name),
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Image.memory(bytes, fit: BoxFit.contain),
          ),
        ],
      );
    } catch (e) {
      debugPrint('Error decoding base64 string for $name: $e');
      // Not a base64 string, treat as plain text
      return ExpansionTile(
        title: Text(name),
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: SelectableText(content),
          ),
        ],
      );
    }
  }

  Widget _buildJsonContentDisplay(String name, Map<String, dynamic> jsonContent) {
    return ExpansionTile(
      title: Text(name),
      children: [
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: _buildFormattedJson(jsonContent),
        ),
      ],
    );
  }

  Widget _buildFormattedJson(Map<String, dynamic> jsonContent) {
    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: jsonContent.length,
      itemBuilder: (context, index) {
        final key = jsonContent.keys.elementAt(index);
        final value = jsonContent[key];

        if (value is Map<String, dynamic>) {
          return ExpansionTile(
            title: Text(key, style: const TextStyle(fontWeight: FontWeight.bold)),
            children: [_buildFormattedJson(value)],
          );
        } else if (value is List) {
          return ExpansionTile(
            title: Text(key, style: const TextStyle(fontWeight: FontWeight.bold)),
            children: value.map((item) {
              if (item is Map<String, dynamic>) {
                return _buildFormattedJson(item);
              } else {
                return ListTile(title: Text(item.toString()));
              }
            }).toList(),
          );
        } else {
          return ListTile(
            title: Text(key, style: const TextStyle(fontWeight: FontWeight.bold)),
            subtitle: Text(value.toString()),
          );
        }
      },
    );
  }

  Future<void> _showApprovalDialog(BuildContext context, String gateId) async {
    final commentsController = TextEditingController();
    return showDialog<void>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text('Approve Gate $gateId'),
          content: TextField(
            controller: commentsController,
            decoration: const InputDecoration(hintText: "Add comments (optional)"),
          ),
          actions: <Widget>[
            TextButton(
              child: const Text('Cancel'),
              onPressed: () => Navigator.of(context).pop(),
            ),
            ElevatedButton(
              child: const Text('Approve'),
              onPressed: () async {
                Navigator.of(context).pop();
                try {
                  final request = GateApprovalRequest(
                    approvedBy: 'FlutterAppUser', // Placeholder user
                    comments: commentsController.text,
                  );
                  final projectId = (context.read<WorkflowBloc>().state as WorkflowLoaded).projectStatus.projectId;
                  await context.read<WorkflowBloc>().apiService.approveGate(projectId, gateId, request);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Gate $gateId approved successfully!'), backgroundColor: Colors.green),
                  );
                  context.read<WorkflowBloc>().add(LoadWorkflow(projectId)); // Refresh the workflow
                } catch (e) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Error approving gate: $e'), backgroundColor: Colors.red),
                  );
                }
              },
            ),
          ],
        );
      },
    );
  }
}
