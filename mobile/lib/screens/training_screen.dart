import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';
import '../services/api_service.dart';

class TrainingScreen extends StatefulWidget {
  const TrainingScreen({super.key});

  @override
  State<TrainingScreen> createState() => _TrainingScreenState();
}

class _TrainingScreenState extends State<TrainingScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final ApiService _apiService = ApiService();
  bool _isLoading = true;
  List<dynamic>? _resources;
  List<dynamic>? _standards;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _fetch();
  }

  Future<void> _fetch() async {
    try {
      final res = await _apiService.getTrainingResources();
      final std = await _apiService.getMilkStandards();
      setState(() { _resources = res; _standards = std; _isLoading = false; });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Training & Standards'),
        bottom: TabBar(controller: _tabController, tabs: const [Tab(text: 'Resources'), Tab(text: 'Standards')]),
      ),
      body: _isLoading 
        ? const Center(child: CircularProgressIndicator())
        : TabBarView(
            controller: _tabController,
            children: [
              _buildList(_resources ?? [], LucideIcons.bookOpen),
              _buildList(_standards ?? [], LucideIcons.checkCircle),
            ],
          ),
    );
  }

  Widget _buildList(List<dynamic> items, IconData icon) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: items.length,
      itemBuilder: (context, index) {
        final item = items[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: ListTile(
            leading: Icon(icon, color: const Color(0xFF2563EB)),
            title: Text(item['title'] ?? 'Standard Item', style: const TextStyle(fontWeight: FontWeight.bold)),
            subtitle: Text(item['description'] ?? item['guidelines'] ?? ''),
            onTap: () {},
          ),
        );
      },
    );
  }
}
