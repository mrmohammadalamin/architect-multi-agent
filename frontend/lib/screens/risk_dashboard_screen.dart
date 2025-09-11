import 'package:flutter/material.dart';
import '../services/api_service.dart';

class RiskDashboardScreen extends StatefulWidget {
  final String projectId;

  const RiskDashboardScreen({super.key, required this.projectId});

  @override
  State<RiskDashboardScreen> createState() => _RiskDashboardScreenState();
}

class _RiskDashboardScreenState extends State<RiskDashboardScreen> {
  late Future<Map<String, dynamic>> _riskSummaryFuture;
  final ApiService _apiService = ApiService();

  @override
  void initState() {
    super.initState();
    _riskSummaryFuture = _apiService.getRiskSummary(widget.projectId);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Risk Dashboard'),
        centerTitle: true,
      ),
      body: FutureBuilder<Map<String, dynamic>>(
        future: _riskSummaryFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          }
          if (!snapshot.hasData || snapshot.data!['risk_register'] == null || snapshot.data!['risk_register'].isEmpty) {
            return const Center(child: Text('No risk data found for this project.'));
          }

          final riskRegister = snapshot.data!['risk_register'] as List;

          return ListView.builder(
            padding: const EdgeInsets.all(16.0),
            itemCount: riskRegister.length,
            itemBuilder: (context, index) {
              final risk = riskRegister[index];
              return Card(
                margin: const EdgeInsets.symmetric(vertical: 8.0),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        risk['risk_description'] ?? 'N/A',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Category: ${risk['risk_category'] ?? 'N/A'}',
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Mitigation: ${risk['mitigation_strategy'] ?? 'N/A'}',
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                    ],
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
