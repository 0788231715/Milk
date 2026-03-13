import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';
import '../services/api_service.dart';

class TransactionsScreen extends StatefulWidget {
  const TransactionsScreen({super.key});

  @override
  State<TransactionsScreen> createState() => _TransactionsScreenState();
}

class _TransactionsScreenState extends State<TransactionsScreen> {
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
      final supplies = await _apiService.getSupplyRecords();
      final sales = await _apiService.getSaleRecords();
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
        appBar: AppBar(
          title: const Text('Transactions', style: TextStyle(fontWeight: FontWeight.bold)),
          elevation: 0,
          backgroundColor: Colors.white,
          foregroundColor: Colors.black,
          bottom: const TabBar(
            labelColor: Colors.blue,
            unselectedLabelColor: Colors.grey,
            indicatorColor: Colors.blue,
            tabs: [
              Tab(text: 'Supplies'),
              Tab(text: 'Sales'),
            ],
          ),
        ),
        body: _isLoading 
          ? const Center(child: CircularProgressIndicator())
          : TabBarView(
              children: [
                _buildList(_supplies, true),
                _buildList(_sales, false),
              ],
            ),
      ),
    );
  }

  Widget _buildList(List<dynamic> items, bool isSupply) {
    if (items.isEmpty) return const Center(child: Text('No records found'));
    
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: items.length,
      itemBuilder: (context, index) {
        final item = items[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: isSupply ? Colors.blue.shade50 : Colors.indigo.shade50,
              child: Icon(isSupply ? LucideIcons.arrowDownLeft : LucideIcons.arrowUpRight, 
                          color: isSupply ? Colors.blue : Colors.indigo, size: 18),
            ),
            title: Text(isSupply ? item['supplier_name'] ?? 'Supplier' : item['buyer_name'] ?? 'Buyer', 
                        style: const TextStyle(fontWeight: FontWeight.bold)),
            subtitle: Text(item['date']),
            trailing: Text('RWF ${item['total_cost'] ?? item['total_revenue']}', 
                           style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.blue)),
          ),
        );
      },
    );
  }
}
