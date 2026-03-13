import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';
import '../services/api_service.dart';

class SiteDetailsScreen extends StatefulWidget {
  final dynamic site;
  const SiteDetailsScreen({super.key, required this.site});

  @override
  State<SiteDetailsScreen> createState() => _SiteDetailsScreenState();
}

class _SiteDetailsScreenState extends State<SiteDetailsScreen> {
  final ApiService _apiService = ApiService();
  List<dynamic> _supplies = [];
  List<dynamic> _sales = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      final supplies = await _apiService.getSupplyRecords(siteId: widget.site['id']);
      final sales = await _apiService.getSaleRecords(siteId: widget.site['id']);
      setState(() {
        _supplies = supplies;
        _sales = sales;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        backgroundColor: const Color(0xFFF8FAFC),
        appBar: AppBar(
          title: Text(widget.site['name']),
          elevation: 0,
          backgroundColor: Colors.white,
          foregroundColor: Colors.black,
          bottom: const TabBar(
            labelColor: Colors.blue,
            unselectedLabelColor: Colors.grey,
            indicatorColor: Colors.blue,
            tabs: [
              Tab(text: 'Intake (Suppliers)'),
              Tab(text: 'Sales (Buyers)'),
            ],
          ),
        ),
        body: _isLoading 
          ? const Center(child: CircularProgressIndicator())
          : TabBarView(
              children: [
                _buildRecordList(_supplies, isSupply: true),
                _buildRecordList(_sales, isSupply: false),
              ],
            ),
        floatingActionButton: FloatingActionButton(
          onPressed: () => _showAddRecordModal(),
          backgroundColor: Colors.blue,
          child: const Icon(LucideIcons.plus),
        ),
      ),
    );
  }

  Widget _buildRecordList(List<dynamic> records, {required bool isSupply}) {
    if (records.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(isSupply ? LucideIcons.truck : LucideIcons.shoppingBag, size: 64, color: Colors.grey.shade300),
            const SizedBox(height: 16),
            Text('No ${isSupply ? "intake" : "sales"} records found', style: TextStyle(color: Colors.grey.shade500)),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: records.length,
      itemBuilder: (context, index) {
        final record = records[index];
        final name = isSupply ? record['supplier_name'] : record['buyer_name'];
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: isSupply ? Colors.blue.shade50 : Colors.indigo.shade50,
              child: Icon(isSupply ? LucideIcons.arrowDownLeft : LucideIcons.arrowUpRight, 
                          color: isSupply ? Colors.blue : Colors.indigo, size: 18),
            ),
            title: Text(name ?? 'Unknown', style: const TextStyle(fontWeight: FontWeight.bold)),
            subtitle: Text(record['date']),
            trailing: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text('${record['litres']} L', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                Text('RWF ${record['total_cost'] ?? record['total_revenue']}', 
                     style: TextStyle(color: Colors.grey.shade500, fontSize: 11)),
              ],
            ),
          ),
        );
      },
    );
  }

  void _showAddRecordModal() {
    // Implementation for adding records via mobile
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Recording via mobile coming soon. Use web portal for grid entry.'))
    );
  }
}
