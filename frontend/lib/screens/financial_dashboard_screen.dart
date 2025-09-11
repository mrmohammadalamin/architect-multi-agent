import 'package:flutter/material.dart';
import '../services/api_service.dart';

class FinancialDashboardScreen extends StatefulWidget {
  final String projectId;

  const FinancialDashboardScreen({super.key, required this.projectId});

  @override
  State<FinancialDashboardScreen> createState() => _FinancialDashboardScreenState();
}

class _FinancialDashboardScreenState extends State<FinancialDashboardScreen> {
  late Future<Map<String, dynamic>> _financialSummaryFuture;
  final ApiService _apiService = ApiService();

  @override
  void initState() {
    super.initState();
    _financialSummaryFuture = _apiService.getFinancialSummary(widget.projectId);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Financial Dashboard'),
        centerTitle: true,
      ),
      body: FutureBuilder<Map<String, dynamic>>(
        future: _financialSummaryFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          }
          if (!snapshot.hasData || snapshot.data!['total_estimated_cost_usd'] == null) {
            return const Center(child: Text('No financial data found for this project.'));
          }

          final financialData = snapshot.data!;
          final costBreakdown = financialData['cost_breakdown'] as Map<String, dynamic>?;

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
                      Text('Total Estimated Cost:', style: Theme.of(context).textTheme.titleLarge),
                      const SizedBox(height: 8),
                      //  done TODO: Display total estimated cost here. Manual fix needed due to string literal issues.
                       
                      Text(
                        '\$${(financialData['total_estimated_cost_usd'] as num?)?.toStringAsFixed(2) ?? 'N/A'}',
                        style: Theme.of(context).textTheme.headlineMedium?.copyWith(color: Colors.green.shade700),
                      ),
      
                      const SizedBox(height: 16),
                      Text('Estimated Duration:', style: Theme.of(context).textTheme.titleLarge),
                      const SizedBox(height: 8),
                      Text(
                        '${financialData['estimated_duration_weeks'] ?? 'N/A'} weeks',
                        style: Theme.of(context).textTheme.bodyLarge,
                      ),
                    ],
                  ),
                ),
              ),
              if (costBreakdown != null) ...[
                const SizedBox(height: 16),
                Text('Cost Breakdown:', style: Theme.of(context).textTheme.headlineSmall),
                const SizedBox(height: 8),
                ...costBreakdown.entries.map((entry) => Card(
                  margin: const EdgeInsets.symmetric(vertical: 4.0),
                  child: Padding(
                    padding: const EdgeInsets.all(12.0),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(entry.key.replaceAll('_', ' ').toUpperCase(), style: Theme.of(context).textTheme.bodyLarge),
                        Text('${entry.value}', style: Theme.of(context).textTheme.bodyMedium),
                      ],
                    ),
                  ),
                )).toList(),
              ],
              const SizedBox(height: 16),
              Text('Key Phases:', style: Theme.of(context).textTheme.headlineSmall),
              const SizedBox(height: 8),
              if (financialData['key_phases'] != null) ...[
                ... (financialData['key_phases'] as List).map((phase) => Card(
                  margin: const EdgeInsets.symmetric(vertical: 4.0),
                  child: Padding(
                    padding: const EdgeInsets.all(12.0),
                    child: Text(phase, style: Theme.of(context).textTheme.bodyLarge),
                  ),
                )).toList(),
              ]
            ],
          );
        },
      ),
    );
  }
}