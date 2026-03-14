import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';
import 'add_resource_screen.dart';

class ListScreen extends StatefulWidget {
  final String title;
  final Future<List<dynamic>> Function() fetchFunction;

  const ListScreen(
      {super.key, required this.title, required this.fetchFunction});

  @override
  State<ListScreen> createState() => _ListScreenState();
}

class _ListScreenState extends State<ListScreen> {
  List<dynamic>? _items;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _fetchItems();
  }

  Future<void> _fetchItems() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final items = await widget.fetchFunction();
      setState(() {
        _items = items;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = 'Failed to load ${widget.title.toLowerCase()}';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    // Determine resource type for adding
    String resourceType = widget.title.endsWith('s')
        ? widget.title.substring(0, widget.title.length - 1)
        : widget.title;

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title,
            style: const TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        elevation: 0,
        foregroundColor: const Color(0xFF1E293B),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () async {
          final result = await Navigator.push(
              context,
              MaterialPageRoute(
                  builder: (_) =>
                      AddResourceScreen(resourceType: resourceType)));
          if (result == true) _fetchItems();
        },
        backgroundColor: const Color(0xFF2563EB),
        child: const Icon(LucideIcons.plus, color: Colors.white),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(
                  child:
                      Text(_error!, style: const TextStyle(color: Colors.red)))
              : RefreshIndicator(
                  onRefresh: _fetchItems,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _items?.length ?? 0,
                    itemBuilder: (context, index) {
                      final item = _items![index];
                      return Card(
                        margin: const EdgeInsets.only(bottom: 12),
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(16)),
                        child: ListTile(
                          contentPadding: const EdgeInsets.all(16),
                          title: Text(item['name'] ?? 'Unknown',
                              style:
                                  const TextStyle(fontWeight: FontWeight.bold)),
                          subtitle: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(item['contact'] ?? 'No contact'),
                              if (item['role'] != null)
                                Text('Role: ${item['role']}',
                                    style: const TextStyle(
                                        fontSize: 12, color: Colors.blueGrey)),
                            ],
                          ),
                          trailing: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: [
                              Text(
                                  '${item['current_balance'] ?? item['base_pay'] ?? 0} RWF',
                                  style: const TextStyle(
                                      fontWeight: FontWeight.bold,
                                      color: Color(0xFF2563EB))),
                              Text(
                                  item['base_pay'] != null
                                      ? 'Base Pay'
                                      : 'Balance',
                                  style: const TextStyle(
                                      fontSize: 10, color: Color(0xFF64748B))),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
    );
  }
}
