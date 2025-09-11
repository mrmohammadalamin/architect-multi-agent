import 'package:flutter/material.dart';
import '../services/api_service.dart';

class KnowledgeDashboardScreen extends StatefulWidget {
  final String projectId;

  const KnowledgeDashboardScreen({super.key, required this.projectId});

  @override
  State<KnowledgeDashboardScreen> createState() => _KnowledgeDashboardScreenState();
}

class _KnowledgeDashboardScreenState extends State<KnowledgeDashboardScreen> {
  late Future<Map<String, dynamic>> _knowledgeSummaryFuture;
  final ApiService _apiService = ApiService();

  @override
  void initState() {
    super.initState();
    _knowledgeSummaryFuture = _apiService.getKnowledgeSummary(widget.projectId);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Knowledge Dashboard'),
        centerTitle: true,
      ),
      body: FutureBuilder<Map<String, dynamic>>(
        future: _knowledgeSummaryFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          }
          if (!snapshot.hasData || snapshot.data!['lessons_learned_summary'] == null) {
            return const Center(child: Text('No knowledge data found for this project.'));
          }

          final knowledgeData = snapshot.data!;

          return ListView(
            padding: const EdgeInsets.all(16.0),
            children: [
              Card(
                margin: const EdgeInsets.symmetric(vertical: 8.0),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Lessons Learned Summary:', style: Theme.of(context).textTheme.titleLarge),
                      const SizedBox(height: 8),
                      Text(
                        knowledgeData['lessons_learned_summary'] ?? 'N/A',
                        style: Theme.of(context).textTheme.bodyLarge,
                      ),
                    ],
                  ),
                ),
              ),
              _buildSection('Key Successes', knowledgeData['key_successes']),
              _buildSection('Challenges Encountered', knowledgeData['challenges_encountered']),
              _buildSection('Actionable Lessons', knowledgeData['actionable_lessons']),
            ],
          );
        },
      ),
    );
  }

  Widget _buildSection(String title, List<dynamic>? items) {
    if (items == null || items.isEmpty) {
      return const SizedBox.shrink();
    }
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8.0),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: Theme.of(context).textTheme.headlineSmall),
            const SizedBox(height: 8),
            ...items.map((item) => Padding(
              padding: const EdgeInsets.only(bottom: 4.0),
              child: Text('- $item', style: Theme.of(context).textTheme.bodyMedium),
            )).toList(),
          ],
        ),
      ),
    );
  }
}
