import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';
import '../services/api_service.dart';

class TransactionsScreen extends StatefulWidget {
  const TransactionsScreen({super.key});

  @override
  State<TransactionsScreen> createState() => _TransactionsScreenState();
}

class _TransactionsScreenState extends State<TransactionsScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final ApiService _apiService = ApiService();
  
  List<dynamic>? _supplies;
  List<dynamic>? _sales;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _fetchData();
  }

  Future<void> _fetchData() async {
    setState(() => _isLoading = true);
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
    return Scaffold(
      appBar: AppBar(
        title: const Text('Transactions', style: TextStyle(fontWeight: FontWeight.bold)),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [Tab(text: 'Supplies'), Tab(text: 'Sales')],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : TabBarView(
              controller: _tabController,
              children: [
                _buildList(_supplies ?? [], 'litres', 'total_cost', true),
                _buildList(_sales ?? [], 'litres', 'total_revenue', false),
              ],
            ),
    );
  }

  Widget _buildList(List<dynamic> items, String volumeKey, String amountKey, bool isSupply) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: items.length,
      itemBuilder: (context, index) {
        final item = items[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: ListTile(
            title: Text('${item[volumeKey]} L @ ${item['price_per_litre']} RWF'),
            subtitle: Text(item['date'].toString().split('T')[0]),
            trailing: Text(
              '${item[amountKey]} RWF',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: isSupply ? Colors.red : Colors.green,
              ),
            ),
          ),
        );
      },
    );
  }
}
