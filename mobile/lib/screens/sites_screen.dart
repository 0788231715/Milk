import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';
import '../services/api_service.dart';
import 'add_resource_screen.dart';
import 'site_details_screen.dart';

class SitesScreen extends StatefulWidget {
  const SitesScreen({super.key});

  @override
  State<SitesScreen> createState() => _SitesScreenState();
}

class _SitesScreenState extends State<SitesScreen> {
  final ApiService _apiService = ApiService();
  List<dynamic>? _sites;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _fetchSites();
  }

  Future<void> _fetchSites() async {
    setState(() { _isLoading = true; _error = null; });
    try {
      final sites = await _apiService.getSites();
      setState(() { _sites = sites; _isLoading = false; });
    } catch (e) {
      setState(() { _error = 'Cannot connect to server'; _isLoading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: const Text('Collection Sites', style: TextStyle(fontWeight: FontWeight.w900, color: Color(0xFF1E293B))),
        backgroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            onPressed: () async {
              final result = await Navigator.push(context, MaterialPageRoute(builder: (_) => const AddResourceScreen(resourceType: 'Site')));
              if (result == true) _fetchSites();
            },
            icon: const Icon(LucideIcons.plus, color: Color(0xFF2563EB)),
          ),
          IconButton(onPressed: _fetchSites, icon: const Icon(LucideIcons.refreshCcw, size: 18))
        ],
      ),
      body: _isLoading 
        ? const Center(child: CircularProgressIndicator())
        : _error != null
          ? Center(child: Text(_error!))
          : ListView.builder(
              padding: const EdgeInsets.all(24),
              itemCount: _sites?.length ?? 0,
              itemBuilder: (context, index) {
                final site = _sites![index];
                return GestureDetector(
                  onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => SiteDetailsScreen(site: site))),
                  child: _buildSiteDetailCard(site),
                );
              },
            ),
    );
  }

  Widget _buildSiteDetailCard(dynamic site) {
    return Container(
      margin: const EdgeInsets.only(bottom: 20),
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(32),
        border: Border.all(color: const Color(0xFFF1F5F9)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(16)),
                child: const Icon(LucideIcons.mapPin, color: Color(0xFF3B82F6), size: 24),
              ),
              PopupMenuButton(
                itemBuilder: (context) => [
                  const PopupMenuItem(value: 'add_supplier', child: Text('Add Supplier to this Site')),
                ],
                onSelected: (value) async {
                  if (value == 'add_supplier') {
                    final result = await Navigator.push(context, MaterialPageRoute(builder: (_) => AddResourceScreen(
                      resourceType: 'Supplier',
                      initialData: {'site': site['id']},
                    )));
                    if (result == true) _fetchSites();
                  }
                },
              )
            ],
          ),
          const SizedBox(height: 20),
          Text(site['name'] ?? 'Unknown Site', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Color(0xFF1E293B))),
          const SizedBox(height: 4),
          Text(site['location'] ?? 'No location set', style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 13)),
          const SizedBox(height: 24),
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('COLLECTED', style: TextStyle(color: Color(0xFF94A3B8), fontSize: 10, fontWeight: FontWeight.bold)),
                    Text('${site['total_collected'] ?? 0} L', style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF1E293B))),
                  ],
                ),
              ),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('REVENUE', style: TextStyle(color: Color(0xFF94A3B8), fontSize: 10, fontWeight: FontWeight.bold)),
                    Text('${site['total_revenue'] ?? 0} RWF', style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF3B82F6))),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
